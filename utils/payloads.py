import datetime


def get_current_time() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime('%c GMT')


def get_login_payload(username: str, password: str, captcha: str) -> dict:
    return {'uname': username, 'passwd': password, 'captchaCheck': captcha}


def get_profile_payload(username: str) -> dict:
    return {'verifyMenu': 'true', 'winImage': 'undefined', 'authorizedID': username,
            'nocache': '@(new Date().getTime()'}


def get_timetable_payload(username: str, semID: str) -> dict:
    return {'semesterSubId': semID, 'authorizedID': username, 'x': get_current_time()}


def get_attendance_payload(username: str, semID: str) -> dict:
    return {'semesterSubId': semID, 'authorizedID': username, 'x': get_current_time()}


def get_attendance_detail_payload(username: str, classID: str, slotName: str) -> dict:
    return {'classId': classID, 'slotName': slotName, 'authorizedID': username, 'x': get_current_time()}


def get_marks_view_sem_ids_payload(username: str) -> dict:
    return get_profile_payload(username)


def get_doMarks_view_payload(username: str, semID: str) -> dict:
    return {'authorizedID': username, 'semesterSubId': semID}


def get_gradeHistory_payload(username: str) -> dict:
    return get_profile_payload(username)


def get_examSchedule_payload(username: str, semID: str) -> dict:
    return get_doMarks_view_payload(username, semID)


def get_weekend_outing_payload(username: str) -> dict:
    return get_profile_payload(username)
