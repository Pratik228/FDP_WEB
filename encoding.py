import cv2
import face_recognition
import firebase_admin
from firebase_admin import credentials, db, storage
import numpy as np
import os
import tempfile  # Add this import

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ.get('FIREBASE_DATABASE_URL'),
    'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET')
})

def encode_and_store():
    bucket = storage.bucket()
    ref = db.reference('Encodings')

    # List all files in the 'Images' folder of Firebase Storage
    blobs = bucket.list_blobs(prefix='Images/')

    for blob in blobs:
        if blob.name.endswith(('.jpg', '.jpeg', '.png')):
            # Download image to a temporary file
            _, temp_local_filename = tempfile.mkstemp()
            blob.download_to_filename(temp_local_filename)

            # Read the image
            img = cv2.imread(temp_local_filename)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Generate encoding
            face_locations = face_recognition.face_locations(img)
            if face_locations:
                encode = face_recognition.face_encodings(img, face_locations)[0]
                student_id = os.path.splitext(os.path.basename(blob.name))[0]
                
                # Store encoding in Firebase Realtime Database
                ref.child(student_id).set({
                    'encoding': encode.tolist(),
                    'name': student_id
                })
                
                print(f"Encoded and stored {student_id}")
            else:
                print(f"No face detected in {blob.name}")

            # Remove the temporary file
            os.remove(temp_local_filename)

    print("All encodings stored in Firebase Realtime Database")

if __name__ == "__main__":
    encode_and_store()