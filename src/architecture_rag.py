from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing_extensions import List, TypedDict
from langgraph.graph import MessagesState, StateGraph
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.memory import ChatMessageHistory

# Loading and proccesing the PDF Document
file_path = "../docs/use-conectores.pdf"
loader = PDFPlumberLoader(file_path)
docs = loader.load()


# Split the content the PDF in fragments
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, 
    chunk_overlap=200, 
    add_start_index=True,  
)
all_splits = text_splitter.split_documents(docs)

structured_splits = [
    Document(page_content=split.page_content, metadata={"source": file_path})
    for split in all_splits
]

# Embeddings and vectorial database Configuration 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vector_store = Chroma(embedding_function=embeddings)

# Indexation the fragments in the vectorial database
document_ids = vector_store.add_documents(documents=all_splits)

test_query = "conjunciones"  
retrieved_docs = vector_store.similarity_search(test_query, k=2)

print("\n🔎 Resultados de la Recuperación Vectorial:")
for i, doc in enumerate(retrieved_docs):
    print(f"\n📄 Documento {i+1}:")
    print(f"Source: {doc.metadata.get('source', 'Unknown')}")
    print(f"Content: {doc.page_content[:500]}...")  


# Define the state of the work path
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

# Recuperation Information Tool
@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        f"Source: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}"
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

#Creaye a history messages intance
message_history = ChatMessageHistory()

# Initialize the state graph
graph_builder = StateGraph(MessagesState)