"""
Complete integration test for Sign Detection workflow.

This script tests:
1. WebSocket connection
2. Real-time webcam sign detection
3. Text accumulation
4. LLM cleaning
5. Database storage

Requirements:
- pip install opencv-python websockets requests pillow
"""

import asyncio
import json
import time
import requests
import cv2
import websockets
from typing import Optional


class SignDetectionTester:
    """Complete test suite for sign detection."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = f"ws://localhost:8000/sign-detection/ws/predict"
        self.accumulated_text = ""
        self.is_recording = False
        
    async def test_full_workflow(
        self,
        receiver_id: str = "test-receiver-456",
        access_token: str = None
    ):
        """Test the complete sign detection workflow."""
        
        print("=" * 60)
        print("SIGN DETECTION - FULL WORKFLOW TEST")
        print("=" * 60)
        
        if not access_token:
            print("\n⚠️ WARNING: No access token provided")
            print("For authenticated testing, pass access_token parameter")
            print("Continuing with mock sender_id for testing...\n")
        
        # Step 1: Check server health
        print("\n[1/5] Checking server connection...")
        if not self.check_server():
            print("❌ Server not running. Start with: uvicorn src.main:app --reload")
            return
        print("✅ Server is running")
        
        # Step 2: Open webcam
        print("\n[2/5] Opening webcam...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Cannot open webcam")
            return
        print("✅ Webcam opened")
        
        # Step 3: Start WebSocket and record
        print("\n[3/5] Starting sign detection (recording for 10 seconds)...")
        print("👉 Show sign language gestures to your webcam!")
        print("Press 'q' to stop early\n")
        
        try:
            async with websockets.connect(self.ws_url) as websocket:
                print("✅ WebSocket connected")
                self.is_recording = True
                start_time = time.time()
                frame_count = 0
                
                while self.is_recording:
                    # Capture frame
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Display frame
                    cv2.putText(
                        frame,
                        f"Recording... {self.accumulated_text}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )
                    cv2.putText(
                        frame,
                        "Press 'q' to stop",
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        1
                    )
                    cv2.imshow('Sign Detection Test', frame)
                    
                    # Send frame to server (every 3rd frame to reduce load)
                    if frame_count % 3 == 0:
                        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                        image_bytes = buffer.tobytes()
                        
                        await websocket.send(image_bytes)
                        
                        # Receive prediction
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                            result = json.loads(response)
                            
                            if result.get("sign") and result.get("is_new"):
                                sign = result["sign"]
                                confidence = result["confidence"]
                                self.accumulated_text += sign
                                print(f"📝 Detected: {sign} (confidence: {confidence:.2%})")
                        except asyncio.TimeoutError:
                            pass
                    
                    frame_count += 1
                    
                    # Stop after 10 seconds or if 'q' pressed
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self.is_recording = False
                    if time.time() - start_time > 10:
                        self.is_recording = False
                
                print(f"\n✅ Recording stopped")
                print(f"📊 Processed {frame_count} frames")
                print(f"📝 Raw text: '{self.accumulated_text}'")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
        
        # Step 4: Process text with LLM
        if not self.accumulated_text:
            print("\n⚠️ No text detected. Try again with clearer signs.")
            return
        
        print(f"\n[4/5] Processing text with LLM...")
        cleaned_text = await self.process_text(
            self.accumulated_text,
            receiver_id,
            access_token
        )
        
        if cleaned_text:
            print(f"✅ Cleaned text: '{cleaned_text}'")
        
        # Step 5: Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Raw Text:     {self.accumulated_text}")
        print(f"Cleaned Text: {cleaned_text}")
        print(f"Receiver ID:  {receiver_id}")
        print(f"Note: sender_id automatically extracted from JWT token")
        print("\n✅ Full workflow test completed!")
        print("=" * 60)
    
    def check_server(self) -> bool:
        """Check if server is running."""
        try:
            response = requests.get(f"{self.base_url}/")
            return response.status_code == 200
        except:
            return False
    
    async def process_text(
        self,
        raw_text: str,
        receiver_id: str,
        access_token: str = None
    ) -> Optional[str]:
        """Process and save detected text."""
        try:
            headers = {'Content-Type': 'application/json'}
            if access_token:
                headers['Authorization'] = f'Bearer {access_token}'
            
            response = requests.post(
                f"{self.base_url}/sign-detection/process-text",
                json={
                    "raw_text": raw_text,
                    "receiver_id": receiver_id
                },
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("cleaned_text")
            else:
                print(f"❌ Error: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Failed to process text: {e}")
            return None


async def main():
    print("\nNote: sender_id will be extracted from JWT token")
    receiver_id = input("Enter receiver ID (or press Enter for default): ").strip() or "test-receiver-456"
    access_token = input("Enter JWT access token (optional, press Enter to skip): ").strip() or None
    
    await tester.test_full_workflow(receiver_id, access_token
    sender_id = input("Enter sender ID (or press Enter for default): ").strip() or "test-sender-123"
    receiver_id = input("Enter receiver ID (or press Enter for default): ").strip() or "test-receiver-456"
    
    await tester.test_full_workflow(sender_id, receiver_id)


if __name__ == "__main__":
    print("\n🚀 Sign Detection Integration Test")
    print("=" * 60)
    print("This will:")
    print("1. Connect to your webcam")
    print("2. Detect sign language gestures")
    print("3. Process the text with LLM")
    print("4. Save to database")
    print("\nMake sure the server is running!")
    print("=" * 60)
    input("\nPress Enter to start...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
