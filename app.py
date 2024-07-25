from flask import Flask, request, abort
from aiohttp import ClientSession

from gen_session import gen_session
from get_profile import get_profile_data
from get_attendance import get_attendance_data
from get_timetable import get_timetable_data
from get_sem_id import _get_all_sem_ids, _get_sem_id
from get_marks import get_marks_data
from get_grades import get_grades_data
from get_exam_schedule import get_examSchedule_data

app = Flask(__name__)


def basic_creds_check(username: str, password: str):
    if username == "" or username is None or password == "" or password is None:
        abort(401)


@app.route("/")
def root():
    return "VTOP-AP API"


async def handle_request(data_func, num_parameters):
    username = request.form.get("username")
    password = request.form.get("password")

    basic_creds_check(username, password)

    async with ClientSession() as sess:
        csrf = await gen_session(sess, username, password)
        if csrf:
            if num_parameters == 3:
                return await data_func(sess, username, csrf)
            else:
                return await data_func(
                    sess, username, await _get_sem_id(sess, username, csrf), csrf
                )
        else:
            abort(401)


@app.route("/api/attendance", methods=["POST"])
@app.route("/api/timetable", methods=["POST"])
@app.route("/api/examSchedule", methods=["POST"])
async def handle_4param_data_functions():
    data_func = {
        "/api/attendance": get_attendance_data,
        "/api/timetable": get_timetable_data,
        "/api/examSchedule": get_examSchedule_data,
    }
    return await handle_request(data_func[request.path], 4)


@app.route("/api/grades", methods=["POST"])
@app.route("/api/profile", methods=["POST"])
@app.route("/api/semIDs", methods=["POST"])
async def handle_3param_data_functinos():
    data_func = {
        "/api/grades": get_grades_data,
        "/api/profile": get_profile_data,
        "/api/semIDs": _get_all_sem_ids,
    }
    return await handle_request(data_func[request.path], 3)


@app.route("/api/verify", methods=["POST"])
async def verify_creds():
    username = request.form.get("username")
    password = request.form.get("password")

    basic_creds_check(username, password)

    async with ClientSession() as sess:
        if await gen_session(sess, username, password) != 0:
            return
        else:
            abort(401)


@app.route("/api/all", methods=["POST"])
async def all_data():
    username = request.form.get("username")
    password = request.form.get("password")

    basic_creds_check(username, password)

    async with ClientSession() as sess:
        csrf = await gen_session(sess, username, password)
        semID = await _get_sem_id(sess, username, csrf)
        data = {
            "profile": await get_profile_data(sess, username, csrf),
            "attendance": await get_attendance_data(sess, username, semID, csrf),
            "semIDs": await _get_all_sem_ids(sess, username, csrf),
            "grades": await get_grades_data(sess, username, csrf),
            "examSchedule": await get_examSchedule_data(sess, username, semID, csrf),
            "timetable": await get_timetable_data(sess, username, semID, csrf),
        }

        return data


@app.route("/api/marks", methods=["POST"])
async def marks():
    username = request.form.get("username")
    password = request.form.get("password")
    semID = request.form.get("semID")

    basic_creds_check(username, password)

    async with ClientSession() as sess:
        return await get_marks_data(
            sess, username, semID, await gen_session(sess, username, password)
        )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
