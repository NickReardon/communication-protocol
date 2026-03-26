import socket



HEATBEAT_INTERVAL = 2  # seconds
DNS_SERVER_PORT = 5000
PRIMARY_SERVER_PORT = 5001
BACKUP_SERVER_PORT = 5002
HEARTBEAT_TIMEOUT = 5  # seconds
RECOVERY_TIME = 10  # seconds
DNS_SOCKET_TIMEOUT = 3  # seconds

active_server_port = PRIMARY_SERVER_PORT



sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP
sock.bind(('', DNS_SERVER_PORT)) # Listen on all interfaces, port 5000


sock.settimeout(DNS_SOCKET_TIMEOUT) # Set timeout for DNS socket operations

while True:
    try:
        data, client_address = sock.recvfrom(1024)
    except socket.timeout:
        continue  # no client message, just keep waiting
    
    print(f"Received: {data.decode()} from {client_address}")
    
    # Handle control messages - these are not client requests, skip forwarding
    if data == b"PRIMARY_DOWN":
        print("PRIMARY_DOWN received - switching to backup")
        active_server_port = BACKUP_SERVER_PORT
        continue # skip to next loop iteration
        
    elif data == b"PRIMARY_UP":
        print("PRIMARY_UP received - switching to primary")
        active_server_port = PRIMARY_SERVER_PORT
        continue  # skip to next loop iteration
    
    # client request
    active_addr = ('127.0.0.1', active_server_port)
    sock.sendto(b"ROUTED: " + data, active_addr)
    
    try:
        response, _ = sock.recvfrom(1024)
        clean = response.replace(b"RESPONSE: ", b"")
        sock.sendto(clean, client_address)
        
    except socket.timeout:
        print(f"Timeout - {active_server_port} unresponsive")
        
        if active_server_port == PRIMARY_SERVER_PORT:
            # Switch to backup and retry
            active_server_port = BACKUP_SERVER_PORT
            sock.sendto(b"ROUTED: " + data, ('127.0.0.1', active_server_port))
            
            try:
                response, _ = sock.recvfrom(1024)
                clean = response.replace(b"RESPONSE: ", b"")
                sock.sendto(clean, client_address)
            except socket.timeout:
                print("Backup also unresponsive - dropping request")