# FastAPI project — from zero to “it all clicks”

This document is a **single map** of your codebase: how a request moves through FastAPI, **Pydantic schemas**, **SQLAlchemy + Postgres**, **routers**, and **JWT auth**. It is aligned with **how you actually built it** (your git history), so you can replay the story in your head instead of memorizing files in isolation.

---

## 1. The one picture to keep in your head

Every API call is a pipeline:

```mermaid
flowchart LR
  Client[Client / Swagger]
  Route[Router + path handler]
  Deps[Depends: get_db, get_current_user]
  Schema[Pydantic: validate body/query]
  ORM[SQLAlchemy models + Session]
  DB[(PostgreSQL)]
  Client --> Route --> Deps --> Schema --> ORM --> DB
  DB --> ORM --> Route --> Client
```

- **FastAPI** wires the path, runs **dependencies** (`Depends`), validates input/output with **Pydantic** (`schemas`), and your handler talks to the DB through a **Session**.
- **Auth** is “just another dependency”: if a route declares `Depends(oauth2.get_current_user)`, FastAPI refuses the request unless a valid **Bearer token** is present.

You do not need to “feel” ten technologies at once — you only need this pipeline, with different boxes filled per route.

---

## 2. Your journey in git (the story order)

Reading bottom-to-top of `git log` is roughly how the project grew:

| Phase | What you did (idea) |
|--------|----------------------|
| Basics + in-memory list | FastAPI app, routes, data in a Python list |
| CRUD on posts | Create, read one, list, delete, update — HTTP status codes |
| Package layout | `app/` package, `main` inside app |
| Postgres | Real database instead of a list |
| SQLAlchemy | Engine, session, `Base`, models; queries as Python instead of raw SQL strings |
| Schemas split | Pydantic models in `schemas.py`; `response_model` for safe JSON output |
| Users + hashing | `User` model, `passlib` bcrypt hash on register, never store plain passwords |
| Login | Verify password, return a token |
| OAuth2 + JWT | `OAuth2PasswordRequestForm` for login body, **PyJWT** for encode/decode (you skipped deprecated `python-jose`) |

That order matters: **routes before DB**, **DB before ORM**, **ORM before auth**. Auth sits on top of “we can identify a user.”

---

## 3. Repo layout (what each file is for)

```
app/
  main.py           # FastAPI app instance, create tables, include routers
  database.py       # Postgres URL, engine, SessionLocal, get_db dependency
  models.py         # SQLAlchemy tables (ORM) — maps to DB rows
  schemas.py        # Pydantic — maps to JSON in/out (validation + serialization)
  oauth2.py         # JWT create/verify + OAuth2PasswordBearer + get_current_user
  utils.py          # hash / verify passwords (bcrypt)
  routers/
    post.py         # /posts CRUD
    user.py         # /users register + get by id
    auth.py         # /login → access token
```

**Rule of thumb**

- **`models.*`** = how data is stored in Postgres (columns, types).
- **`schemas.*`** = what the API promises to accept or return (JSON shape, docs, validation).
- **`routers.*`** = URLs + HTTP verbs + orchestration (call DB, return schema).

---

## 4. Postgres + SQLAlchemy (`database.py`, `models.py`)

**Connection string** (`SQLALCHEMY_DATABASE_URL`) tells SQLAlchemy where Postgres lives. Special characters in passwords (e.g. `@`) must be URL-encoded (`@` → `%40`) so the parser does not treat them as separators.

**Engine** = connection pool to the server.  
**`SessionLocal`** = factory for one “unit of work” session per request.  
**`get_db`** yields a session and **always closes it** in `finally` — so you do not leak connections.

**`models.Base.metadata.create_all(bind=engine)`** in `main.py` creates tables if they do not exist (fine for learning; production often uses migrations such as Alembic).

**`models.Post` / `models.User`** define tables (`__tablename__`) and columns. That is the **source of truth for the database shape** from SQLAlchemy’s perspective.

---

## 5. Pydantic schemas (`schemas.py`)

Schemas answer: *What JSON must the client send? What JSON will we return?*

- **`PostCreate` / `UserCreate`** — input for creating resources (no `id` yet).
- **`Post` / `UserOut`** — output with `id`, `created_at`, etc.
- **`model_config = {"from_attributes": True}`** — lets Pydantic build a response model from an **ORM object** (`models.Post`), not only from dicts.

**`token` / `TokenData`**

- **`token`** (consider renaming to `Token` for PEP 8): shape of login response — `access_token`, `token_type`.
- **`TokenData`**: small object holding claims you care about after decoding JWT (here mainly `id` as string).

---

## 6. Routers and `response_model`

**`APIRouter`** groups paths and optional `prefix` / `tags` (Swagger sections).

**`response_model=...`** tells FastAPI:

1. Validate what you return against that schema.
2. **Strip extra fields** — e.g. never accidentally return `password` if the schema does not include it.

**`Depends(get_db)`** injects a `Session`. You query with `db.query(models.Post)...` etc.

---

## 7. Passwords (`utils.py`, `user.py`)

- On **register**, you replace `user.password` with **`utils.hash(...)`** before `models.User(**user.model_dump())`.
- On **login**, you use **`utils.verify(plain, hashed)`** — bcrypt compares safely.

You never compare or log plain passwords in production code paths beyond what is required for verify.

---

## 8. Auth end-to-end (the part that feels “magical” until it is not)

### 8.1 Login: `POST /login` (`routers/auth.py`)

You use **`OAuth2PasswordRequestForm`**. That is not random — it is the standard OAuth2 “password grant” **shape**:

- Fields are named **`username`** and **`password`** in the form body.
- You store users by **email**, so you map **`username` → email** when querying:  
  `filter(models.User.email == user_credentials.username)`.

If user missing or password wrong → **`403`** with a generic message (many apps use **401** for both; pick one policy and stay consistent).

On success you call:

```python
oauth2.create_access_token(data={"user_id": user.id})
```

So the JWT payload carries **`user_id`** (your `oauth2.verify_access_token` reads `user_id`).

### 8.2 JWT (`oauth2.py`)

- **`create_access_token`**: copies your data dict, adds **`exp`** (expiry in UTC), signs with **`SECRET_KEY`** and **`HS256`** via **PyJWT**.
- **`verify_access_token`**: decodes, checks **`user_id`**, returns **`TokenData`**, or raises your **`credentials_exception`** on bad/missing token.

**`SECRET_KEY` in source code is only for local learning.** For anything real, use an environment variable and a long random key.

### 8.3 Protecting routes: `OAuth2PasswordBearer` + `get_current_user`

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
```

- Clients must send: **`Authorization: Bearer <access_token>`**.
- **`tokenUrl`** is mainly for **OpenAPI/Swagger** (“where do I get a token?”). Your login path is **`/login`**; using **`"/login"`** is clearer for tools. If “Authorize” in Swagger feels off, check this matches your real route.

**`get_current_user`** depends on **`oauth2_scheme`**, so FastAPI **requires** a Bearer token, then **`verify_access_token`**, then returns **`TokenData`**.

Any route that lists:

```python
current_user: schemas.TokenData = Depends(oauth2.get_current_user)
```

is **private** unless the token is valid. Routes **without** that dependency are **public** — you already saw that with posts earlier.

### 8.4 Mental model of a protected request

```mermaid
sequenceDiagram
  participant C as Client
  participant F as FastAPI
  participant O as oauth2_scheme
  participant V as verify_access_token
  participant H as Your handler

  C->>F: GET /posts + Authorization Bearer JWT
  F->>O: extract token
  alt missing/invalid token
    O-->>C: 401 Unauthorized
  else valid token
    O->>V: decode + check user_id
    V->>H: TokenData as current_user
    H-->>C: 200 + JSON
  end
```

---

## 9. Posts router (`routers/post.py`) — how it fits

| Method | Path | Typical role |
|--------|------|----------------|
| GET | `/posts/` | List posts (now requires token in your version) |
| GET | `/posts/{id}` | One post |
| POST | `/posts/` | Create |
| PUT | `/posts/{id}` | Update |
| DELETE | `/posts/{id}` | Delete |

**`commit` / `refresh`**: after insert, `refresh` reloads DB-generated fields (e.g. `id`, `created_at`).

**Design note:** your `Post` model has **no `owner_id`**. So “logged in” only means **some** user — not necessarily the **author** of that post. Next evolution is often: add `owner_id` on `Post`, set it on create from `current_user.id`, and check it on update/delete.

---

## 10. How to run the app (typical)

From the project root (where `app` is importable), with dependencies installed:

```bash
uvicorn app.main:app --reload
```

Open **`http://127.0.0.1:8000/docs`** — interactive Swagger.

**Happy path in Swagger**

1. **`POST /users/`** — create a user (password is hashed server-side).
2. **`POST /login`** — use **OAuth2 form**: `username` = your email, `password` = your password. Copy **`access_token`**.
3. Click **Authorize**, paste token (often as raw token; Swagger adds `Bearer` depending on UI).
4. Call protected routes (e.g. **`GET /posts/`**).

If you use another client (Postman, fetch), send:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 11. Dependencies you are implicitly using

Your imports imply packages such as:

- `fastapi`, `uvicorn[standard]`
- `sqlalchemy`, `psycopg2-binary` (or `psycopg` v3 driver, depending on your setup)
- `pydantic[email]` (for `EmailStr`)
- `passlib[bcrypt]`
- `PyJWT`
- `python-multipart` (required for **`OAuth2PasswordRequestForm`** form bodies)

Pin them in a `requirements.txt` or `pyproject.toml` when you are ready — it saves the “version compatibility” pain you already hit once in git.

---

## 12. Short “exam cram” checklist

1. **Request** hits a **path** on an **`APIRouter`**.
2. **`Depends(get_db)`** gives a **Session**; you query **`models`**.
3. **Input** is validated by **Pydantic** types in the signature or `Body`/`Form`.
4. **Output** is shaped by **`response_model`** using **`schemas`**.
5. **Auth**: login returns **JWT**; protected routes use **`Depends(oauth2.get_current_user)`**; client sends **`Authorization: Bearer ...`**.
6. **Passwords**: **hash** on create, **verify** on login; only **hashes** in the DB.

If you can narrate those six bullets for your own project without opening files, you have the whole architecture — the rest is syntax and Postgres details.

---

## 13. Optional next steps (when you want to level up)

- Environment variables for **`SECRET_KEY`** and **`DATABASE_URL`**.
- **`owner_id`** on posts and authorization checks.
- **Refresh tokens**, **HTTPS**, rate limiting, and structured logging.
- **Alembic** migrations instead of only `create_all`.

---

*This README describes the project as of the conversation date; if you change routes or auth behavior, update the “Happy path” and table sections to match.*
