from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uuid

app = FastAPI(title="API Health Monitor")

# In-memory store (will replace with DynamoDB later)
ENDPOINTS = {}

class HealthConfig(BaseModel):
    url: str
    expected_status: int = 200
    timeout_seconds: int = 5
    check_interval: int = 60
    failure_threshold: int = 3

@app.post("/endpoints")
def create_endpoint(config: HealthConfig):
    endpoint_id = str(uuid.uuid4())
    ENDPOINTS[endpoint_id] = {
        "id": endpoint_id,
        "config": config,
        "status": "UNKNOWN",
        "fail_count": 0
    }
    return {"endpoint_id": endpoint_id}

@app.get("/endpoints")
def list_endpoints():
    return ENDPOINTS

@app.get("/health")
def health():
    return {"status": "ok"}

