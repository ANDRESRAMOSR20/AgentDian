# architecture_rag.py

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.confg import vector_store  # Importa tu vector_store desde el archivo de configuración
from langchain_core.tools import tool
import os
from langchain.schema import Document
from langchain.vectorstores import Chroma




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

        # Agregar metadatos personalizados a cada documento
        for doc in docs:
            doc.metadata["source"] = pdf_path

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
    retrieved_docs = vector_store.similarity_search(query, k=5)  # Busca los 5 documentos más similares
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\n" f"Content: {doc.page_content}"
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs


# Función para buscar documentos relacionados con una categoría usando embeddings
def get(category_query: str, k: int = 5):
    """
    Busca documentos relacionados con una categoría usando embeddings.

    Args:
        category_query (str): La consulta relacionada con la categoría (ej. "legal").
        k (int): El número de documentos más similares a devolver.

    Returns:
        List[Document]: Una lista de documentos más similares.
    """
    # Realiza una búsqueda de similitud en la base de datos vectorial
    retrieved_docs = vector_store.similarity_search(category_query, k=k)
    return retrieved_docs

def get_by_id(doc_id: str):
    """
    Busca un documento por su ID (en este caso, usando 'ModDate' como ID en metadata).
    No requiere embeddings ni vector stores.

    Args:
        doc_id (str): El ID del documento a buscar.

    Returns:
        Document: El documento encontrado, o None si no se encuentra.
    """
    retrieved_docs = get(doc_id, k=5)  
    
    for doc in retrieved_docs:
        if doc.metadata.get('ModDate') == doc_id:
            return doc  
    return None  


from pydantic import BaseModel, ValidationError
from typing import List

class Document(BaseModel):
    page_content: str
    metadata: dict

def update(doc_ids: List[str], updated_docs: List[str]):
    try:
        # Validar que doc_ids y updated_docs no estén vacíos
        if not doc_ids or not updated_docs:
            raise ValueError("Las listas doc_ids y updated_docs no pueden estar vacías.")

        if len(doc_ids) != len(updated_docs):
            raise ValueError("Las listas doc_ids y updated_docs deben tener la misma longitud.")

        documents = []
        for doc_id, content in zip(doc_ids, updated_docs):
            # Buscar el documento por ID usando el método get_by_id
            retrieved_doc = get_by_id(doc_id)
            
            if not retrieved_doc:
                print(f"⚠️ El documento con ID {doc_id} no existe. No se actualizará.")
                continue  
            
            if not isinstance(content, str):
                raise TypeError(f"El contenido del documento con ID {doc_id} debe ser una cadena de texto.")
            
            try:
                # Validación de contenido utilizando Pydantic
                document = Document(page_content=content, metadata={"id": doc_id})
                documents.append(document)
            except ValidationError as ve:
                print(f"Error en la validación del documento con ID {doc_id}: {ve}")
                continue  

        if not documents:
            raise ValueError("No se generaron documentos válidos para actualizar.")

        # Realiza la actualización de los documentos en el almacén de vectores
        vector_store.update_documents(ids=doc_ids, documents=documents)

        print("✅ Actualización completada con éxito.")
        return True
    except (ValueError, TypeError) as e:
        print(f"⚠️ Error en la validación de entrada: {e}")
    except Exception as e:
        print(f"❌ Error inesperado al actualizar documentos: {e}")
    return False

# Método DELETE para eliminar documentos de la base de datos
def delete(doc_ids: List[str]):
    """Elimina documentos de la base de datos vectorial por sus IDs."""
    if not isinstance(doc_ids, list):
        raise ValueError("doc_ids debe ser una lista de IDs de documentos a eliminar.")
    
    try:
        # Verificar si los IDs existen antes de intentar eliminarlos
        for doc_id in doc_ids:
            if not get_by_id(doc_id):
                print(f"⚠️ El documento con ID {doc_id} no existe. No se eliminará.")
                doc_ids.remove(doc_id)

        if not doc_ids:
            print("⚠️ No hay documentos válidos para eliminar.")
            return False
        
        success = vector_store.delete(ids=doc_ids)
        if success:
            print(f"✅ Documentos con IDs {doc_ids} eliminados con éxito.")
        return success
    except Exception as e:
        print(f"❌ Error al eliminar documentos: {e}")
        return False
