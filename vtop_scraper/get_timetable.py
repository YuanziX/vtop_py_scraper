from io import StringIO

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

from vtop_scraper.constants.constants import vtop_process_timetable_url
from vtop_scraper.models.period import Period
from vtop_scraper.utils.payloads import get_timetable_payload


DAYS_MAP = {
    "MON": "Monday",
    "TUE": "Tuesday",
    "WED": "Wednesday",
    "THU": "Thursday",
    "FRI": "Friday",
    "SAT": "Saturday",
    "SUN": "Sunday",
}

VALID_DAYS = {"Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"}


async def _get_timetable_page(
    sess: aiohttp.ClientSession, username: str, semID: str, csrf: str
) -> str:
    async with sess.post(
        vtop_process_timetable_url, data=get_timetable_payload(username, semID, csrf)
    ) as req:
        return await req.text()


def _get_course_code_name_dict(soup: BeautifulSoup) -> dict:
    course_data = soup.find("div", attrs={"id": "studentDetailsList"}).find_all(
        "td",
        attrs={
            "style": "padding: 3px; font-size: 12px; border-color: #b2b2b2;vertical-align: middle;"
        },
    )
    return {
        data.text.split("-")[0].strip(): data.text.split("-")[1].split("\n")[0].strip()
        for data in course_data
    }


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
    timetable = {day: [] for day in VALID_DAYS}
    soup = BeautifulSoup(timetable_page, "lxml")
    course_code_dict = _get_course_code_name_dict(soup)
    dataframes = pd.read_html(StringIO(timetable_page))
    course_details, timetable_df = dataframes[0], dataframes[1]

    for row in timetable_df.itertuples(index=False):
        if len(row) < 2 or row[1].lower() not in {"theory", "lab"}:
            continue
        day = DAYS_MAP.get(row[0], "Sunday")
        is_theory = row[1].lower() == "theory"
        if day not in timetable:
            continue
        for col_idx, cell in enumerate(row[2:], start=2):
            cell_str = str(cell).strip()
            if len(cell_str) > 3 and cell_str.count("-") >= 3:
                code, location = _parse_course_vals(cell_str)
                class_id = course_details.loc[
                    course_details["Slot - Venue"].str.contains(
                        cell_str.split("-")[0], na=False
                    ),
                    "Class Nbr",
                ].iloc[0]
                start_time = timetable_df.iloc[0, col_idx]
                period = Period(
                    class_id=class_id,
                    slot=course_details.loc[
                        course_details["Class Nbr"] == class_id, "Slot - Venue"
                    ]
                    .iloc[0]
                    .split(" - ")[0],
                    courseName=course_code_dict[code],
                    code=code,
                    location=location,
                    startTime=start_time,
                    endTime=_get_end_time(start_time, is_theory),
                )
                if period not in timetable[day]:
                    timetable[day].append(period)
    return timetable


async def get_timetable_data(
    sess: aiohttp.ClientSession, username: str, semID: str, csrf: str
):
    timetable = _parse_timetable(await _get_timetable_page(sess, username, semID, csrf))
    for key in timetable:
        timetable[key].sort()
    return {
        key: [period.to_dict() for period in period_list]
        for key, period_list in timetable.items()
    }
