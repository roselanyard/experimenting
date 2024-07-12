import time

import pydantic
import logging
import asyncio
import pygame
import websockets
import aioconsole
import uuid
import experimenting10_data as exp10_data
import experimenting10_game as exp10_game
import typing

HOST = "127.0.0.1"
PORT = 5001

asyncio_logger = logging.getLogger("asyncio")
server_logger = logging.getLogger("server")
logging.basicConfig(level=logging.INFO)

broadcast_outbound_messages = asyncio.Queue()
unicast_outbound_messages: typing.Dict[uuid.UUID, asyncio.Queue] = dict()
uuid_table: typing.Dict[websockets.WebSocketServerProtocol, uuid.UUID] = dict()
game_event_queue = asyncio.Queue()

global_game_state: exp10_data.GameState
global_game_state = exp10_data.get_init_game_state()
global_game_state_lock = asyncio.Lock()

async def consumer(message: str,websocket: websockets.WebSocketServerProtocol) -> None:
    try:
        message_obj: exp10_data.Message = exp10_data.Message.parse_raw(message)
        match message_obj.message_type:
            case exp10_data.EventMessage.__name__:
                player_uuid = uuid_table[websocket]
                message_obj: exp10_data.EventMessage = exp10_data.EventMessage.parse_raw(message)
                await game_event_queue.put((player_uuid,message_obj.data))

    except pydantic.ValidationError as e:
        server_logger.warning(f"invalid message: {message}")
    await aioconsole.aprint(message)

async def consume_game_event(game_event: tuple[uuid.UUID,exp10_data.PygameEvent]):
    if game_event[1].pygame_type == pygame.KEYDOWN:
        match game_event[1].pygame_dict['key']:
            case pygame.K_d:
                async with global_game_state_lock:
                    velocity = global_game_state.players.get(game_event[0]).sprite.velocity
                    new_velocity = (5,velocity[1])
                    global_game_state.players.get(game_event[0]).sprite.velocity = new_velocity
            case pygame.K_a:
                async with global_game_state_lock:
                    velocity = global_game_state.players.get(game_event[0]).sprite.velocity
                    new_velocity = (-5, velocity[1])
                    global_game_state.players.get(game_event[0]).sprite.velocity = new_velocity
            case pygame.K_w:
                async with global_game_state_lock:
                    velocity = global_game_state.players.get(game_event[0]).sprite.velocity
                    new_velocity = (velocity[0],5)
                    global_game_state.players.get(game_event[0]).sprite.velocity = new_velocity
            case pygame.K_s:
                async with global_game_state_lock:
                    velocity = global_game_state.players.get(game_event[0]).sprite.velocity
                    new_velocity = (velocity[0], -5)
                    global_game_state.players.get(game_event[0]).sprite.velocity = new_velocity

    if game_event[1].pygame_type == pygame.KEYUP:
        match game_event[1].pygame_dict['key']:
            case pygame.K_d:
                async with global_game_state_lock:
                    velocity = global_game_state.players.get(game_event[0]).sprite.velocity
                    if velocity[0] == 5:
                        new_velocity = (0, velocity[1])
                        global_game_state.players.get(game_event[0]).sprite.velocity = new_velocity
            case pygame.K_a:
                async with global_game_state_lock:
                    velocity = global_game_state.players.get(game_event[0]).sprite.velocity
                    if velocity[0] == -5:
                        new_velocity = (0, velocity[1])
                        global_game_state.players.get(game_event[0]).sprite.velocity = new_velocity
            case pygame.K_w:
                async with global_game_state_lock:
                    velocity = global_game_state.players.get(game_event[0]).sprite.velocity
                    if velocity[1] == 5:
                        new_velocity = (velocity[0], 0)
                        global_game_state.players.get(game_event[0]).sprite.velocity = new_velocity
            case pygame.K_s:
                async with global_game_state_lock:
                    velocity = global_game_state.players.get(game_event[0]).sprite.velocity
                    if velocity[1] == -5:
                        new_velocity = (velocity[0], 0)
                        global_game_state.players.get(game_event[0]).sprite.velocity = new_velocity
    global_game_state.timestamp = int(time.time_ns()/1000)
    await resend_game_state()

async def game_event_handler():
    while True:
        event = await game_event_queue.get()
        await consume_game_event(event)

async def consumer_handler(websocket: websockets.WebSocketServerProtocol, client_uuid: uuid.UUID) -> None:
    async for message in websocket:
        await consumer(message,websocket)

async def producer(client_uuid: uuid.UUID) -> str:
    message = await unicast_outbound_messages[client_uuid].get()
    await aioconsole.aprint(message)
    return message

async def broadcaster():
    while True:
        message = await broadcast_outbound_messages.get()
        recipients = uuid_table.keys()
        websockets.broadcast(recipients,message)

async def game_tick_producer():
    pygame.init()
    clock = pygame.Clock()
    while True:
        for player in global_game_state.players.keys():
            old_position = global_game_state.players[player].sprite.position
            velocity = global_game_state.players[player].sprite.velocity
            new_position = (old_position[0]+velocity[0],old_position[1]+velocity[1])
            global_game_state.players[player].sprite.position = new_position
        await resend_game_state()
        await asyncio.sleep(0.2)


async def producer_handler(websocket: websockets.WebSocketServerProtocol,client_uuid: uuid.UUID) -> None:
    while True:
        message = await producer(client_uuid)
        await websocket.send(message)

async def resend_game_state():
    game_state_message_dict = dict()
    game_state_message_dict["data"] = global_game_state
    game_state_message_dict["timestamp"] = (time.time_ns()/1000)
    game_state_message_obj = exp10_data.GameStateMessage(**game_state_message_dict)
    game_state_message_obj_json = game_state_message_obj.model_dump_json()

    await broadcast_outbound_messages.put(game_state_message_obj_json)

async def handler(websocket: websockets.WebSocketServerProtocol) -> None:
    global global_game_state
    client_uuid = uuid.uuid4()
    uuid_table[websocket] = client_uuid
    unicast_outbound_messages[client_uuid] = asyncio.Queue()
    await unicast_outbound_messages[client_uuid].put("server connected")

    init_game_state_message_dict = dict()
    init_game_state_message_dict["data"] = global_game_state
    init_game_state_message_dict["timestamp"] = (time.time_ns()/1000)
    init_game_state_message_obj = exp10_data.GameStateMessage(**init_game_state_message_dict)
    init_game_state_message_obj_json = init_game_state_message_obj.json()
    await unicast_outbound_messages[client_uuid].put(init_game_state_message_obj_json)

    global_game_state.players[client_uuid] = exp10_data.get_default_player()

    try:
        await asyncio.gather(consumer_handler(websocket,client_uuid), producer_handler(websocket,client_uuid),
                             broadcaster(),game_event_handler())#game_tick_producer())
    except (websockets.ConnectionClosedOK, websockets.ConnectionClosedError):
        server_logger.info("connection closed")
    finally:
        global_game_state.players.pop(client_uuid)
        unicast_outbound_messages.pop(client_uuid)
        uuid_table.pop(websocket)
        await resend_game_state()


async def main() -> None:
    uri = f"ws://{HOST}:{PORT}"
    server = websockets.serve(handler, HOST, PORT)
    stop = asyncio.Future()
    async with server:
        await asyncio.gather(stop)


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
