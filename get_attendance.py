import re
import aiohttp
import pandas as pd
from io import StringIO

from constants.constants import (
    vtop_process_attendance_url,
    vtop_process_attendance_detail_url,
)
from utils.payloads import (
    get_attendance_payload,
    get_attendance_detail_payload,
)

from get_sem_id import _get_sem_id

async def _get_attendance_page(
    sess: aiohttp.ClientSession, username: str, semID: str, csrf: str
):
    async with sess.post(
        vtop_process_attendance_url, data=get_attendance_payload(username, semID, csrf)
    ) as req:
        return await req.text()


async def _get_attendance_detail_page(
    sess: aiohttp.ClientSession, csrf, semID, username, courseID, courseType
):
    async with sess.post(
        vtop_process_attendance_detail_url,
        data=get_attendance_detail_payload(csrf, semID, username, courseID, courseType),
    ) as req:
        return await req.text()


def _get_class_type(classType: str):
    if classType == "Embedded Theory":
        return "ETH"
    elif classType == "Embedded Lab":
        return "ELA"
    elif classType == "Theory Only":
        return "TH"
    elif classType == "Lab Only":
        return "LO"


def _parse_attendance_detail(attendance_detail_page: str):
    attendance_detail_table = pd.read_html(StringIO(attendance_detail_page))
    if len(attendance_detail_table) < 2:
        return {}
    attendance_detail_table = attendance_detail_table[1]
    attendance_detail = {}

    for index, row in attendance_detail_table.iterrows():
        attendance_detail[str(row["Sl.No."])] = {
            "status": row["Status"],
            "date": row["Date"],
            "time": row["Day / Time"],
        }

    return attendance_detail


async def _parse_attendance(
    attendance_page: str,
    sess: aiohttp.ClientSession,
    username: str,
    csrf: str,
    semID: str,
):
    table_df = pd.read_html(StringIO(attendance_page))[0]

    attendance = []

    for index, row in table_df.iterrows():
        code = row["Course Detail"].split("-")[0].strip()
        slot = row["Class Detail"].split("-")[1].strip()
        if "Total Number Of Credits" in code:
            if "0" in code:
                raise Exception
            continue

        attendance.append(
            {
                "classID": row["Class Detail"].split("-")[0].strip(),
                "name": row["Course Detail"].split("-")[1].strip(),
                "courseType": row["Course Detail"].split("-")[2].strip(),
                "slot": slot,
                "totalClasses": str(row["Total Classes"]),
                "attendedClasses": str(row["Attended Classes"]),
                "attendancePercentage": row["Attendance Percentage"][:-1],
                "attendanceDetail": _parse_attendance_detail(
                    await _get_attendance_detail_page(
                        sess,
                        csrf,
                        semID,
                        username,
                        re.search(f";(\w*_{code}_\d*)&", attendance_page).group(1),
                        _get_class_type(row["Course Detail"].split("-")[2].strip()),
                    )
                ),
            }
        )

    return attendance


async def get_attendance_data(sess: aiohttp.ClientSession, username: str, csrf: str):
    return await _parse_attendance(
        await _get_attendance_page(
            sess, username, await _get_sem_id(sess, username, csrf), csrf
        ),
        sess,
        username,
        csrf,
        await _get_sem_id(sess, username, csrf),
    )
