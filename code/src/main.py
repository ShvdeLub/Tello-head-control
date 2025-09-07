import numpy as np
import serial
import keyboard
import socket
from djitellopy import Tello
import threading

# Read data on the serial port
arduino = serial.Serial(port='COM3',  baudrate=115200, timeout=.1) # Change the COM port if needed
arduino.write(b'RESET\n')

def read(arduino):
    try:
        arduino.reset_input_buffer()
        data = arduino.readline()
        string = data.decode()
        stripped_string = string.strip()
        if stripped_string:
            liste = stripped_string.split(",")
            liste_flt = list(map(float, liste))
            return liste_flt
    except (ValueError, UnicodeDecodeError):
        return None
    return None

def trigger(tello, arduino):
    init = np.array(read(arduino)[2:])
    print(init)
    set_angle, set_speed = 30, 100
    while True:
        value = np.array(read(arduino))
        dif = value[2:] - init 
        bwd, fwd = value[:2]
        alpha, beta, gamma = ((dif + 180) % 360) - 180    
        if keyboard.is_pressed('q'):
            init = value[2:]  # re-define init values
        forward_backward, left_right, up_down, yaw = 0, 0, 0, 0
        if fwd == 1:
            forward_backward = set_speed
        elif bwd == 1:
            forward_backward = -set_speed
        if gamma < -set_angle:
            left_right = -set_speed
        elif gamma > set_angle:
            left_right = set_speed
        if beta < -set_angle:
            up_down = set_speed
        elif beta > set_angle:
            up_down = -set_speed
        if alpha > set_angle:
            yaw = -set_speed
        elif alpha < -set_angle:
            yaw = set_speed
        tello.send_rc_control(left_right, forward_backward, up_down, yaw)
        print(forward_backward, left_right, up_down, yaw)

def stream_video():
    global send_address, send_sock, recv_sock
    udp_address = ('0.0.0.0', 11111)  # UDP address of the Tello
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock.bind(udp_address)
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_address = ('127.0.0.1', 22222)
    
    while True:
        frame, _ = recv_sock.recvfrom(65536)  # Buffer size
        send_sock.sendto(frame, send_address)  # pipe the frames to the other UDP port

def control_drone():
    tello = Tello()
    tello.connect()
    battery_level = tello.get_battery()
    print(f"Battery level: {battery_level}%")
    tello.streamon()
    tello.takeoff()
    
    # Create and start the streaming thread
    stream_thread = threading.Thread(target=stream_video)
    stream_thread.start()
    
    # Run the trigger function in the main thread
    try:
        trigger(tello, arduino)
    finally:
        recv_sock.close()
        send_sock.close()
        tello.streamoff()
        tello.land()
        print("Landed")

control_drone()