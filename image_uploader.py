import firebase_admin
import os
from firebase_admin import credentials
from firebase_admin import storage
from dotenv import load_dotenv
from datetime import datetime
import cv2
import concurrent.futures

load_dotenv()

cred = credentials.Certificate(os.getenv("FIREBASE_ACCOUNT_KEY"))
firebase_admin.initialize_app(cred, {
    'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")
})

bucket = storage.bucket()

pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)

def upload_image_internal(image, folder):
    ret, buffer =  cv2.imencode(".jpg", image)
    if not ret:
        print("Encode failed")
        return
    name = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    blob = bucket.blob("{}/{}".format(folder, name))
    blob.upload_from_string(buffer.tobytes(), content_type="image/jpeg")

def upload_image(image, folder):
    pool.submit(upload_image_internal, image, folder)

def shutdown():
    pool.shutdown()