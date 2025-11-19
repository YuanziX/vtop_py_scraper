import re

import aiohttp
from bs4 import BeautifulSoup

from vtop_scraper.constants.constants import vtop_semID_list_url
from vtop_scraper.utils.payloads import get_attendance_semID_list_payload


async def _get_sem_id(sess: aiohttp.ClientSession, username: str, csrf: str):
    async with sess.post(
        vtop_semID_list_url,
        data=get_attendance_semID_list_payload(username, csrf),
    ) as req:
        return re.search('<option value="(A.*)"', await req.text()).group(1)


async def _get_all_sem_ids(sess: aiohttp.ClientSession, username: str, csrf: str):
    async with sess.post(
        vtop_semID_list_url,
        data=get_attendance_semID_list_payload(username, csrf),
    ) as req:
        # sem as list
        # return re.findall('<option value="(A.*)"', await req.text())

        soup = BeautifulSoup(await req.text(), "lxml")

        sem_ids = {}
        sem_ids_soup = soup.findAll("option")
        for elem in sem_ids_soup:
            id = elem["value"]
            if id != "":
                sem_ids[id] = elem.text.strip()
        return sem_ids
