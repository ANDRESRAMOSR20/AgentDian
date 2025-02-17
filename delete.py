from src.architecture_rag import delete, get

# IDs de documentos a eliminar (deben existir en vector_store)
doc_ids_to_delete = ["D:20210430151333Z"]  # Reemplaza con un ID real

print(f"🗑 Intentando eliminar documentos con IDs: {doc_ids_to_delete}")

# Ejecutar eliminación
success = delete(doc_ids_to_delete)

if success:
    print("✅ Documentos eliminados exitosamente.")
    
    # Verificar que los documentos ya no existen
    retrieved_docs = get("", k=10)  # Buscar todos los documentos disponibles
    remaining_ids = [doc.metadata.get("id") for doc in retrieved_docs]
    
    if any(doc_id in remaining_ids for doc_id in doc_ids_to_delete):
        print("❌ Error: Algunos documentos aún aparecen en la base de datos.")
    else:
        print("✅ Confirmación: Documentos eliminados correctamente.")
else:
    print("❌ Error al eliminar los documentos.")
