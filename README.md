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
