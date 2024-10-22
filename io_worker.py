import queue
import asyncio
import threading
import firebase_util
import cv2
from datetime import datetime
from firebase_admin import firestore_async
import concurrent.futures
import aiohttp
import core
import json
import requests

pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
thread = None
mission_end = threading.Event()

def wait_mission():
    while True:
        mission = json.loads(requests.get(f"{core.companionServerRoot}/mission").text)
        if mission["started"]:
            return mission

async def upload_gps_task(gps_data):
    print("Start uploading gps")
    await firebase_util.gpsCollection.add({
        "loc": [gps_data["lat"], gps_data["lng"]],
        "speed": gps_data["speed"],
        "timestamp": firestore_async.firestore.SERVER_TIMESTAMP
    })
    print("Uploading gps finished")

def upload_image_internal(image, folder):
    ret, buffer =  cv2.imencode(".jpg", image)
    if not ret:
        print("Encode failed")
        return
    name = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    blob = firebase_util.bucket.blob("{}/{}".format(folder, name))
    blob.upload_from_string(buffer.tobytes(), content_type="image/jpeg")


async def upload_image_task(image, folder):
    print("Start uploading image")
    await asyncio.get_running_loop().run_in_executor(pool, upload_image_internal, image, folder)
    print("Uploading image finished")

async def mission_stop_worker():
    global mission_end
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(f"{core.companionServerRoot}/mission") as resp:
                mission = json.loads(await resp.text())
                if not mission["started"]:
                    print("Mission end")
                    mission_end.set()
                    break
            if mission_end.is_set():
                break
            await asyncio.sleep(1)

task_queue = queue.Queue()
async def worker_async():
    asyncio.create_task(mission_stop_worker())
    while True:
        if not task_queue.empty():
            task = task_queue.get()
            if "gps" in task:
                asyncio.create_task(upload_gps_task(task["gps"]))
            if "image" in task:
                asyncio.create_task(upload_image_task(task["image"], task["folder"]))
        if mission_end.is_set():
            break
        await asyncio.sleep(0.1)
                

def worker():
    asyncio.run(worker_async())
    print("Closed")

def start():
    global thread
    mission_end.clear()
    thread = threading.Thread(target=worker)
    thread.start()

def shutdown():
    mission_end.set()
    thread.join()

def upload_image(img, folder):
    task_queue.put({
        "image": img,
        "folder": folder
    })

def upload_gps(gps):
    task_queue.put({
        "gps": gps
    })