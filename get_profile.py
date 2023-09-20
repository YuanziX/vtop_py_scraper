import aiohttp
import pandas as pd
import string
import re

from constants.constants import vtop_profile_url
from utils.payloads import get_profile_payload


def _get_value_from_column1(text: str, df: pd.DataFrame):
    row = df[df[0] == text]
    if not row.empty:
        return row.iloc[0, 1]
    else:
        return None


async def _get_profile_page(sess: aiohttp.ClientSession, uname: str) -> str:
    async with sess.post(vtop_profile_url, data=get_profile_payload(uname)) as req:
        return await req.text()


async def get_profile_data(sess: aiohttp.ClientSession, uname: str) -> dict:
    profile_page = await _get_profile_page(sess, uname)
    data = {}
    tables = pd.read_html(profile_page)
    desired_fields_table_0 = {'Student Name': 'Student  Name',
                              'VIT Registration Number': 'VIT  Register Number',
                              'Application Number': 'Application  Number',
                              'Program': 'Program',
                              'Branch': 'Branch',
                              'School': 'School'
                              }

    desired_fields_table_4 = {'Mentor Name': 'Faculty Name',
                              'Mentor Cabin': 'Cabin',
                              'Mentor Email': 'Faculty Email',
                              'Mentor intercom': 'Faculty  intercom',
                              'Mentor Mobile Number': 'Faculty  Mobile Number'
                              }

    data['image'] = re.findall(r'src="data:null;base64,(.*)"', profile_page)[0]
    for key, field in desired_fields_table_0.items():
        data[key] = string.capwords(_get_value_from_column1(field, tables[0]))
    for key, field in desired_fields_table_4.items():
        data[key] = _get_value_from_column1(field, tables[3])

    return data
