import pickle

def load_known_encodings_and_ids():
    file = open('EncodeFile.p', 'rb')
    encodeKnownwithIds = pickle.load(file)
    file.close()
    encodeKnown, studId = encodeKnownwithIds
    return encodeKnown, studId
