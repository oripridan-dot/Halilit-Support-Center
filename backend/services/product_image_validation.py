import logging
import asyncio
from typing import Union

import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageValidationRequest(BaseModel):
    image_url: HttpUrl


class ImageValidationResponse(BaseModel):
    is_valid: bool


ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
CACHE_KEY_PREFIX = "image_validation:"
CACHE_EXPIRY_SECONDS = 24 * 60 * 60  # 24 hours


async def is_image_type_allowed(image_url: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(image_url, timeout=5) as response:
                content_type = response.headers.get("Content-Type")
                return content_type in ALLOWED_IMAGE_TYPES
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.error(f"Error checking image type for {image_url}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking image type for {image_url}: {e}")
        return False

async def validate_image_url(image_url: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(image_url, timeout=5) as response:
                if 200 <= response.status < 300:
                    return await is_image_type_allowed(image_url)
                else:
                    logger.info(f"Image validation failed for {image_url}: Status {response.status}")
                    return False
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.error(f"Network error validating {image_url}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error validating {image_url}: {e}")
        return False


@app.post("/api/validate_image", response_model=ImageValidationResponse)
async def validate_image(request: ImageValidationRequest) -> ImageValidationResponse:
    is_valid = await validate_image_url(request.image_url)
    return ImageValidationResponse(is_valid=is_valid)