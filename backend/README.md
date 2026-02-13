---
title: Phase3
emoji: ⚡
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# Todo API Backend

This is a secure, multi-user todo management API built with FastAPI, SQLModel, and Neon Serverless PostgreSQL.

## Features

- JWT-based authentication and authorization
- User isolation - users can only access their own tasks
- Complete CRUD operations for task management
- Task completion toggle functionality
- Input validation and error handling
- RESTful API design

## Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL (Neon Serverless)
- **Authentication**: JWT tokens
- **Serialization**: Pydantic models

## Installation

1. Clone the repository
2. Navigate to the backend directory
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the required environment variables:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/todo_db
BETTER_AUTH_SECRET=your_better_auth_secret_here
BETTER_AUTH_URL=http://localhost:8000
SECRET_KEY=your_secret_key_here_must_be_32_chars_at_least
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
NEON_DB_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/todo_db
```

## Running the Application

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Endpoints

All endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

### Tasks API

- `POST /api/{user_id}/` - Create a new task
- `GET /api/{user_id}/{task_id}` - Get a specific task
- `GET /api/{user_id}/` - Get all tasks for a user
- `PUT /api/{user_id}/{task_id}` - Update a task
- `DELETE /api/{user_id}/{task_id}` - Delete a task
- `PATCH /api/{user_id}/{task_id}/toggle` - Toggle task completion status

## Environment Variables

- `DATABASE_URL`: PostgreSQL database URL
- `BETTER_AUTH_SECRET`: Secret for Better Auth
- `BETTER_AUTH_URL`: Better Auth URL
- `SECRET_KEY`: Secret key for JWT signing
- `ALGORITHM`: Algorithm for JWT encoding (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT expiration time (default: 30)
- `NEON_DB_URL`: Neon Serverless PostgreSQL URL
- `ALLOWED_ORIGINS`: Origins allowed for CORS (default: ["*"])

## Database Migrations

This project uses Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "Migration message"

# Apply migrations
alembic upgrade head
```

## Security Features

- JWT token validation
- User ID validation in URL path matches token
- User data isolation
- Input validation
- Rate limiting (to be implemented)
- SQL injection prevention via ORM

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK` - Successful GET, PUT, PATCH requests
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Invalid or missing authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error
