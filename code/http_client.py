import socket
with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
    s.settimeout(3)
    s.connect(("2001:db8:2::2", 8000))
    s.sendall(b"GET / HTTP/1.0\r\nHost: iot-cloud\r\n\r\n")
    print(s.recv(4096).decode(errors="replace"))
