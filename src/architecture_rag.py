from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_community.chat_message_histories import RedisChatMessageHistory
from typing import List, TypedDict
import uuid
from datetime import datetime

# 📌 1️⃣ Carga y Procesamiento del Documento PDF
file_path = "C:/Users/USER/Documents/AgentDian/docs/use-conectores.pdf"
print(f"🔹 Cargando documento desde: {file_path}")
try:
    loader = PDFPlumberLoader(file_path)
    docs = loader.load()
    if docs:
        print(f"✅ Documento cargado con éxito. Total de páginas: {len(docs)}")
    else:
        print("⚠️ No se cargaron documentos, revisa la ruta del archivo.")
except Exception as e:
    print(f"❌ Error al cargar el documento: {e}")
    docs = []  

# 📌 2️⃣ Fragmentación de Texto para Indexación
print("🔹 Fragmentando el documento en partes más pequeñas...")

try:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200, 
        add_start_index=True  
    )
    all_splits = text_splitter.split_documents(docs)

    if all_splits:
        print(f"✅ Fragmentación completada. Total de fragmentos: {len(all_splits)}")
    else:
        print("⚠️ No se generaron fragmentos. Revisa el contenido del documento.")

except Exception as e:
    print(f"❌ Error al fragmentar el documento: {e}")
    all_splits = []


# 📌 3️⃣ Creación de Embeddings y Base Vectorial

print("🔹 Creando embeddings y base de datos vectorial...")

try:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vector_store = Chroma(embedding_function=embeddings)
    print("✅ Embeddings y base vectorial creados correctamente.")
except Exception as e:
    print(f"❌ Error al crear los embeddings o la base vectorial: {e}")

# 📌 4️⃣ Indexación de Fragmentos en la Base Vectorial

print("🔹 Indexando fragmentos en la base vectorial...")
try:
    if all_splits:
        vector_store.add_documents(documents=all_splits)
        print("✅ Fragmentos indexados con éxito.")
    else:
        print("⚠️ No hay fragmentos para indexar.")
except Exception as e:
    print(f"❌ Error al indexar los fragmentos: {e}")


# 📌 5️⃣ Herramienta de Recuperación de Información
@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Recupera información relevante basada en la consulta."""
    print(f"🔍 Ejecutando recuperación de información para: {query}")
    try:
        retrieved_docs = vector_store.similarity_search(query, k=2)
        if retrieved_docs:
            print(f"✅ Se recuperaron {len(retrieved_docs)} documentos.")
            serialized = "\n\n".join(
                f"Source: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}"
                for doc in retrieved_docs
            )
            return serialized, retrieved_docs
        else:
            print("⚠️ No se recuperaron documentos relevantes.")
            return "No se encontraron documentos relevantes.", []
    except Exception as e:
        print(f"❌ Error en la recuperación de información: {e}")
        return "Error en la recuperación de información.", []

# # 📌 6️⃣ Generación del session_id para Redis
# print("🔹 Generando session_id...")
# try:
#     session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
#     print(f"✅ session_id generado: {session_id}")
# except Exception as e:
#     print(f"❌ Error al generar session_id: {e}")
#     session_id = "session_error"

# # 📌 7️⃣ Configuración del Historial de Mensajes en Redis
# print("🔹 Conectando con Redis para gestionar historial de mensajes...")

# try:
#     message_history = RedisChatMessageHistory(
#         session_id=session_id, 
#         url="redis://localhost:6379/0",  
#         ttl=600  
#     )
#     print("✅ RedisChatMessageHistory creado correctamente.")
# except Exception as e:
#     print(f"❌ Error al crear RedisChatMessageHistory: {e}")

# # 📌 8️⃣ Definición del Estado Inicial
# class CustomState(TypedDict):
#     messages: List[Document]  # Lista de mensajes/documentos
#     history: RedisChatMessageHistory  # Historial de conversación

# print("🔹 Creando estado inicial...")

# try:
#     initial_state = CustomState(messages=[], history=message_history)
#     print("✅ Estado inicial creado correctamente.")
# except Exception as e:
#     print(f"❌ Error al crear estado inicial: {e}")
