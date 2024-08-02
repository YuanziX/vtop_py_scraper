import re
import aiohttp
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup

from constants.constants import vtop_process_timetable_url
from models.period import Period
from utils.payloads import get_timetable_payload


async def _get_timetable_page(
    sess: aiohttp.ClientSession, username: str, semID: str, csrf: str
) -> str:
    async with sess.post(
        vtop_process_timetable_url, data=get_timetable_payload(username, semID, csrf)
    ) as req:
        return await req.text()


def _get_course_details(soup: BeautifulSoup) -> dict:
    coursetable = soup.find("div", attrs={"id": "studentDetailsList"})
    course_data = coursetable.find_all(
        "td",
        attrs={
            "style": "padding: 3px; font-size: 12px; border-color: #b2b2b2;vertical-align: middle;"
        },
    )

    class_ids = coursetable.find_all("p", string=re.compile(r"AP\d+"))

    course_data_dict = {}

    for data_cell, class_id in zip(course_data, class_ids):
        data = data_cell.text.split("-")
        # code: [id, name]
        course_data_dict[data[0].strip()] = [
            data[1].split("\n")[0].strip(),
            class_id.text,
        ]

    return course_data_dict


def _parse_course_vals(cell_str: str):
    temp_arr = str(cell_str).strip().split("-")
    course_code = temp_arr[1]
    cls = "-".join(temp_arr[3 : len(temp_arr) - 1])

    return course_code, cls


def _get_end_time(start_time: str, is_theory: bool = True):
    if is_theory:
        return f'{start_time.split(":")[0]}:50'
    else:
        return f'{int(start_time.split(":")[0]) + 1}:40'


def _parse_timetable(timetable_page: str):
    timetable = {
        "Tuesday": [],
        "Wednesday": [],
        "Thursday": [],
        "Friday": [],
        "Saturday": [],
    }

    soup = BeautifulSoup(timetable_page, "lxml")

    course_code_dict = _get_course_details(soup)
    days_map = {
        "MON": "Monday",
        "TUE": "Tuesday",
        "WED": "Wednesday",
        "THU": "Thursday",
        "FRI": "Friday",
        "SAT": "Saturday",
        "SUN": "Sunday",
    }

    dataframes = pd.read_html(StringIO(timetable_page))
    course_details = dataframes[0]
    timetable_df = dataframes[1]

    for row_idx in range(3, timetable_df.shape[0]):
        is_theory = timetable_df.iloc[row_idx, 1].lower() == "theory"
        day = days_map.get(str(timetable_df.iloc[row_idx, 0]), "Sunday")

        for col_idx in range(2, timetable_df.shape[1]):
            cell = timetable_df.iloc[row_idx, col_idx]
            cell_str = str(cell).strip()
            is_cell_empty = (
                cell_str.count("-") < 3
                or len(cell_str) <= 3
                or all([char == "-" for char in cell_str])
            )
            if not is_cell_empty:
                code, location = _parse_course_vals(cell_str)
                class_id = course_code_dict[code][1]

                start_time = timetable_df.iloc[0, col_idx]

                cell = Period(
                    class_id=class_id,
                    slot=course_details[course_details["Class Nbr"] == class_id][
                        "Slot - Venue"
                    ]
                    .iloc[0]
                    .split(" - ")[0],
                    courseName=course_code_dict[code][0],
                    code=code,
                    location=location,
                    startTime=start_time,
                    endTime=_get_end_time(start_time, is_theory),
                )

                if cell not in timetable[day]:
                    timetable[day].append(cell)

    return timetable


async def get_timetable_data(
    sess: aiohttp.ClientSession, username: str, semID: str, csrf: str
):
    timetable = _parse_timetable(await _get_timetable_page(sess, username, semID, csrf))
    for key, periods in timetable.items():
        timetable[key] = sorted(periods)

    timetable_dict = {
        key: [period.to_dict() for period in period_list]
        for key, period_list in timetable.items()
    }

    return timetable_dict
