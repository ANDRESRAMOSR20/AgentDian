import streamlit as st
from PyPDF2 import PdfReader
from src.architecture_rag import insert_document, get
from langchain.docstore.document import Document


# Función encargarda de permitr al usuario subir nuevos documentos
@st.dialog("Subir documentos")
def view_up_document():
    st.header("📄 Cargar Documentos en PDF")
    up_documents()


# Función encargarda de permitr al usuario subir buscard docuemntos
@st.dialog("Subir documentos")
def search_documents():
    # Widgets para la búsqueda
    category_query = st.text_input("Término de búsqueda (ej. 'legal'):")
    num_results = st.number_input("Número de resultados:", min_value=1, value=5)

    if st.button("Buscar"):
        with st.spinner("Buscando documentos..."):
            # Simulación de la función get() para obtener documentos
            retrieved_docs = get(category_query, k=num_results)

            # Filtrar documentos únicos por ID
            unique_docs = {}
            for doc in retrieved_docs:
                id_document = doc.metadata.get("id")
                doc_id = id_document  # Asume que el ID está en los metadatos
                if doc_id and doc_id not in unique_docs:
                    unique_docs[doc_id] = doc

            # Convertir el diccionario de nuevo a una lista
            unique_docs_list = list(unique_docs.values())

            # Mostrar los resultados
            if unique_docs_list:
                st.subheader(f"🔍 Documentos Relacionados con '{category_query}':")

                # Mostrar cada documento en una tarjeta
                for i, doc in enumerate(retrieved_docs, start=1):
                    with st.container():
                        id_document = doc.metadata.get("id")
                        st.markdown(f"### Documento {i}")
                        st.subheader(f"Idenficador: ...{id_document[-4:]}")
                        st.markdown("#### Contenido:")
                        st.markdown(
                            f"> {doc.page_content}"
                        )  # Mostrar contenido como un bloque de cita
                        st.divider()  # Separador visual entre documentos
            else:
                st.warning("No se encontraron documentos relacionados con la búsqueda.")


# Funcion que sirve para mostrar y permitir surbir el
def up_documents():
    uploaded_file = st.file_uploader(
        "Selecciona un archivo",
        type=["pdf"],
        accept_multiple_files=False,
    )

    if uploaded_file is not None:
        cargar_documento(uploaded_file)


# Funcion encartgada de subir el documento a la BD
def cargar_documento(uploaded_file):
    try:
        # Validar nombre y extensión
        if "." not in uploaded_file.name:
            raise ValueError("El archivo no tiene extensión válida")

        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension not in ["pdf"]:
            raise ValueError("Formato no soportado")

        # Leer contenido
        content = ""
        pdf_reader = PdfReader(uploaded_file)
        content = "\n".join([page.extract_text() or "" for page in pdf_reader.pages])

        # Validar contenido no vacío
        if not content.strip():
            raise ValueError("El archivo está vacío o no tiene texto extraíble")

        # Mostrar vista previa
        with st.expander("Vista previa del contenido"):
            st.text(content[:2000] + ("..." if len(content) > 2000 else ""))

        # Botón de carga
        if st.button("Cargar documento", key=f"btn_{uploaded_file.name}"):
            with st.spinner("Procesando..."):
                # Convertir el contenido en un objeto Document
                document = Document(page_content=content, metadata={"source": uploaded_file.name})
                insert_document([document])  # Pasar como una lista de documentos

    except Exception as e:
        st.error(f"🚨 Error al procesar el archivo: {str(e)}")
