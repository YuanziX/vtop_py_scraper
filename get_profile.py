import re
import string
import aiohttp
import pandas as pd
from io import StringIO

from constants.constants import vtop_profile_url
from utils.payloads import get_profile_payload


def _get_value_from_column1(text: str, df: pd.DataFrame):
    row = df[df[0] == text]
    if not row.empty:
        return row.iloc[0, 1]
    else:
        return None


async def _get_profile_page(sess: aiohttp.ClientSession, username: str, csrf: str) -> str:
    async with sess.post(vtop_profile_url, data=get_profile_payload(username, csrf)) as req:
        return await req.text()


async def get_profile_data(sess: aiohttp.ClientSession, username: str, csrf: str) -> dict:
    profile_page = await _get_profile_page(sess, username, csrf)
    data = {}
    tables = pd.read_html(StringIO(profile_page))

    desired_fields_table_0 = {'Student Name': 'STUDENT NAME',
                              'Application Number': 'APPLICATION NUMBER',
                              }


    desired_fields_table_3 = {'Mentor Name': 'FACULTY NAME',
                              'Mentor Cabin': 'CABIN',
                              'Mentor Email': 'FACULTY EMAIL',
                              'Mentor intercom': 'FACULTY INTERCOM',
                              'Mentor Mobile Number': 'FACULTY MOBILE NUMBER'
                              }

    data['image'] = re.findall(r'src="data:null;base64,(.*)"', profile_page)[0]
    data['VIT Registration Number'] = username
    for key, field in desired_fields_table_0.items():
        data[key] = string.capwords(_get_value_from_column1(field, tables[0]))
    for key, field in desired_fields_table_3.items():
        data[key] = _get_value_from_column1(field, tables[3])

    return data
