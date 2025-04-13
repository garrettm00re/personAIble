from dotenv import load_dotenv
load_dotenv(override=True)

from langchain import hub
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langgraph.graph import START, StateGraph
from langchain_core.documents import Document
from typing_extensions import List, TypedDict
import numpy as np
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import os
from qdrant_client.http.models import Filter
from langchain_community.vectorstores import Qdrant
from ..personAIble.extensions import qdrant # this must be bad form

class State(TypedDict):
    QA: List[tuple[str, List[str]]] # list of tuples (question, answer(s))
    desiredInformation: List[str] # list of the questions we want to retrieve information for (includes the intiial user question)
    question: str
    context: List[Document]
    answer: str
    google_id: str
    first_name: str
    
class PersonAIble:
    def __init__(self):
        # Initialize once, reuse for all questions
        self.embeddings = None
        self.vector_stores = {} # handle multiple users this way (google_id : vector_store). Not a good approach but functional for low # users.
        self.Ks = {} # google_id : K (length of vector store)
        self.graph = self._setup_graph()
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.llm = ChatOpenAI(model="chatgpt-4o-latest")
        self.prompt = lambda state: f"""You are {state['first_name']}'s assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
        Question: {state['question']}
        Context: {[f"{question} : {answer}" for question, answer in state['context']]}
        """ 
        self.API = os.getenv("PRODUCTION_API") if os.getenv("ENV") == "PRODUCTION" else os.getenv("DEVELOPMENT_API")
        print("MODEL INITIALIZED")

    # NOTE : when implementing "chat history" for context you should add a "timestamp" each message in the database (and also store messages) 
    # you can use the timestamp in a function to compute relevance based on recency
    
    def _setup_graph(self):
        # research, retrieve, followup, generate
        graph_builder = StateGraph(State)
        graph_builder.add_sequence([self.research, self.retrieve, self.followUp, self.generate])
        graph_builder.add_edge(START, "research")
        graph_builder.add_edge("research", "retrieve")
        graph_builder.add_edge("retrieve", "followUp")
        graph_builder.add_edge("followUp", "generate")
        return graph_builder.compile()
    
    def research(self, state: State):
        ## 2-3 questions could be too much or too little. How to decide depending on the request?
        prompt = f"You are a helpful assistant preparing to answer the following question: {state['question']}. \
        Generate the shortest list of questions about the user, {state['first_name']}, that would help you to answer their request \
        accurately. Return the list as a newline-separated string. \
        \
        Rules: \
        - If there are no questions, return exactly 'NA'. \
        "

        response = self.llm.invoke(prompt)
        questions = response.content.split("\n") if response.content != "NA" else []
        desiredInformation = [question for question in questions] + [state["question"]]
        return {"desiredInformation": desiredInformation}

    def retrieve(self, state: State, minRelevance = 0.4, numStdDev = 2):
        def getMostRelevant(question):
            raw_results = vector_store.similarity_search_with_score(question, k = K)
            scores = np.array([cosine_similarity for _, cosine_similarity in raw_results])
            mean = np.mean(scores)
            std = np.std(scores)
            return [raw_results[i][0] for i in np.where(scores >= mean + (std*numStdDev))[0] if raw_results[i][1] >= minRelevance]
        
        vector_store = self.vector_stores[state["google_id"]]
        K = self.Ks[state["google_id"]]
        desiredInformation = state["desiredInformation"]
        qa_pairs = []
        with ThreadPoolExecutor() as executor:
            future_to_info = {
                    executor.submit(
                        getMostRelevant, question
                ): question for question in desiredInformation
            }
            
            # Process completed searches as they finish
            for future in as_completed(future_to_info):
                question = future_to_info[future]
                results = future.result()
                context = []
                for result in results:
                    context.append(result.page_content)
                qa_pairs.append((question, context))
        return {"QA": qa_pairs}
    
    def followUp(self, state: State):
        print("FOLLOWUP")
        allQA = state["QA"]
        print("ALLQA: ", allQA)
        for idx, QA in enumerate(allQA):
            if QA[1] == [] and QA[0] != state["question"]:
                # Get answer from askUser endpoint
                response = requests.post(
                    self.API + '/api/followup',
                    json={'QA': QA, 'google_id': state['google_id'], 'first_name': state['first_name']},
                    headers={'Authorization': f'Bearer {os.environ.get("FOLLOW_UP")}'}
                )
                if response.status_code == 200:
                    summary = response.json()['summary']
                    allQA[idx] = (QA[0], [summary])

                    # make document and add concise answer to vector store
                    document = Document(page_content=summary, metadata={"source": "followup"})

                    ### MAY NEED A LOCK HERE
                    self.vector_stores[state["google_id"]].add_documents([document])
                    self.Ks[state["google_id"]] += 1
    
        return {"context": allQA}
    
    def generate(self, state: State):
        print('generating')
        prompt = self.prompt(state)
        response = self.llm.invoke(prompt)
        #self.chat_history.append({"question": state["question"], "answer": response.content})

        return {"answer": response.content}
    
    def answer_question(self, question: str, google_id: str, first_name: str):
        collection_name = f"user_{google_id}"
        
        # Create Langchain wrapper for collection
        vector_store = Qdrant(
            client=qdrant,
            collection_name=collection_name,
            embeddings=self.embeddings
        )
        
        # Use for similarity search
        docs = vector_store.similarity_search(question)
        # ... rest of your code ...
    
    def initUser(self, google_id: str, documents):
        collection_name = f"user_{google_id}"
        
        # Create and populate collection
        create_user_collection(google_id, documents)
        
        # No need to store in memory anymore!
        # vector_stores[google_id] = store
    
    def deleteUser(self, google_id: str):
        collection_name = f"user_{google_id}"
        try:
            qdrant.delete_collection(collection_name)
        except Exception as e:
            print(f"Error deleting collection: {e}")