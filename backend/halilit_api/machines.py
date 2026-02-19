from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pytz

app = FastAPI()

# Assume this data source is available
machine_data = {
    "MCHN-001": {
        "status": "Running",
        "production_rate": 120.5,
        "error_code": None,
        "last_updated": datetime(2024, 10, 27, 10, 0, 0, tzinfo=pytz.utc),
    },
    "MCHN-002": {
        "status": "Error",
        "production_rate": None,
        "error_code": "E101",
        "last_updated": datetime(2024, 10, 27, 10, 15, 0, tzinfo=pytz.utc),
    },
}


class MachineStatus(BaseModel):
    machine_id: str
    status: str
    production_rate: Optional[float] = None
    error_code: Optional[str] = None
    last_updated: datetime


@app.get("/machines/{machine_id}/status", response_model=MachineStatus)
async def get_machine_status(machine_id: str):
    try:
        if machine_id in machine_data:
            data = machine_data[machine_id]
            return MachineStatus(
                machine_id=machine_id,
                status=data["status"],
                production_rate=data["production_rate"],
                error_code=data["error_code"],
                last_updated=data["last_updated"],
            )
        else:
            raise HTTPException(
                status_code=404, detail=f"Machine with ID '{machine_id}' not found."
            )
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error.")