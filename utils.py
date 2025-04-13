from cryptography.fernet import Fernet
import os

# Initialize encryption key
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
fernet = Fernet(ENCRYPTION_KEY)

def encrypt_user_id(google_id: str) -> str:
    return fernet.encrypt(google_id.encode()).decode()

def decrypt_user_id(encrypted_id: str) -> str:
    return fernet.decrypt(encrypted_id.encode()).decode()

def consolidateIntoContext(question, answer, user_first_name, llm):
    prompt = f"""The system asked {user_first_name} the question '{question}', and {user_first_name} \
    answered the question '{answer}'.
    
    Return a concise summary of the question and answer.
     
    Do not reference the question or answer directly. Instead, write a series of statements \
    with the user being the subject.
    """
    return llm.invoke(prompt).content

def get_onboarding_maps():
    questionToColumnMap = {}
    columnToQuestionMap = {}
    with open('static/onboardingQuestionMap.txt', 'r') as file:
        for line in file:
            line = line.strip()
            line = line.split(" : ")
            questionToColumnMap[line[0]] = line[1]
            columnToQuestionMap[line[1]] = line[0]
    return questionToColumnMap, columnToQuestionMap

def get_user_from_request(request, db):
    try:
        user_id = request.args.get('uid')
        google_id = decrypt_user_id(user_id)
        user = db.get_by_google_id(google_id)
        return user
    except Exception as e:
        print('Error getting user from request: ', e)
        print(request.args, 'ARGZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ')
        print(request, 'request')
        return None
