from fastapi import FastAPI
import asyncio # Need this for the sleep!
import os

app = FastAPI()

# --- SYSTEM VARIABLE ---
PROCESSING_DELAY = float(os.getenv("PROCESSING_DELAY", 0.5)) # 0.5 seconds default

DATABASE = {
    "item1": {"title": "Welcome to the CDN", "content": "This is data from the origin server."},
    "item2": {"title": "Performance Specs", "content": "Origin latency is now simulated."},
}

@app.get("/data/{item_id}")
async def get_raw_data(item_id: str):
    await asyncio.sleep(PROCESSING_DELAY) 
    
    return DATABASE.get(item_id, {"error": "Not Found"})