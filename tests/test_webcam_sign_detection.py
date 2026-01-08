"""
Real-world example: Capture webcam frames and send to Sign Detection API.

This shows how a frontend (or Python client) would capture real images.
"""

import asyncio
import json
import cv2
import websockets


async def webcam_sign_detection():
    """Capture webcam frames and send to sign detection endpoint."""
    
    # Connect to WebSocket
    uri = "ws://localhost:8000/sign-detection/ws/predict"
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Cannot open webcam")
        return
    
    print("📹 Webcam opened. Press 'q' to quit.")
    
    async with websockets.connect(uri) as websocket:
        print("✅ Connected to server")
        
        while True:
            # Capture frame from webcam
            ret, frame = cap.read()
            
            if not ret:
                print("❌ Failed to capture frame")
                break
            
            # Display the frame
            cv2.imshow('Sign Language Detection', frame)
            
            # Convert frame to JPEG bytes
            _, buffer = cv2.imencode('.jpg', frame)
            image_bytes = buffer.tobytes()
            
            # Send to server
            await websocket.send(image_bytes)
            
            # Receive prediction
            response = await websocket.recv()
            result = json.loads(response)
            
            # Display prediction
            if result.get("sign"):
                sign = result["sign"]
                confidence = result["confidence"]
                print(f"🖐️ Detected: {sign} ({confidence:.2%} confidence)")
                
                # Overlay text on frame
                cv2.putText(
                    frame,
                    f"Sign: {sign} ({confidence:.2%})",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
            
            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        asyncio.run(webcam_sign_detection())
    except KeyboardInterrupt:
        print("\n👋 Stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
