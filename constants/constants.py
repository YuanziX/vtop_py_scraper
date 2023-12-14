import os
import sys
user_agent_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67'}


vtop_base_url = "https://vtop2.vitap.ac.in/vtop/"

vtop_login_url = f"{vtop_base_url}vtopLogin"
vtop_doLogin_url = f"{vtop_base_url}doLogin"
vtop_profile_url = f"{vtop_base_url}studentsRecord/StudentProfileAllView"
vtop_timetable_url = f"{vtop_base_url}academics/common/StudentTimeTable"
vtop_process_timetable_url = f"{vtop_base_url}processViewTimeTable"
vtop_process_attendance_url = f"{vtop_base_url}processViewStudentAttendance"
vtop_process_attendance_detail_url = f"{vtop_base_url}processViewAttendanceDetail"
vtop_marks_view_url = f"{vtop_base_url}examinations/StudentMarkView"
vtop_doMarks_view_url = f"{vtop_base_url}examinations/doStudentMarkView"
vtop_gradeHistory_url = f"{vtop_base_url}examinations/examGradeView/StudentGradeHistory"
vtop_examSchedule_url = f"{vtop_base_url}examinations/doSearchExamScheduleForStudent"

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.sem_ids import semIDs
current_sem_IDs = list(semIDs)[:5]
