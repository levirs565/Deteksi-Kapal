from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import firestore_async
from dotenv import load_dotenv
import firebase_admin
import os

load_dotenv()

cred = credentials.Certificate(os.getenv("FIREBASE_ACCOUNT_KEY"))
firebase_admin.initialize_app(cred, {
    'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")
})

bucket = storage.bucket()
db = firestore_async.client()
gpsCollection = db.collection("gps")

def rebuild_db():
    db = firestore_async.client()