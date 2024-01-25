import datetime


def get_current_time() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%c GMT")


def get_login_payload(username: str, password: str, captcha: str) -> dict:
    return {"uname": username, "passwd": password, "captchaCheck": captcha}


def get_profile_payload(username: str, csrf: str) -> dict:
    return {
        "verifyMenu": "true",
        "authorizedID": username,
        "_csrf": csrf,
        "nocache": "@(new Date().getTime()",
    }


def get_timetable_payload(username: str, semID: str, csrf: str) -> dict:
    return {
        "_csrf": csrf,
        "semesterSubId": semID,
        "authorizedID": username,
        "x": get_current_time(),
    }


def get_attendance_payload(username: str, semID: str, csrf: str) -> dict:
    return get_timetable_payload(username, semID, csrf)


def get_attendance_semID_list_payload(username: str, csrf: str) -> dict:
    return get_profile_payload(username, csrf)


def get_attendance_detail_payload(
    csrf: str, semID: str, username: str, courseID: str, courseType: str
) -> dict:
    return {
        "_csrf": csrf,
        "semesterSubId": semID,
        "registerNumber": username,
        "courseId": courseID,
        "courseType": courseType,
        "authorizedID": username,
        "x": get_current_time(),
    }


def get_marks_view_sem_ids_payload(username: str) -> dict:
    return get_profile_payload(username)


def get_doMarks_view_payload(username: str, semID: str, csrf: str) -> dict:
    return {"authorizedID": username, "semesterSubId": semID, "_csrf": csrf}


def get_gradeHistory_payload(username: str, csrf: str) -> dict:
    return get_profile_payload(username, csrf)


def get_examSchedule_payload(username: str, semID: str, csrf: str) -> dict:
    return get_doMarks_view_payload(username, semID, csrf)


def get_weekend_outing_payload(username: str) -> dict:
    return get_profile_payload(username)


def get_goto_page_payload(username: str, csrf: str) -> dict:
    return get_profile_payload(username, csrf)
