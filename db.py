from flask import current_app
from flask_login import UserMixin
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

_db = None

class User(UserMixin):
    def __init__(self, _id, email, role, password_hash):
        self.id = str(_id)
        self.email = email
        self.role = role
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

def init_db(app):
    global _db
    client = MongoClient(app.config["MONGO_URI"])
    _db = client[app.config["MONGO_DB"]]
    # Ensure indexes
    _db.users.create_index("email", unique=True)
    _db.assignments.create_index([("student_id", 1), ("created_at", -1)])
    _db.similarity_logs.create_index("created_at")

    # Seed sample users if empty
    if _db.users.count_documents({}) == 0:
        _db.users.insert_many([
            {"email": "student1@example.com", "role": "student", "password_hash": generate_password_hash("student123")},
            {"email": "faculty1@example.com", "role": "faculty", "password_hash": generate_password_hash("faculty123")},
        ])

def get_db():
    return _db

def get_user_by_email(email):
    doc = _db.users.find_one({"email": email})
    if not doc:
        return None
    return User(doc["_id"], doc["email"], doc["role"], doc["password_hash"])

def get_user_by_id(user_id):
    try:
        doc = _db.users.find_one({"_id": ObjectId(user_id)})
        if not doc:
            return None
        return User(doc["_id"], doc["email"], doc["role"], doc["password_hash"])
    except Exception:
        return None