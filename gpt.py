import asyncio
import base64
import time
import cv2
import numpy as np
from nats.aio.client import Client as NATS

nc = NATS()


# กำหนดช่วงสีเขียวในระบบ HSV
lower_green = np.array([40, 40, 40])
upper_green = np.array([80, 255, 255])

# เริ่มจับภาพจากกล้อง
cap = cv2.VideoCapture(0)


def image_to_base64(image):
    """แปลงภาพ BGR เป็น Base64"""
    _, buffer = cv2.imencode(".jpg", image)
    base64_str = base64.b64encode(buffer).decode("utf-8")
    return base64_str


async def publish(topic, image):
    """ส่งภาพไปยัง NATS"""
    base64_image = image_to_base64(image)
    await nc.publish(topic, base64_image.encode())


def detect_green_direction(frame):
    """ตรวจจับเส้นสีเขียวและระบุทิศทาง"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # ตัดเฉพาะช่วงล่างของภาพ
    height, width = mask.shape
    mask_roi = np.zeros_like(mask)
    polygon = np.array(
        [
            [
                (0, height),
                (width, height),
                (width, int(height * 0.6)),
                (0, int(height * 0.6)),
            ]
        ]
    )
    cv2.fillPoly(mask_roi, polygon, 255)
    masked = cv2.bitwise_and(mask, mask_roi)

    # ตรวจเส้นใน mask
    edges = cv2.Canny(masked, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, minLineLength=50, maxLineGap=150)

    direction = "ไม่พบเส้นสีเขียว"
    slopes = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
            slope = (y2 - y1) / (x2 - x1 + 1e-6)
            slopes.append(slope)

        avg_slope = np.mean(slopes)

        if avg_slope < -0.3:
            direction = "เลี้ยวขวา"
        elif avg_slope > 0.3:
            direction = "เลี้ยวซ้าย"
        else:
            direction = "ตรง"
        
        print(f"{time.time()}: {direction}")

    # แสดงข้อความทิศทาง
    cv2.putText(
        frame,
        f"ทิศทาง: {direction}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (0, 255, 0),
        3,
    )

    return frame, direction


async def main():
    await nc.connect("nats://192.168.1.6:4222")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # frame = cv2.resize(frame, (640, 480))
        frame = cv2.resize(frame, (160, 120))

        # ตรวจจับทิศทางจากเส้นสีเขียว
        green_frame, direction = detect_green_direction(frame.copy())

        # ส่งภาพไปยัง NATS
        await publish("original_image", frame)

        # (Optional) ส่งข้อความทิศทางด้วย
        # mask_image = cv2.cvtColor(green_frame, cv2.COLOR_GRAY2BGR)
        # await nc.publish("mask_image", mask_image)

        # กด q เพื่อออก
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


asyncio.run(main())
