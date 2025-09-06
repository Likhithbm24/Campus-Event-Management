# Campus Event Management

A web-based application for managing campus events, student registrations, reports, and logs.

---

## Features

- Create, update, and delete events.
- Manage student registrations and attendees.
- Generate reports and maintain event logs.
- Admin interface for complete control.
- Ready-to-use templates and static files.

---

## Prerequisites

Make sure you have the following installed:

- **Python 3.8+**
- **pip** (Python package manager)
- **Virtualenv** (recommended)

---

## Installation & Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/Likhithbm24/Campus-Event-Management.git
   cd Campus-Event-Management
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux / macOS:
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   Copy the example file and update the values:

   ```bash
   cp env.example .env
   ```

   ### Example `.env`

   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///db.sqlite3
   ```

5. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (Admin login)**
   ```bash
   python manage.py createsuperuser
   ```

---

## Running the Application

Start the development server:

```bash
python manage.py runserver
```

Visit the app in your browser:

```
http://127.0.0.1:8000
```

To access the admin panel:

```
http://127.0.0.1:8000/admin
```

---

## Running Tests

```bash
pytest
# or
python manage.py test
```

---

## Project Structure

```
Campus-Event-Management/
├── campus_events/        # Main app logic
├── events/               # Event management
├── logs/                 # Logging features
├── reports/              # Reports module
├── students/             # Student-related features
├── static/css/           # CSS files
├── templates/            # HTML templates
├── tests/                # Test cases
├── manage.py             # Django management script
├── check_status.py       # Utility script for monitoring
├── quick_start.py        # Script to bootstrap setup
├── requirements.txt      # Python dependencies
├── env.example           # Example environment variables
└── db.sqlite3            # Default database (SQLite)
```

---

## Useful Commands

- **Start development server**
  ```bash
  python manage.py runserver
  ```
- **Apply migrations**
  ```bash
  python manage.py migrate
  ```
- **Create migrations**
  ```bash
  python manage.py makemigrations
  ```
- **Create superuser**
  ```bash
  python manage.py createsuperuser
  ```
- **Run quick start script (if needed)**
  ```bash
  python quick_start.py
  ```
- **Run status check**
  ```bash
  python check_status.py
  ```

---

## License

This project is licensed under the MIT License.
