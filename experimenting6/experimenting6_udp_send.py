import socket
import sys

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = b"test"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # udp

def main():
    running = True
   # conn, addr = sock.accept()
    while running:
        s = input()
        if s == "exit":
            sys.exit()
        sock.sendto((s.encode()), (UDP_IP, UDP_PORT))

if __name__ == "__main__":
    main()