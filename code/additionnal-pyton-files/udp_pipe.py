import socket
from djitellopy import Tello
import threading

# Function to receive video stream from Tello and forward it to another UDP port
def forward_video_stream():
    # Create a Tello object
    tello = Tello()
    
    # Connect to the Tello drone
    tello.connect()
    tello.query_battery()  # Check battery status
    # Start the video stream
    tello.streamon()

    # Get the video stream address
    udp_address = ('0.0.0.0', 11111)
    
    # Create a UDP socket to receive the video stream from Tello
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock.bind(udp_address)

    # Create a UDP socket to send the video stream to another port
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_address = ('127.0.0.1', 22222)

    try:
        while True:
            # Receive the video frame from Tello
            frame, _ = recv_sock.recvfrom(65536)  # Buffer size is 2048 bytes
            
            # Forward the frame to the other UDP port
            send_sock.sendto(frame, send_address)
    except KeyboardInterrupt:
        print("Stream forwarding stopped")
    finally:
        # Close the sockets
        recv_sock.close()
        send_sock.close()
        tello.streamoff()
        tello.end()

# Run the video forwarding in a separate thread
thread = threading.Thread(target=forward_video_stream)
thread.start()
