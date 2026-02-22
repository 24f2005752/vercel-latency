from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from statistics import mean

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/")
async def analytics(payload: dict):
    regions = payload["regions"]
    threshold = payload["threshold_ms"]

    # Correct file path for Vercel serverless
    BASE_DIR = os.path.dirname(__file__)
    file_path = os.path.join(BASE_DIR, "..", "q-vercel-latency.json")

    with open(file_path) as f:
        data = json.load(f)

    result = {}

    for region in regions:
        region_data = [d for d in data if d["region"] == region]

        if not region_data:
            continue

        latencies = [d["latency_ms"] for d in region_data]
        uptimes = [d["uptime"] for d in region_data]

        sorted_lat = sorted(latencies)
        p95_index = max(int(0.95 * len(sorted_lat)) - 1, 0)
        p95 = sorted_lat[p95_index]

        result[region] = {
            "avg_latency": mean(latencies),
            "p95_latency": p95,
            "avg_uptime": mean(uptimes),
            "breaches": sum(1 for l in latencies if l > threshold)
        }

    return result
