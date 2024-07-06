import socket
import asyncio
import experimenting6_locks
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
async def main():
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        async with experimenting6_locks.net_lock:
            experimenting6_locks.net_string = sock.recvfrom(1024)
            time.sleep(100)

def exec_input_mode():
    while True:
        data, addr = sock.recvfrom(1024)
        try:
            exec(data)
        except:
            print("malformed command")

def real_time_chat_app_mode():
    while True:
        data, addr = sock.recvfrom(1024)

if __name__ == "__main__":
    asyncio.run(main())