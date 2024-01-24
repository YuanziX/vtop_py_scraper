import re
import aiohttp
import pandas as pd
from io import StringIO

from utils.payloads import get_examSchedule_payload, get_goto_page_payload
from constants.constants import vtop_examSchedule_url, vtop_doExamSchedule_url, current_sem_IDs


async def _get_examSchedule_page(sess: aiohttp.ClientSession, uname: str, semID: str, csrf: str) -> str:
    await sess.post(vtop_examSchedule_url, data=get_goto_page_payload(uname, csrf))
    async with sess.post(vtop_doExamSchedule_url, data=get_examSchedule_payload(uname, semID, csrf)) as req:
        if (req.status != 200):
            return "", False
        return await req.text(), True

def _return_dash_if_not_str(value):
    if type(value) is str:
        return value
    else:
        return '-'


async def _parse_examSchedule(examSchedule_page: str):
    examSchedule_table = pd.read_html(StringIO(examSchedule_page))[0]
    examSchedule_data = {}

    current_exam = ''
    for index, row in examSchedule_table.iterrows():
        if index == 0:
            continue
        if re.search('\D', row[0]):
            current_exam = row[0]
            examSchedule_data[current_exam] = {}
        else:
            examSchedule_data[current_exam][row[1]] = {
                'name': row[2],
                'type': row[3],
                'classID': row[4],
                'slot': row[5],
                'date': _return_dash_if_not_str(row[6]),
                'session': _return_dash_if_not_str(row[7]),
                'reportingTime': _return_dash_if_not_str(row[8]),
                'duration': _return_dash_if_not_str(row[9]),
                'venue': row[10].split('-')[0],
                'roomNo': row[10].split('-')[1],
                'seatLocation': row[11],
                'seatNo': row[12],
            }

    return examSchedule_data

async def _get_valid_examSchedule_data(examSchedule_page: str):
    try:
        return await _parse_examSchedule(examSchedule_page), True
    except:
        return {}, False


async def get_examSchedule_data(sess: aiohttp.ClientSession, uname: str, csrf: str) -> dict:
    for semID in current_sem_IDs:
        receivedData = False
        while (receivedData != True):
            examSchedule_page = await _get_examSchedule_page(sess, uname, semID, csrf)
            receivedData = examSchedule_page[1]
        examSchedule_data = await _get_valid_examSchedule_data(examSchedule_page[0])
        if examSchedule_data[1]:
            return examSchedule_data[0]
    else:
        return {}
