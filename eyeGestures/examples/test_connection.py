"""
Test script to verify WebSocket server is working
"""
import asyncio
import websockets
import json

async def test_client():
    uri = "ws://localhost:8765"
    print(f"Testing connection to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✓ Connected successfully!")
            print("Receiving data for 10 seconds...\n")
            
            start_time = asyncio.get_event_loop().time()
            message_count = 0
            
            while asyncio.get_event_loop().time() - start_time < 10:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    message_count += 1
                    
                    if message_count % 10 == 0:  # Print every 10th message
                        print(f"Message #{message_count}: x={data.get('x')}, y={data.get('y')}, fixation={data.get('fixation'):.2f}")
                        if data.get('calibrating'):
                            print(f"  → Calibrating: {data.get('calibration_progress')}/25")
                    
                except asyncio.TimeoutError:
                    print("No data received in 1 second...")
            
            print(f"\n✓ Test completed! Received {message_count} messages")
            
    except ConnectionRefusedError:
        print("✗ Connection refused. Is the server running?")
        print("\nTo start the server, run:")
        print("  python minigames_server.py")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("="*60)
    print("EyeGestures WebSocket Connection Test")
    print("="*60)
    print()
    asyncio.run(test_client())
