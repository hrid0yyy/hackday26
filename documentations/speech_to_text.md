# Speech to Text Module

Converts audio/voice to text using OpenAI Whisper API and saves to database.

---

## 📡 API Endpoint

**POST** `/speech-to-text/convert`

Converts audio to text and saves as a conversation message.

### Request

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: multipart/form-data
```

**Form Data:**
- `audio` (file): Audio file (wav, mp3, m4a, webm, etc.)
- `receiver_id` (string): ID of user receiving the message

**Note:** `sender_id` is automatically extracted from JWT token.

### Response

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440222",
  "sender_id": "550e8400-e29b-41d4-a716-446655440000",
  "receiver_id": "660e8400-e29b-41d4-a716-446655440111",
  "transcribed_text": "Hello, how are you today?",
  "created_at": "2026-01-08T12:34:56.789Z"
}
```

---

## 🎯 Frontend Usage

### HTML Form Example

```html
<form id="audioForm">
  <input type="file" id="audioFile" accept="audio/*" required>
  <input type="hidden" id="receiverId" value="user-uuid">
  <button type="submit">Send Voice Message</button>
</form>

<script>
document.getElementById('audioForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const formData = new FormData();
  formData.append('audio', document.getElementById('audioFile').files[0]);
  formData.append('receiver_id', document.getElementById('receiverId').value);
  
  const response = await fetch('/speech-to-text/convert', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    },
    body: formData
  });
  
  const result = await response.json();
  console.log('Transcribed:', result.transcribed_text);
});
</script>
```

### JavaScript Fetch Example

```javascript
async function sendVoiceMessage(audioBlob, receiverId, accessToken) {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.wav');
  formData.append('receiver_id', receiverId);
  
  const response = await fetch('/speech-to-text/convert', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    },
    body: formData
  });
  
  const result = await response.json();
  return result.transcribed_text;
}
```

### Recording Audio from Microphone

```javascript
let mediaRecorder;
let audioChunks = [];

// Start recording
async function startRecording() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  
  mediaRecorder.ondataavailable = (event) => {
    audioChunks.push(event.data);
  };
  
  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    audioChunks = [];
    
    // Send to API
    const text = await sendVoiceMessage(audioBlob, receiverId, accessToken);
    console.log('Transcribed:', text);
  };
  
  mediaRecorder.start();
}

// Stop recording
function stopRecording() {
  mediaRecorder.stop();
}
```

---

## 🎤 Supported Audio Formats

- WAV (`.wav`)
- MP3 (`.mp3`)
- M4A (`.m4a`)
- MP4 (`.mp4`)
- MPEG (`.mpeg`, `.mpga`)
- WebM (`.webm`)

---

## 💾 Database Storage

Messages are stored in the `chat_conversation` table:

```sql
INSERT INTO chat_conversation (
  id,
  sender_id,
  receiver_id,
  raw_text,
  cleaned_text,
  created_at
) VALUES (
  'uuid',
  'sender-uuid',
  'receiver-uuid',
  'Hello, how are you today?',  -- Transcribed text
  'Hello, how are you today?',  -- Same as raw (no cleaning needed)
  NOW()
);
```

---

## 🔒 Security

- ✅ Requires JWT authentication
- ✅ Sender ID extracted from token (can't be spoofed)
- ✅ File size limits enforced by FastAPI
- ✅ Audio format validation

---

## 🐛 Error Handling

### Invalid File Type
```json
{
  "detail": "Invalid file type. Please upload an audio file."
}
```

### Transcription Failed
```json
{
  "detail": "Failed to transcribe audio: [error details]"
}
```

### Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

---

## 🧪 Testing

### Test with cURL

```bash
curl -X POST http://localhost:8000/speech-to-text/convert \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "audio=@recording.wav" \
  -F "receiver_id=660e8400-e29b-41d4-a716-446655440111"
```

### Test in Swagger UI

1. Go to `http://localhost:8000/docs`
2. Find `/speech-to-text/convert`
3. Click "Try it out"
4. Upload audio file
5. Enter receiver_id
6. Click "Execute"

---

## ⚙️ Configuration

Uses OpenAI Whisper API (configured in `.env`):

```env
OPENAI_API_KEY=your-openai-api-key
```

No additional configuration needed - Whisper is included with OpenAI API!

---

## 🔄 Workflow

```
User records audio
    ↓
Upload to /speech-to-text/convert
    ↓
OpenAI Whisper API transcribes
    ↓
Save to chat_conversation table
    ↓
Return transcribed text
    ↓
Display in chat
```

---

## 📊 Performance

- **Transcription time:** 1-3 seconds for 30-second audio
- **Supported languages:** 50+ languages auto-detected
- **Max audio length:** ~25MB file size limit
- **Accuracy:** 95%+ for clear audio

---

## 💡 Use Cases

1. **Voice messaging:** Send voice instead of text
2. **Accessibility:** Convert speech to text for deaf users
3. **Multilingual:** Auto-detect and transcribe any language
4. **Transcription:** Convert recorded audio to text
