from langchain import hub
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langgraph.graph import START, StateGraph
from langchain_core.documents import Document
from typing_extensions import List, TypedDict
import numpy as np
from dotenv import load_dotenv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
load_dotenv(override=True)

class State(TypedDict):
    desiredInformation: List[str]
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
        self.user = None
        self.chat_history = []
        
    def initialize(self):
        """Lazy loading of expensive components"""
        if self.graph is None:
            # Only load these when first needed
            self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
            self.vector_store = InMemoryVectorStore(self.embeddings)
            self.llm = ChatOpenAI(model="gpt-4-turbo-preview")
            self.user = json.load(open("./charlesRiverAssets/who.json"))["Name"]
            self.prompt = lambda state: f"""You are {self.user}'s assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
            Question: {state['question']}
            Context: {state['context']}
            Chat History: {self.chat_history}
            """
            # Set up the graph
            self._setup_graph()
    
    def _setup_graph(self):
        graph_builder = StateGraph(State)
        graph_builder.add_sequence([self.research, self.retrieve, self.generate])
        graph_builder.add_edge(START, "research")
        graph_builder.add_edge("research", "retrieve")
        graph_builder.add_edge("retrieve", "generate")
        self.graph = graph_builder.compile()
    
    def research(self, state: State):
        prompt = f"You are a helpful assistant preparing to answer the following question: {state['question']}. Generate a short (2 - 3 item) list of information about the user that would help you to answer their question accurately. Return the list as a newline-separated string."
        response = self.llm.invoke(prompt)
        return {"desiredInformation": response.content.split("\n")}

    def retrieve(self, state: State, minRelevance = 0.2, numStdDev = 2):
        def getMostRelevant(raw_results):
            scores = np.array([cosine_similarity for _, cosine_similarity in raw_results])
            mean = np.mean(scores)
            std = np.std(scores)
            return [raw_results[i][0] for i in np.where(scores >= mean + (std*numStdDev))[0] if raw_results[i][1] >= minRelevance]
        
        desiredInformation = state["desiredInformation"]
        docs = {}
        for info in desiredInformation:
            # Create a thread pool for parallel similarity searches
            with ThreadPoolExecutor() as executor:
                # Submit similarity search tasks for each info item
                future_to_info = {
                    executor.submit(
                        self.vector_store.similarity_search_with_score, info, k=self.k
                    ): info for info in desiredInformation
                }
                
                # Process completed searches as they finish
                for future in as_completed(future_to_info):
                    print("a future finished")
                    raw_results = future.result()
                    relevant = getMostRelevant(raw_results)
                    # Add relevant docs to shared dict
                    for doc in relevant:
                        docs[doc.id] = doc
            relevant = getMostRelevant(self.vector_store.similarity_search_with_score(info, k = self.k))
            for doc in relevant:
                docs[doc.id] = doc
        return {"context": list(docs.values())}

    def generate(self, state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        formatted_history = "\n".join([
            f"Human: {exchange['question']}\nAssistant: {exchange['answer']}"
            for exchange in self.chat_history
        ])
        
        prompt = self.prompt(state)
        print(prompt)
        response = self.llm.invoke(prompt)
        self.chat_history.append({"question": state["question"], "answer": response.content})
        print("STATE PRINT", state)
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