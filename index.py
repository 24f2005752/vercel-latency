import json
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from statistics import mean

app = FastAPI()

# Enable CORS manually
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.post("/")
async def analytics(request: Request):
    body = await request.json()
    regions = body["regions"]
    threshold = body["threshold_ms"]

    # Load telemetry file
    with open("q-vercel-latency.json") as f:
        data = json.load(f)

    result = {}

    for region in regions:
        region_data = [d for d in data if d["region"] == region]

        if not region_data:
            continue

        latencies = [d["latency_ms"] for d in region_data]
        uptimes = [d["uptime"] for d in region_data]

        latencies_sorted = sorted(latencies)
        p95_index = int(0.95 * len(latencies_sorted)) - 1

        result[region] = {
            "avg_latency": mean(latencies),
            "p95_latency": latencies_sorted[p95_index],
            "avg_uptime": mean(uptimes),
            "breaches": sum(1 for l in latencies if l > threshold)
        }

    return JSONResponse(result)