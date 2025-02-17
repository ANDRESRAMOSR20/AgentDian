import streamlit as st
from src.tools import graph  # Importa el grafo con memoria
import uuid  # Para generar IDs únicos
from src.architecture_rag import get,update,delete
from langchain.schema import Document

# Configuración inicial de la página
st.set_page_config(page_title="Asistente Virtual", layout="wide")
st.title("📄 Asistente Virtual basado para la DIAN")
st.markdown("Este asistente responde preguntas basadas en el contenido de los documentos PDF cargados.")

# Entrada del usuario para buscar por categoría
st.sidebar.header("Buscar Documentos por Categoría")
category_query = st.sidebar.text_input("Término de búsqueda (ej. 'legal'):")
num_results = st.sidebar.number_input("Número de resultados:", min_value=1, value=5)

if st.sidebar.button("Buscar Documentos"):
    with st.spinner("Buscando documentos..."):
        # Buscar documentos relacionados con la categoría
        retrieved_docs = get(category_query, k=num_results)

        # Mostrar los resultados
        st.subheader(f"🔍 Documentos Relacionados con '{category_query}':")
        for doc in retrieved_docs:
            st.write(f"**Metadata:** {doc.metadata}")
            st.write(f"**Content:** {doc.page_content}")
            st.markdown("---")

from pydantic import BaseModel
from typing import List

class Document(BaseModel):
    page_content: str
    metadata: dict


st.sidebar.header("Actualizar Documentos")
doc_ids_update = st.sidebar.text_area("IDs de documentos a actualizar (separados por coma):")
updated_docs = st.sidebar.text_area("Nuevos contenidos de documentos (separados por coma):")

if st.sidebar.button("Actualizar Documentos"):
    with st.spinner("Actualizando documentos..."):
        doc_ids_list = [id.strip() for id in doc_ids_update.split(",") if id.strip()]
        updated_docs_list = [
            doc.strip() for doc in updated_docs.split(",") if doc.strip()
        ]
        
        success = update(doc_ids_list, updated_docs_list)
        if success:
            st.sidebar.success("Documentos actualizados exitosamente.")
        else:
            st.sidebar.error("Error al actualizar documentos.")


# Entrada del usuario para eliminar documentos
st.sidebar.header("Eliminar Documentos")
doc_ids_delete = st.sidebar.text_area("IDs de documentos a eliminar (separados por coma):")

if st.sidebar.button("Eliminar Documentos"):
    with st.spinner("Eliminando documentos..."):
        doc_ids_list = [id.strip() for id in doc_ids_delete.split(",") if id.strip()]
        
        try:
            success = delete(doc_ids_list)
            if success:
                st.sidebar.success("Documentos eliminados exitosamente.")
            else:
                st.sidebar.error("Error al eliminar documentos.")
        except Exception as e:
            st.sidebar.error(f"Error al eliminar documentos: {e}")

# Genera un thread_id único para la sesión actual
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())  # Genera un ID único

# Inicializa el historial de mensajes si no existe
if "message_history" not in st.session_state:
    st.session_state.message_history = []

# Mostrar el historial de mensajes en la parte principal
for msg in st.session_state.message_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Entrada de texto en la parte inferior
query = st.chat_input(placeholder="Escribe tu pregunta aquí...")

if query:
    # Agrega el mensaje del usuario al historial
    st.session_state.message_history.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    # Ejecutar el flujo en el grafo
    with st.spinner("Buscando respuesta..."):
        try:
            response = None
            for step in graph.stream(
                {"messages": st.session_state.message_history},
                config={"configurable": {"thread_id": st.session_state.thread_id}},  # Proporciona el thread_id
                stream_mode="values",
            ):
                response = step["messages"][-1].content  # Obtener la última respuesta

            # Agrega la respuesta del modelo al historial
            st.session_state.message_history.append({"role": "assistant", "content": response})

            # Muestra la respuesta del asistente
            with st.chat_message("assistant"):
                st.write(response)

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")