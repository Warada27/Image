from numpy import asarray
import numpy as np
from v_motor import velocity
from scipy.stats import zscore
from send_serial import send_data


def find_line(mask):

    # change image to array
    array_img = asarray(mask)

    # find length of column and row image
    col = len(array_img[0, :])
    row = len(array_img[:, 0])

    # find center of image from row and column
    center_x = col / 2
    center_y = row / 2

    middle_line = []
    x_axis = []
    y_axis = []

    # scan rows every 90 row
    for i in range(0, row - 1, 90):
        find_line = []  # collect the scanned point
        index = 0  # number of index
        # scan row
        for j in array_img[i, :]:
            if index > 0 and index < col - 1:  # not first index and last index
                bf_array = array_img[i, index - 1]  # value before array
                af_array = array_img[i, index + 1]  # value after array
                # j is value now
                if (
                    j == 255 and bf_array == 255 and af_array == 255
                ):  # before array, last array and j are white
                    find_line.append(index)
            if j == 255 and index == 0:  # first index j is white
                find_line.append(index)
            index += 1

        if len(find_line) != 0:
            # choose first and last point to find mid-line
            first_col = find_line[0]
            last_col = find_line[-1]
            mid_col = (first_col + last_col) / 2
            # transpose x and y
            center_zero_x = i - center_y
            center_zero_y = mid_col - center_x
            mid_point = [center_zero_x, center_zero_y]  # (y,x)
            middle_line.append(mid_point)
            x_axis.append(center_zero_x)
            y_axis.append(center_zero_y)

    if len(x_axis) != 0 or len(y_axis) != 0:
        x = np.array(x_axis, dtype=float)
        y = np.array(y_axis, dtype=float)

        # delete outlier
        z_scores = zscore(y)

        threshold = 3

        filtered_indices = np.where(np.abs(z_scores) < threshold)
        filtered_x = x[filtered_indices]
        filtered_y = y[filtered_indices]

        # find a, b
        if len(filtered_x) != 0 and len(filtered_y) != 0:
            a, b = np.polyfit(filtered_x, filtered_y, 1)
            # print(f"true,{a},{b}")
            right_speed, left_speed = velocity("true", a, b)
            print(f"R: {right_speed} L:{left_speed}")

        else:
            a, b = np.polyfit(x, y, 1)
            # print(f"true,{a},{b}")
            right_speed, left_speed = velocity("true", a, b)
            print(f"R: {right_speed} L:{left_speed}")

    else:
        # print(f"false,NaN,NaN")
        right_speed, left_speed = velocity("false", 0, 0)
        # print(f"Right: {right_speed} Left:{left_speed}")

    send_data(left_speed, right_speed)
