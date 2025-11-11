from mongoengine import Document, StringField, IntField, DateTimeField
from datetime import datetime

class Admin_And_User(Document):
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    # Optional mobile number for login via phone. Unique when present.
    phone = StringField(required=False, unique=True, sparse=True)
    password = StringField(required=True)
    role = StringField(required=True, choices=['admin', 'user'])
    auth_token = StringField()
    full_name = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)



    def to_json(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "full_name": self.full_name,
            "created_at": self.created_at.isoformat()
        }