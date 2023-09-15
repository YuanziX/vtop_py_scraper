import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

from constants.constants import vtop_process_attendance_url, vtop_process_attendance_detail_url, current_sem_IDs
from utils.payloads import get_attendance_payload, get_attendance_detail_payload


async def _get_attendance_page(sess: aiohttp.ClientSession, username: str, semID: str):
    async with sess.post(vtop_process_attendance_url, data=get_attendance_payload(username, semID)) as req:
        return await req.text()


async def _get_attendance_detail_page(sess: aiohttp.ClientSession, classID: str, slotName: str, username: str):
    async with sess.post(vtop_process_attendance_detail_url, data=get_attendance_detail_payload(username, classID, slotName.replace("+", " "))) as req:
        return await req.text()


def _parse_attendance_detail(attendance_detail_page: str):
    attendance_detail_table = pd.read_html(attendance_detail_page)[0]
    attendance_detail = {}

    for index, row in attendance_detail_table.iterrows():
        attendance_detail[row['Sl.No']] = {
            'status': row['Attendance Status'],
            'date': row['Attendance Date'],
            'time': row['Day And Timing']
        }

    return attendance_detail


def get_sub_ids(attendance_page: str):

    soup = BeautifulSoup(attendance_page, 'html.parser')
    slot_subid_dict = dict()
    for link in soup.find_all('a', {'class': 'btn-link'}):
        on_click_str = link.get('onclick')
        sub_id = on_click_str.split("'")[1]
        slot = on_click_str.split("'")[3]
        slot_subid_dict[slot] = sub_id

    return slot_subid_dict


async def _parse_attendance(attendance_page: str, sess: aiohttp.ClientSession, username: str):
    table_df = pd.read_html(attendance_page)[0]

    attendance = []
    sub_ids = get_sub_ids(attendance_page)

    for index, row in table_df.iterrows():
        code = row['Course  Code']
        if 'Total Number Of Credits' in code:
            if '0' in code:
                raise Exception
            continue

        classID = sub_ids.get(row['Slot'], '')
        attendance.append({
            'classID': classID,
            'name': row['Course  Title'],
            'courseType': row['Course  Type'],
            'slot': row['Slot'],
            'totalClasses': row['Total Classes'],
            'attendedClasses': row['Attended Classes'],
            'attendancePercentage': row['Attendance Percentage'],
            'attendanceDetail': _parse_attendance_detail(await _get_attendance_detail_page(sess, classID, row['Slot'], username)),
        })

    return attendance


async def _get_valid_attendance_data(attendance_page: str, sess: aiohttp.ClientSession, username: str):
    try:
        return await _parse_attendance(attendance_page, sess, username), True
    except Exception as e:
        print(e)
        return {}, False


async def get_attendance_data(sess: aiohttp.ClientSession, username: str):
    for id in current_sem_IDs:
        attendance = await _get_valid_attendance_data(await _get_attendance_page(sess, username, id), sess, username)
        if attendance[1]:
            return attendance[0]
    else:
        return {}
