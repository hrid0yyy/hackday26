# FastAPI Authentication with Supabase

A complete authentication system built with FastAPI and Supabase, featuring secure user management, JWT tokens, and comprehensive auth endpoints.

## Features

✨ **Complete Authentication System**
- User registration (sign up) with email verification
- User login (sign in) with JWT tokens
- Secure logout functionality
- Password reset via email
- Change password for authenticated users
- Email verification
- Refresh token mechanism
- Rate limiting on sensitive endpoints

🔐 **Security Features**
- Strong password validation (uppercase, lowercase, digit, special char)
- JWT access and refresh tokens
- Token expiration handling
- HTTP Bearer authentication
- Password hashing with bcrypt
- Prevention of email enumeration attacks

🏗️ **Architecture**
- Clean separation of concerns (routes, services, models, utilities)
- Supabase integration for auth and user management
- Pydantic models for request/response validation
- Dependency injection for authentication
- Comprehensive error handling
- CORS support

## Project Structure

```
backend/
├── src/
│   ├── main.py                          # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py                  # Core module exports
│   │   ├── config.py                    # Application settings
│   │   └── db.py                        # Supabase client initialization
│   └── modules/
│       └── authentication/
│           ├── __init__.py              # Authentication module exports
│           ├── models.py                # Pydantic models
│           ├── service.py               # Business logic layer
│           ├── routes.py                # API endpoints
│           ├── dependencies.py          # Authentication dependencies
│           └── utils.py                 # Utility functions
├── requirements.txt                      # Python dependencies
├── .env.example                         # Environment variables template
└── README.md                            # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- Supabase account and project
- Virtual environment (recommended)

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your credentials
# Required: SUPABASE_URL, SUPABASE_KEY, JWT_SECRET_KEY
```

**Generate JWT Secret Key:**
```bash
# Using Python
python -c "import secrets; print(secrets.token_hex(32))"

# Or using OpenSSL
openssl rand -hex 32
```

### 4. Supabase Setup

1. Create a Supabase project at https://supabase.com
2. Go to Project Settings > API
3. Copy your:
   - Project URL → `SUPABASE_URL`
   - anon/public key → `SUPABASE_KEY`
   - service_role key → `SUPABASE_SERVICE_ROLE_KEY`
4. Enable Email Auth in Authentication > Providers

### 5. Run the Application

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Base URL: `http://localhost:8000`

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/signup` | Register new user | No |
| POST | `/auth/signin` | Sign in user | No |
| POST | `/auth/signout` | Sign out user | Yes |
| POST | `/auth/forgot-password` | Request password reset | No |
| POST | `/auth/reset-password` | Reset password with token | No |
| POST | `/auth/change-password` | Change password | Yes |
| POST | `/auth/refresh` | Refresh access token | Yes (Refresh Token) |
| POST | `/auth/verify-email` | Verify email with token | No |
| POST | `/auth/resend-verification` | Resend verification email | No |
| GET | `/auth/me` | Get current user info | Yes |
| GET | `/auth/health` | Health check | No |

### General Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API welcome message |
| GET | `/health` | Application health check |
| GET | `/docs` | Interactive API documentation (Swagger UI) |
| GET | `/redoc` | Alternative API documentation (ReDoc) |

## API Usage Examples

### 1. Sign Up

```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "email_verified": false,
    "created_at": "2026-01-07T...",
    "last_sign_in_at": null
  }
}
```

### 2. Sign In

```bash
curl -X POST "http://localhost:8000/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### 3. Get Current User

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Forgot Password

```bash
curl -X POST "http://localhost:8000/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "redirect_url": "http://localhost:3000/reset-password"
  }'
```

### 5. Change Password

```bash
curl -X POST "http://localhost:8000/auth/change-password" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "SecurePass123!",
    "new_password": "NewSecurePass456!"
  }'
```

### 6. Refresh Token

```bash
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN"
```

## Password Requirements

Passwords must meet the following criteria:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (!@#$%^&*(),.?":{}|<>)

## Error Handling

All endpoints return structured error responses:

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "success": false
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid/missing credentials)
- `404` - Not Found
- `409` - Conflict (user already exists)
- `500` - Internal Server Error

## Security Best Practices

1. **Never commit `.env` file** - Always use `.env.example` as template
2. **Use strong JWT secret keys** - Generate with `openssl rand -hex 32`
3. **Keep service_role_key secure** - Only use server-side
4. **Enable HTTPS in production** - Never send credentials over HTTP
5. **Configure CORS properly** - Restrict to your frontend domain
6. **Implement rate limiting** - Prevent brute force attacks
7. **Regular token rotation** - Use refresh tokens to get new access tokens
8. **Monitor auth logs** - Check Supabase dashboard for suspicious activity

## Rate Limiting

Rate limiting is configured for sensitive endpoints:
- Auth endpoints: 5 requests per minute
- Password reset: 3 requests per 5 minutes

To implement actual rate limiting, integrate with Redis:
```python
# TODO: Implement Redis-based rate limiting
```

## Development Tips

### Interactive API Documentation

Visit `http://localhost:8000/docs` for Swagger UI - you can test all endpoints directly!

### Testing with cURL

All examples use cURL. For a better experience, use:
- [Postman](https://www.postman.com/)
- [Insomnia](https://insomnia.rest/)
- [HTTPie](https://httpie.io/)

### Database Management

Use Supabase Dashboard to:
- View user table
- Monitor authentication logs
- Configure email templates
- Set up email providers (SMTP)

## Troubleshooting

### "Could not validate credentials"
- Check if token is expired
- Verify JWT_SECRET_KEY matches
- Ensure Bearer token format: `Bearer <token>`

### "User with this email already exists"
- Email is already registered
- Check Supabase dashboard > Authentication > Users

### Email not sending
- Configure SMTP in Supabase > Project Settings > Auth
- Check email templates
- Verify email provider settings

### CORS errors
- Add frontend URL to CORS_ORIGINS in .env
- Restart the server after changing .env

## Future Enhancements

- [ ] Redis-based rate limiting
- [ ] OAuth providers (Google, GitHub, etc.)
- [ ] Two-factor authentication (2FA)
- [ ] Session management
- [ ] Account lockout after failed attempts
- [ ] Audit logs
- [ ] User roles and permissions
- [ ] API key authentication
- [ ] WebSocket authentication

## License

MIT License - feel free to use in your projects!

## Support

For issues or questions:
1. Check the [FastAPI documentation](https://fastapi.tiangolo.com/)
2. Review [Supabase Auth docs](https://supabase.com/docs/guides/auth)
3. Open an issue in the repository

---

**Built with ❤️ using FastAPI and Supabase**
