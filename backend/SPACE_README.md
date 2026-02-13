# Todo API Backend - Hugging Face Space

This is a secure, multi-user todo management API built with FastAPI, deployed as a Hugging Face Space.

## Features

- JWT-based authentication and authorization
- User isolation - users can only access their own tasks
- Complete CRUD operations for task management
- Task completion toggle functionality
- Input validation and error handling
- RESTful API design

## API Endpoints

All endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

### Authentication API

- `POST /api/v1/register` - Register a new user
- `POST /api/v1/login` - Login and get JWT token

### Tasks API

- `POST /api/v1/{user_id}/` - Create a new task
- `GET /api/v1/{user_id}/{task_id}` - Get a specific task
- `GET /api/v1/{user_id}/` - Get all tasks for a user
- `PUT /api/v1/{user_id}/{task_id}` - Update a task
- `DELETE /api/v1/{user_id}/{task_id}` - Delete a task
- `PATCH /api/v1/{user_id}/{task_id}/toggle` - Toggle task completion status

### Chat API

- `POST /api/chat` - Chat with the AI assistant

## Environment Variables

The following environment variables can be configured in the Space secrets:

- `DATABASE_URL`: PostgreSQL database URL (defaults to SQLite for demo)
- `SECRET_KEY`: Secret key for JWT signing
- `BETTER_AUTH_SECRET`: Secret for authentication
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `OPEN_ROUTER_API_KEY`: OpenRouter API key for AI features

## Security Note

For security reasons, this demo uses a SQLite database. For production deployments, please use a persistent PostgreSQL database.

## Usage

1. Register a new user via the `/api/v1/register` endpoint
2. Login via the `/api/v1/login` endpoint to get a JWT token
3. Use the JWT token in the Authorization header for all other API calls
4. Manage your tasks via the tasks API endpoints

## Local Development

If you want to run this locally:

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`.