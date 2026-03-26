import socket
import threading
import time

HEATBEAT_INTERVAL = 2  # seconds
DNS_SERVER_PORT = 5000
PRIMARY_SERVER_PORT = 5001
BACKUP_SERVER_PORT = 5002
HEARTBEAT_TIMEOUT = 5  # seconds
RECOVERY_TIME = 10  # seconds


def heartbeat_loop():
    hb_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        hb_sock.sendto(b"HEARTBEAT", ('127.0.0.1', BACKUP_SERVER_PORT)) # Send heartbeat to backup server
        print("Sent heartbeat sent to backup server" + time.strftime(" (%H:%M:%S)"))
        time.sleep(HEATBEAT_INTERVAL) # Wait for the specified interval before sending the next heartbeat


heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
heartbeat_thread.start()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP
sock.bind(('', PRIMARY_SERVER_PORT)) # Listen on all interfaces, port 5001


while True:
    data, addr = sock.recvfrom(1024) # Buffer size 1024 bytes
    print(f"Received message: {data.decode()} from {addr}")

    if data.startswith(b"ROUTED: "):
        original_message = data[len(b"ROUTED: "):] # Remove "ROUTED: " prefix
        print(f"Original message extracted: {original_message.decode()}")

        response = b"RESPONSE: " + original_message.upper() # Create response by converting to uppercase
        sock.sendto(response, addr) # Send response back to the DNS server
        print(f"Sent response: {response.decode()} to {addr}")
