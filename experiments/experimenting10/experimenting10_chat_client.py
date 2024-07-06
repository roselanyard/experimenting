import pydantic
import logging
import asyncio
import pygame
import websockets
import aioconsole
import uuid
import experimenting10_data as exp10_data
import experimenting10_game as exp10_game
import sys
import json

HOST = "127.0.0.1"
PORT = 5001

asyncio_logger = logging.getLogger("asyncio")
client_logger = logging.getLogger("client")
logging.basicConfig(level=logging.INFO)

outbound_queue = asyncio.Queue()

local_game_state: exp10_data.GameState | None
local_game_state = None
local_game_state_lock = asyncio.Lock()
local_game_state_init: asyncio.Future


async def update_game_state(new_game_state: exp10_data.GameState):
    global local_game_state
    async with local_game_state_lock:
        local_game_state = new_game_state


async def consumer(message: str):
    await aioconsole.aprint(message)
    try:
        message_obj: exp10_data.Message = exp10_data.Message.parse_raw(message)
        match message_obj.message_type:
            case exp10_data.GameStateMessage.__name__:
                # this is a hack
                message_obj: exp10_data.GameStateMessage = exp10_data.GameStateMessage.parse_raw(message)
                message_obj.data: exp10_data.GameState
                await update_game_state(message_obj.data)
    except pydantic.ValidationError as e:
        client_logger.warning(f"invalid message: {message}")


async def consumer_handler(websocket: websockets.WebSocketClientProtocol):
    async for message in websocket:
        await consumer(message)
        await asyncio.sleep(0)


async def producer():
    message = await outbound_queue.get()
    await aioconsole.aprint(message)
    return message


async def producer_handler(websocket: websockets.WebSocketClientProtocol):
    while True:
        message = await producer()
        await websocket.send(message)


async def handler(websocket: websockets.WebSocketClientProtocol):
    try:
        await outbound_queue.put("client connected")
        await asyncio.gather(consumer_handler(websocket), producer_handler(websocket))
    except (websockets.ConnectionClosedOK, websockets.ConnectionClosedError):
        client_logger.info("connection closed")


async def gui():
    global local_game_state
    pygame.init()
    display = pygame.display.set_mode((640, 480))
    clock = pygame.Clock()

    await asyncio.gather(handle_pygame_events(),render(display,clock))

async def handle_pygame_events():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                event_obj = exp10_data.encode_pygame_event(event)
                event_message_dict = dict()
                event_message_dict['data'] = event_obj
                event_message_obj = exp10_data.EventMessage(**event_message_dict)
                event_message_json = event_message_obj.json()
                await outbound_queue.put(event_message_json)
        await asyncio.sleep(0)

async def render(display: pygame.Surface,clock:pygame.Clock):
    while True:
        if local_game_state is not None:
            async with local_game_state_lock:
                game_state_text = local_game_state
                game_state_text: exp10_data.GameState
            display.fill((0, 0, 0))
            game_state_text_json = game_state_text.model_dump_json()
            game_state_text_json_pretty = json.dumps(json.loads(game_state_text_json), indent=4)

            game_state_text_render = exp10_game.font.render(game_state_text_json_pretty, False, (255, 255, 255), (0, 0, 0),
                                                            exp10_game.x_res)
            display.blit(game_state_text_render, (0, 0))
            for player in game_state_text.players.keys():
                pos = game_state_text.players.get(player).sprite.position
                display.blit(exp10_game.player_img,(pos[0],-pos[1]))
            pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(240)

async def main():
    global local_game_state_init
    local_game_state_init = asyncio.Future()
    #gui_loop = asyncio.new_event_loop()
    #gui_task = asyncio.run_coroutine_threadsafe(gui(),gui_loop)
    #gui_loop.run_forever()
    await asyncio.gather(client(), gui())


async def client():
    uri = f"ws://{HOST}:{PORT}"
    async for websocket in websockets.connect(uri):
        websocket: websockets.WebSocketClientProtocol
        await handler(websocket)


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
