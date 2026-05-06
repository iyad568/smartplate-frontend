# SmartPlate Auth API

A **secure, production-ready** FastAPI backend implementing:

- **Email + password signup** restricted to **Gmail addresses only**
- **6-digit OTP email verification** (signup) and **2-step OTP login** (no Google OAuth)
- **Role-based access control** with roles: `user`, `sos`, `depanage`, `admin`
- bcrypt password & OTP hashing, JWT access + refresh tokens, slowapi rate limits

---

## Project Structure

```
smartplate_auth/
├── main.py                          # App entry point
├── requirements.txt
├── .env.example
├── schema.sql                       # Plain-SQL reference schema
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/                    # Auto-generated migrations
└── app/
    ├── api/
    │   ├── __init__.py              # Router aggregator
    │   └── routes/
    │       ├── auth.py              # /auth/* (signup, login, OTP, refresh, me)
    │       ├── admin.py             # /admin/* — admin only
    │       ├── sos.py               # /sos/*   — sos role
    │       ├── depanage.py          # /depanage/* — depanage role
    │       └── users.py             # /users/me — any authenticated user
    ├── core/
    │   ├── config.py                # Pydantic settings (.env)
    │   ├── security.py              # bcrypt + OTP gen + JWT helpers
    │   ├── dependencies.py          # get_current_user, require_roles
    │   └── logging.py
    ├── db/
    │   ├── session.py               # Async SQLAlchemy engine + get_db()
    │   └── repositories/
    │       ├── user_repo.py
    │       └── otp_repo.py
    ├── models/
    │   ├── user.py                  # users  +  UserRole enum
    │   └── otp_code.py              # otp_codes  +  OtpPurpose enum
    ├── schemas/
    │   └── auth.py                  # all request/response models
    └── services/
        ├── auth_service.py          # signup, login, OTP, refresh
        ├── otp_service.py           # OTP issuance + verification
        └── email_service.py         # aiosmtplib (Gmail SMTP)
```

---

## Quick Start

### 1. Prerequisites
- Python 3.11+
- PostgreSQL 14+
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords)

### 2. Install
```bash
cd smartplate_auth
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure `.env`
```bash
cp .env.example .env
# Fill in DATABASE_URL, SECRET_KEY, SMTP credentials
openssl rand -hex 32              # generates a SECRET_KEY value
```

### 4. Set up the database

Either:

```bash
psql "$DATABASE_URL" -f schema.sql
```

or use Alembic:

```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

In **development**, tables are also created automatically on startup
(`create_tables()` is called from the lifespan).

### 5. Run
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Interactive docs: http://localhost:8000/docs

---

## Auth Flows

### Signup → email verification

```
┌──────────┐  POST /auth/signup            ┌────────────┐
│  Client  │ ──────────────────────────►  │  Server    │
└──────────┘  full_name, gmail, phone,     └────────────┘
              password, confirm, role          │
                                               │ hash pw, save user
                                               │ generate OTP, store hash
                                               │ email OTP
                                               ▼
              { message, expires_in_minutes,
                resend_in_seconds, email }

┌──────────┐  POST /auth/verify-email      ┌────────────┐
│  Client  │ ──────────────────────────►  │  Server    │
└──────────┘  email + 6-digit code             │
                                               │ verify OTP, mark used
                                               │ flip is_verified=true
                                               ▼
              { access_token, refresh_token, user }
```

### Login (2-step)

```
┌──────────┐  POST /auth/login             ┌────────────┐
│  Client  │ ──────────────────────────►  │  Server    │
└──────────┘  email, password                  │
                                               │ verify password
                                               │ issue login OTP, email it
                                               │ mint pre_auth_token (10 min)
                                               ▼
              { pre_auth_token, expires_in_minutes }

┌──────────┐  POST /auth/verify-login-otp  ┌────────────┐
│  Client  │ ──────────────────────────►  │  Server    │
└──────────┘  pre_auth_token + 6-digit code    │
                                               │ verify pre-auth JWT
                                               │ verify OTP, mark used
                                               ▼
              { access_token, refresh_token, user }
```

The `pre_auth_token` is a JWT with `type=otp_pending`. It is **rejected** by
every protected endpoint, so attackers cannot use it to access resources
without completing the OTP step.

---

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### Public

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/auth/signup` | `SignupRequest` | Register; sends signup OTP. **role** must be `user` \| `sos` \| `depanage` (default `user`). **email** must end with `@gmail.com`. |
| POST | `/auth/verify-email` | `{ email, code }` | Verify signup OTP, activate account, return JWT pair. |
| POST | `/auth/login` | `{ email, password }` | Step 1 — verify password, send login OTP, return `pre_auth_token`. |
| POST | `/auth/verify-login-otp` | `{ pre_auth_token, code }` | Step 2 — exchange OTP for JWT pair. |
| POST | `/auth/resend-otp` | `{ email, purpose }` | Resend signup or login OTP (rate-limited via cooldown). |
| POST | `/auth/refresh` | `{ refresh_token }` | Rotate access + refresh tokens. |
| GET  | `/health` | — | Health check. |

### Authenticated (require `Authorization: Bearer <access_token>`)

| Method | Path | Required role | Description |
|--------|------|---------------|-------------|
| GET    | `/auth/me` or `/users/me` | any | Current user profile |
| GET    | `/admin/users` | `admin` | List all users |
| PATCH  | `/admin/users/{id}/role` | `admin` | Change a user's role (incl. granting admin) |
| GET    | `/sos/requests` | `sos` (or admin) | List SOS requests |
| POST   | `/sos/requests/{id}/claim` | `sos` (or admin) | Claim an SOS request |
| GET    | `/depanage/jobs` | `depanage` (or admin) | List dépannage jobs |
| POST   | `/depanage/jobs/{id}/accept` | `depanage` (or admin) | Accept a dépannage job |

`admin` implicitly has access to every role-gated route.

### Example signup body
```json
{
  "full_name": "Jane Doe",
  "email": "jane@gmail.com",
  "phone": "+213555123456",
  "password": "Secure@123",
  "confirm_password": "Secure@123",
  "role": "user"
}
```

### 201 response
```json
{
  "message": "Account created. Check your email for the verification code.",
  "email": "jane@gmail.com",
  "expires_in_minutes": 10,
  "resend_in_seconds": 60
}
```

### 200 response from `/auth/verify-email` or `/auth/verify-login-otp`
```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "full_name": "Jane Doe",
    "email": "jane@gmail.com",
    "phone": "+213555123456",
    "role": "user",
    "is_verified": true,
    "created_at": "2026-04-30T..."
  }
}
```

---

## Roles & RBAC

| Role | How obtained | Typical access |
|------|--------------|----------------|
| `user` | Default at signup | Basic features (`/users/me`) |
| `sos` | Self-selected at signup, or admin grant | `/sos/*` |
| `depanage` | Self-selected at signup, or admin grant | `/depanage/*` |
| `admin` | **DB only** or via existing admin (`PATCH /admin/users/{id}/role`) | Everything, including `/admin/*` |

Public clients **cannot** request `role=admin` at signup — pydantic returns
422, and even if bypassed at the schema layer, `auth_service.signup`
enforces a `SIGNUP_ALLOWED_ROLES` whitelist server-side.

To grant admin to an existing user manually:

```sql
UPDATE users SET role = 'admin' WHERE email = 'someone@gmail.com';
```

### Using the middleware

```python
from fastapi import APIRouter, Depends
from app.core.dependencies import require_roles, require_admin
from app.models.user import UserRole

router = APIRouter()

# Admin-only on every endpoint in the router:
@router.get("/admin/things", dependencies=[Depends(require_admin)])
async def list_things(): ...

# Either sos or admin:
@router.post("/sos/something")
async def something(user = Depends(require_roles(UserRole.SOS))):
    return {"by": user.email}
```

---

## Security Features

| Feature | Implementation |
|---------|----------------|
| Password hashing | bcrypt via passlib |
| OTP hashing | bcrypt — never stored in plaintext |
| OTPs | 6 digits, 10 min expiry, single-use, prior actives invalidated on resend |
| Resend cooldown | 60 s per (user, purpose), enforced server-side |
| Rate limits | slowapi: signup 5/min, login 5/min (configurable), verify 10/min, resend 3/min |
| User-enumeration | `/auth/login` always runs password compare; `/auth/resend-otp` returns generic success |
| JWT | python-jose (HS256), separate types: `access`, `refresh`, `otp_pending` |
| Pre-auth scope | `otp_pending` JWTs are rejected by `get_current_user` — they only work on `/auth/verify-login-otp` |
| Gmail enforcement | regex + Pydantic `EmailStr` |
| Phone validation | `phonenumbers` (E.164) |
| Password policy | 8+ chars, upper + lower + digit + special |
| CORS | Locked to `FRONTEND_URL` in production |
| Secrets | All via `.env` |

---

## Configuration (.env)

| Var | Purpose | Default |
|-----|---------|---------|
| `DATABASE_URL` | Async PG URL (`postgresql+asyncpg://…`) | — |
| `SECRET_KEY` | JWT signing key (`openssl rand -hex 32`) | — |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | | 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | | 7 |
| `PRE_AUTH_TOKEN_EXPIRE_MINUTES` | Login step-1 token TTL | 10 |
| `OTP_LENGTH` | | 6 |
| `OTP_EXPIRE_MINUTES` | | 10 |
| `OTP_RESEND_COOLDOWN_SECONDS` | | 60 |
| `OTP_MAX_ATTEMPTS` | | 5 |
| `MAX_LOGIN_ATTEMPTS_PER_MINUTE` | slowapi limit on `/auth/login` | 5 |
| `SMTP_HOST`/`SMTP_PORT`/`SMTP_USERNAME`/`SMTP_PASSWORD` | Gmail SMTP creds | — |
| `EMAILS_FROM_NAME`/`EMAILS_FROM_EMAIL` | Sender identity | — |
| `FRONTEND_URL` | CORS allow-origin in prod | http://localhost:3000 |
| `APP_ENV` | `development` or `production` | development |

---

## Running tests

```bash
pytest tests/ -v
```

---

## Frontend integration tips

```js
// 1) Signup → user is told to check email
await fetch('/api/v1/auth/signup', { method:'POST', body: JSON.stringify(form) });
// 2) /verify-email page collects 6-digit OTP and POSTs:
const r = await fetch('/api/v1/auth/verify-email', {
    method:'POST',
    body: JSON.stringify({ email, code })
});
const { access_token, refresh_token, user } = await r.json();

// Login is two POSTs in a row:
const { pre_auth_token } = await (await fetch('/api/v1/auth/login', { … })).json();
const session = await fetch('/api/v1/auth/verify-login-otp', {
    method:'POST',
    body: JSON.stringify({ pre_auth_token, code })
});
```

UX recommendations: 6-input OTP component, countdown timer driven by
`expires_in_minutes`, resend button disabled for `resend_in_seconds`.
