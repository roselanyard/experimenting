import asyncio
import types

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
import multiprocessing
import threading


# nest_asyncio.apply()

class ContextObject:
    def __init__(self):
        pass


class Message:
    # message content only encoded upon sending
    def __init__(self, headers=None, body=None):
        if headers is None:
            self.headers = dict()
        if body is None:
            self.body = None
        self.headers = headers
        self.body = body


logging.basicConfig(level=logging.DEBUG)

context = ContextObject()
context.username = str(uuid.uuid4())
context.websock_timeout = 2
context.input_timeout = 0.5
context.logger = logging.getLogger('client')
context.input_message_buffer = []
context.event_buffer = []
context.received_message_buffer = []
context.websocket_connection = None
context.locks = ContextObject()
context.locks.input_message_buffer = asyncio.Lock()
context.locks.received_message_buffer = asyncio.Lock()
context.intervals = ContextObject()
context.intervals.sleep = ContextObject()
context.intervals.sleep.get_input = 0.2
context.intervals.sleep.queue_input = 0.3
context.intervals.sleep.receive = 0.5
context.intervals.sleep.handle_received = 0.2
context.intervals.timeout = ContextObject()
context.intervals.timeout.handle_received = 1
context.intervals.timeout.receive = 0.5
context.running = False

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


def _handle_task_result(task: asyncio.Task):
    # noinspection PyBroadException
    try:
        task.result()
    except asyncio.CancelledError:
        pass
    except Exception:
        logging.exception("Exception raised by %r", task)


async def get_input():
    # while True in event loop instead of here (or not)
    while True:
        try:
            user_input = await aioconsole.ainput("Enter prompt: ")
            async with context.locks.input_message_buffer:
                context.input_message_buffer.append(user_input)
        except UnicodeDecodeError:
            context.logger.info("unicode decode error in get_input")
        await asyncio.sleep(context.intervals.sleep.get_input)


def encode_as_message(message_content: str):
    message = dict()
    message['username'] = username
    message['content'] = message_content
    message_json = json.dumps(message)
    return message_json


async def send(message_json: str):
    if context.websocket_connection is None:
        context.logger.debug(f"Failed to send json; context.websocket_connection was None: \n {message_json}")
        context.websocket_connection = await get_connection()
        return
    context.websocket_connection.send(message_json)


async def queue_input():
    # while True in event loop instead of here
    while True:
        try:
            async with context.locks.input_message_buffer:
                for user_input in context.input_message_buffer:
                    context.logger.debug(f"Handling input {user_input}")
                    await handle_input(user_input)
                    context.input_message_buffer.pop(0)
                    break
        except websockets.exceptions.WebSocketException:
            return
        await asyncio.sleep(context.intervals.sleep.queue_input)


async def handle_input(user_input):
    input_parsed = user_input.split(" ")
    context.logger.debug(f"split message into {input_parsed}")
    match input_parsed:
        case [message]:
            await send(encode_as_message(message))
        case ["msg", *text] if type(text) == type([""]):
            text: list[str] = text
            text_rejoin = " ".join(text)
            await send(encode_as_message(text_rejoin))
        case [*text] if type(text) == type([""]):
            text: list[str] = text
            text_rejoin = " ".join(text)
            await send(encode_as_message(text_rejoin))
        case _:
            await aioconsole.aprint("Couldn't send")


async def receive():
    websock = context.websocket_connection
    # while True running in event loop instead of here
    while True:
        await asyncio.sleep(context.intervals.sleep.receive)
        all_messages_read = False
        async with asyncio.timeout(context.intervals.timeout.receive):
            try:
                while not all_messages_read:
                    if type(websock) is type(None):
                        context.websocket_connection = await get_connection()
                        websock = context.websocket_connection
                    try:
                        message_json = websock.recv()
                    except (websockets.exceptions.WebSocketException):
                        context.logger.info("connection closed")
                        all_messages_read = True
                        context.websocket_connection = await get_connection()
#except Exception:
                   #     print(Exception)
                   #     all_messages_read = True
            except TimeoutError:
                context.logger.debug("message handler timed out")
                all_messages_read = True
                continue

            async with context.locks.received_message_buffer:
                context.received_message_buffer.append(message_json)
            # await aioconsole.aprint(f"server sends {message_json}")


async def handle_message(message):
    await aioconsole.aprint(f"received {message}")


async def handle_received():
    # while True running in event loop instead of here
    while True:
        all_messages_read = len(context.received_message_buffer) == 0
        async with asyncio.timeout(context.intervals.timeout.handle_received):
            while not all_messages_read:
                async with context.locks.received_message_buffer:
                    for message in context.received_message_buffer:
                        try:
                            await handle_message(message)
                        except TimeoutError:
                            context.logger.info("handle_received timed out")
        await asyncio.sleep(context.intervals.sleep.handle_received)


def guitestfunction(event):
    pass


def gui():
    root = tk.Tk()
    mainframe = tk.Frame(root)
    mainframe.grid(column=0, row=0)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    button = tk.Button(mainframe, text="send message")
    button.grid(column=2, row=2)
    button.bind("<Button>", guitestfunction)
    # root.bind("<Return>",guitestfunction)
    root.mainloop()
    return


async def get_connection():
    retry_time = 5
    while context.websocket_connection is None:
        context.logger.debug("restarting the while loop")
        try:
            client_websocket = websockets.sync.client.connect(f"ws://{username}:{password}@localhost:8001")
            if client_websocket is not None:
                context.logger.info("connection to server established")
                return client_websocket
        except (ConnectionError, websockets.exceptions.WebSocketException, websockets.exceptions.ConnectionClosedError):
            context.websocket_connection = None
            context.logger.info(f"connection refused, retry in {retry_time}")
            retry_time = retry_time * 2
        #await asyncio.sleep(retry_time)


async def main():
    backend_loop = asyncio.get_event_loop()
    backend_loop.set_debug(enabled=True)

    get_input_task = backend_loop.create_task(get_input())
    get_input_task.add_done_callback(_handle_task_result)

    handle_received_task = backend_loop.create_task(handle_received())
    handle_received_task.add_done_callback(_handle_task_result)

    # gui_task = backend_loop.create_task(gui())
    # gui_task.add_done_callback(_handle_task_result)

    receive_task = backend_loop.create_task(receive())
    receive_task.add_done_callback(_handle_task_result)

    queue_input_task = backend_loop.create_task(queue_input())
    queue_input_task.add_done_callback(_handle_task_result)
    context.running = True

    context.websocket_connection = await get_connection()

    while context.running:
        await asyncio.sleep(0)
        try:
            if not backend_loop.is_running():
                backend_loop.run_forever()
        except websockets.exceptions.WebSocketException:
            context.websocket_connection = await get_connection()
        except websockets.exceptions.ConnectionClosedError:
            context.websocket_connection = await get_connection()
    backend_loop.stop()


if __name__ == "__main__":
    username = input("Enter username: ")
    password = input("Enter password: ")
    try:
        multiprocessing.Process(target=gui)
        asyncio.run(main(), debug=True)
        # asyncio.get_event_loop().run_until_complete(receive)
    except KeyboardInterrupt:
        sys.exit()
