import aiohttp
from bs4 import BeautifulSoup

from constants.constants import vtop_marks_view_url
from utils.payloads import get_marks_view_sem_ids_payload


async def _get_marks_view_page(sess: aiohttp.ClientSession, uname: str) -> str:
    async with sess.post(vtop_marks_view_url, data=get_marks_view_sem_ids_payload(uname), verify_ssl=False) as req:
        return await req.text()


async def get_sem_ids(sess: aiohttp.ClientSession, uname: str):
    soup = BeautifulSoup(await _get_marks_view_page(sess, uname), 'lxml')

    sem_ids = {}
    sem_ids_soup = soup.findAll('option')
    for elem in sem_ids_soup:
        id = elem['value']
        if id != '':
            sem_ids[id] = elem.text.strip()
    return sem_ids
