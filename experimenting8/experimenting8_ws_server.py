import asyncio
import websockets
import aioconsole

HOST = "127.0.0.1"
PORT = 5001

inbound_queue = []
outbound_queue = []
inbound_queue_lock = asyncio.Lock()
outbound_queue_lock = asyncio.Lock()

async def consumer(message):
    await aioconsole.aprint(f"<<< {message}")
async def producer():
    await asyncio.sleep(2)
    await aioconsole.aprint(f">>> message from producer of server")
    return "message from producer of server"

async def consumer_handler(websocket):
    async for message in websocket:
        await consumer(message)

async def producer_handler(websocket):
    while True:
        message = await producer()
        await websocket.send(message)

async def handler(websocket):
    try:
        await asyncio.gather(consumer_handler(websocket),producer_handler(websocket))
    except websockets.ConnectionClosedOK:
        print("client closed connection OK")

auth_protocol = websockets.basic_auth_protocol_factory(realm="my dev server", credentials=("test", "testing"))
async def main():
    server = await websockets.serve(ws_handler=handler, host=HOST, port=PORT, create_protocol=auth_protocol)
    stop = asyncio.Future()
    async with server:
        await stop

if __name__ == "__main__":
    asyncio.run(main())