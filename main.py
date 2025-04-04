import asyncio
import cv2
import time
import base64
from nats.aio.client import Client as NATS

from start_camera import capture
from img_processing import filter_img
from send_serial import get_serial, send_data
from line import find_line

# สร้าง Client ของ NATS
nc = NATS()

frame = None

def image_to_base64(image):
    """แปลงภาพ BGR เป็น Base64"""
    _, buffer = cv2.imencode('.jpg', image)
    base64_str = base64.b64encode(buffer).decode('utf-8')
    return base64_str

async def publish(topic, image):
    """ส่งภาพไปยัง NATS"""
    base64_image = image_to_base64(image)
    await nc.publish(topic, base64_image.encode())

async def capture_frames():
    """ฟังก์ชันจับภาพจากกล้อง"""
    global frame
    cap = capture()

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Failed to capture frame")
            await asyncio.sleep(0.01)  # หยุดสักเล็กน้อยเพื่อไม่ให้บล็อก
            continue
        
        await publish("original_image", frame)
        frame = cv2.resize(frame, (160, 120))
        # ส่งภาพไปยัง NATS (ภาพต้นฉบับ)
        await asyncio.sleep(0.01)  # ป้องกันการบล็อก Event Loop

async def process_image():
    """ฟังก์ชันประมวลผลภาพ"""
    global frame
    while True:
        start = time.time()

        if frame is not None:
            mask = filter_img(frame)
            find_line(mask)

            # แปลงภาพให้เป็น BGR ก่อนส่ง
            mask_image = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            await publish("mask_image", mask_image)

            end = time.time()
            # print("Processing(s):", end - start)
        else:
            print("Waiting for frame...")
        
        await asyncio.sleep(0.01)  # ป้องกันการบล็อก Event Loop

async def main():
    """ฟังก์ชันหลัก"""
    await nc.connect("nats://192.168.1.6:4222")

    try:
        get_serial()

        # ใช้ asyncio.gather() เพื่อรันฟังก์ชัน async ทั้งสองพร้อมกัน
        await asyncio.gather(
            capture_frames(),
            process_image()
        )

    except KeyboardInterrupt:
        send_data(0, 0)
        print("Exit")
        await nc.close()
        cv2.destroyAllWindows()

asyncio.run(main())
