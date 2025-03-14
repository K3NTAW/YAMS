import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)

async def handle_client(websocket):
    try:
        # Wait for authentication
        auth_message = await websocket.recv()
        auth_data = json.loads(auth_message)
        
        if auth_data["type"] == "auth":
            client_id = auth_data["client_id"]
            logging.info(f"Client authenticated: {client_id}")
            
            # Send authentication success
            await websocket.send(json.dumps({
                "status": "success",
                "message": "Authentication successful"
            }))
            
            # Keep connection alive and handle messages
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    logging.info(f"Received message from {client_id}: {data}")
                    
                    # Echo back the message
                    await websocket.send(json.dumps({
                        "status": "success",
                        "message": "Message received",
                        "data": data
                    }))
                except websockets.exceptions.ConnectionClosed:
                    logging.info(f"Client disconnected: {client_id}")
                    break
                
    except Exception as e:
        logging.error(f"Error handling client: {e}")

async def main():
    async with websockets.serve(handle_client, "localhost", 8765):
        logging.info("Test server running on ws://localhost:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
