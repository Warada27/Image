from send_serial import send_data

global state


def velocity(status, x, y):

    slope = float(x)
    intersect = float(y)
    base_speed = 120
    max_speed = 200
    k_slope = 50
    maxline = 60  # max straight line
    minline = 30  # min straight line
    a = 30  # value's motor to left right of straight line

    if status == "true":
        # straight line
        if (slope < 0 and intersect < 0) or (slope > 0 and intersect > 0):
            # straight on
            if -1 < slope < 1 and minline <= intersect <= maxline:
                right_speed = base_speed
                left_speed = base_speed
                print(f"ตรง: {right_speed}, {left_speed}")

            # b is not in range maxline and minline
            elif intersect > maxline or intersect < minline:
                # the robot is to the left of the line
                if intersect > maxline:
                    send_data(intersect * 10, 0)  # left, right
                    print("เลี้ยวขวาตรง", intersect)
                    right_speed = 0
                    left_speed = a

                # the robot is to the right of the line.
                if intersect < minline:
                    if intersect < 0:
                        intersect = -intersect - minline
                    send_data(0, intersect * 20)
                    print("เลี้ยวซ้ายตรง", intersect)
                    right_speed = a
                    left_speed = 0
        # turn left
        elif slope > 0 and intersect < 0:
            right_speed = 80 + k_slope * slope + (-intersect) / 60
            left_speed = 80 - k_slope * slope - (-intersect) / 20
            print(f"เลี้ยวซ้าย: {right_speed}, {left_speed}")

        # turn right
        elif slope < 0 and intersect > 0:
            slope = -slope
            right_speed = 80 - k_slope * slope - intersect / 60
            left_speed = 80 + k_slope * slope + intersect / 20
            print(f"เลี้ยวขวา: {right_speed}, {left_speed}")

    else:
        if x != 0 and y != 0:
            right_speed = x
            left_speed = y
            # print(left_speed, right_speed)
        else:
            right_speed = 0
            left_speed = 0
            # print(left_speed, right_speed)

    try:
        # Limit the motor speeds to the maximum value
        left_speed = max(-max_speed, min(max_speed, left_speed))
        right_speed = max(-max_speed, min(max_speed, right_speed))
    except:
        left_speed = 0
        right_speed = 0
        send_data(0, 0)

    return right_speed, left_speed
