from datetime import datetime
import cv2
import concurrent.futures
import firebase_util

pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)

def upload_image_internal(image, folder):
    ret, buffer =  cv2.imencode(".jpg", image)
    if not ret:
        print("Encode failed")
        return
    name = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    blob = firebase_util.bucket.blob("{}/{}".format(folder, name))
    blob.upload_from_string(buffer.tobytes(), content_type="image/jpeg")

def upload_image(image, folder):
    pool.submit(upload_image_internal, image, folder)

def shutdown():
    pool.shutdown()