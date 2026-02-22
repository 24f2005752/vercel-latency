from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from statistics import mean

app = FastAPI()

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

    with open("q-vercel-latency.json") as f:
        data = json.load(f)

    result = {}

    for region in regions:
        region_data = [d for d in data if d["region"] == region]

        if not region_data:
            continue

        latencies = [d["latency_ms"] for d in region_data]
        uptimes = [d["uptime"] for d in region_data]

        sorted_lat = sorted(latencies)
        p95 = sorted_lat[int(0.95 * len(sorted_lat)) - 1]

        result[region] = {
            "avg_latency": mean(latencies),
            "p95_latency": p95,
            "avg_uptime": mean(uptimes),
            "breaches": sum(1 for l in latencies if l > threshold)
        }

    return result
