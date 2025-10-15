# Ganana - Stock Take Agent

A web-based inventory stock take and variance reporting tool.

## Features
- Mobile-first UI for physical stock counts
- Variance report generation
- One-click stock adjustment
- FastAPI backend, SQLite, SQLAlchemy, Alembic
- Bootstrap CSS for responsive UI
- Dockerized for easy deployment

## Quick Start

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run database migrations:
   ```sh
   alembic upgrade head
   ```
3. Start the app:
   ```sh
   uvicorn app.main:app --reload
   ```
4. Visit [http://localhost:8000/docs](http://localhost:8000/docs) for API docs.

## Docker

```sh
docker-compose up --build
```
