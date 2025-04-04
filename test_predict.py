import base64
import cv2
import time
import asyncio
from fastai.vision.all import *
from nats.aio.client import Client as NATS

nc = NATS()

# 📌 โหลดโมเดล
learn = load_learner("fastai_model.pkl")
print("✅ Model loaded successfully!")

# 📌 โหลดวิดีโอจากกล้อง
cap = cv2.VideoCapture(0)

# ตรวจสอบการเปิดกล้อง
if not cap.isOpened():
    print("❌ Error: Cannot open video stream.")
    exit()


def image_to_base64(image):
    """แปลงภาพ BGR เป็น Base64"""
    _, buffer = cv2.imencode(".jpg", image)
    base64_str = base64.b64encode(buffer).decode("utf-8")
    return base64_str


async def publish(topic, image):
    """ส่งภาพไปยัง NATS"""
    base64_image = image_to_base64(image)
    await nc.publish(topic, base64_image.encode())


async def main():
    await nc.connect("nats://192.168.1.6:4222")

    # 🔥 เริ่มวนลูปการอ่านเฟรมวิดีโอ
    prev_time = time.time()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("🚀 Video playback finished.")
            break

        # 🔥 ทำการทำนาย
        start_time = time.time()
        pred_class, pred_idx, outputs = learn.predict(frame)
        end_time = time.time()

        # 🔹 รายชื่อคลาสจากโมเดล
        class_names = learn.dls.vocab
        percentages = outputs * 100

        # 🔹 แสดงข้อมูลบนเฟรม
        cv2.putText(
            frame,
            f"Predicted: {pred_class}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        # 🔥 แสดงคะแนนของแต่ละคลาส
        for i, (cls, score) in enumerate(zip(class_names, percentages)):
            text = f"{cls}: {score:.2f}%"
            cv2.putText(
                frame,
                text,
                (10, 60 + i * 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 0),
                2,
            )

        # 🔥 แสดง FPS
        fps = 1 / (end_time - start_time)
        cv2.putText(
            frame,
            f"FPS: {fps:.2f}",
            (10, 450),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
        )

        # 🖥️ แสดงเฟรมพร้อมข้อมูล
        # cv2.imshow("Video Preview", frame)
        await publish("original_image", frame)

        # กด 'q' เพื่อออก
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # 🔥 ปิดกล้องและหน้าต่าง
    cap.release()
    cv2.destroyAllWindows()
    print("🔒 Video stream closed.")


asyncio.run(main())
