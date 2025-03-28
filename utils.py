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