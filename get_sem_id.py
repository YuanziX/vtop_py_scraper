import re
import aiohttp
from constants.constants import vtop_semID_list_url
from utils.payloads import get_attendance_semID_list_payload

async def _get_sem_id(sess: aiohttp.ClientSession, username: str, csrf: str):
    async with sess.post(
        vtop_semID_list_url,
        data=get_attendance_semID_list_payload(username, csrf),
    ) as req:
        return re.search('<option value="(A.*)"', await req.text()).group(1)

