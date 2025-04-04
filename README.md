
## Pi 3 (64 Bit)
user: pi
pass: 123456

## Remote pi ssh
```
sshpass -p '123456' ssh pi@192.168.1.12
```

## python version
```
$ python --version
Python 3.11.2
```

# ✅ วิธีที่ 2: ใช้ Virtual Environment (venv) และ pip (แนะนำ)
## 1. ติดตั้ง Virtual Environment
```
sudo apt update    # อัปเดตฐานข้อมูลแพ็กเกจ
sudo apt upgrade -y  # อัปเกรดแพ็กเกจที่มีการอัปเดต

sudo apt install -y python3-venv python3-pip
```

## 🔹 2. ติดตั้ง picamera2
```
sudo apt install libcamera-apps libcamera-dev python3-libcamera
sudo apt install -y python3-picamera2
## or
pip install picamera2
```

## 2. สร้าง Virtual Environment
```
python -m venv venv
python -m venv --system-site-packages venv
source venv/bin/activate
```

## 3. ติดตั้ง OpenCV ผ่าน pip
```
pip install --upgrade pip
pip install opencv-python numpy

python -c "import cv2; print(cv2.__version__)"
```

## ✅ ส่งไฟล์:
```
sshpass -p '123456' scp main.py pi@192.168.1.12:/home/pi/Desktop/robot

## AI-classification
sshpass -p '123456' scp image-classitication/fastai_model.pkl pi@192.168.1.12:/home/pi/Desktop/robot
sshpass -p '123456' scp image-classitication/2_test.py pi@192.168.1.12:/home/pi/Desktop/robot

## Line-Robot
sshpass -p '123456' scp -r line-robot pi@192.168.1.12:/home/pi/Desktop/robot/line-robot

sshpass -p '123456' scp line-robot/gpt.py pi@192.168.1.12:/home/pi/Desktop/robot/line-robot/gpt.py
sshpass -p '123456' scp line-robot/main.py pi@192.168.1.12:/home/pi/Desktop/robot/line-robot/main.py
sshpass -p '123456' scp line-robot/img_processing.py pi@192.168.1.12:/home/pi/Desktop/robot/line-robot/img_processing.py
sshpass -p '123456' scp line-robot/util.py pi@192.168.1.12:/home/pi/Desktop/robot/line-robot/util.py
sshpass -p '123456' scp line-robot/line.py pi@192.168.1.12:/home/pi/Desktop/robot/line-robot/line.py
sshpass -p '123456' scp line-robot/send_serial.py pi@192.168.1.12:/home/pi/Desktop/robot/line-robot/send_serial.py
sshpass -p '123456' scp line-robot/test_predict.py pi@192.168.1.12:/home/pi/Desktop/robot/line-robot/test_predict.py
```

## ✅ รันโปรแกรม:
```
python main.py
```


# ----- Raspberry Pi and Pi Camera with YOLOv5 and YOLOv8
[### ](https://dagshub.com/Ultralytics/ultralytics/pulls/6537/files?page=0&path=docs%2Fen%2Fguides%2Fraspberry-pi.md)

https://medium.com/@zippylll1123/train-custom-object-detection-by-yolov8-%E0%B8%AD%E0%B8%A2%E0%B9%88%E0%B8%B2%E0%B8%87%E0%B8%87%E0%B9%88%E0%B8%B2%E0%B8%A2-%E0%B9%82%E0%B8%94%E0%B8%A2%E0%B9%83%E0%B8%8A%E0%B9%89-python-9e2042dbc000

## ดาวน์โหลด yolov8n.pt (Nano version ของ YOLOv8) ที่ผ่านการ pretrained จาก Ultralytics
curl -L -o yolov8n.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt


### การ Train โมเดล YOLOv8 สำหรับ Object Detection มี 5 ขั้นตอนหลัก:
เตรียมข้อมูล (Collect & Annotate Data)
จัดรูปแบบข้อมูลให้เป็น YOLO Format
ติดตั้ง Ultralytics YOLOv8
Train โมเดล
Evaluate & Export โมเดล




## nats
docker run -d --name nats-server -p 4222:4222 -p 8222:8222 nats:latest
