# Testing Guide: Sign Detection Full Workflow

Complete guide to test the sign detection system from webcam to database.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install opencv-python websockets requests
```

### 2. Start Server

```bash
uvicorn src.main:app --reload
```

### 3. Run Complete Test

```bash
python tests/test_full_workflow.py
```

---

## 📋 Test Options

### Option A: Full Automated Test (Recommended)

**What it does:**
- Opens webcam
- Records for 10 seconds
- Detects signs in real-time
- Shows detections on screen
- Processes with LLM
- Saves to database

**Command:**
```bash
python tests/test_full_workflow.py
```

**Expected Output:**
```
[1/5] Checking server connection... ✅
[2/5] Opening webcam... ✅
[3/5] Starting sign detection...
📝 Detected: I (confidence: 92.5%)
📝 Detected: A (confidence: 88.3%)
📝 Detected: M (confidence: 91.2%)
[4/5] Processing text with LLM...
✅ Cleaned text: 'i am'

TEST SUMMARY
Raw Text:     IAM
Cleaned Text: i am
```

---

### Option B: Simple Webcam Test

**Command:**
```bash
python tests/test_webcam_sign_detection.py
```

**What it does:**
- Opens webcam
- Shows real-time predictions
- Press 'q' to quit

---

### Option C: Basic Connection Test

**Command:**
```bash
python tests/test_sign_detection.py
```

**What it does:**
- Tests WebSocket connection
- Sends test image
- No webcam needed

---

## 🎯 Manual Testing Steps

### Step 1: Start Server
```bash
uvicorn src.main:app --reload
```

Server should be running at `http://localhost:8000`

### Step 2: Test WebSocket Endpoint

Open browser console and run:
```javascript
const ws = new WebSocket('ws://localhost:8000/sign-detection/ws/predict');

ws.onopen = () => {
  console.log('Connected!');
  
  // Create test image
  const canvas = document.createElement('canvas');
  canvas.width = 224;
  canvas.height = 224;
  canvas.toBlob(blob => ws.send(blob));
};

ws.onmessage = (e) => {
  console.log('Response:', JSON.parse(e.data));
};
```

### Step 3: Test Process-Text Endpoint

```bash
curl -X POST http://localhost:8000/sign-detection/process-text \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "iaamhriidoy",
    "sender_id": "test-sender-123",
    "receiver_id": "test-receiver-456"
  }'
```

**Expected Response:**
```json
{
  "id": "uuid-here",
  "sender_id": "test-sender-123",
  "receiver_id": "test-receiver-456",
  "raw_text": "iaamhriidoy",
  "cleaned_text": "i am hridoy",
  "created_at": "2026-01-08T12:34:56.789Z"
}
```

### Step 4: Verify Database

Go to Supabase Dashboard → Table Editor → `chat_conversation`

You should see your test record.

---

## 🐛 Troubleshooting

### Issue: "Cannot open webcam"

**Solutions:**
- Check camera permissions
- Close other apps using webcam
- Try different camera: `cv2.VideoCapture(1)`

### Issue: "Connection refused"

**Solution:**
- Make sure server is running: `uvicorn src.main:app --reload`
- Check port is 8000

### Issue: "Model loading very slow"

**Normal behavior:**
- First run downloads ~400MB model
- Takes 1-2 minutes
- Subsequent runs are instant

### Issue: "No sign detected"

**Tips:**
- Ensure good lighting
- Hold sign steady for 1-2 seconds
- Try clearer hand gestures
- Increase confidence threshold in `.env`

### Issue: "Low confidence detections"

**Solutions:**
- Better lighting
- Clearer hand gestures
- Adjust `SIGN_DETECTION_CONFIDENCE_THRESHOLD` in `.env`

---

## 📊 Test Scenarios

### Scenario 1: Single Letter
1. Run test
2. Show sign "A" to camera
3. Hold for 2 seconds
4. Expect: "A" detected

### Scenario 2: Word Spelling
1. Run test
2. Spell "H-I" letter by letter
3. Expect: Raw "HI", Cleaned "hi"

### Scenario 3: Repeated Letters
1. Run test
2. Show "A" and hold for 5 seconds
3. Expect: Only 2 "A"s detected (deduplication working)

### Scenario 4: Full Name
1. Run test
2. Spell your name letter by letter
3. Expect: LLM cleans spacing

---

## ✅ Success Criteria

- [ ] Server starts without errors
- [ ] Webcam opens and shows video
- [ ] Signs are detected in real-time
- [ ] Predictions appear on screen
- [ ] Deduplication works (no spam)
- [ ] LLM cleans text properly
- [ ] Record saved to database
- [ ] Can query record from Supabase

---

## 📝 Performance Benchmarks

**Expected Performance:**
- Frame rate: 10-15 FPS
- Prediction latency: 200-500ms per frame
- WebSocket response: < 100ms
- LLM cleaning: 1-3 seconds
- Total workflow: 10-15 seconds

---

## 🎓 Next Steps

After successful testing:

1. **Integrate with Frontend:**
   - Use the working WebSocket endpoint
   - Implement start/stop recording
   - Show real-time predictions

2. **Add User Authentication:**
   - Pass real user IDs instead of test IDs
   - Integrate with your auth system

3. **Improve UI:**
   - Add visual feedback for detections
   - Show confidence scores
   - Display cleaned text

4. **Deploy:**
   - Test on production server
   - Configure environment variables
   - Set up monitoring
