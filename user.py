#from flask_login import UserMixin
from utils import encrypt_user_id

class User:
    # Simple user model - you'll want to connect this to a database
    def __init__(self, google_id, email, first_name, last_name, profile_pic, onboarded=False):
        self.id = google_id
        self.google_id = google_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.profile_pic = profile_pic
        self.onboarded = onboarded
        self.uid = encrypt_user_id(google_id)