import socket

def read_exactly(sock, n):
    """Read exactly n bytes from the socket."""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:  # Socket closed
            raise ConnectionError("Connection closed unexpectedly")
        data += packet
    return data

def send_message(sock, msg):
    """Send a message with length prefix."""
    msg_bytes = msg.encode('utf-8')
    length = len(msg_bytes)
    sock.sendall(length.to_bytes(4, 'big') + msg_bytes)

def receive_message(sock):
    """Receive a message with length prefix."""
    length_bytes = read_exactly(sock, 4)
    length = int.from_bytes(length_bytes, 'big')
    msg_bytes = read_exactly(sock, length)
    return msg_bytes.decode('utf-8')