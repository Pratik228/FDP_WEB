import cv2
import face_recognition
import pickle
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL' : 'https://facialattendance-d2c63-default-rtdb.firebaseio.com/',
    'storageBucket' : 'facialattendance-d2c63.appspot.com'
    })

# Importing images to list
folderPath = 'Images'
modePath = os.listdir(folderPath)
imgList = []
studId = []
for path in modePath:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studId.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)
    print(path)

def findEncodings(imgList):
    encodeList=[]
    for img in imgList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(img)
        if len(face_locations) > 0:
            encode = face_recognition.face_encodings(img, face_locations)[0]
            encodeList.append(encode)

    return encodeList

encodeKnown = findEncodings(imgList)
encodeKnownwithIds = [encodeKnown, studId]
print(encodeKnown)

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeKnownwithIds, file)
file.close()

print("File saved successfully")
