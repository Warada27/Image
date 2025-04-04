import cv2
from util import get_limits


def filter_img(frame):
    yellow = [0, 255, 255]
    black = [0, 0, 0]
    green = [0, 255, 0]

    # flip image
    flip_img = cv2.flip(frame, 0)
    flip_img_hz = cv2.flip(flip_img, 1)

    # convert image to hsv
    hsvImage = cv2.cvtColor(flip_img_hz, cv2.COLOR_BGR2HSV)

    # get lower & upper color
    lowerLimit, upperLimit = get_limits(color=yellow)

    # filter images are in range lower and upper
    mask = cv2.inRange(hsvImage, lowerLimit, upperLimit)

    return mask
