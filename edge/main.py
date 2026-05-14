from fastapi import FastAPI, HTTPException
import httpx
import os
import time

app = FastAPI()

# System Variables
REGION = os.getenv("REGION", "Default-Edge")
ORIGIN_URL = os.getenv("ORIGIN_URL", "http://cdn-origin:8000")

# The Caching Layer 
CACHE = {}

@app.get("/content/{item_id}")
async def get_content(item_id: str):
    start_time = time.time()
    
    # Check if the item is in the cache (CACHE HIT)
    if item_id in CACHE:
        return {
            "region": REGION,
            "status": "HIT",
            "latency_ms": round((time.time() - start_time) * 1000, 4),
            "data": CACHE[item_id],
            "note": "Served instantly from local Edge memory."
        }

    # Not in cache (CACHE MISS) -> Go to Origin
    async with httpx.AsyncClient() as client:
        try:
            # The 'Connect Error' was fixed by using the service name 'cdn-origin'
            response = await client.get(f"{ORIGIN_URL}/data/{item_id}", timeout=5.0)
            
            if response.status_code == 200:
                data = response.json()
                
                # Update cache for next user
                CACHE[item_id] = data 
                
                return {
                    "region": REGION,
                    "status": "MISS",
                    "latency_ms": round((time.time() - start_time) * 1000, 4),
                    "data": data,
                    "note": "Fetched from Origin and saved to local cache."
                }
            else:
                raise HTTPException(status_code=404, detail="Item not found at Origin")
                
        except httpx.RequestError:
            # Router's failover logic
            raise HTTPException(status_code=504, detail="Origin Server Unreachable")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "region": REGION}