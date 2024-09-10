import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from dotenv import load_dotenv
import os

load_dotenv() 

def initialize_firebase():
    cred = credentials.Certificate("serviceAccountKey.json")
    
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app(cred, {
            'databaseURL': os.getenv('FIREBASE_DATABASE_URL'),
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
        })

    ref = db.reference('Students')
    encodings_ref = db.reference('Encodings')
    bucket = storage.bucket()
    
    return bucket, ref, encodings_ref
