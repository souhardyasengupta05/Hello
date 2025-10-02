from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np

app = FastAPI()

# Allow CORS from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/api/metrics")
async def get_metrics(request: Request):
    data = await request.json()
    regions = data.get("regions", [])
    threshold = data.get("threshold_ms", 180)

    # Load telemetry bundle
    import json, os
    filepath = os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")
    with open(filepath, "r") as f:
        telemetry = json.load(f)

    result = {}
    for region in regions:
        region_data = [r for r in telemetry if r["region"] == region]
        if not region_data:
            result[region] = {"error": "no data"}
            continue

        latencies = np.array([r["latency_ms"] for r in region_data])
        uptimes = np.array([r["uptime"] for r in region_data])

        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        breaches = int(np.sum(latencies > threshold))

        result[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 4),
            "breaches": breaches,
        }

    return JSONResponse(result)
