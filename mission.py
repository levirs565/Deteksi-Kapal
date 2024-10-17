import core
import threading
import time

def wait_mission():
    while True:
        mission = core.json_get(f"{core.companionServerRoot}/mission")
        if mission["started"]:
            return mission
        
mission_end = threading.Event()
mission_end_kill = threading.Event()
def wait_stop_worker():
    global mission_end
    while True:
        mission = core.json_get(f"{core.companionServerRoot}/mission")
        if not mission["started"]:
            mission_end.set()
            break
        if mission_end_kill.wait(1):
            break

mission_end_thread = threading.Thread(target=wait_stop_worker)

def start_mission_end_listener():
    global mission_end_thread
    mission_end_thread.start()

def stop_mission_end_listener():
    global mission_end_thread
    if mission_end.is_set(): return
    mission_end_kill.set()
    mission_end_thread.join()