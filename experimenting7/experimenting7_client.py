import asyncio
import websockets
import websockets.sync.client
import uuid
import ssl
import logging
import json
import experimenting7_responses
import sys

logging.basicConfig(stream=sys.stderr,level=logging.INFO)
logger = logging.getLogger('websockets')

username = str(uuid.uuid4())
password = ""
async def main():
    while True:
        try:
            with websockets.sync.client.connect(f"ws://{username}:{password}@localhost:8001") as websocket:
                logger.info("connection to server established")
                #message = dict()
                #message['sender'] = sender
                #message_json = json.dumps(message)
                #websocket.send(message_json)
                #message = websocket.recv()
                #print(f"Received: {message}")
                sendtask = asyncio.Task(queue_input(websocket))
                recvtask = asyncio.Task(receive(websocket))
                await sendtask, recvtask
        except websockets.exceptions.WebSocketException:
            continue
        except ConnectionError:
            logger.info("connection refused")
            continue

async def get_input():
    while True:
        yield input()

def encode_as_message(message_content: str):
    message = dict()
    message['username'] = username
    message['content'] = message_content
    message_json = json.dumps(message)
    return message_json

def send(websock, message_json: str):
    websock.send(message_json)

async def queue_input(websock):
    while True:
        try:
            async for input_ in get_input():
                handle_input(input_,websock)
        except websockets.exceptions.WebSocketException:
            return

def handle_input(input_,websock):
    input_parsed = input_.split(" ")
    logger.debug(f"split message into {input_parsed}")
    match input_parsed:
        case [message]:
            send(websock, encode_as_message(message))
        case ["msg", *text] if type(text) == type([""]):
            text: list[str] = text
            text_rejoin = " ".join(text)
            send(websock, encode_as_message(text_rejoin))
        case[*text] if type(text) == type([""]):
            text: list[str] = text
            text_rejoin = " ".join(text)
            send(websock, encode_as_message(text_rejoin))
        case _:
            print("Couldn't send")


async def receive(websock):
    retry_time = 5
    while True:
        try:
            message = await websock.recv()
            print(f"Received: {message}")
            retry_time = 5
        except websockets.exceptions.WebSocketException:
        #except websockets.exceptions.ConnectionClosedOK:
            logger.info(f"client closed connection, retry in {retry_time}")
            retry_time = retry_time * 2
            await asyncio.sleep(retry_time)
        except websockets.exceptions.ConnectionClosedError:
            logger.info(f"server closed connection, retry in {retry_time}")
            retry_time = retry_time * 2
            await asyncio.sleep(retry_time)



if __name__ == "__main__":
    username = input("Enter username: ")
    password = input("Enter password: ")
    try:
        asyncio.run(main(), debug=True)
    except KeyboardInterrupt:
        main().close()
        sys.exit()
