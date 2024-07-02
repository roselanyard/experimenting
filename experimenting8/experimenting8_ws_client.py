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
    await asyncio.sleep(5)
    await aioconsole.aprint(f">>> message from producer of client")
    return "message from producer of client"

async def consumer_handler(websocket):
    async for message in websocket:
        await consumer(message)

async def producer_handler(websocket):
    while True:
        message = await producer()
        await websocket.send(message)

async def handler(websocket):
    await asyncio.gather(consumer_handler(websocket),producer_handler(websocket))

auth_protocol = websockets.basic_auth_protocol_factory(realm="my dev server", credentials=("test", "testing"))
async def main():
    stop = asyncio.Future()
    async for websocket in websockets.connect(uri=f"ws://test:testing@{HOST}:{PORT}"):
        try:
            await handler(websocket)
            await stop
        except websockets.ConnectionClosed:
            continue

if __name__ == "__main__":
    asyncio.run(main(),debug=True)