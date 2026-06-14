# FastAPI Social App

A production-ready RESTful API built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy** — featuring full CRUD operations on posts, user authentication with JWT tokens, and a voting system.

## Features

- **Posts** — Create, read, update, and delete posts with owner-based authorization
- **Users** — Register and authenticate users with bcrypt-hashed passwords
- **Votes** — Upvote/unvote posts (one vote per user per post enforced)
- **JWT Auth** — Secure token-based authentication using PyJWT and OAuth2 Bearer
- **Alembic Migrations** — Version-controlled database schema changes
- **Docker** — Fully containerized with Docker Compose for one-command local setup
- **CI with GitHub Actions** — Automated test suite runs on every push against a real PostgreSQL instance

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Auth | PyJWT + passlib (bcrypt) |
| Validation | Pydantic v2 + pydantic-settings |
| Testing | Pytest with isolated test database |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |

## Quick Start

```bash
# Clone and set up environment
cp .env.example .env   # fill in your values

# Run with Docker Compose
docker-compose up

# App available at http://localhost:8000
# Swagger UI at http://localhost:8000/docs
```

## Running Tests Locally

```bash
# Requires a running PostgreSQL instance with a fastapi_test database
pytest -v
```

## API Overview

| Method | Path | Auth Required | Description |
|---|---|---|---|
| POST | `/users/` | No | Register a new user |
| POST | `/login` | No | Login and get access token |
| GET | `/posts/` | Yes | List all posts with vote counts |
| POST | `/posts/` | Yes | Create a new post |
| GET | `/posts/{id}` | Yes | Get a single post |
| PUT | `/posts/{id}` | Yes | Update your own post |
| DELETE | `/posts/{id}` | Yes | Delete your own post |
| POST | `/vote/` | Yes | Upvote or remove vote on a post |
