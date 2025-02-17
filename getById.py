from langchain.vectorstores import Chroma
from src.architecture_rag import get_by_id

# ID del documento a buscar
doc_id = "D:20210430151333Z"

# Buscar documento por ID
retrieved_doc = get_by_id(doc_id)

# Mostrar resultados
if retrieved_doc:
    print(f"\n📄 Documento encontrado:")
    print(f"🔗 Metadata: {retrieved_doc.metadata}")
    print(f"📜 Contenido:\n{retrieved_doc.page_content}")
else:
    print("⚠ No se encontraron documentos con el ID especificado.")
