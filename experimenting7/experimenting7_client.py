import asyncio
import websockets
import websockets.sync.client
import uuid
import ssl
import logging
import json
import experimenting7_responses
import sys
import nest_asyncio
import tkinter as tk
import aioconsole

nest_asyncio.apply()

logger = logging.getLogger('websockets')
logging.basicConfig(stream=sys.stderr,level=logging.DEBUG)

username = str(uuid.uuid4())
password = ""
websock_timeout = 2
input_timeout = 0.5

def _handle_task_result(task: asyncio.Task):
    # noinspection PyBroadException
    try:
        task.result()
    except asyncio.CancelledError:
        pass
    except Exception:
        logging.exception("Exception raised by %r", task)



async def get_input():
    while True:
        #input_ = await asyncio.to_thread(input, "Accepting input: ")
        #async with asyncio.timeout(input_timeout):
        try:
            #yield input()
            yield "test string"
            #yield await aioconsole.ainput("Input: ")
        except UnicodeDecodeError:
            logger.info("unicode decode error")
            yield "unicode decode error"
        await asyncio.sleep(0.2)

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
                logger.debug(f"Handling input {input_}")
                handle_input(input_,websock)
                break
        except websockets.exceptions.WebSocketException:
            return
        await asyncio.sleep(0.3)

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
    while True:
        await asyncio.sleep(0.5)
        all_messages_read = False
        while not all_messages_read:
            try:
                message_json = websock.recv()
            except TimeoutError:
                logger.debug("message handler timed out")
                continue
            except websockets.exceptions.WebSocketException:
                logger.info("connection closed")

            print(f"server sends {message_json}")

    #while True:
    #try:
        #message = await asyncio.wait_for(websock.recv(), websock_timeout)
    #    message = websock.recv()
    #    print(f"Received: {message}")
    #except TimeoutError:
    #    logger.info(f"client timed out receiving messages")
    #except TypeError:
    #    print(type(websock.recv()))

def guitestfunction():
    pass
def gui():
    root = tk.Tk()
    mainframe = tk.Frame(root)
    mainframe.grid(column=0,row=0)
    root.columnconfigure(0,weight=1)
    root.rowconfigure(0,weight=1)
    tk.Button(mainframe,text="send message").grid(column=2,row=2)
    root.bind("<Return>",guitestfunction)
    root.mainloop()
    return




async def connection_loop():
    retry_time = 5
    while True:
        logger.debug("restarting the while loop")
        try:
            with (websockets.sync.client.connect(f"ws://{username}:{password}@localhost:8001") as client_websocket):
                logger.info("connection to server established")
                #message = dict()
                #message['sender'] = sender
                #message_json = json.dumps(message)
                #websocket.send(message_json)
                #message = websocket.recv()
                #print(f"Received: {message}")
                sendtask = asyncio.Task(queue_input(client_websocket))
                # = asyncio.Task(get_input())
                #recvtask = asyncio.Task(receive(websocket))
                #asyncio.get_event_loop().create_task(asyncio.wait_for(receive(websocket),websock_timeout))
                #.run_forever(asyncio.wait_for(receive(websocket),websock_timeout))
                message_handler_task = asyncio.create_task(receive(client_websocket))
                message_handler_task.add_done_callback(_handle_task_result)
                # asyncio.get_event_loop().run_forever()
                await sendtask
        except ConnectionError:
            logger.info(f"connection refused, retry in {retry_time}")
            retry_time = retry_time * 2
            await asyncio.sleep(retry_time)
        except websockets.exceptions.WebSocketException:
            # except websockets.exceptions.ConnectionClosedOK:
            logger.info(f"client closed connection, retry in {retry_time}")
            retry_time = retry_time * 2
            await asyncio.sleep(retry_time)
        except websockets.exceptions.ConnectionClosedError:
            logger.info(f"server closed connection, retry in {retry_time}")
            retry_time = retry_time * 2
            await asyncio.sleep(retry_time)

async def main():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    #loop.default_exception_handler()
    asyncio.to_thread(gui())
    asyncio.run(connection_loop(),debug=True)
    result = await loop.run_in_executor(None,connection_loop(),debug=True)
    #await asyncio.gather(gui(), connection_loop(), return_exceptions=True)

if __name__ == "__main__":
    username = input("Enter username: ")
    password = input("Enter password: ")
    try:
        asyncio.run(main(),debug=True)
        #asyncio.get_event_loop().run_until_complete(receive)
    except KeyboardInterrupt:
        main().close()
        sys.exit()
