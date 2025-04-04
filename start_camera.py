import cv2
import time


def capture():
    start = time.time()
    # cap = cv2.VideoCapture("/dev/video0")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()
    else:
        print("Open Camera")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    end = time.time()
    print("Open Camera(s):", end - start)
    return cap
