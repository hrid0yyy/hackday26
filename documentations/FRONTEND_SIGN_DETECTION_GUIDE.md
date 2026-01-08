# Frontend Implementation Guide: Sign Language Video Detection

## Overview
Implement real-time sign language detection with video recording. When users press the video icon, start webcam capture and detect signs in real-time. When they press stop, process and save the accumulated text.

---

## Backend API Endpoints

```
WebSocket: ws://localhost:8000/sign-detection/ws/predict
POST: http://localhost:8000/sign-detection/process-text
POST: http://localhost:8000/chat/send
POST: http://localhost:8000/chat/history
```

---

## Complete React Component

```tsx
import React, { useRef, useState, useEffect } from 'react';

interface SignLanguageRecorderProps {
    senderId: string;
    receiverId: string;
    onMessageSent?: (message: any) => void;
}

const SignLanguageRecorder: React.FC<SignLanguageRecorderProps> = ({
    senderId,
    receiverId,
    onMessageSent
}) => {
    const [isRecording, setIsRecording] = useState(false);
    const [detectedWords, setDetectedWords] = useState<string[]>([]);
    const [currentWord, setCurrentWord] = useState("");
    const [isProcessing, setIsProcessing] = useState(false);

    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const intervalRef = useRef<NodeJS.Timeout | null>(null);
    const streamRef = useRef<MediaStream | null>(null);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stopRecording();
        };
    }, []);

    const startRecording = async () => {
        try {
            // 1. Request camera access
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: "user"
                },
                audio: false
            });

            streamRef.current = stream;

            // 2. Attach stream to video element
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                await videoRef.current.play();
            }

            // 3. Connect WebSocket
            connectWebSocket();

            // 4. Start capturing frames every 500ms
            intervalRef.current = setInterval(() => {
                captureAndSendFrame();
            }, 500);

            setIsRecording(true);
            setDetectedWords([]);
            setCurrentWord("");

        } catch (error) {
            console.error("Failed to start recording:", error);
            alert("Could not access camera. Please grant camera permissions.");
        }
    };

    const connectWebSocket = () => {
        const ws = new WebSocket("ws://localhost:8000/sign-detection/ws/predict");

        ws.onopen = () => {
            console.log("WebSocket connected for sign detection");
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                if (data.predicted_class && data.is_new) {
                    // New word detected
                    const word = data.predicted_class.toLowerCase();
                    setCurrentWord(word);
                    setDetectedWords(prev => [...prev, word]);
                    console.log("Detected:", word);
                }
            } catch (error) {
                console.error("Error parsing WebSocket message:", error);
            }
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        ws.onclose = () => {
            console.log("WebSocket closed");
        };

        wsRef.current = ws;
    };

    const captureAndSendFrame = () => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            return;
        }

        if (!videoRef.current || !canvasRef.current) {
            return;
        }

        const video = videoRef.current;
        const canvas = canvasRef.current;
        const context = canvas.getContext('2d');

        if (!context || video.videoWidth === 0) {
            return;
        }

        // Set canvas dimensions to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Draw current video frame to canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert to base64 JPEG
        const base64Image = canvas.toDataURL('image/jpeg', 0.8).split(',')[1];

        // Send to WebSocket
        wsRef.current.send(JSON.stringify({
            image: base64Image
        }));
    };

    const stopRecording = async () => {
        // 1. Stop frame capture
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
        }

        // 2. Close WebSocket
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }

        // 3. Stop video stream
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }

        // 4. Clear video element
        if (videoRef.current) {
            videoRef.current.srcObject = null;
        }

        setIsRecording(false);

        // 5. Process accumulated text if any
        if (detectedWords.length > 0) {
            await processAndSendMessage();
        }
    };

    const processAndSendMessage = async () => {
        setIsProcessing(true);

        try {
            // Join all detected words
            const rawText = detectedWords.join("");
            
            console.log("Processing text:", rawText);

            // Call process-text API to clean with LLM and save to DB
            const response = await fetch("http://localhost:8000/sign-detection/process-text", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    // If you're using JWT authentication, include it:
                    // "Authorization": `Bearer ${yourJwtToken}`
                },
                body: JSON.stringify({
                    text: rawText,
                    receiver_id: receiverId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            console.log("Message saved:", result);
            
            // Notify parent component
            if (onMessageSent) {
                onMessageSent(result);
            }

            // Clear detected words
            setDetectedWords([]);
            setCurrentWord("");

        } catch (error) {
            console.error("Failed to process and send message:", error);
            alert("Failed to send message. Please try again.");
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div style={{ width: '100%', maxWidth: '640px', margin: '0 auto' }}>
            {/* Video Preview */}
            <div style={{ position: 'relative', backgroundColor: '#000', borderRadius: '8px', overflow: 'hidden' }}>
                <video
                    ref={videoRef}
                    style={{
                        width: '100%',
                        display: isRecording ? 'block' : 'none',
                        transform: 'scaleX(-1)' // Mirror video
                    }}
                    autoPlay
                    playsInline
                    muted
                />
                
                {!isRecording && (
                    <div style={{
                        width: '100%',
                        height: '300px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backgroundColor: '#1a1a1a',
                        color: '#666'
                    }}>
                        <p>Camera Off</p>
                    </div>
                )}

                {/* Recording Indicator */}
                {isRecording && (
                    <div style={{
                        position: 'absolute',
                        top: '10px',
                        right: '10px',
                        backgroundColor: 'red',
                        color: 'white',
                        padding: '5px 10px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 'bold'
                    }}>
                        ● REC
                    </div>
                )}
            </div>

            {/* Hidden Canvas for frame capture */}
            <canvas ref={canvasRef} style={{ display: 'none' }} />

            {/* Controls */}
            <div style={{ marginTop: '16px', display: 'flex', gap: '12px', alignItems: 'center', justifyContent: 'center' }}>
                {!isRecording ? (
                    <button
                        onClick={startRecording}
                        disabled={isProcessing}
                        style={{
                            padding: '12px 24px',
                            fontSize: '16px',
                            backgroundColor: '#007bff',
                            color: 'white',
                            border: 'none',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        }}
                    >
                        🎥 Start Sign Detection
                    </button>
                ) : (
                    <button
                        onClick={stopRecording}
                        style={{
                            padding: '12px 24px',
                            fontSize: '16px',
                            backgroundColor: '#dc3545',
                            color: 'white',
                            border: 'none',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        }}
                    >
                        ⏹️ Stop & Send
                    </button>
                )}
            </div>

            {/* Current Detection Display */}
            {isRecording && (
                <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                    <p style={{ margin: '0 0 8px 0', fontSize: '12px', color: '#666', fontWeight: 'bold' }}>
                        Detected Signs:
                    </p>
                    <p style={{ margin: 0, fontSize: '18px', fontWeight: 'bold', color: '#333', minHeight: '27px' }}>
                        {detectedWords.join(" ") || "Waiting for signs..."}
                    </p>
                    {currentWord && (
                        <p style={{ margin: '8px 0 0 0', fontSize: '14px', color: '#007bff' }}>
                            Latest: {currentWord}
                        </p>
                    )}
                </div>
            )}

            {/* Processing Indicator */}
            {isProcessing && (
                <div style={{ marginTop: '16px', textAlign: 'center', color: '#007bff' }}>
                    <p>Processing and sending message...</p>
                </div>
            )}
        </div>
    );
};

export default SignLanguageRecorder;
```

---

## Usage in Your Chat Component

```tsx
import SignLanguageRecorder from './SignLanguageRecorder';

const ChatPage = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const CURRENT_USER_ID = "your-user-id";
    const activeUserId = "receiver-user-id";

    const handleMessageSent = (message: any) => {
        // Add the new message to your chat
        const newMessage: Message = {
            id: message.id,
            senderId: message.sender_id,
            senderName: 'You',
            content: message.cleaned_text, // Use cleaned text
            timestamp: new Date(message.created_at),
            status: 'sent',
            type: 'text'
        };
        setMessages(prev => [...prev, newMessage]);
    };

    return (
        <div>
            {/* Your existing chat UI */}
            
            {/* Add Sign Language Recorder */}
            <SignLanguageRecorder
                senderId={CURRENT_USER_ID}
                receiverId={activeUserId}
                onMessageSent={handleMessageSent}
            />
        </div>
    );
};
```

---

## How It Works

### 1. Start Recording
- User clicks "🎥 Start Sign Detection"
- Request camera permissions
- Connect to WebSocket: `ws://localhost:8000/sign-detection/ws/predict`
- Start capturing frames every 500ms
- Send base64 encoded frames to backend

### 2. Real-time Detection
- Backend processes each frame with ML model
- Returns predictions: `{predicted_class: "hello", is_new: true}`
- Only show new detections (backend handles deduplication)
- Display detected words in real-time

### 3. Stop & Send
- User clicks "⏹️ Stop & Send"
- Stop frame capture and WebSocket
- Join all detected words: `["hello", "how", "are", "you"]` → `"hellohowareyou"`
- Call `POST /sign-detection/process-text` with raw text
- Backend cleans text with GPT-4o-mini: `"hellohowareyou"` → `"hello how are you"`
- Backend saves to `chat_conversation` table
- Message appears in chat

---

## Key Features

✅ **Real-time Detection**: Shows detected signs as they appear  
✅ **Visual Feedback**: Recording indicator, detected words display  
✅ **Automatic Cleanup**: LLM cleans text ("hellohowareyou" → "hello how are you")  
✅ **Database Storage**: Automatically saves to `chat_conversation` table  
✅ **Error Handling**: Camera permissions, WebSocket errors  
✅ **Mirrored Video**: Self-view like a mirror  
✅ **Processing State**: Shows when cleaning/saving message  
✅ **Deduplication**: Backend prevents spam (max 2 repeats, 2s cooldown)

---

## API Reference

### WebSocket: `/sign-detection/ws/predict`

**Send:**
```json
{
    "image": "base64_encoded_jpeg_string"
}
```

**Receive:**
```json
{
    "predicted_class": "hello",
    "confidence": 0.95,
    "is_new": true
}
```

### POST: `/sign-detection/process-text`

**Request:**
```json
{
    "text": "hellohowareyou",
    "receiver_id": "user-uuid"
}
```

**Response:**
```json
{
    "id": "msg-uuid",
    "sender_id": "user-uuid",
    "receiver_id": "user-uuid",
    "raw_text": "hellohowareyou",
    "cleaned_text": "hello how are you",
    "created_at": "2026-01-08T10:30:00"
}
```

### POST: `/chat/send`

**Request:**
```json
{
    "sender_id": "user-uuid",
    "receiver_id": "user-uuid",
    "message": "Hello!"
}
```

**Response:**
```json
{
    "id": "msg-uuid",
    "sender_id": "user-uuid",
    "receiver_id": "user-uuid",
    "raw_text": "Hello!",
    "cleaned_text": "Hello!",
    "created_at": "2026-01-08T10:30:00"
}
```

### POST: `/chat/history`

**Request:**
```json
{
    "user_id": "current-user-uuid",
    "other_user_id": "other-user-uuid",
    "limit": 50,
    "offset": 0
}
```

**Response:**
```json
{
    "user_id": "other-user-uuid",
    "messages": [
        {
            "id": "msg-uuid",
            "sender_id": "user-uuid",
            "receiver_id": "user-uuid",
            "raw_text": "hellohowareyou",
            "cleaned_text": "hello how are you",
            "created_at": "2026-01-08T10:30:00"
        }
    ],
    "total_count": 45
}
```

---

## Testing Checklist

1. ✅ Click "Start" - camera should activate
2. ✅ Show hand signs - words should appear below video
3. ✅ Multiple same signs - only shows max 2 times
4. ✅ Wait 2 seconds - same sign can be detected again
5. ✅ Click "Stop" - processing indicator shows
6. ✅ Message appears in chat with cleaned text
7. ✅ Call `/chat/history` - message is in database
8. ✅ Refresh page - message persists

---

## Environment Requirements

```bash
# Backend must be running on:
http://localhost:8000

# WebSocket endpoint:
ws://localhost:8000/sign-detection/ws/predict

# Required permissions:
- Camera access (getUserMedia API)

# Browser support:
- Chrome/Edge: ✅
- Firefox: ✅
- Safari: ✅
- Mobile browsers: ✅ (use facingMode: "user" for front camera)
```

---

## Configuration

### Backend (.env)
```env
SIGN_DETECTION_MAX_REPEATS=2  # Output same sign max 2 times
SIGN_DETECTION_COOLDOWN=2.0   # Reset after 2 seconds
OPENAI_API_KEY=your-key        # For text cleaning
OPENAI_MODEL=gpt-4o-mini       # LLM model
```

### Frontend
```typescript
// Frame capture interval (milliseconds)
const FRAME_INTERVAL = 500; // Capture every 500ms

// WebSocket URL
const WS_URL = "ws://localhost:8000/sign-detection/ws/predict";

// API Base URL
const API_BASE_URL = "http://localhost:8000";
```

---

## Troubleshooting

### Camera Not Working
- Check browser permissions
- Ensure HTTPS or localhost (getUserMedia requires secure context)
- Try different browsers

### WebSocket Not Connecting
- Check backend is running: `http://localhost:8000/docs`
- Check WebSocket endpoint in browser console
- Verify no firewall blocking WebSocket connections

### No Detections Appearing
- Ensure good lighting
- Position hand clearly in front of camera
- Check backend logs for ML model errors
- Verify ML model loaded (check startup logs)

### Slow Performance
- Increase frame interval: `setInterval(() => ..., 1000)` // 1 second
- Reduce video quality: `width: { ideal: 320 }, height: { ideal: 240 }`
- Check CPU usage on backend

### Message Not Saving
- Check `/chat/history` to verify message saved
- Verify `sender_id` and `receiver_id` are valid UUIDs
- Check backend logs for database errors
- Ensure Supabase connection is working

---

## Production Considerations

### Security
- Add JWT authentication to WebSocket connection
- Validate user IDs on backend
- Rate limit WebSocket connections
- Sanitize text before LLM processing

### Performance
- Use Redis for caching ML model predictions
- Implement WebSocket connection pooling
- Optimize image compression (lower quality for mobile)
- Add frame skip logic if backend is slow

### UX Improvements
- Add countdown before recording starts
- Show confidence scores for detections
- Add manual edit before sending
- Support continuous detection mode (no stop button)
- Add haptic feedback on mobile when sign detected
- Show list of supported signs

### Monitoring
- Track WebSocket connection health
- Log detection accuracy
- Monitor LLM API costs
- Alert on high error rates

---

That's it! Copy this code and integrate into your frontend. The backend is already fully configured and ready to use.
