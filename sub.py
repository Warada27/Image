import asyncio
import base64
import time
import cv2
import numpy as np
from nats.aio.client import Client as NATS

def base64_to_image(base64_str):
    """แปลง Base64 เป็นภาพ BGR"""
    img_data = base64.b64decode(base64_str)
    np_arr = np.frombuffer(img_data, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return image

async def subscribe():
    nc = NATS()
    await nc.connect("nats://192.168.1.6:4222")
    print("Connected to NATS server")

    async def mask_image_handler(msg):
        """แปลง Base64 เป็นภาพ BGR และแสดงภาพ"""
        base64_str = msg.data.decode()
        image = base64_to_image(base64_str)
        if image is not None:
            cv2.imshow("Mask Image", image)
            cv2.waitKey(1)
        print(f"Received mask image")

    async def original_image_handler(msg):
        """แปลง Base64 เป็นภาพ BGR และแสดงภาพ"""
        base64_str = msg.data.decode()
        image = base64_to_image(base64_str)
        if image is not None:
            cv2.imshow("Original Image", image)
            cv2.waitKey(1)
        print(f"{time.time()} Received original image")

    # Subscribe to the topics
    await nc.subscribe("mask_image", cb=mask_image_handler)
    await nc.subscribe("original_image", cb=original_image_handler)
    await nc.flush()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await nc.close()
        cv2.destroyAllWindows()

asyncio.run(subscribe())
