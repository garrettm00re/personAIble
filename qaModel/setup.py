from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from .model import PersonAIble

def load_initial_data():
    # Load JSON files
    loader1 = JSONLoader(
        file_path="charlesRiverAssets/how.json",
        jq_schema='.',
        text_content=False
    )
    
    loader2 = JSONLoader(
        file_path="charlesRiverAssets/whereTo.json",
        jq_schema='.',
        text_content=False
    )
    
    loader3 = JSONLoader(
        file_path="charlesRiverAssets/who.json",
        jq_schema='.',
        text_content=False
    )

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
    
    with open("charlesRiverAssets/charlesRiverInterview.txt", "r", encoding="utf-8") as file:
        text = file.read()
        qa_pairs = text.split("\n\n")
    
    all_splits.extend([Document(page_content=qa, metadata={"source": "charlesRiverAssets/charlesRiverInterview.txt"}) for qa in qa_pairs])

    # Create and initialize model
    model = PersonAIble(k = len(all_splits))
    model.load_data(all_splits)
    
    return model