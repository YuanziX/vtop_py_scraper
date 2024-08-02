import uvicorn
from aiohttp import ClientSession
from gen_session import gen_session
from get_marks import get_marks_data
from get_grades import get_grades_data
from get_profile import get_profile_data
from fastapi.responses import JSONResponse
from get_timetable import get_timetable_data
from get_attendance import get_attendance_data
from get_exam_schedule import get_examSchedule_data
from get_sem_id import _get_all_sem_ids, _get_sem_id
from fastapi import FastAPI, Request, HTTPException, status, Form

app = FastAPI()


def basic_creds_check(username: str | None, password: str | None):
    if not username or not password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@app.get("/")
async def root():
    return {"message": "VTOP-AP API"}


async def handle_request(data_func, num_parameters, username, password):
    basic_creds_check(username, password)
    async with ClientSession() as sess:
        session_result = await gen_session(sess, username, password)
        if session_result == 0:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        if num_parameters == 3:
            return await data_func(sess, username, session_result)
        else:
            return await data_func(
                sess,
                username,
                await _get_sem_id(sess, username, session_result),
                session_result,
            )


@app.post("/api/attendance")
@app.post("/api/timetable")
@app.post("/api/examSchedule")
async def handle_4param_data_functions(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    data_func = {
        "/api/attendance": get_attendance_data,
        "/api/timetable": get_timetable_data,
        "/api/examSchedule": get_examSchedule_data,
    }
    return await handle_request(data_func[request.url.path], 4, username, password)


@app.post("/api/grades")
@app.post("/api/profile")
@app.post("/api/semIDs")
async def handle_3param_data_functions(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    data_func = {
        "/api/grades": get_grades_data,
        "/api/profile": get_profile_data,
        "/api/semIDs": _get_all_sem_ids,
    }
    return await handle_request(data_func[request.url.path], 3, username, password)


@app.post("/api/verify")
async def verify_creds(username: str = Form(...), password: str = Form(...)):
    basic_creds_check(username, password)

    async with ClientSession() as sess:
        session_result = await gen_session(sess, username, password)
        if session_result == 0:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        else:
            return JSONResponse(
                content={"csrf_token": session_result}, status_code=status.HTTP_200_OK
            )


@app.post("/api/all")
async def all_data(username: str = Form(...), password: str = Form(...)):
    basic_creds_check(username, password)

    async with ClientSession() as sess:
        session_result = await gen_session(sess, username, password)
        if session_result == 0:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        semID = await _get_sem_id(sess, username, session_result)
        data = {
            "profile": await get_profile_data(sess, username, session_result),
            "attendance": await get_attendance_data(
                sess, username, semID, session_result
            ),
            "semIDs": await _get_all_sem_ids(sess, username, session_result),
            "grades": await get_grades_data(sess, username, session_result),
            "examSchedule": await get_examSchedule_data(
                sess, username, semID, session_result
            ),
            "timetable": await get_timetable_data(
                sess, username, semID, session_result
            ),
        }

        return data


@app.post("/api/marks")
async def marks(
    username: str = Form(...), password: str = Form(...), semID: str = Form(...)
):
    basic_creds_check(username, password)

    async with ClientSession() as sess:
        session_result = await gen_session(sess, username, password)
        if session_result == 0:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        return await get_marks_data(sess, username, semID, session_result)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
