import os
from supabase import create_client
from user import User

class Database:
    # currently this is just a wrapper around the supabase client specifically for the user table
    def __init__(self):
        self.db_client = self.initSupabase()
    
    def initSupabase(self):# Initialize Supabase client
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_GOD_KEY") # probably not best practice but it works for now
        db_client = create_client(supabase_url, supabase_key)
        return db_client

    def get_by_google_id(self, google_id):
        data = self.db_client.table('profiles').select('*').eq('google_id', google_id).execute()
        return data.data[0] if data.data else None
    
    def save(self, user):
        """
        Save a user to the database
        """
        self.db_client.table('profiles').insert({
            'google_id': user.google_id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_pic': user.profile_pic,
            'onboarded': user.onboarded,
            'information': "" # information should be put in a different table (though assoc w  profile, it is more relevant to onboarding)
        }).execute()
    
    def addOnboardingQA(self, column_name, answer, google_id):
        print("ADDING ONBOARDING QA")
        #question = question.strip()
        #column_name = onboarding_qa_map[question]
        response = self.db_client.table('onboarding').upsert({ # upsert is used to update the row if it already exists, inserts otherwise
            'google_id': google_id,
            column_name: answer
        }, on_conflict='google_id').execute()
        print("RESPONSE: ", response)

    def get_by_google_id(self, google_id):
        data = self.db_client.table('profiles').select('*').eq('google_id', google_id).execute()
        if not data.data:
            return None
        user_data = data.data[0]
        return User(
            google_id=user_data['google_id'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            profile_pic=user_data['profile_pic'],
            onboarded=user_data['onboarded']
        )
    
    def add_followup_QA(self, google_id, question, answer, summary):  # add_followup_QA(question, answer, ai_model.llm, google_id, first_name)
        # google_id is passed in because of the unique way model calls the follow up endpoint
        # ... can't assume current_user is set
        result = self.db_client.table('QA').insert({
            'google_id': google_id,
            'question': question,
            'answer': answer,
            'summary': summary
        }).execute()
        return result
    
    def finished_onboarding(self, user: User):
        user.onboarded = True
        self.db_client.table('profiles').update({'onboarded': True}).eq('google_id', user.google_id).execute()