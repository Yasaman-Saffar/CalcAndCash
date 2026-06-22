# CalcAndCash
**CalcAndCash** is a mathematics and economics competition platform designed to challenge users' analytical thinking, mathematical reasoning, and economic decision-making skills.

The project originated from an earlier mathematics competition platform and it provides a competitive environment where participants can join contests, manage virtual assets, interact with other users, and receive real-time updates throughout the competition.

**[Live Demo](https://calcandcash.ir)**


# Features
- OTP authentication via SMS
- Real-time competition management
- Real-time notifications using WebSockets
- Live leaderboard updates
- Mathematical and economic challenges
- Virtual banking and asset management system
- User profiles and ranking system
- Group creation and management
- Scheduled contests and automated tasks
- OTP authentication
- Staff management panel
- Contest control dashboard
- Inflation announcements and event broadcasting
- Background task processing with Celery
- Redis-powered messaging and caching


# Technology Stack
**Backend**
- Python
- Django
- Django Channels
- Celery
- PostgreSQL
- Redis
  
**Frontend**
- HTML
- CSS
- JavaScript
- Bootstrap
  
**Infrastructure**
- Daphne (ASGI Server)
- WebSockets
- Linux VPS

**External Services**
- SMS Gateway for OTP verification


# Architecture
The project follows a real-time architecture built on Django Channels and Redis.
- Django handles HTTP requests and business logic.
- Channels provides WebSocket support.
- Redis acts as the channel layer and task broker.
- Celery and Celery Beat execute background and scheduled tasks.
- PostgreSQL stores application data.
This architecture enables real-time updates for notifications, contests, and leaderboard changes without requiring page refreshes.


# Installation
Clone the repository:
```bash
git clone https://github.com/Yasaman-Saffar/CalcAndCash.git
cd CalcAndCash
```
Create a virtual environment:
```bash
python -m venv venv
```
Activate the virtual environment:
Linux/macOS:
```bash
source venv/bin/activate
```
Windows:
```bash
venv\Scripts\activate
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Apply migrations:
```bash
python manage.py migrate
```
Run the development server:
```bash
python manage.py runserver 8001
```


# Environment Variables
Create a .env file in the project root and configure the required settings:
```bash
SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=

DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

SMS_API_URL=
SMS_FROM_NUMBER=

CELERY_BROKER_URL=
CELERY_RESULT_BACKEND=

REDIS_OTP_URL=
CHANNEL_REDIS_URL=
CACHE_REDIS_URL=
```

# Running Background Services
Start Celery Worker:
```bash
celery -A Core worker -l info
```
Start Celery Beat:
```bash
celery -A Core beat -l info
```
Start Daphne:
```bash
daphne Core.asgi:application
--port 8000
```
