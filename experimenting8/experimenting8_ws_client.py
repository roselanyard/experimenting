import asyncio
import websockets
import aioconsole
import logging
import json
import pygame
import experimenting8_gamestate
import pydantic
import sys
from collections import deque

logger = logging.getLogger("websockets")
logging.basicConfig(level=logging.INFO)

HOST = "127.0.0.1"
PORT = 5001

inbound_queue = []
outbound_queue = asyncio.Queue()
inbound_queue_lock = asyncio.Lock()
outbound_queue_lock = asyncio.Lock()

display = pygame.display.set_mode((640,480))
clock = pygame.Clock()
pygame.font.init()
font = pygame.font.Font()
state_changed = asyncio.Event()

async def consumer(message: str):
    try:
        message_obj: experimenting8_gamestate.GameState = experimenting8_gamestate.GameState.parse_raw(message)
        print(message_obj)
        await pygame_handle(message_obj)
    except pydantic.ValidationError as e:
        pass
    await aioconsole.aprint(f"<<< {message}")
async def producer():
    return await outbound_queue.get()
    #else:
    #    await asyncio.sleep(5)
    #    await aioconsole.aprint(f">>> message from producer of client")
    #    return "message from producer of client"

async def consumer_handler(websocket):
    async for message in websocket:
        #deque.append(message)
        await consumer(message)

async def producer_handler(websocket):
    while True:
        try:
            message = await asyncio.wait_for(producer(),0.2)
            await websocket.send(message)
        except TimeoutError as e:
            logger.debug("producer_handler timed out")

async def pygame_handle(message_obj):
    global display
    global font

    display.fill(message_obj.color)
    text = font.render(str(message_obj.angle),False,(0,0,0))
    display.blit(text,(0,0))
    for player_uuid in message_obj.players.keys():
        player: experimenting8_gamestate.Player
        player = message_obj.players[player_uuid]
        player_name = font.render(player.name,False,(255,255,255),player.color)

        display.blit(player_name,player.position)
    pygame.display.flip()

async def pygame_loop():
    global outbound_queue
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click_event = dict()
                click_event['type'] = event.type
                click_event['pygame_dict'] = event.dict
                click_event_obj = experimenting8_gamestate.GameEvent(**click_event)
                click_event_json = click_event_obj.json()
                await outbound_queue.put(click_event_json)

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(0)

async def handler(websocket):
    await asyncio.gather(consumer_handler(websocket),producer_handler(websocket),pygame_loop())

def dump_credentials():
    credentials = dict()
    credentials['username'] = "test"
    credentials['password'] = "testing"
    return json.dumps(credentials)

async def main():

    pygame.init()

    stop = asyncio.Future()
    while not stop.done():
        # try:
        async for websocket in websockets.connect(uri=f"ws://{HOST}:{PORT}"):
            await websocket.send(dump_credentials())
            try:
                await handler(websocket)
                await stop
            except websockets.ConnectionClosed:
                continue

if __name__ == "__main__":
    asyncio.run(main(),debug=True)