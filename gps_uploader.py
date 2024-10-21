import firebase_util
import concurrent.futures
from firebase_admin import firestore

pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)

def upload_gps_internal(gps_data):
    firebase_util.gpsCollection.add({
        "loc": [gps_data["lat"], gps_data["lng"]],
        "speed": gps_data["speed"],
        "timestamp": firestore.firestore.SERVER_TIMESTAMP
    })

def upload_gps(gps_data):
    pool.submit(upload_gps_internal, gps_data)

def shutdown():
    pool.shutdown()