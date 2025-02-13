from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
llm = ChatOllama(model="hf.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF:IQ4_NL")
# Configuración de Chroma con una ruta persistente

import tempfile
persist_directory = os.path.join(tempfile.gettempdir(), "chroma_db")
vector_store = Chroma(persist_directory=persist_directory, embedding_function=embeddings)