from langchain import hub
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langgraph.graph import START, StateGraph
from langchain_core.documents import Document
from typing_extensions import List, TypedDict
import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv(override=True)

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

class PersonAIble:
    def __init__(self, k = 0):
        # Initialize once, reuse for all questions
        self.embeddings = None
        self.vector_store = None
        self.llm = None
        self.graph = None
        self.prompt = None
        self.k = k
        
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
    
    def retrieve(self, state: State, minRelevance = 0.2, stdDev = 0.5, document = None):
        raw_results = self.vector_store.similarity_search_with_score(state["question"], self.k) # score is cosine similarity
        if len(raw_results) == 1:
            return {"context": [raw_results[0][0]]}
        else:
            # I think absolute value of score measures true similarity, will test this hypothesis somehow
            scores = np.array([cosine_similarity for _, cosine_similarity in raw_results])
            indicesAboveMinRelevance = np.where(scores > minRelevance)[0]
            #meanScore = np.mean(scores)
            #stdScore = np.std(scores)

            if len(indicesAboveMinRelevance):
                return {"context": [raw_results[i][0] for i in indicesAboveMinRelevance]} # return all documents above minRelevance
            else:
                #maxScoreIndex = np.argmax(scores)
                return {"context": [raw_results[0][0]]} # return the most relevant documen
    
    def generate(self, state: State):
        print("state['context']", state["context"])
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = self.prompt.invoke({"question": state["question"], "context": docs_content})
        response = self.llm.invoke(messages)
        return {"answer": response.content}
    
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