# Auth Microservice

A small REST API for user registration, JWT-based authentication, profile management, and administrator-controlled user management. It is built with FastAPI, SQLAlchemy, Alembic, SQLite, bcrypt, and `python-jose`.

## What it provides

- Account registration with email and password validation
- Password hashing with bcrypt
- Access and refresh JWTs
- Authenticated profile retrieval, update, password change, and deactivation
- Administrator-only user listing, lookup, role toggling, and deletion
- Database schema versioning through Alembic
- Interactive OpenAPI documentation from FastAPI

## Tech stack

| Area | Technology |
| --- | --- |
| Web API | FastAPI |
| ORM | SQLAlchemy 2 |
| Database | SQLite (`userdb.db`) |
| Migrations | Alembic |
| Authentication | OAuth2 bearer tokens and JWT (HS256) |
| Password hashing | bcrypt |
| Dependency management | uv |

## Requirements

- Python **3.14 or later** (as declared in `pyproject.toml`)
- [uv](https://docs.astral.sh/uv/) (recommended)

## Quick start

Clone the repository, then install the locked dependencies and apply the database migrations:

```bash
uv sync
uv run alembic upgrade head
```

Start the development server:

```bash
uv run fastapi dev main.py
```

The API is now available at `http://127.0.0.1:8000`.

| Resource | URL |
| --- | --- |
| Health check | <http://127.0.0.1:8000/> |
| Swagger UI | <http://127.0.0.1:8000/docs> |
| ReDoc | <http://127.0.0.1:8000/redoc> |
| OpenAPI schema | <http://127.0.0.1:8000/openapi.json> |

Alternatively, run the module directly:

```bash
uv run python main.py
```

## Configuration and data

The application and Alembic both use the SQLite database at `./userdb.db`. Run commands from the repository root so they refer to the same database file.

```text
Auth_Microservice/
├── main.py                 # FastAPI application and health endpoint
├── routes/                 # Authentication and user endpoints
├── schemas/                # Pydantic request/response models
├── models/                 # SQLAlchemy models
├── core/setting.py         # JWT and authentication helpers
├── database.py             # SQLite engine, session, and declarative base
├── migrations/             # Alembic migration scripts
└── alembic.ini             # Alembic configuration
```

To inspect the current migration revision or create a migration during development:

```bash
uv run alembic current
uv run alembic revision --autogenerate -m "describe the change"
uv run alembic upgrade head
```

## Authentication flow

1. Create an account with `POST /auth/register`.
2. Exchange the email and password at `POST /auth/login`; it returns an access token and refresh token.
3. Send the access token in `Authorization: Bearer <access_token>` when calling protected endpoints.
4. When the access token expires, call `POST /auth/refresh` with the refresh token to obtain a new access token.
5. Call `POST /auth/logout` with the current access token to revoke it for the lifetime of the running process.

Access tokens expire after **30 minutes**. Refresh tokens expire after **7 days**.

## API reference

### Health

| Method | Path | Authentication | Description |
| --- | --- | --- | --- |
| `GET` | `/` | None | Returns a simple server health response. |

### Authentication

| Method | Path | Authentication | Description |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | None | Create a user account. |
| `POST` | `/auth/login` | None | Exchange credentials for an access and refresh token. |
| `POST` | `/auth/refresh` | None | Create a new access token from a refresh token. |
| `POST` | `/auth/logout` | Bearer access token | Revoke the supplied access token. Returns `204`. |

#### Register a user

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Ada Lovelace",
    "email": "ada@example.com",
    "raw_password": "SecurePass1@"
  }'
```

Example response:

```json
{
  "id": 1,
  "name": "Ada Lovelace",
  "email": "ada@example.com",
  "role": "user",
  "created_at": "2026-10-19T10:00:00",
  "is_active": true
}
```

#### Sign in

`/auth/login` uses the OAuth2 password form, so the request body must be form-encoded. Put the email address in the `username` field.

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=ada@example.com&password=SecurePass1@'
```

Example response:

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer"
}
```

Save the access token for later examples:

```bash
export ACCESS_TOKEN='<paste access_token here>'
export REFRESH_TOKEN='<paste refresh_token here>'
```

#### Refresh an access token

The refresh token is currently a required **query parameter**, not a JSON body.

```bash
curl -X POST "http://127.0.0.1:8000/auth/refresh?refresh_token=${REFRESH_TOKEN}"
```

#### Log out

```bash
curl -i -X POST http://127.0.0.1:8000/auth/logout \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

### Current-user endpoints

| Method | Path | Authentication | Description |
| --- | --- | --- | --- |
| `GET` | `/users/me` | Bearer access token | Retrieve the current user's public profile. |
| `PATCH` | `/users/me` | Bearer access token | Update the current user's name and/or email. |
| `PATCH` | `/users/password` | Bearer access token | Set a new password. Returns `202`. |
| `DELETE` | `/users/me` | Bearer access token | Deactivate the current user's account. Returns `204`. |

```bash
curl http://127.0.0.1:8000/users/me \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"

curl -X PATCH http://127.0.0.1:8000/users/me \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{"name":"Ada Byron"}'

curl -X PATCH http://127.0.0.1:8000/users/password \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{"new_password":"NewSecurePass1@"}'
```

An inactive account cannot use protected endpoints; it returns `403`.

### Administrator endpoints

All endpoints below require an authenticated user whose role is `admin`.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/users/?offset=0&limit=10` | List users, newest first. `offset` must be at least 0; `limit` is 1–25. |
| `GET` | `/users/{id}` | Retrieve a user by ID. |
| `PATCH` | `/users/{id}/role` | Toggle the user's role between `user` and `admin`. |
| `DELETE` | `/users/{id}` | Permanently delete a user. Returns `204`. |

```bash
curl 'http://127.0.0.1:8000/users/?offset=0&limit=10' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"

curl -X PATCH http://127.0.0.1:8000/users/2/role \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

There is no API bootstrap route for the first administrator. For local development, promote a known account directly in the database; a production application should add a controlled bootstrap or provisioning mechanism before deployment.

## Validation rules

Registration requires:

- `name`: 3–50 characters, alphabetic characters and spaces only
- `email`: a valid email address; it is trimmed and lowercased
- `raw_password`: 8–50 characters, no spaces, and at least one uppercase letter, lowercase letter, digit, and one of `@`, `#`, or `.`

Updating `/users/me` accepts optional `name` and `email` fields and applies the same name and email validation. `PATCH /users/password` accepts only `new_password` and applies the same password rules as registration.

## Response and error behavior

- Successful deletion and logout return `204 No Content`.
- Invalid credentials, invalid/expired tokens on authentication-protected routes, and a refresh token used as an access token return `401 Unauthorized`.
- A revoked access token, an inactive account, or a non-admin account returns `403 Forbidden`.
- Missing resources return `404 Not Found`.
- Invalid input is returned by FastAPI as `422 Unprocessable Entity`.
- Registering an existing email currently returns `403 Forbidden`.

## License

No license is currently specified for this repository.
