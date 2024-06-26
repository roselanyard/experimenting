import asyncio
import threading

net_lock = asyncio.Lock()
net_bytestring = ""