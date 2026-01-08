# Sign Detection Tests

Test utilities for the Sign Detection module.

## Installation

Install test dependencies:

```bash
pip install -r tests/requirements-test.txt
```

## Tests

### 1. Basic Connection Test

Tests the WebSocket endpoint with a simple test image:

```bash
python tests/test_sign_detection.py
```

**What it does:**
- Creates a blank test image
- Connects to WebSocket endpoint
- Sends image and receives prediction
- Verifies the endpoint is working

### 2. Webcam Real-Time Test

Tests with real webcam input (requires camera):

```bash
python tests/test_webcam_sign_detection.py
```

**What it does:**
- Opens your webcam
- Captures frames in real-time
- Sends to sign detection API
- Displays predictions on screen
- Press 'q' to quit

**Requirements:**
- Working webcam
- `opencv-python` installed

## Prerequisites

Make sure your FastAPI server is running:

```bash
uvicorn src.main:app --reload
```

The server should be available at `http://localhost:8000`

## Expected Output

### Successful Test:
```
Connecting to ws://localhost:8000/sign-detection/ws/predict...
✅ Connected successfully!

📤 Sending test image (3456 bytes)...
📥 Received response:
{
  "sign": "A",
  "confidence": 0.8532
}

✅ Prediction: A (confidence: 0.8532)
```

### Low Confidence:
```
📥 Received response:
{
  "sign": null,
  "confidence": 0.0,
  "message": "No confident detection"
}

⚠️ No confident detection (low confidence)
```

## Troubleshooting

### Connection Refused
- Ensure the server is running: `uvicorn src.main:app --reload`
- Check the server is on port 8000

### Webcam Not Opening
- Check camera permissions
- Ensure no other app is using the webcam
- Try a different camera index: `cv2.VideoCapture(1)`

### Import Errors
- Install test dependencies: `pip install -r tests/requirements-test.txt`
