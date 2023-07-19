from flask import Flask, jsonify, request, abort
from aiohttp import ClientSession

from gen_session import gen_session
from get_profile import get_profile_data
from get_attendance import get_attendance_data
from get_timetable import get_timetable_data

app = Flask(__name__)


@app.route('/')
def root():
    return 'VTOP-AP API'


async def handle_request(data_func):
    username = request.form.get('username')
    password = request.form.get('password')

    if username == '' or username is None or password == '' or password == None:
        abort(401)

    async with ClientSession() as sess:
        if await gen_session(sess, username, password):
            return jsonify(await data_func(sess, username))
        else:
            abort(401)


@app.route('/api/profile', methods=['POST'])
@app.route('/api/attendance', methods=['POST'])
@app.route('/api/timetable', methods=['POST'])
async def handle_data():
    data_func = {
        '/api/profile': get_profile_data,
        '/api/attendance': get_attendance_data,
        '/api/timetable': get_timetable_data
    }
    return await handle_request(data_func[request.path])


@app.route('/api/all', methods=['POST'])
async def all_data():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == '' or username == None or password == '' or password == None:
        abort(401)

    async with ClientSession() as sess:
        if await gen_session(sess, username, password):
            data = {
                'profile': await get_profile_data(sess, username),
                'attendance': await get_attendance_data(sess, username),
                'timetable': await get_timetable_data(sess, username)
            }

            return jsonify(data)
        else:
            abort(401)

if __name__ == "__main__":
    app.run(debug=True)
