import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP
sock.bind(('', 5001)) # Listen on all interfaces, port 5001

while True:
    data, addr = sock.recvfrom(1024) # Buffer size 1024 bytes
    print(f"Received message: {data.decode()} from {addr}")

    if data.startswith(b"ROUTED: "):
        original_message = data[len(b"ROUTED: "):] # Remove "ROUTED: " prefix
        print(f"Original message extracted: {original_message.decode()}")

        response = b"RESPONSE: " + original_message.upper() # Create response by converting to uppercase
        sock.sendto(response, addr) # Send response back to the DNS server
        print(f"Sent response: {response.decode()} to {addr}")
