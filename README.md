# CalcAndCash

**CalcAndCash** is a mathematics and economics competition platform designed to challenge users' analytical thinking, mathematical reasoning, and economic decision-making skills.

The project originated from an earlier mathematics competition platform and it provides a competitive environment where participants can join contests, manage virtual assets, interact with other users, and receive real-time updates throughout the competition.

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

- Docker
- Docker Compose

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

The application is containerized with Docker, while Docker Compose manages the application services and their dependencies.

# Running with Docker

## Prerequisites

Install:

- Docker
- Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/Yasaman-Saffar/CalcAndCash.git
cd CalcAndCash
```

### 2. Configure environment variables

Create your local `.env` file from the provided example:

```bash
cp .env.example .env
```

Update the values in `.env` with your local credentials and configuration.

OTP authentication requires an SMS gateway/provider. Configure your own SMS service credentials in .env:

```bash
SMS_API_URL=your_sms_api_url
SMS_FROM_NUMBER=your_sms_sender_number
```

You must have an active SMS service account and use the API URL and sender number provided by your SMS provider.

### 3. Build and start the containers

```bash
docker compose up -d --build
```

### 4. Apply database migrations

```bash
docker compose run --rm web python manage.py migrate
```

### 5. Open the application

The application is available at:

```text
http://localhost:8000
```
