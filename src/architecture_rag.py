# architecture_rag.py

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .confg import vector_store  # Importa tu vector_store desde el archivo de configuración
from langchain_core.tools import tool
import os

# Función para cargar y procesar múltiples PDFs
def load_and_process_pdfs(pdf_paths):
    all_docs = []
    for pdf_path in pdf_paths:
        # Construir la ruta absoluta basada en el directorio del script
        abs_path = os.path.join(os.path.dirname(__file__), pdf_path)
        abs_path = str(abs_path)  # Convierte explícitamente a str
        # Verificar que el archivo existe
        if not os.path.isfile(abs_path):
            raise FileNotFoundError(f"El archivo {abs_path} no existe.")
        # Cargar el PDF
        loader = PDFPlumberLoader(abs_path)
        docs = loader.load()
        # Agregar los documentos cargados a la lista general
        all_docs.extend(docs)
    return all_docs

# Lista de rutas relativas de los PDFs
pdf_paths = [
    "../docs/use-conectores.pdf",  # Ruta relativa al directorio del script
    "../docs/dian.pdf",
]

# Cargar y procesar los PDFs
docs = load_and_process_pdfs(pdf_paths)

# Dividir el contenido de los PDFs en chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Tamaño del chunk (caracteres)
    chunk_overlap=200,  # Solapamiento entre chunks (caracteres)
    add_start_index=True,  # Rastrear el índice en el documento original
)
all_splits = text_splitter.split_documents(docs)

# Indexar los chunks en la base de datos vectorial
document_ids = vector_store.add_documents(documents=all_splits)

@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Recuperar información relacionada con una consulta."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\n" f"Content: {doc.page_content}"
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs