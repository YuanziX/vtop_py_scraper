import aiohttp
import pandas as pd
import string
import re

from constants.constants import vtop_profile_url
from utils.payloads import get_profile_payload


def _clean_up_text(s: str) -> str:
    return re.sub('\W+', r' ', s)


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
    desired_fields = ['Student  Name',
                      'Application  Number', 'Program', 'Branch', 'School']

    profile_df = pd.read_html(profile_page)[0]

    data['image'] = re.findall(r'src="data:null;base64,(.*)"', profile_page)[0]
    for field in desired_fields:
        data[_clean_up_text(field)] = string.capwords(
            _get_value_from_column1(field, profile_df))
    data['VIT Registration Number'] = _get_value_from_column1(
        'VIT  Register Number', profile_df)

    return data
