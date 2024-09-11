import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import os


def initialize_firebase():
    cred = credentials.Certificate("serviceAccountKey.json")
    
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app(cred, {
            'databaseURL': os.environ.get('FIREBASE_DATABASE_URL'),
            'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET')
        })

    ref = db.reference('Students')
    encodings_ref = db.reference('Encodings')
    bucket = storage.bucket()
    
    return bucket, ref, encodings_ref
