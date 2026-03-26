import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP
sock.bind(('', 5000)) # Listen on all interfaces, port 5000

while True:
    data, client_address = sock.recvfrom(1024) # Buffer size 1024 bytes
    print(f"Received message: {data.decode()} from {client_address}")

    routed_message = b"ROUTED: " + data
    sock.sendto(routed_message, ('127.0.0.1', 5001)) # Send routed message to the primary server

    response, _ = sock.recvfrom(1024) # Wait for response from primary server
    print(f"Received response from primary server: {response.decode()}")

    clean_response = response.replace(b"RESPONSE: ", b"")
    sock.sendto(clean_response, client_address) # Send final response back to the original client