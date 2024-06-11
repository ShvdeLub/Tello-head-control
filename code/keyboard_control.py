import keyboard
from djitellopy import Tello


def rc_control(tello):
    set_speed = 80
    while True:
        forward_backward = 0
        left_right = 0
        up_down = 0
        yaw = 0
        if keyboard.is_pressed("up"):
            forward_backward = set_speed
        elif keyboard.is_pressed("down"):
            forward_backward = -set_speed
        if keyboard.is_pressed("left"):
            left_right = -set_speed
        elif keyboard.is_pressed("right"):
            left_right = set_speed
        if keyboard.is_pressed("z"):
            up_down = set_speed
        elif keyboard.is_pressed("s"):
            up_down = -set_speed
        if keyboard.is_pressed("q"):
            yaw = -set_speed
        elif keyboard.is_pressed("d"):
            yaw = set_speed
        if keyboard.is_pressed("t"):
            tello.takeoff()
        print(left_right, forward_backward, up_down, yaw)
        tello.send_rc_control(left_right, forward_backward, up_down, yaw)

def control_drone():
    # Create a Tello instance
    tello = Tello()

    # Connect to the drone
    tello.connect()

    battery_level = tello.get_battery()
    if not battery_level:
        print("Failed to connect to Tello drone")
        return
    else:
        print(f"Battery level: {battery_level}%")
    tello.takeoff()
    tello.streamon()

    try:
        rc_control(tello)
    except KeyboardInterrupt:
        print("Stream forwarding stopped")
    finally:
        tello.streamoff()
        tello.end()
        print("Landed")

control_drone()