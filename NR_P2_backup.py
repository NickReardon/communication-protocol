import socket
import threading
import time

HEATBEAT_INTERVAL = 2  # seconds
DNS_SERVER_PORT = 5000
PRIMARY_SERVER_PORT = 5001
BACKUP_SERVER_PORT = 5002
HEARTBEAT_TIMEOUT = 5  # seconds
RECOVERY_TIME = 10  # seconds

state = "STANDBY"  # Initial state of the backup server
active_server_port = PRIMARY_SERVER_PORT
last_heartbeat_time = time.time()


def primary_server_no_longer_responding():
    global state, active_server_port
    state = "ACTIVE"
    active_server_port = BACKUP_SERVER_PORT
    sock.sendto(b"PRIMARY_DOWN", ('127.0.0.1', DNS_SERVER_PORT))

def primary_server_has_stabilized():
    global state, active_server_port
    state = "STANDBY"
    active_server_port = PRIMARY_SERVER_PORT
    sock.sendto(b"PRIMARY_UP", ('127.0.0.1', DNS_SERVER_PORT))

def heartbeat_monitor():
    global state, last_heartbeat_time
    recovery_start_time = None
    
    while True:
        time.sleep(1)
        
        current_time = time.time()
        
        if state == "STANDBY":
            if current_time - last_heartbeat_time > HEARTBEAT_TIMEOUT:
                print("Primary server heartbeat missed. Switching to backup server.")
                primary_server_no_longer_responding()
                
        elif state == "ACTIVE":
            if current_time - last_heartbeat_time > HEARTBEAT_TIMEOUT:
                # Gap detected - primary still unstable, reset the recovery clock
                recovery_start_time = None
                
            else:
                # Heartbeats are arriving - start the clock if not already running
                if recovery_start_time is None:
                    recovery_start_time = current_time
                    print("Primary heartbeats detected - starting recovery timer")
                    
                # Check if primary has been stable long enough
                elif current_time - recovery_start_time >= RECOVERY_TIME:
                    print("Primary stable - switching back to STANDBY")
                    recovery_start_time = None
                    primary_server_has_stabilized()
                

heartbeat_thread = threading.Thread(target=heartbeat_monitor, daemon=True)
heartbeat_thread.start()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP
sock.bind(('', BACKUP_SERVER_PORT)) # Listen on all interfaces, port 5002

sock.settimeout(1) # Set timeout for socket operations to allow periodic heartbeat checks
while True:
    try: 
        data, addr = sock.recvfrom(1024) # Buffer size 1024 bytes
    except socket.timeout:
        continue  # No data received, just keep waiting
    
    print(f"Received message: {data.decode()} from {addr}")
    if data == b"HEARTBEAT":
        last_heartbeat_time = time.time()
        print(f"Heartbeat received from primary (state: {state})")
        
    elif state == "ACTIVE":
        if data.startswith(b"ROUTED: "):
            original_message = data[len(b"ROUTED: "):]
            response = b"RESPONSE: " + original_message.lower()
            sock.sendto(response, addr)
            print(f"Sent response to DNS: {response.decode()}")
            
    elif state == "STANDBY" and data.startswith(b"ROUTED: "):
        print("Received client request while in STANDBY - should never happen")
