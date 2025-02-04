from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


embeddings = OllamaEmbeddings(model="llama3")
llm = ChatOllama(model="llama3.2:1b")
vector_store = Chroma(embedding_function=embeddings)