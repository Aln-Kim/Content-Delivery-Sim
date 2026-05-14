from fastapi import FastAPI, Header
import httpx

app = FastAPI()

# Map simulated IP prefixes defined in docker-compose
REGION_MAP = {
    "1.0.0.": "edge-us-east",
    "2.0.0.": "edge-europe"
}

@app.get("/proxy/{item_id}")
async def route_request(item_id: str, x_client_ip: str = Header(None)):
    # Default US-East
    target_node = "edge-us-east"
    
    if x_client_ip:
        for prefix, node in REGION_MAP.items():
            if x_client_ip.startswith(prefix):
                target_node = node
                break

    async with httpx.AsyncClient() as client:
        url = f"http://{target_node}:8000/content/{item_id}"
        try:
            resp = await client.get(url)
            return resp.json()
        except Exception:
            # If the primary fails, try the other one
            fallback = "edge-us-east" if target_node == "edge-europe" else "edge-europe"
            resp = await client.get(f"http://{fallback}:8000/content/{item_id}")
            return {"alert": "Failover Active", "payload": resp.json()}