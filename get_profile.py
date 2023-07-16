import aiohttp
from bs4 import BeautifulSoup
import re

from constants import vtop_profile_url
from payloads import get_profile_payload


def _clean_up_text(s: str) -> str:
    s = re.sub('\W+', r' ', s)
    return s if not re.match('[A-Z ].', s) else s.title()


async def _get_profile_page(sess: aiohttp.ClientSession, uname: str) -> str:
    async with sess.post(vtop_profile_url, data=get_profile_payload(uname)) as req:
        return await req.text()


async def get_profile_data(sess: aiohttp.ClientSession, uname: str) -> dict:
    profile_page = await _get_profile_page(sess, uname)
    data = {}
    desired_fields = ['Application Number', 'Student Name', 'Date Of Birth',
                      'Gender', 'VIT Register Number', 'Program', 'Branch', 'School', 'Mobile Number']

    soup = BeautifulSoup(profile_page, 'lxml')
    rows = soup.find_all('tr')

    for row in rows:
        field_name = _clean_up_text(row.contents[1].string)
        if (field_name in desired_fields):
            data[field_name] = _clean_up_text(row.contents[3].string)
    data['Program'] = '.'.join(data['Program'].split())

    return data
