# VTOP Python Scraper

A FastAPI-based API for scraping and accessing VTOP (VIT Online Portal) data, including attendance, grades, timetables, exam schedules, and more.

## Features

- 🎓 Student profile information
- 📊 Attendance tracking with detailed history
- 📝 Grade history and CGPA
- 📅 Timetable parsing
- 📋 Exam schedule with venue details
- 🔢 Marks data for each semester
- 🔐 Session management with CAPTCHA solving

## Installation

### Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd vtop_py_scraper
```

2. Install dependencies using Poetry:

```bash
poetry install
```

3. Activate the virtual environment:

```bash
poetry shell
```

## Usage

### Running the Server

Start the FastAPI server:

```bash
poetry run vtop-server
```

Or with uvicorn directly:

```bash
poetry run uvicorn vtop_scraper.app:app --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

### API Endpoints

#### Authentication

- `POST /api/verify` - Verify credentials and get CSRF token

#### Student Data

- `POST /api/profile` - Get student profile information
- `POST /api/attendance` - Get attendance data
- `POST /api/grades` - Get grade history
- `POST /api/timetable` - Get course timetable
- `POST /api/examSchedule` - Get exam schedule
- `POST /api/marks` - Get marks for a specific semester (requires semID)
- `POST /api/semIDs` - Get all available semester IDs
- `POST /api/all` - Get all student data in one request

All endpoints require form data with:

- `username`: VIT registration number
- `password`: VTOP password
- `semID` (for marks endpoint only): Semester ID

## Development

### Project Structure

```
vtop_scraper/
├── __init__.py
├── app.py              # FastAPI application
├── gen_session.py      # Session generation and CAPTCHA solving
├── get_attendance.py   # Attendance data parsing
├── get_grades.py       # Grade history parsing
├── get_profile.py      # Profile data parsing
├── get_timetable.py    # Timetable parsing
├── get_exam_schedule.py # Exam schedule parsing
├── get_marks.py        # Marks data parsing
├── get_sem_id.py       # Semester ID retrieval
├── outing.py           # Outing application (placeholder)
├── constants/          # Constants and configuration
│   ├── bitmaps.py
│   ├── constants.py
│   └── weights.json
├── models/             # Data models
│   └── period.py
└── utils/              # Utility functions
    ├── captcha_solver.py
    ├── payloads.py
    └── sem_ids.py
```

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

Format code with Black:

```bash
poetry run black vtop_scraper/
```

Lint with Ruff:

```bash
poetry run ruff check vtop_scraper/
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
