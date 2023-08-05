import aiohttp
import pandas as pd

from constants.constants import vtop_gradeHistory_url
from utils.payloads import get_gradeHistory_payload

async def _get_grades_page(sess: aiohttp.ClientSession, uname: str) -> str:
    async with sess.post(vtop_gradeHistory_url, data=get_gradeHistory_payload(uname)) as req:
        return await req.text()

async def get_grades_data(sess: aiohttp.ClientSession, uname: str):
    grades_page = await _get_grades_page(sess, uname)
    tables = pd.read_html(grades_page)
    
    grade_data = {}

    grade_data['creditsEarned'] = tables[-1].iloc[1, 1]
    grade_data['cgpa'] = tables[-1].iloc[1, 2]

    grade_data['numOfEachGrade'] = {}
    grade_data['subjects'] = {}
    grade_data['numOfEachGrade']['S'] = tables[-1].iloc[1, 3]

    for i in range (0, 6):
        grade_data['numOfEachGrade'][chr(65 + i)] = tables[-1].iloc[1, 4+i]
    
    for i in range (2, len(tables[1])):
        grade_data['subjects'][tables[1].iloc[i, 1]] = {
            'name': tables[1].iloc[i, 2],
            'type': tables[1].iloc[i, 3],
            'credits': tables[1].iloc[i, 4],
            'grade': tables[1].iloc[i, 5],
        }
    
    return grade_data