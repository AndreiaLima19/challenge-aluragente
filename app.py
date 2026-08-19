import re

import faiss
import pdfplumber
import numpy as np
import streamlit as st

from sentence_transformers import SentenceTransformer
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)



# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Agente IA para análise de PDF",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Agente IA para análise de PDF")

st.write("Selecione um documento PDF para começar.")


# ============================================================
# FUNÇÕES DE PROCESSAMENTO
# ============================================================

def limpar_texto(texto):
    texto = re.sub(r"\n+", "\n", texto)
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\s{2,}", " ", texto)

    return texto.strip()


def extrair_paginas(pdf_file):
    paginas = []

    with pdfplumber.open(pdf_file) as pdf:

        for numero, pagina in enumerate(pdf.pages, start=1):

            texto = pagina.extract_text()

            if texto:
                paginas.append({
                    "pagina": numero,
                    "texto": limpar_texto(texto)
                })

    return paginas


def criar_chunks_paginas(
    paginas,
    tamanho=600,
    sobreposicao_palavras=80
):

    chunks = []

    for item in paginas:

        palavras = item["texto"].split()

        atual = []
        contador = 0

        for palavra in palavras:

            atual.append(palavra)
            contador += len(palavra) + 1

            if contador >= tamanho:

                chunks.append({
                    "pagina": item["pagina"],
                    "texto": " ".join(atual)
                })

                atual = atual[-sobreposicao_palavras:]

                contador = sum(
                    len(p) + 1
                    for p in atual
                )

        if atual:

            chunks.append({
                "pagina": item["pagina"],
                "texto": " ".join(atual)
            })

    return chunks


# ============================================================
# MODELOS
# ============================================================

@st.cache_resource
def carregar_modelo_embedding():

    return SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )


@st.cache_resource
def carregar_llm():

    tokenizer = AutoTokenizer.from_pretrained(
        "google/flan-t5-base"
    )

    model = AutoModelForSeq2SeqLM.from_pretrained(
        "google/flan-t5-base"
    )

    return tokenizer, model



# ============================================================
# CRIAÇÃO DO ÍNDICE FAISS
# ============================================================

def criar_indice(chunks, modelo_embedding):

    textos_chunks = [
        chunk["texto"]
        for chunk in chunks
    ]

    embeddings = modelo_embedding.encode(
        textos_chunks,
        convert_to_numpy=True,
        show_progress_bar=False
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(
        embeddings.shape[1]
    )

    index.add(embeddings)

    return index


# ============================================================
# BUSCA SEMÂNTICA
# ============================================================

def buscar_contexto(
    pergunta,
    chunks,
    index,
    modelo_embedding,
    k=5,
    limiar=0.32
):

    pergunta_emb = modelo_embedding.encode(
        [pergunta],
        convert_to_numpy=True
    )

    pergunta_emb = np.asarray(
        pergunta_emb,
        dtype="float32"
    )

    faiss.normalize_L2(pergunta_emb)

    scores, ids = index.search(
        pergunta_emb,
        min(k, len(chunks))
    )

    resultados = []

    for score, idx in zip(
        scores[0],
        ids[0]
    ):

        if idx == -1:
            continue

        if score >= limiar:

            resultados.append({
                "pagina": chunks[idx]["pagina"],
                "texto": chunks[idx]["texto"],
                "score": float(score)
            })

    return resultados


# ============================================================
# GERAÇÃO DA RESPOSTA
# ============================================================

def responder(
    pergunta,
    chunks,
    index,
    modelo_embedding,
    llm
):

    resultados = buscar_contexto(
        pergunta=pergunta,
        chunks=chunks,
        index=index,
        modelo_embedding=modelo_embedding,
        k=5,
        limiar=0.20
    )

    if not resultados:
        return {
            "resposta": (
                "Não encontrei essa informação "
                "no documento."
            ),
            "paginas": []
        }

    # Ordena os resultados do mais relevante
    # para o menos relevante
    resultados = sorted(
        resultados,
        key=lambda x: x["score"],
        reverse=True
    )

    contexto = ""

    paginas_utilizadas = []

    for resultado in resultados:

        paginas_utilizadas.append(
            resultado["pagina"]
        )

        contexto += (
            f"\n[PÁGINA {resultado['pagina']}]\n"
            f"{resultado['texto']}\n"
        )

    # Mantém somente uma quantidade razoável
    # de caracteres para o modelo
    contexto = contexto[:3500]

    prompt = f"""
Você é um assistente que responde perguntas
sobre documentos.

Use somente as informações do CONTEXTO.

Não invente informações.

Se a resposta estiver no contexto,
responda de forma completa e clara.

Se houver várias informações relacionadas
à pergunta, inclua todas elas.

Se a informação não estiver no contexto,
responda:

"Não encontrei essa informação no documento."

CONTEXTO:

{contexto}

PERGUNTA:

{pergunta}

RESPOSTA:
"""

    tokenizer, model = llm

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=768

    )

    outputs = model.generate(
        **inputs,
        max_new_tokens=300,
        min_new_tokens=20,
        num_beams=4,
        early_stopping=True
    )

    resposta = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    ).strip()

    # Corrige "PGINA" gerado pelo modelo para "PÁGINA"
    resposta = re.sub(
        r"\bPGINA\s*(\d+)",
        r"PÁGINA \1",
        resposta,
        flags=re.IGNORECASE
    )

    # Corrige também "PGINA" sem número
    resposta = re.sub(
        r"\bPGINA\b",
        "PÁGINA",
        resposta,
        flags=re.IGNORECASE
    )

    return {
        "resposta": resposta,
        "paginas": sorted(
            set(paginas_utilizadas)
        )
    }




# ============================================================
# UPLOAD DO PDF
# ============================================================

arquivo_pdf = st.file_uploader(
    "Escolha um arquivo PDF",
    type=["pdf"]
)


if arquivo_pdf is not None:

    st.success(
        f"PDF selecionado: {arquivo_pdf.name}"
    )

    # --------------------------------------------------------
    # EXTRAÇÃO
    # --------------------------------------------------------

    with st.spinner("Lendo o PDF..."):

        paginas = extrair_paginas(
            arquivo_pdf
        )

    if not paginas:

        st.error(
            "Não foi possível extrair texto "
            "deste PDF."
        )

        st.stop()

    st.info(
        f"{len(paginas)} páginas com texto foram lidas."
    )


    # --------------------------------------------------------
    # CHUNKS
    # --------------------------------------------------------

    with st.spinner("Criando trechos do documento..."):

        chunks = criar_chunks_paginas(
            paginas
        )

    st.info(
        f"{len(chunks)} trechos foram criados."
    )


    # --------------------------------------------------------
    # MODELO DE EMBEDDINGS
    # --------------------------------------------------------

    with st.spinner(
        "Carregando modelo de embeddings..."
    ):

        modelo_embedding = (
            carregar_modelo_embedding()
        )


    # --------------------------------------------------------
    # FAISS
    # --------------------------------------------------------

    with st.spinner(
        "Criando índice vetorial FAISS..."
    ):

        index = criar_indice(
            chunks,
            modelo_embedding
        )


    st.success(
        "Índice vetorial criado com sucesso."
    )


    # --------------------------------------------------------
    # FLAN-T5
    # --------------------------------------------------------

    with st.spinner(
        "Carregando modelo de IA..."
    ):

        llm = carregar_llm()


    st.success(
        "Agente de IA pronto!"
    )


    # ========================================================
    # INTERFACE DE PERGUNTAS
    # ========================================================

    st.divider()

    st.subheader(
        "💬 Faça uma pergunta sobre o documento"
    )

    pergunta = st.text_input(
        "Digite sua pergunta:",
        placeholder=(
            "Ex.: Qual é o principal objetivo "
            "do documento?"
        )
    )


    if st.button(
        "🔎 Perguntar",
        type="primary"
    ):

        if not pergunta.strip():

            st.warning(
                "Digite uma pergunta antes de continuar."
            )

        else:

            with st.spinner(
                "Analisando o documento..."
            ):

                resultado = responder(
                    pergunta=pergunta,
                    chunks=chunks,
                    index=index,
                    modelo_embedding=modelo_embedding,
                    llm=llm
                )


            # ------------------------------------------------
            # RESPOSTA
            # ------------------------------------------------

            st.subheader("🤖 Resposta")

            st.write(
                resultado["resposta"]
            )


            # ------------------------------------------------
            # PÁGINAS UTILIZADAS
            # ------------------------------------------------

            if resultado["paginas"]:

                paginas_consultadas = ", ".join(
                    map(
                        str,
                        resultado["paginas"]
                    )
                )

                st.caption(
                    "📄 Páginas consultadas: "
                    f"{paginas_consultadas}"
                )

else:

    st.info(
        "👆 Envie um arquivo PDF para começar."
    )
