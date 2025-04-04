import serial

# open port
def get_serial():
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1.0)  
    ser.reset_input_buffer()
    return ser

# send value's motor data
def send_data(left_speed, right_speed):
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1.0)  
    ser.reset_input_buffer()

    right_speed = right_speed if right_speed >= 0 else 0
    left_speed = left_speed if left_speed >= 0 else 0
    
    message = f"{right_speed},{left_speed}\n"
    ser.write(message.encode('utf-8'))