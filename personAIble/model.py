from langchain import hub
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langgraph.graph import START, StateGraph
from langchain_core.documents import Document
from typing_extensions import List, TypedDict
import numpy as np
import matplotlib.pyplot as plt

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

class PersonAIble:
    def __init__(self):
        # Initialize once, reuse for all questions
        self.embeddings = None
        self.vector_store = None
        self.llm = None
        self.graph = None
        self.prompt = None
        
    def initialize(self):
        """Lazy loading of expensive components"""
        if self.graph is None:
            # Only load these when first needed
            self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
            self.vector_store = InMemoryVectorStore(self.embeddings)
            self.llm = ChatOpenAI(model="gpt-4-turbo-preview")
            self.prompt = hub.pull("rlm/rag-prompt")
            
            # Set up the graph
            self._setup_graph()
    
    def _setup_graph(self):
        graph_builder = StateGraph(State)
        graph_builder.add_sequence([self.retrieve, self.generate])
        graph_builder.add_edge(START, "retrieve")
        self.graph = graph_builder.compile()
    
    def retrieve(self, state: State):
        # Your existing retrieve function
        # ... (same as notebook)
        pass
    
    def generate(self, state: State):
        # Your existing generate function
        # ... (same as notebook)
        pass
    
    def load_data(self, documents):
        """Load documents into vector store"""
        self.initialize()  # Ensure components are ready
        self.vector_store.add_documents(documents=documents)
    
    def answer_question(self, question: str) -> str:
        """Main interface for getting answers"""
        self.initialize()  # Lazy loading
        
        result = self.graph.invoke({
            "question": question
        })
        
        return result['answer']