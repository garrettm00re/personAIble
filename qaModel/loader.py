from langchain_core.documents import Document
from database import Database

def get_all_followup_qa_summaries(google_id, db : Database) -> list[dict[str, str]]:
    # get all summaries from the QA table where google_id matches
    qa_summaries = db.db_client.table('QA').select('summary').eq('google_id', google_id).execute()
    return qa_summaries.data

def followupLoader(google_id, db : Database):
    # get all rows from the QA table where google_id matches
    qa_summaries = get_all_followup_qa_summaries(google_id, db)
    for summary in qa_summaries:
        yield Document(page_content=summary['summary'], metadata={"source": "followup"})

def get_all_onboarding_data(google_id, db : Database):
    onboarding_cols = db.db_client.table('onboarding').select('*').eq('google_id', google_id).execute()
    return onboarding_cols.data[0]

def onboardingLoader(google_id, db : Database):
    skipCols = set(['google_id', 'created_at', 'id'])
    onboarding_cols = get_all_onboarding_data(google_id, db)
    for question, answer in onboarding_cols.items():
        if question not in skipCols:
                yield Document(page_content=f"{question} : {answer}", metadata={"source": "onboarding"})

def getUserDocuments(google_id, db : Database):
    # load all columns from the users row in the onboarding table
    onboardingLoader = onboardingLoader(google_id, db)
    followupLoader = followupLoader(google_id, db)
    
    # for each QA for google_id, load the summaries

    # Combine documents
    documents = []
    for loader in [onboardingLoader, followupLoader]:
        documents.extend(loader.load())
    return documents