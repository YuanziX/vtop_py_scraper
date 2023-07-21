from typing import Union
from payloads import get_login_payload
import aiohttp
from constants import *
import json
import base64
import numpy as np
import os
import io
import re
from PIL import Image


CAPTCHA_DIM = (180, 45)
CHARACTER_DIM = (30, 32)

bitmaps_path = os.path.join(os.path.dirname(__file__), 'bitmaps.json')
BITMAPS = json.load(open(bitmaps_path))
BITMAPS = {k: np.array(v) for k, v in BITMAPS.items()}


def _img_match_percentage(img_char_matrix: np.ndarray, char_matrix: np.ndarray) -> float:
    match_count = 1
    mismatch_count = 1

    match_count = np.sum(img_char_matrix == char_matrix)
    w, h = img_char_matrix.shape
    mismatch_count = w*h - match_count

    percent_match = match_count / mismatch_count
    return percent_match


def _identify_chars(img: np.ndarray) -> str:
    img_width = CAPTCHA_DIM[0]
    char_width = CHARACTER_DIM[0]

    up_thresh, low_thresh = 12, 44

    captcha = ""

    for i in range(0, img_width, char_width):
        img_char_matrix = img[up_thresh:low_thresh, i: i+char_width]
        matches = {}
        global BITMAPS
        for char, char_matrix in BITMAPS.items():
            perc = _img_match_percentage(img_char_matrix, char_matrix)
            matches.update({perc: char.upper()})
        try:
            captcha += matches[max(matches.keys())]
        except ValueError:
            captcha += "0"
    return captcha


def _solve_captcha(src: str) -> Union[str, None]:
    im = base64.b64decode(src)
    img = Image.open(io.BytesIO(im)).convert("L")
    img = np.array(img)
    if img is None:
        print("Captcha not found, returning .... None")
        return None
    captcha = None
    try:
        captcha = _identify_chars(img)
    except Exception as e:
        print(e)
    return captcha


async def gen_session(sess: aiohttp.ClientSession, uname: str, passwd: str) -> bool:
    await sess.get(vtop_base_url, headers=user_agent_header)
    async with sess.post(vtop_login_url) as req:
        captcha = _solve_captcha(re.search(r';base64, (.+)" />', await req.text()).group(1))
        async with sess.post(vtop_doLogin_url, data=get_login_payload(uname, passwd, captcha)) as resp:
            text = await resp.text()
            if ('Invalid' in text or 'exception' in text):
                return False
            return True
