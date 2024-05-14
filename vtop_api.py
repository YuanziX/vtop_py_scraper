import re
import aiohttp
from utils.captcha_solver import solve_base64
from constants.constants import *
from utils.payloads import *

# import parsers
from parsers.profile_parser import profile_parser


class VtopAPI:
    """
    VtopAPI class to get data from VIT-AP's VTOP website
    
    Usage:
        Use with context manager:
        async with VtopAPI(username, password) as api:
            # do stuff here

        Use without direct context manager: (here you need to handle the session object yourself)
        async with aiohttp.ClientSession() as sess:
            api = await VtopAPI.create(sess, username, password)
            # do stuff here
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @classmethod
    async def create(self, sess, username, password):
        self = VtopAPI()
        self.username = username
        self.password = password
        self.sess = sess
        await self.login()
        return self

    def loginstatus(self):
        return self.logged_in

    async def __aenter__(self):
        self.sess = aiohttp.ClientSession()
        self.sess.headers.update(user_agent_header)
        await self.login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.sess.close()
        self.sess = None

    async def login(self):
        try:
            async with self.sess.get("https://vtop.vitap.ac.in/vtop/"):
                async with self.sess.get(
                    "https://vtop.vitap.ac.in/vtop/open/page"
                ) as csrf:
                    csrf_token = re.search(
                        r'name="_csrf" value="(.*)"', await csrf.text()
                    ).group(1)
                    await self.sess.post(
                        "https://vtop.vitap.ac.in/vtop/prelogin/setup",
                        data={"_csrf": csrf_token, "flag": "VTOP"},
                    )
                    await self.sess.get("https://vtop.vitap.ac.in/vtop/init/page")
                    async with self.sess.get(
                        "https://vtop.vitap.ac.in/vtop/login"
                    ) as req:
                        captcha = solve_base64(
                            re.search(r';base64,(.+)"', await req.text()).group(1)
                        )
                        async with self.sess.post(
                            "https://vtop.vitap.ac.in/vtop/login",
                            data={
                                "_csrf": csrf_token,
                                "username": self.username,
                                "password": self.password,
                                "captchaStr": captcha,
                            },
                        ) as final:
                            csrf = re.search(
                                r'var csrfValue = "(.*)";', await final.text()
                            ).group(1)
                            if "Invalid" in await final.text():
                                return
                            elif len(csrf) == 36:
                                self.logged_in = True
                                self.csrf = csrf
                                return
                            else:
                                return await self.login()

        except Exception:
            return await self.login()

    async def get_student_details(self):
        async with self.sess.post(
            vtop_profile_url, data=get_profile_payload(self.username, self.csrf)
        ) as req:
            return profile_parser(await req.text(), self.username)

