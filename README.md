# Challenge Alura Agente


## 🚀 Aplicação

👉 [Acesse a aplicação](https://challenge-aluragente.streamlit.app/)

## 📋 Sobre o projeto

O objetivo é desenvolver um agente de inteligência artificial que consiga responder a perguntas sobre o documento escolhido (PDF), buscando as informações e devolvendo-as de forma clara.

A melhor arquitetura para um agente de IA é RAG (Retrieval-Augmented Generation), utilizando pdfplumber + Sentence Transformers + FAISS + um modelo gerativo da Hugging Face. É significativamente
mais preciso do que passar todo o PDF como contexto.

Arquitetura do agente:
1. O usuário envia um PDF.
2. O PDF é convertido em texto.
3. O texto é dividido em pequenos trechos (chunks).
4. Cada trecho recebe um embedding vetorial.
5. A pergunta é convertida em embedding.
6. O FAISS encontra os trechos mais relevantes.
7. Um modelo de linguagem gera a resposta apenas com aquele contexto.

O agente, neste exemplo, acessa o documento "Política de Atendimento, trocas, devoluções e privacidade.pdf" do Mercado Central 24h.

🛠️ Ferramentas e tecnologias utilizadas

Para o desenvolvimento deste projeto foram utilizadas diferentes ferramentas e bibliotecas para construção da aplicação, processamento dos documentos, geração de embeddings e implementação do modelo de inteligência artificial.

🐍 Python

Linguagem principal utilizada no desenvolvimento da aplicação, responsável pela integração entre as diferentes bibliotecas e componentes do projeto.

🎈 Streamlit

Framework utilizado para criar a interface web da aplicação de forma simples e interativa, permitindo que o usuário envie documentos e interaja com o sistema.

📄 PDFPlumber

Biblioteca utilizada para realizar a leitura e extração de textos presentes nos arquivos PDF utilizados pelo projeto.

🔢 NumPy

Biblioteca utilizada para operações numéricas e manipulação dos dados gerados durante o processamento.

🔎 FAISS

Biblioteca utilizada para indexação e busca eficiente de vetores. No projeto, é utilizada para encontrar os conteúdos mais relevantes a partir dos embeddings gerados.

🧠 Sentence Transformers

Utilizada para transformar os textos em embeddings, representações numéricas que permitem comparar semanticamente os conteúdos dos documentos.

🤗 Hugging Face Transformers

Biblioteca utilizada para carregar e executar o modelo de linguagem responsável pela geração das respostas.

🤖 Google FLAN-T5

Modelo de linguagem utilizado na aplicação para gerar respostas a partir dos conteúdos relevantes recuperados dos documentos.

🔥 PyTorch

Framework utilizado como base para execução do modelo de linguagem e processamento necessário para o funcionamento do FLAN-T5.

🔗 Git e GitHub

Utilizados para controle de versão, armazenamento do código-fonte e acompanhamento do desenvolvimento do projeto.

📌 Resumo

A combinação dessas tecnologias permite implementar um fluxo de perguntas e respostas baseado em documentos, utilizando técnicas de processamento de linguagem natural, embeddings e busca vetorial para recuperar informações relevantes antes da geração das respostas.
