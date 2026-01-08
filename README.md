# Hackday Accessibility Communication Backend

A comprehensive FastAPI backend for an accessibility-focused communication platform. Enables seamless communication between users with different abilities through real-time sign language detection, speech-to-text conversion, and AI-powered text processing.

## Features

🎯 **Core Modules**

### 1. Authentication & User Management
- User registration with disability status (deaf/mute/blind/normal)
- JWT-based authentication
- User profile management with accessibility preferences
- Email verification and password reset
- User search by email

### 2. Real-time Sign Language Detection
- WebSocket-based video frame processing
- ML model: `prithivMLmods/Alphabet-Sign-Language-Detection`
- Anti-spam deduplication (max 2 repeats, 2s cooldown)
- AI-powered text cleaning with GPT-4o-mini
- Automatic message storage in conversation history

### 3. Speech-to-Text Conversion
- Audio file transcription using OpenAI Whisper
- Multiple audio format support
- Automatic message storage with sender/receiver context

### 4. Chat & Messaging
- Send text messages between users
- Retrieve conversation history (bidirectional)
- Pagination support for chat history
- Messages ordered by most recent first

### 5. AI Chatbot Integration
- Context-aware conversational AI
- Supabase vector store integration
- OpenAI embeddings for semantic search

🔐 **Security Features**
- JWT access and refresh tokens
- Supabase Row Level Security (RLS)
- Service role key for admin operations
- Strong password validation
- HTTP Bearer authentication

🏗️ **Architecture**
- Modular monolith design
- Clean separation of concerns
- Async/await for optimal performance
- Pydantic models for validation
- CORS support for frontend integration

## Project Structure

```
backend/
├── src/
│   ├── main.py                          # FastAPI application entry point
│   ├── core/
│   │   ├── config.py                    # Application settings & environment variables
│   │   └── db.py                        # Supabase client initialization (anon + admin)
│   └── modules/
│       ├── authentication/              # Auth & user management
│       │   ├── models.py                # Request/response models with user status
│       │   ├── service.py               # Sign up, sign in, profile management
│       │   ├── routes.py                # Auth API endpoints
│       │   ├── dependencies.py          # JWT authentication dependencies
│       │   └── utils.py                 # Password validation utilities
│       ├── sign_detection/              # Real-time sign language detection
│       │   ├── models.py                # Prediction models
│       │   ├── service.py               # ML model, deduplication, LLM cleaning
│       │   ├── routes.py                # WebSocket + text processing endpoints
│       │   └── dependencies.py          # Service dependency injection
│       ├── speech_to_text/              # Audio transcription
│       │   ├── models.py                # Audio conversion models
│       │   ├── service.py               # OpenAI Whisper integration
│       │   └── routes.py                # Audio upload endpoint
│       ├── chat/                        # Messaging & conversation history
│       │   ├── models.py                # Message & history models
│       │   ├── service.py               # Chat operations
│       │   └── routes.py                # Send message, get history endpoints
│       ├── general/                     # General utilities
│       │   ├── models.py                # User search models
│       │   ├── service.py               # User search logic
│       │   └── routes.py                # Search endpoints
│       └── chatbot/                     # AI chatbot (optional)
│           ├── agent.py                 # Conversational AI logic
│           ├── models.py                # Chat models
│           ├── service.py               # Chatbot service
│           └── routes.py                # Chatbot endpoints
├── documentations/
│   ├── profiles_table.sql               # User profiles database schema
│   ├── sign_detections_table.sql        # Chat conversation schema
│   ├── TESTING_GUIDE.md                 # Testing documentation
│   └── FRONTEND_SIGN_DETECTION_GUIDE.md # Frontend integration guide
├── tests/
│   └── test_full_workflow.py            # Integration tests
├── requirements.txt                      # Python dependencies
├── .env                                 # Environment variables
├── run.bat                              # Windows run script
├── push.bat                             # Windows git push script
└── README.md                            # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.12+ (tested with 3.12.6)
- Supabase account and project
- OpenAI API key (for LLM text cleaning and Whisper)
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
# Create .env file with the following variables
```

**Required Environment Variables:**

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Application Configuration
APP_NAME=Hackday FastAPI Backend
APP_VERSION=1.0.0
DEBUG=True

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Frontend URL
FRONTEND_URL=http://localhost:3000

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Sign Detection Configuration
SIGN_DETECTION_MAX_REPEATS=2  # Max times same sign appears consecutively
SIGN_DETECTION_COOLDOWN=2.0    # Seconds before sign can repeat
```

### 4. Supabase Setup

1. Create a Supabase project at https://supabase.com
2. Go to Project Settings > API
3. Copy your:
   - Project URL → `SUPABASE_URL`
   - anon/public key → `SUPABASE_KEY`
   - service_role key → `SUPABASE_SERVICE_ROLE_KEY`
4. Enable Email Auth in Authentication > Providers
5. Run database migrations:

**Create profiles table:**
```sql
-- See documentations/profiles_table.sql
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    status TEXT CHECK (status IN ('mute', 'deaf', 'blind', 'normal')) DEFAULT 'normal',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can view own profile" ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);
```

**Create chat_conversation table:**
```sql
-- See documentations/sign_detections_table.sql
CREATE TABLE chat_conversation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    receiver_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    raw_text TEXT,
    cleaned_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE chat_conversation ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can view own conversations" ON chat_conversation 
    FOR SELECT USING (auth.uid() = sender_id OR auth.uid() = receiver_id);
```

### 5. Run the Application

```bash
# Windows (using run.bat)
.\run.bat

# Or manually
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The ML model will automatically download on first startup (this may take a few minutes).

Access the API:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Base URL**: http://localhost:8000

## API Endpoints

### Base URL: `http://localhost:8000`

### 🔐 Authentication (`/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/signup` | Register new user with status | No |
| POST | `/auth/signin` | Sign in user (returns status) | No |
| POST | `/auth/signout` | Sign out user | Yes |
| POST | `/auth/forgot-password` | Request password reset | No |
| POST | `/auth/reset-password` | Reset password with token | No |
| POST | `/auth/change-password` | Change password | Yes |
| POST | `/auth/refresh` | Refresh access token | Yes |
| GET | `/auth/me` | Get current user info | Yes |

### 🎥 Sign Language Detection (`/sign-detection`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| WebSocket | `/sign-detection/ws/predict` | Real-time sign detection | No |
| POST | `/sign-detection/process-text` | Clean text with LLM & save | Yes (JWT) |

### 🎤 Speech-to-Text (`/speech-to-text`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/speech-to-text/convert` | Convert audio to text | No |

### 💬 Chat (`/chat`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/chat/send` | Send text message | No |
| POST | `/chat/history` | Get conversation history | No |

### 👥 General (`/general`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/general/search-user` | Search user by email | No |
| GET | `/general/search-user` | Search user by email (GET) | No |

### 🤖 Chatbot (`/chatbot`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/chatbot/chat` | Chat with AI assistant | No |

### 🏥 Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API welcome message |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI documentation |
| GET | `/redoc` | ReDoc documentation |

## API Usage Examples

### 1. Sign Up with Status

```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe",
    "status": "deaf"
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
    "status": "deaf",
    "email_verified": false,
    "created_at": "2026-01-08T...",
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

### 3. Send Text Message

```bash
curl -X POST "http://localhost:8000/chat/send" \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "sender-uuid",
    "receiver_id": "receiver-uuid",
    "message": "Hello, how are you?"
  }'
```

### 4. Get Conversation History

```bash
curl -X POST "http://localhost:8000/chat/history" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "current-user-uuid",
    "other_user_id": "other-user-uuid",
    "limit": 50,
    "offset": 0
  }'
```

**Response:**
```json
{
  "user_id": "other-user-uuid",
  "messages": [
    {
      "id": "msg-uuid",
      "sender_id": "sender-uuid",
      "receiver_id": "receiver-uuid",
      "raw_text": "hello",
      "cleaned_text": "Hello",
      "created_at": "2026-01-08T10:30:00"
    }
  ],
  "total_count": 45
}
```

### 5. Speech-to-Text Conversion

```bash
curl -X POST "http://localhost:8000/speech-to-text/convert" \
  -F "audio=@recording.mp3" \
  -F "sender_id=sender-uuid" \
  -F "receiver_id=receiver-uuid"
```

**Response:**
```json
{
  "id": "msg-uuid",
  "sender_id": "sender-uuid",
  "receiver_id": "receiver-uuid",
  "transcription": "Hello, this is a test message",
  "created_at": "2026-01-08T10:30:00"
}
```

### 6. Search User by Email

```bash
curl -X POST "http://localhost:8000/general/search-user" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

### 7. Real-time Sign Detection (WebSocket)

```javascript
// Frontend JavaScript example
const ws = new WebSocket("ws://localhost:8000/sign-detection/ws/predict");

ws.onopen = () => {
    // Send base64 encoded image
    ws.send(JSON.stringify({
        image: "base64_encoded_jpeg_string"
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Detected sign:", data.predicted_class);
    console.log("Is new:", data.is_new);
};
```

### 8. Process Detected Text

```bash
curl -X POST "http://localhost:8000/sign-detection/process-text" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "hellohowareyou",
    "receiver_id": "receiver-uuid"
  }'
```

**Response:**
```json
{
  "id": "msg-uuid",
  "sender_id": "sender-uuid",
  "receiver_id": "receiver-uuid",
  "raw_text": "hellohowareyou",
  "cleaned_text": "hello how are you",
  "created_at": "2026-01-08T10:30:00"
}
```

## User Status Types

The system supports four user accessibility statuses:

| Status | Description | Use Case |
|--------|-------------|----------|
| `deaf` | User cannot hear | Requires visual communication (sign language, text) |
| `mute` | User cannot speak | Can use sign language or typing |
| `blind` | User cannot see | Requires audio output (text-to-speech) |
| `normal` | No accessibility needs | Standard text/audio communication |

Status is set during signup and returned in authentication responses.

## Sign Detection Workflow

1. **Frontend**: User starts video recording
2. **WebSocket**: Frames sent to `/sign-detection/ws/predict` every 500ms
3. **Backend**: ML model detects signs in real-time
4. **Deduplication**: Same sign limited to 2 repeats, 2-second cooldown
5. **Frontend**: Accumulates detected words
6. **Stop Recording**: User stops video
7. **Process Text**: Call `/sign-detection/process-text`
8. **AI Cleaning**: GPT-4o-mini fixes "hellohowareyou" → "hello how are you"
9. **Database**: Message saved to `chat_conversation` table
10. **Display**: Cleaned message appears in chat

See `documentations/FRONTEND_SIGN_DETECTION_GUIDE.md` for complete integration guide.

## Speech-to-Text Workflow

1. **Frontend**: User records audio
2. **Upload**: Send audio file to `/speech-to-text/convert`
3. **Transcription**: OpenAI Whisper converts to text
4. **Database**: Message saved to `chat_conversation` table
5. **Response**: Transcribed text returned and displayed

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

## Dependencies

Key Python packages:

```
fastapi>=0.109.0          # Web framework
uvicorn[standard]>=0.27.0 # ASGI server
supabase>=2.3.4           # Database & auth
pydantic>=2.5.3           # Data validation
python-multipart>=0.0.6   # File uploads
transformers>=4.37.0      # Hugging Face ML models
torch>=2.1.2              # PyTorch for ML
pillow>=10.2.0            # Image processing
openai>=1.10.0            # OpenAI API (GPT, Whisper)
python-dotenv>=1.0.0      # Environment variables
```

For complete list, see `requirements.txt`.

## Machine Learning Models

### Sign Language Detection
- **Model**: `prithivMLmods/Alphabet-Sign-Language-Detection`
- **Framework**: Hugging Face Transformers
- **Input**: Base64 encoded JPEG images
- **Output**: Predicted sign class + confidence
- **First Run**: Model downloads automatically (~500MB)
- **Device**: CPU (configurable to GPU)

### Text Cleaning
- **Model**: OpenAI GPT-4o-mini
- **Purpose**: Fix concatenated text from sign detection
- **Example**: "hellohowareyou" → "hello how are you"

### Speech Recognition
- **Model**: OpenAI Whisper
- **Supported Formats**: mp3, mp4, mpeg, mpga, m4a, wav, webm
- **Max File Size**: 25MB

## Testing

### Run Integration Tests

```bash
# Install test dependencies
pip install opencv-python websockets requests

# Run full workflow test
python tests/test_full_workflow.py
```

### Manual Testing with Webcam

See `documentations/TESTING_GUIDE.md` for detailed testing instructions.

### Test WebSocket Connection

```bash
# Using Python websockets library
python -c "
import asyncio
import websockets
import json

async def test():
    uri = 'ws://localhost:8000/sign-detection/ws/predict'
    async with websockets.connect(uri) as ws:
        print('Connected!')

asyncio.run(test())
"
```

## Development Tips

### Interactive API Documentation

Visit http://localhost:8000/docs for Swagger UI - test all endpoints with built-in interface!

### Frontend Integration

- **WebSocket URL**: `ws://localhost:8000/sign-detection/ws/predict`
- **API Base URL**: `http://localhost:8000`
- **CORS**: Add your frontend URL to `CORS_ORIGINS` in `.env`

Complete React component example available in `documentations/FRONTEND_SIGN_DETECTION_GUIDE.md`.

### Database Management

Use Supabase Dashboard to:
- View `profiles` and `chat_conversation` tables
- Monitor authentication logs
- Test RLS policies
- Run SQL queries

### Model Warmup

The sign detection model loads on application startup. First request may be slow as the model initializes. Consider adding a warmup endpoint call in your deployment script.

### Performance Optimization

- **Frame Rate**: Adjust WebSocket frame interval (default: 500ms)
- **Image Quality**: Lower JPEG quality for faster processing
- **Caching**: Consider Redis for ML model predictions
- **Workers**: Use multiple Uvicorn workers in production

## Troubleshooting

### ML Model Not Loading
- Check internet connection (model downloads on first run)
- Verify disk space (~500MB required)
- Check logs for model loading errors
- Ensure `transformers` and `torch` are installed

### WebSocket Connection Failed
- Verify backend is running on port 8000
- Check firewall settings
- Ensure WebSocket URL uses `ws://` not `http://`
- Test with `tests/test_full_workflow.py`

### "Could not validate credentials"
- Check if JWT token is expired
- Verify Bearer token format: `Bearer <token>`
- Ensure token was obtained from `/auth/signin` or `/auth/signup`

### Sign Detection Not Working
- Ensure good lighting conditions
- Position hand clearly in front of camera
- Check that model loaded successfully (startup logs)
- Verify image is base64 encoded JPEG

### Audio Upload Failed
- Check file format (mp3, wav, etc.)
- Verify file size < 25MB
- Ensure OpenAI API key is valid
- Check `OPENAI_API_KEY` in `.env`

### Text Not Cleaning Properly
- Verify OpenAI API key has credits
- Check `OPENAI_MODEL=gpt-4o-mini` in `.env`
- Review backend logs for LLM errors

### Messages Not Saving
- Verify `sender_id` and `receiver_id` are valid UUIDs
- Check Supabase RLS policies
- Ensure service_role_key is correct for admin operations
- Review `chat_conversation` table structure

### CORS Errors
- Add frontend URL to `CORS_ORIGINS` in `.env`
- Restart server after changing `.env`
- Format: `["http://localhost:3000","http://localhost:5173"]`

## Production Deployment

### Environment Configuration

```env
DEBUG=False
CORS_ORIGINS=["https://your-frontend-domain.com"]
```

### Security Checklist

- [ ] Set `DEBUG=False`
- [ ] Use HTTPS for all endpoints
- [ ] Restrict CORS to production domain only
- [ ] Keep `.env` file secure (never commit)
- [ ] Rotate API keys regularly
- [ ] Enable Supabase RLS policies
- [ ] Use environment-specific service_role_key
- [ ] Implement rate limiting (Redis recommended)
- [ ] Monitor API usage and costs
- [ ] Set up error tracking (Sentry, etc.)

### Deployment Options

**Docker:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Cloud Platforms:**
- **Railway**: Connect GitHub repo, auto-deploys
- **Render**: Web service from Git
- **AWS EC2**: Full control, requires manual setup
- **Google Cloud Run**: Serverless container deployment
- **Heroku**: Easy deployment with Procfile

### Performance Tuning

```bash
# Multiple workers for production
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# With environment variable workers
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Monitoring

- Track OpenAI API usage (costs)
- Monitor Supabase database size
- Set up health check alerts
- Log ML model inference times
- Track WebSocket connection counts

## Documentation

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (Alternative API docs)
- **Frontend Guide**: `documentations/FRONTEND_SIGN_DETECTION_GUIDE.md`
- **Testing Guide**: `documentations/TESTING_GUIDE.md`
- **Database Schema**: `documentations/*.sql`

## Future Enhancements

### Planned Features
- [ ] Text-to-sign language conversion endpoint
- [ ] Video message storage and playback
- [ ] Group chat support
- [ ] Real-time notifications (WebSocket broadcast)
- [ ] Message read receipts
- [ ] Typing indicators
- [ ] Image/video file uploads
- [ ] Voice message recording UI
- [ ] Sign language dictionary API
- [ ] User preferences for accessibility
- [ ] Multi-language support
- [ ] Dark mode preference
- [ ] Message search functionality

### Technical Improvements
- [ ] Redis caching for ML predictions
- [ ] Rate limiting with Redis
- [ ] Horizontal scaling support
- [ ] Message queue for async processing
- [ ] CDN for static assets
- [ ] WebRTC for peer-to-peer video
- [ ] Automated testing suite
- [ ] Performance benchmarks
- [ ] API versioning
- [ ] GraphQL alternative endpoint

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Add docstrings to functions/classes
- Keep functions focused and small
- Write descriptive commit messages

## Tech Stack

- **Framework**: FastAPI 0.109+
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth (JWT)
- **ML Framework**: Hugging Face Transformers + PyTorch
- **AI Services**: OpenAI (GPT-4o-mini, Whisper)
- **Real-time**: WebSocket (FastAPI native)
- **Validation**: Pydantic v2
- **Server**: Uvicorn (ASGI)

## License

MIT License - feel free to use in your projects!

## Support

For issues or questions:
1. Check the documentation in `/documentations`
2. Review [FastAPI docs](https://fastapi.tiangolo.com/)
3. Check [Supabase docs](https://supabase.com/docs)
4. Review [OpenAI API docs](https://platform.openai.com/docs)
5. Open an issue in the repository

## Credits

- **Sign Language Model**: [prithivMLmods/Alphabet-Sign-Language-Detection](https://huggingface.co/prithivMLmods/Alphabet-Sign-Language-Detection)
- **AI Services**: OpenAI (GPT-4o-mini, Whisper)
- **Backend**: Supabase
- **Framework**: FastAPI

---

**Built for Hackday 2026** 🚀  
*Enabling accessible communication for everyone*
