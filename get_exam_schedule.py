import re
import aiohttp
import pandas as pd
from math import isnan

from utils.payloads import get_examSchedule_payload
from constants.constants import vtop_examSchedule_url, current_sem_IDs


async def _get_examSchedule_page(sess: aiohttp.ClientSession, uname: str, semID: str) -> str:
    async with sess.post(vtop_examSchedule_url, data=get_examSchedule_payload(uname, semID)) as req:
        return await req.text()

def _return_dash_if_nan(value):
    if isnan(value):
        return '-'
    else:
        return value


async def _parse_examSchedule(examSchedule_page: str):    
    examSchedule_table = pd.read_html(examSchedule_page)[0]
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
                'date': _return_dash_if_nan(row[6]),
                'session': _return_dash_if_nan(row[7]),
                'reportingTime': _return_dash_if_nan(row[8]),
                'duration': _return_dash_if_nan(row[9]),
                'venue': row[10],
                'roomNo': row[11],
                'seatLocation': row[12],
                'seatNo': row[13],
            }
    
    return examSchedule_data

async def _get_valid_examSchedule_data(examSchedule_page: str):
    try:
        return await _parse_examSchedule(examSchedule_page), True
    except:
        return {}, False


async def get_examSchedule_data(sess: aiohttp.ClientSession, uname: str) -> dict:
    for semID in current_sem_IDs:
        examSchedule_page = await _get_examSchedule_page(sess, uname, semID)
        examSchedule_data = await _get_valid_examSchedule_data(examSchedule_page)
        if examSchedule_data[1]:
            return examSchedule_data[0]
    else:
        return {}