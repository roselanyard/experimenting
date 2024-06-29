import asyncio
import websockets
import websockets.server
import ssl
import uuid
import logging
import json
import pymongo
import datetime
import sys

logger = logging.getLogger('websockets')
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class PersistentServerData:
    pass


class Context:
    pass


p_server_data = PersistentServerData()
p_server_data.users = []
connections = []

uuid = uuid.uuid4()
ssl_ = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
timeout_threshold = datetime.timedelta(seconds=6)
recv_timeout_threshold = 0.2
lock_timeout_threshold = 2
# ssl_.load_dh_params("./experimenting7_params.pem")

# mongodb_client = pymongo.MongoClient("mongodb://localhost:27017")
# mongodb_database = mongodb_client["database"]
# user_collection = mongodb_database['users']

data_lock = asyncio.Lock()

users = dict()
sessions = dict()


async def authenticate_user(username: str, password_hash: str, lock_acquired_above: bool = False):
    async with data_lock:
        logger.debug("data lock acquired by authenticate user")
        if username in users.keys() and password_hash == users[username]:
            context = Context()
            context.lock_acquired_above = False
            await create_session(username, lock_acquired_above=True)
            logger.info(f"created session for user {username}")
        logger.debug("data lock released by authenticate user")


async def create_user(username: str, password_hash: str, lock_acquired_above: bool = False):
    if not lock_acquired_above:
        try:
            await asyncio.wait_for(data_lock.acquire(), lock_timeout_threshold)
            logger.debug("data lock acquired by create user")
        except TimeoutError:
            logger.info(f"could not acquire lock, user {username} not created")
            return
    if username not in users.keys():
        users[username] = password_hash
        logger.info(f"created user {username}")
    if not lock_acquired_above:
        data_lock.release()
        logger.debug("data lock released by create user")


async def create_session(username: str, lock_acquired_above: bool = False):
    if not lock_acquired_above:
        try:
            await asyncio.wait_for(data_lock.acquire(), lock_timeout_threshold)
            logger.debug("data lock acquired by create session")
        except TimeoutError:
            logger.info(f"could not acquire lock, user {username} not created")
            return
    if username not in sessions.keys():
        sessions[username] = dict()
        sessions[username]['lastseen'] = datetime.datetime.now()
        logger.info(f"created session for user {username}")
    if not lock_acquired_above:
        data_lock.release()
        logger.debug("data lock released by create session")


async def session_handler(lock_acquired_above: bool = False):
    while True:
        logger.info("session handler checking")
        if not lock_acquired_above:
            try:
                await asyncio.wait_for(data_lock.acquire(), lock_timeout_threshold)
                logger.debug("data lock acquired by session handler")
            except TimeoutError:
                logger.info(f"session handler timed out acquiring data lock")
                continue
        termination_queue = []
        for user in sessions.keys():
            assert (user in sessions.keys() and
                    'lastseen' in sessions[user].keys())
            if datetime.datetime.now() - sessions[user]['lastseen'] >= timeout_threshold:
                termination_queue.append(user)
        for user in termination_queue:
            await terminate_session(user,lock_acquired_above=True)
        if not lock_acquired_above:
            data_lock.release()
            logger.debug("data lock released by session handler")
        await asyncio.sleep(5)


async def message_handler(websocket):
    while True:
        await asyncio.sleep(0.5)
        username = "none"
        content = "none"
        message_json = ""
        try:
            message_json = await asyncio.wait_for(websocket.recv(), recv_timeout_threshold)
        except TimeoutError:
            logger.debug("message handler timed out")
            continue
        except websockets.exceptions.WebSocketException:
            logger.info("connection closed")
        if message_json == "":
            continue
        message: dict = json.loads(message_json)
        logger.debug(f"received message is {message}")
        try:
            username = message['username']
            content = message['content']
        except KeyError:
            logger.error("reading username or content failed")
            continue
        await refresh_session(username)
        print(username, "sends", content)


async def refresh_session(username, lock_acquired_above: bool = False):
    async with data_lock:
        logger.debug("data lock acquired by refresh_session")
        try:
            sessions[username]['lastseen'] = datetime.datetime.now()
        except KeyError:
            logger.info("user session already terminated or does not exist")
            await create_session(username,lock_acquired_above=True)
        logger.debug("data lock released by create session")


async def terminate_session(user, lock_acquired_above: bool = False):
    if not lock_acquired_above:
        try:
            await asyncio.wait_for(data_lock.acquire(),lock_timeout_threshold)
        except TimeoutError:
            logger.info("could not terminate session - lock timed out")
            return
    logger.debug("data lock acquired by terminate session")
    try:
        sessions.pop(user)
        logger.info(f"terminated {user}")
    except KeyError:
        logger.info("user session already terminated or does not exist")
    if not lock_acquired_above:
        data_lock.release()
        logger.debug("data lock released by terminate session")


async def main():
    while True:
        websock = websockets.serve(message_handler, "127.0.0.1", 8001)  # ,ssl=ssl_)
        session_handler_task = asyncio.create_task(session_handler())
        session_handler_task.add_done_callback(_handle_task_result)
        async with websock:
            await asyncio.Future()


def _handle_task_result(task: asyncio.Task):
    # noinspection PyBroadException
    try:
        task.result()
    except asyncio.CancelledError:
        pass
    except Exception:
        logging.exception("Exception raised by %r", task)


if __name__ == "__main__":
    try:
        asyncio.run(main(), debug=True)
    except KeyboardInterrupt:
        main().close()
        sys.exit()
