import re
from io import StringIO

import aiohttp
import pandas as pd

from vtop_scraper.constants.constants import vtop_doExamSchedule_url
from vtop_scraper.utils.payloads import get_examSchedule_payload


async def _get_examSchedule_page(
    sess: aiohttp.ClientSession, username: str, semID: str, csrf: str
) -> str:
    async with sess.post(
        vtop_doExamSchedule_url, data=get_examSchedule_payload(username, semID, csrf)
    ) as req:
        return await req.text()


def _return_dash_if_not_str(value):
    if isinstance(value, str):
        return value
    else:
        return "-"


async def _parse_examSchedule(examSchedule_page: str):
    try:
        examSchedule_table = pd.read_html(StringIO(examSchedule_page))[0]
    except ValueError:
        return {}
    examSchedule_data = {}

    current_exam = ""
    for index, row in examSchedule_table.iterrows():
        if index == 0:
            continue
        if re.search(r"\D", row[0]):
            current_exam = row[0]
            examSchedule_data[current_exam] = {}
        else:
            examSchedule_data[current_exam][row[1]] = {
                "name": row[2],
                "type": row[3],
                "classID": row[4],
                "slot": row[5],
                "date": _return_dash_if_not_str(row[6]),
                "session": _return_dash_if_not_str(row[7]),
                "reportingTime": _return_dash_if_not_str(row[8]),
                "duration": _return_dash_if_not_str(row[9]),
                "venue": row[10].split("-")[0],
                "roomNo": row[10].split("-")[1],
                "seatLocation": row[11],
                "seatNo": row[12],
            }

    examSchedule_data.pop("S.No.")
    return examSchedule_data


async def get_examSchedule_data(
    sess: aiohttp.ClientSession, username: str, semID: str, csrf: str
) -> dict:
    examSchedule_page = await _get_examSchedule_page(sess, username, semID, csrf)
    examSchedule_data = await _parse_examSchedule(examSchedule_page)
    return examSchedule_data
