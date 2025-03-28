from langchain_core.documents import Document
from database import Database

def get_all_followup_qa_summaries(google_id, db : Database) -> list[dict[str, str]]:
    # get all summaries from the QA table where google_id matches
    qa_summaries = db.db_client.table('QA').select('summary').eq('google_id', google_id).execute()
    return qa_summaries.data

def getFollowupDocuments(google_id, db : Database):
    # get all rows from the QA table where google_id matches
    qa_summaries = get_all_followup_qa_summaries(google_id, db)
    followup_docs = []
    for summary in qa_summaries:
        followup_docs.append(Document(page_content=summary['summary'], metadata={"source": "followup"}))
    return followup_docs

def get_all_onboarding_data(google_id, db : Database):
    onboarding_cols = db.db_client.table('onboarding').select('*').eq('google_id', google_id).execute()
    return onboarding_cols.data[0]

def getOnboardingDocuments(google_id, db : Database, columnToQuestionMap : dict[str, str]):
    skipCols = set(['google_id', 'created_at', 'id'])
    onboarding_cols = get_all_onboarding_data(google_id, db)
    onboarding_docs = []
    for column, answer in onboarding_cols.items():
        if column not in skipCols:
            question = columnToQuestionMap[column]
            onboarding_docs.append(Document(page_content=f"{question} : {answer}", metadata={"source": "onboarding"}))
    return onboarding_docs

def getUserDocuments(google_id, db : Database, columnToQuestionMap : dict[str, str]):
    # load all columns from the users row in the onboarding table
    onboarding_docs = getOnboardingDocuments(google_id, db, columnToQuestionMap)
    followup_docs = getFollowupDocuments(google_id, db)
    
    # Combine documents
    documents = onboarding_docs + followup_docs
    return documents