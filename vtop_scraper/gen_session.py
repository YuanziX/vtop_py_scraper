import re

import aiohttp

from vtop_scraper.constants.constants import user_agent_header
from vtop_scraper.utils.captcha_solver import solve_base64
from vtop_scraper.utils.payloads import get_login_payload


async def gen_session(sess: aiohttp.ClientSession, username: str, password: str):
    try:
        async with sess.get(
            "https://vtop.vitap.ac.in/vtop/", headers=user_agent_header
        ):
            async with sess.get("https://vtop.vitap.ac.in/vtop/open/page") as csrf:
                csrf_token = re.search(
                    r'name="_csrf" value="(.*)"', await csrf.text()
                ).group(1)
                await sess.post(
                    "https://vtop.vitap.ac.in/vtop/prelogin/setup",
                    data={"_csrf": csrf_token, "flag": "VTOP"},
                )
                await sess.get("https://vtop.vitap.ac.in/vtop/init/page")
                async with sess.get("https://vtop.vitap.ac.in/vtop/login") as req:
                    captcha = solve_base64(
                        re.search(r';base64,(.+)"', await req.text()).group(1)
                    )
                    async with sess.post(
                        "https://vtop.vitap.ac.in/vtop/login",
                        data=get_login_payload(
                            csrf_token,
                            username,
                            password,
                            captcha,
                        ),
                    ) as final:
                        csrf = re.search(
                            r'var csrfValue = "(.*)";', await final.text()
                        ).group(1)
                        if "Invalid" in await final.text():
                            return 0
                        elif len(csrf) == 36:
                            return csrf
                        else:
                            return await gen_session(sess, username, password)

    except Exception:
        return await gen_session(sess, username, password)
