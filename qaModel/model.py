from dotenv import load_dotenv
load_dotenv(override=True)

from phoenix.otel import register
tracer_provider = register(project_name="personAIble", endpoint="https://app.phoenix.arize.com/v1/traces")

from openinference.instrumentation.langchain import LangChainInstrumentor
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

print("INSTRUMENTED")

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
from supabase import create_client
import os

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_GOD_KEY") # probably not best practice but it works for now
supabase = create_client(supabase_url, supabase_key)

class State(TypedDict):
    QA: List[tuple[str, List[str]]] # list of tuples (question, answer(s))
    desiredInformation: List[str] # list of the questions we want to retrieve information for (includes the intiial user question)
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
            self.llm = ChatOpenAI(model="chatgpt-4o-latest")
            self.user = json.load(open("./charlesRiverAssets/who.json"))["Name"]
            self.prompt = lambda state: f"""You are {self.user}'s assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
            Question: {state['question']}
            Context: {[f"{question} : {answer}" for question, answer in state['context']]}
            """  
            self._setup_graph()
    
    def _setup_graph(self):
        graph_builder = StateGraph(State)
        graph_builder.add_sequence([self.research, self.retrieve, self.followUp, self.generate])
        graph_builder.add_edge(START, "research")
        graph_builder.add_edge("research", "retrieve")
        graph_builder.add_edge("retrieve", "followUp")
        graph_builder.add_edge("followUp", "generate")
        self.graph = graph_builder.compile()
    
    def research(self, state: State):
        ## 2-3 questions could be too much or too little. How to decide depending on the request?
        prompt = f"You are a helpful assistant preparing to answer the following question: {state['question']}. Generate a short (2 - 3 item) list of questions about the user that would help you to answer their request accurately. Return the list as a newline-separated string."
        response = self.llm.invoke(prompt)
        questions = response.content.split("\n")
        desiredInformation = [question for question in questions] + [state["question"]]
        return {"desiredInformation": desiredInformation}

    def retrieve(self, state: State, minRelevance = 0.4, numStdDev = 2):
        def getMostRelevant(question):
            raw_results = self.vector_store.similarity_search_with_score(question, k = self.k)
            scores = np.array([cosine_similarity for _, cosine_similarity in raw_results])
            mean = np.mean(scores)
            std = np.std(scores)
            return [raw_results[i][0] for i in np.where(scores >= mean + (std*numStdDev))[0] if raw_results[i][1] >= minRelevance]
        
        desiredInformation = state["desiredInformation"]
        QA = []
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
                QA.append((question, context))
        return {"QA": QA}
    
    def followUp(self, state: State):
        def consolidateIntoContext(question, answer):
            prompt = f"""You are given this question: {question} and answer: {answer}. 
            Return a concise summary of the question and answer. 
            The subject of the summary is the person who answered the question."""
            return self.llm.invoke(prompt).content
        
        print("FOLLOWUP")
        allQA = state["QA"]
        print("ALLQA: ", allQA)
        for idx, QA in enumerate(allQA):
            if QA[1] == [] and QA[0] != state["question"]:
                # Get answer from askUser endpoint
                response = requests.post(
                    'http://localhost:5000/api/followup',
                    json={'QA': QA}
                )
                if response.status_code == 200:
                    answer = response.json()['answer']
                    conciseAnswer = consolidateIntoContext(QA[0], answer)
                    allQA[idx] = (QA[0], [conciseAnswer])

                    # make document and add concise answer to vector store
                    document = Document(page_content=conciseAnswer, metadata={"source": "followup"})
                    self.vector_store.add_documents([document])

                    # add concise answer to supabase
                    supabase.table('QA').insert(
                        {"questions": QA[0], 
                         "answers": conciseAnswer}
                        ).execute()
    
        return {"context": allQA}
    
    def generate(self, state: State):
        print('generating')
        prompt = self.prompt(state)
        #print('prompt: ', prompt)
        response = self.llm.invoke(prompt)
        self.chat_history.append({"question": state["question"], "answer": response.content})

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