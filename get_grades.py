import aiohttp
import pandas as pd
from io import StringIO
from constants.constants import vtop_gradeHistory_url
from utils.payloads import get_gradeHistory_payload


async def _get_grades_page(
    sess: aiohttp.ClientSession, username: str, csrf: str
) -> str:
    async with sess.post(
        vtop_gradeHistory_url, data=get_gradeHistory_payload(username, csrf)
    ) as req:
        return await req.text()


async def get_grades_data(sess: aiohttp.ClientSession, username: str, csrf: str):
    grades_page = await _get_grades_page(sess, username, csrf)

    try:
        tables = pd.read_html(StringIO(grades_page))
        data_table = tables[1]
        data_summary_table = tables[-1]
    except Exception:
        return {}

    grade_data = {}

    grade_data["creditsEarned"] = data_summary_table.iloc[0, 1]
    grade_data["cgpa"] = data_summary_table.iloc[0, 2]

    grade_data["numOfEachGrade"] = {}
    grade_data["subjects"] = {}
    grade_data["numOfEachGrade"]["S"] = str(data_summary_table.iloc[0, 3])
    for i in range(0, 6):
        grade_data["numOfEachGrade"][chr(65 + i)] = str(
            data_summary_table.iloc[0, 4 + i]
        )

    for i in range(2, len(data_table)):
        grade_data["subjects"][data_table.iloc[i, 1]] = {
            "name": data_table.iloc[i, 2],
            "type": data_table.iloc[i, 3],
            "credits": data_table.iloc[i, 4],
            "grade": data_table.iloc[i, 5],
        }

    return grade_data
