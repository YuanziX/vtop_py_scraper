import aiohttp
import pandas as pd

from constants.constants import vtop_doMarks_view_url
from utils.payloads import get_doMarks_view_payload


async def _get_doMarks_view_page(sess: aiohttp.ClientSession, username: str, semID: str, csrf: str) -> str:
    async with sess.post(vtop_doMarks_view_url, data=get_doMarks_view_payload(username, semID, csrf)) as req:
        return await req.text()


def _parse_marks(marks_page):
    try:
        tables = pd.read_html(marks_page)
    except ValueError:
        return {}
    
    course_details = tables[0].iloc[1::2, :]
    marks_data = {}

    for i in range(course_details.shape[0]):
        course = course_details.iloc[i]
        marks_data[course[1]] = {
            "courseName": course[3],
            "courseType": course[4],
            "professor": course[6],
            "courseSlot": course[7],
            "marks": {}
        }

        current_course_table = tables[i+1]
        for j in range(1, current_course_table.shape[0]):
            entry = current_course_table.iloc[j]
            marks_data[course[1]]["marks"][entry[1]] = {
                'maxMarks': entry[2], 'maxWeightageMarks': entry[3], 'scoredMarks': entry[5], 'scoredWeightageMarks': entry[6]}

    return marks_data


async def get_marks_data(sess: aiohttp.ClientSession, username: str, semID: str, csrf: str):
    return _parse_marks(await _get_doMarks_view_page(sess, username, semID, csrf))
