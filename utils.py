import os
import pickle
import numpy as np
from firebase_admin import db

def load_known_encodings_and_ids():
    use_firebase = os.environ.get('USE_FIREBASE', 'False').lower() == 'true'
    print(f"Using Firebase: {use_firebase}")

    if use_firebase:
        encodeKnown, studId = load_from_firebase()
    else:
        encodeKnown, studId = load_from_local()

    print(f"Total loaded: {len(encodeKnown)} encodings and {len(studId)} IDs")
    return encodeKnown, studId

def load_from_firebase():
    ref = db.reference('Encodings')
    encodings_data = ref.get()
    
    if not encodings_data:
        print("No encodings found in the Firebase database")
        return [], []
    
    encodeKnown = []
    studId = []
    
    for student_id, data in encodings_data.items():
        if 'encoding' in data:
            encodeKnown.append(np.array(data['encoding']))
            studId.append(student_id)
        else:
            print(f"Warning: No encoding found for student {student_id}")
    
    print(f"Loaded {len(encodeKnown)} encodings from Firebase")
    return encodeKnown, studId

def load_from_local():
    file_path = 'EncodeFile.p'
    if not os.path.exists(file_path):
        print(f"Encoding file not found at {file_path}")
        return [], []
    
    try:
        with open(file_path, 'rb') as file:
            encodeKnownwithIds = pickle.load(file)
        encodeKnown, studId = encodeKnownwithIds
        print(f"Loaded {len(encodeKnown)} encodings from local file")
        return encodeKnown, studId
    except Exception as e:
        print(f"Error loading encodings from local file: {str(e)}")
        return [], []