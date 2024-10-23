import cv2
import io_worker

cam = cv2.VideoCapture(0)
cam.set(3, 640)
cam.set(4, 480)

io_worker.start()

force_stop = False

try:
    while not force_stop:
        print("Wait mission")
        io_worker.wait_mission()
        print("Mission started")
        io_worker.start_mission_end_listener()

        while True:
            ret, frame = cam.read()

            if not ret:
                break

            print("A")
            io_worker.upload_image(frame, "Bawah")
            io_worker.upload_gps({
                "lat": 0,
                "lng": 0,
                "speed": 0,
            })
            print("B")

            if cv2.waitKey(10000) == ord('q'):
                force_stop = True
                break

            if io_worker.mission_end.wait(0.01):
                break
finally:
    io_worker.shutdown()