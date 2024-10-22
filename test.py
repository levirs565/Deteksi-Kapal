import threading
import asyncio
import time
import queue

# Inisialisasi queue untuk mengirim tugas
task_queue = queue.Queue()

async def handle_tasks():    
    while True:
        # Jika ada tugas baru dari task_queue, buat task baru
        if not task_queue.empty():
            task = task_queue.get()
            if task == 'upload_gps':
                asyncio.create_task(upload_gps())
            elif task == 'upload_image':
                asyncio.create_task(upload_image())
            elif task == 'wait_for_mission':
                asyncio.create_task(wait_for_mission())
        await asyncio.sleep(0.1)

async def upload_gps():
    print("Mengupload GPS data...")
    await asyncio.sleep(1)  # Simulasi penundaan jaringan
    print("GPS data terupload.")

async def upload_image():
    print("Mengupload gambar...")
    await asyncio.sleep(2)  # Simulasi penundaan jaringan
    print("Gambar terupload.")

async def wait_for_mission():
    print("Menunggu misi baru dari HTTP...")
    await asyncio.sleep(3)  # Simulasi penundaan jaringan
    print("Misi baru diterima.")

def asyncio_thread():
    asyncio.run(handle_tasks())

def main_thread():
    # Mengirim tugas baru ke thread asyncio
    for i in range(3):
        task_queue.put('upload_gps')
        task_queue.put('upload_image')
        task_queue.put('wait_for_mission')
        time.sleep(2)  # Simulasi pengiriman tugas dari thread utama

# Membuat thread untuk asyncio
asyncio_thread_handle = threading.Thread(target=asyncio_thread, daemon=True)
asyncio_thread_handle.start()

# Thread utama mengirim tugas ke thread asyncio
main_thread()

# Menjaga program tetap berjalan
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Program dihentikan")
