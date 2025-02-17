from src.architecture_rag import get

# Parámetros de búsqueda
category_query = "legal"  # Cambia esto según tu caso
num_results = 5  # Número de documentos a recuperar

print(f"🔍 Buscando documentos relacionados con: {category_query}")

# Buscar documentos en la base de datos vectorial
retrieved_docs = get(category_query, k=num_results)

# Mostrar resultados
if retrieved_docs:
    for i, doc in enumerate(retrieved_docs, start=1):
        print(f"\n📄 Documento {i}:")
        print(f"🔗 Metadata: {doc.metadata}")
        print(f"📜 Contenido:\n{doc.page_content}")
else:
    print("⚠ No se encontraron documentos relacionados.")
