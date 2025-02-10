from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
llm = ChatOllama(model="hf.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF:IQ4_NL")
vector_store = Chroma(embedding_function=embeddings)