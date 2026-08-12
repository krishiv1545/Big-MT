# Big-MT / Big Empty

This project is a Django-based backend application.

## Project Structure

- `backend/`: Contains the Django project source code.
    - `core/`: Main Django configuration and settings.
    - `core_APP/`: Primary application logic, models, and views.
    - `manage.py`: Django command-line utility.
- `deploy/`: Deployment configurations for Nginx and Systemd.
- `requirements.txt`: Python dependencies.

## Prerequisites

- Python 3.x
- pip

## Installation

1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the environment template:
   ```bash
   cp backend/.env.example backend/.env
   ```
2. Edit `backend/.env` and provide the necessary values (e.g., `SECRET_KEY`).

## Development

To run the development server:
```bash
cd backend
python manage.py runserver
```

## Deployment

Deployment instructions for staging environments (Ubuntu) are located in `deploy/commands.md`. This includes configurations for Gunicorn and Nginx.

