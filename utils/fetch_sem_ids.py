import os, sys
import json
import asyncio
from aiohttp import ClientSession

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_sem_ids import get_sem_ids
from gen_session import gen_session
from constants.priv_constants import uname, passwd

async def save_sem_ids():
    async with ClientSession() as sess:
        if await gen_session(sess, uname, passwd):
            with open('constants/sem_ids.json', 'w') as f:
                json.dump(await get_sem_ids(sess, uname), f, indent=4)

asyncio.run(save_sem_ids())