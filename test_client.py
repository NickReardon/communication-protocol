import socket
import sys

# sys.argv[0] is always the script name
# sys.argv[1] is the message, sys.argv[2] is the port
if len(sys.argv) < 3:
    print("Usage: python3 test_client.py <message> <port>")
    sys.exit(1)

message = sys.argv[1].encode()  # convert string to bytes
port = int(sys.argv[2])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)

server_addr = ('127.0.0.1', port)
sock.sendto(message, server_addr)
print(f"Sent: {message.decode()} to {server_addr}")

try:
    data, addr = sock.recvfrom(1024)
    print(f"Received: {data.decode()} from {addr}")
except socket.timeout:
    print("No response - server may be down")

sock.close()