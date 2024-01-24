import aiohttp
from constants.constants import *
from utils.captcha_solver import solve_base64
import re

async def gen_session(sess: aiohttp.ClientSession, username: str, password: str):
    try:
        async with sess.get("https://vtop.vitap.ac.in/vtop/", headers=user_agent_header):
            async with sess.get("https://vtop.vitap.ac.in/vtop/open/page") as csrf:
                csrf_token = re.search(r'name="_csrf" value="(.*)"', await csrf.text()).group(1)
                await sess.post("https://vtop.vitap.ac.in/vtop/prelogin/setup", data={'_csrf': csrf_token, 'flag': 'VTOP'})
                await sess.get("https://vtop.vitap.ac.in/vtop/init/page")
                async with sess.get("https://vtop.vitap.ac.in/vtop/login") as req:
                    captcha = solve_base64(re.search(r';base64,(.+)"', await req.text()).group(1))
                    print(captcha)
                    async with sess.post("https://vtop.vitap.ac.in/vtop/login", data={'_csrf': csrf_token, 'username': username, 'password': password, 'captchaStr': captcha}) as final:
                        return re.search(r'var csrfValue = "(.*)";', await final.text()).group(1)
    except:
        await gen_session(sess, username, password)

