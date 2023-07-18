import aiohttp
import pandas as pd

from constants import vtop_process_attendance_url, current_semIDs
from payloads import get_attendance_payload


async def _get_attendance_page(sess: aiohttp.ClientSession, username: str, semID: str):
    async with sess.post(vtop_process_attendance_url, data=get_attendance_payload(username, semID)) as req:
        return await req.text()


def _parse_attendance(attendance_page: str):
    table_df = pd.read_html(attendance_page)[0]

    attendance = {}

    for index, row in table_df.iterrows():
        code = row['Course  Code']
        if code == 'Total Number Of Credits: 0':
            raise Exception

        attendance.setdefault(code, {})[row['Course  Type']] = {
            'Name': row['Course  Title'],
            'Slot': row['Slot'],
            'Total Classes': row['Total Classes'],
            'Attended Classes': row['Attended Classes'],
            'Attendance Percentage': row['Attendance Percentage']
        }

    attendance.popitem()
    return attendance


def _get_valid_attendance_data(attendance_page: str):
    try:
        return _parse_attendance(attendance_page), True
    except:
        return {}, False


async def get_attendance_data(sess: aiohttp.ClientSession, username: str):
    for id in current_semIDs:
        attendance = _get_valid_attendance_data(await _get_attendance_page(sess, username, id))
        if attendance[1]:
            return attendance[0]
    else:
        return {'result': 'fail'}
