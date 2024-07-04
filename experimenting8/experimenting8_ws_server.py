import asyncio
import logging

import pygame
import urllib3.util
import websockets
import aioconsole
import uuid
import urllib.parse
import pydantic
import experimenting8_gamestate
import random

HOST = "127.0.0.1"
PORT = 5001

inbound_queue = []
outbound_queue = []
inbound_queue_lock = asyncio.Lock()
outbound_queue_lock = asyncio.Lock()

asyncio_logger = logging.getLogger('asyncio')
server_logger = logging.getLogger('server')
logging.basicConfig(level=logging.WARNING)

connected_users = set()
connected_user_information = dict()

got_input = asyncio.Event()
state_changed = asyncio.Event()

game_state = dict()
game_state['color'] = (255,255,255)
game_state['angle'] = 1
game_state['players'] = dict()
#game_state_changed = asyncio.Future()

async def consumer(message):
    await aioconsole.aprint(f"<<< {message}")
async def producer():
    await state_changed.wait()
    string = f"message from producer of server: there are {len(connected_users)} users online"
    string = experimenting8_gamestate.GameState(**game_state)
    string = string.json()
    await aioconsole.aprint(f">>> {string}")
    state_changed.clear()
    return string

async def consumer_handler(websocket:websockets.BasicAuthWebSocketServerProtocol):
    async for message in websocket:
        try:
            message_obj = experimenting8_gamestate.GameEvent.parse_raw(message)
            if message_obj.type == pygame.MOUSEBUTTONDOWN:
                game_state['players'][connected_user_information[websocket]].position = message_obj.pygame_dict['pos']
                game_state['angle'] += 1
                game_state['color'] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                state_changed.set()
        except pydantic.ValidationError as e:
            server_logger.debug("received non-event message")
            message_with_context = f"\nSOCKET: {websocket}\nCONN_UUID: {connected_user_information[websocket]}\nCONTENT: {message}\n"
            await consumer(message_with_context)

async def producer_handler(websocket):
    while True:
        message = await producer()
        await websocket.send(message)

async def handler(websocket:websockets.BasicAuthWebSocketServerProtocol, path):
    connected_user_player_obj = None
    try:
        connected_users.add(websocket)
        connected_user_information[websocket] = uuid.uuid4()
        connected_user_player = dict()
        connected_user_player['color'] = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        connected_user_player['position'] = (0,0)
        connected_user_player['name'] = str(connected_user_information[websocket])
        connected_user_player['id'] = connected_user_information[websocket]
        connected_user_player_obj = experimenting8_gamestate.Player(**connected_user_player)
        game_state['players'][connected_user_information[websocket]] = connected_user_player_obj
        state_changed.set()
        await asyncio.gather(consumer_handler(websocket),producer_handler(websocket))
    except websockets.ConnectionClosedOK:
        print("client closed connection OK")
    finally:
        if connected_user_player_obj is not None:
            game_state['players'].pop(connected_user_information[websocket])
        connected_users.remove(websocket)
async def main():
    server = await websockets.serve(ws_handler=handler, host=HOST, port=PORT)
    stop = asyncio.Future()
    async with server:
        await stop

if __name__ == "__main__":
    asyncio.run(main())