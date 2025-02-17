from src.architecture_rag import update, get_by_id
from pydantic import BaseModel
from typing import List

class Document(BaseModel):
    page_content: str
    metadata: dict

updated_docs = "Contenido actualizado para el documento"  

doc_ids_list = ["D:20210430151333Z"]  

updated_docs_list = [updated_docs.strip()]

success = update(doc_ids_list, updated_docs_list)

if success:
    print("✅ Actualización exitosa. Verificando el cambio...")

    retrieved_docs = [get_by_id(doc_id) for doc_id in doc_ids_list]  

    for doc in retrieved_docs:
        if doc:
            print(f"📄 Documento recuperado: {doc.page_content}\n🔗 Metadata: {doc.metadata}")
        else:
            print(f"⚠️ No se encontró el documento con ID {doc}.")
else:
    print("❌ La actualización falló.")
