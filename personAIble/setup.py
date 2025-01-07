from langchain.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .model import PersonAIble

def load_initial_data():
    # Load JSON files
    loader1 = JSONLoader(
        file_path="userModel/how.json",
        jq_schema='.',
        text_content=False
    )
    # ... other loaders ...
    
    # Combine documents
    documents = []
    for loader in [loader1, loader2, loader3]:
        documents.extend(loader.load())
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=40,
        separators=["{", "}", ",", "\n"]
    )
    all_splits = text_splitter.split_documents(documents)
    
    # Create and initialize model
    model = PersonAIble()
    model.load_data(all_splits)
    
    return model