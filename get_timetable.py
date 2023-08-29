import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

from constants.constants import vtop_process_timetable_url, current_sem_IDs
from models.period import Period
from utils.payloads import get_timetable_payload


async def _get_timetable_page(sess: aiohttp.ClientSession, username: str, semID: str) -> str:
    async with sess.post(vtop_process_timetable_url, data=get_timetable_payload(username, semID)) as req:
        return await req.text()


def _get_course_code_with_name(soup: BeautifulSoup) -> dict:
    coursetable = soup.find('div', attrs={'id': 'studentDetailsList'})
    course_data = coursetable.find_all('td', attrs={
                                       'style': 'padding: 3px; font-size: 12px; border-color: #3c8dbc;vertical-align: middle;text-align: left;'})

    course_data_dict = {}

    for data_cell in course_data:
        data = data_cell.text.split('-')
        course_data_dict[data[0].strip()] = data[1].strip()

    return course_data_dict


def _parse_theory_vals(s):
    temp_arr = str(s).strip().split("-")
    slot = temp_arr[0]
    course_code = temp_arr[1]
    cls = f"{temp_arr[4]}-{temp_arr[3]}"

    return slot, course_code, cls


def _get_lab_slot(slot: str) -> str:
    num = int(slot.replace('L', ''))

    return f'L{num}+{num + 1}' if num % 2 else f'L{num - 1}+{num}'


def _parse_lab_vals(s):
    temp_arr = str(s).strip().split("-")
    slot = _get_lab_slot(temp_arr[0])
    course_code = temp_arr[1]
    cls = "-".join(temp_arr[3:])

    return slot, course_code, cls


def _get_theory_end_time(start_time: str):
    return f'{start_time.split(":")[0]}:50'


def _get_lab_end_time(start_time: str):
    return f'{int(start_time.split(":")[0]) + 1}:40'


def _parse_timetable(timetable_page: str):
    timetable = {
        'Tuesday': [],
        'Wednesday': [],
        'Thursday': [],
        'Friday': [],
        'Saturday': [],
    }

    soup = BeautifulSoup(timetable_page, 'lxml')

    course_code_dict = _get_course_code_with_name(soup)
    days_map = {"MON": "Monday", "TUE": 'Tuesday', "WED": 'Wednesday',
                "THU": 'Thursday', "FRI": 'Friday', "SAT": "Saturday", "SUN": "Sunday"}

    timetable_df = pd.read_html(timetable_page)[1]

    for row_idx in range(3, timetable_df.shape[0]):
        is_theory = (timetable_df.iloc[row_idx, 1] == 'Theory')
        day = days_map.get(str(timetable_df.iloc[row_idx, 0]), "Sunday")

        for col_idx in range(2, timetable_df.shape[1]):
            cell = timetable_df.iloc[row_idx, col_idx]
            cell_str = str(cell).strip()
            is_cell_empty = cell_str.count(
                '-') < 3 or len(cell_str) <= 3 or all([char == '-' for char in cell_str])
            if not is_cell_empty:
                if is_theory:
                    slot, code, location = _parse_theory_vals(cell_str)
                    start_time = timetable_df.iloc[0, col_idx]

                    cell = Period(
                        slot=slot, courseName=course_code_dict[code], code=code, location=location, startTime=start_time, endTime=_get_theory_end_time(start_time))

                else:
                    slot, code, location = _parse_lab_vals(cell_str)
                    start_time = timetable_df.iloc[0, col_idx]

                    cell = Period(slot=slot, courseName=course_code_dict[code], code=code,
                                  location=location, startTime=start_time, endTime=_get_lab_end_time(start_time))

                if cell not in timetable[day]:
                    timetable[day].append(cell)

    return timetable


def _get_valid_timetable_data(timetable_page: str):
    try:
        return _parse_timetable(timetable_page), True
    except:
        return {}, False


async def get_timetable_data(sess: aiohttp.ClientSession, username: str):
    for id in current_sem_IDs:
        timetable = _get_valid_timetable_data(await _get_timetable_page(sess, username, id))
        if timetable[1]:
            temp_tt = timetable[0]
            for key, periods in temp_tt.items():
                temp_tt[key] = sorted(periods)

            timetable_dict = {
                key: [period.to_dict() for period in period_list]
                for key, period_list in temp_tt.items()
            }

            return timetable_dict
    else:
        return {}
