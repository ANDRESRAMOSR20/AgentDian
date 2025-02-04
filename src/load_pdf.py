from langchain_community.document_loaders import PDFPlumberLoader

file_path = "../docs/use-conectores.pdf"
loader = PDFPlumberLoader(file_path)
docs = loader.load()

print(docs[0].page_content)
