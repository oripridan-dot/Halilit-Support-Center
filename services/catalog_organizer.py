import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError, validator

logger = logging.getLogger(__name__)

app = FastAPI()

# --- Data Models ---
class SensorReadings(BaseModel):
    temperature: float
    pressure: float
    vibration: float

class RawDataEntry(BaseModel):
    product_id: str
    timestamp: str
    sensor_readings: SensorReadings
    defect_code: Optional[str] = None

    @validator('timestamp')
    def validate_timestamp(cls, value):
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
            return value
        except ValueError:
            raise ValueError('Invalid timestamp format.  Must be ISO 8601')

class OrganizedDataEntry(BaseModel):
    product_id: str
    timestamp: str
    sensor_readings: SensorReadings
    defect_code: Optional[str] = None
    category: str

# --- In-Memory Storage ---
organized_data: List[OrganizedDataEntry] = []

# --- Categorization Rules (Hardcoded for now) ---
def categorize_data(data: RawDataEntry) -> str:
    """Categorizes data based on hardcoded rules."""
    if data.defect_code:
        return "defective"
    if data.sensor_readings.temperature > 30:
        return "electronics"
    return "mechanical"

# --- API Endpoints ---
@app.post("/catalog/organize", status_code=status.HTTP_200_OK)
async def organize_data(data: Dict[str, Any]):
    """Receives raw data, validates, categorizes, and stores it."""
    try:
        raw_data_list: List[RawDataEntry] = [RawDataEntry(**item) for item in data.get("raw_data", [])]
    except ValidationError as e:
        error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        logger.error(f"Data validation failed: {error_messages}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": "error", "message": "Data validation failed.", "errors": error_messages},
        )

    for raw_data in raw_data_list:
        try:
            category = categorize_data(raw_data)
            organized_entry = OrganizedDataEntry(
                product_id=raw_data.product_id,
                timestamp=raw_data.timestamp,
                sensor_readings=raw_data.sensor_readings,
                defect_code=raw_data.defect_code,
                category=category,
            )
            organized_data.append(organized_entry)
            logger.info(f"Data organized: product_id={raw_data.product_id}, category={category}")
        except Exception as e:
            logger.error(f"Error during categorization: {e}")
            # Consider returning a partial success in a real-world scenario

    return {"status": "success", "message": "Data successfully organized and stored."}


@app.get("/catalog/retrieve", status_code=status.HTTP_200_OK)
async def retrieve_data(category: str, start_time: str, end_time: str):
    """Retrieves organized data based on category and time range."""
    try:
        start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_datetime = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    except ValueError:
        logger.error("Invalid request parameters: Invalid date/time format")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request parameters.",
        )

    retrieved_data = []
    for entry in organized_data:
        try:
            entry_datetime = datetime.fromisoformat(entry.timestamp.replace('Z', '+00:00'))
        except ValueError:
            logger.warning(f"Invalid timestamp in stored data: {entry.timestamp}")
            continue

        if (
            entry.category == category
            and start_datetime <= entry_datetime <= end_datetime
        ):
            retrieved_data.append(entry)

    if not retrieved_data:
        logger.info(
            f"No data found for category={category}, start_time={start_time}, end_time={end_time}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data found for the specified criteria.",
        )

    return {"status": "success", "data": retrieved_data}

# --- Startup Event (Optional) ---
@app.on_event("startup")
async def startup_event():
    logging.basicConfig(level=logging.INFO)
    logger.info("Catalog Organizer Service started.")