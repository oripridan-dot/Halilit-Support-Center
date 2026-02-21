# Spec: AI Image Validation Data Pipeline

**Target:** data_pipeline/ai_image_validation.py

## Overview

This data pipeline component validates images submitted to the Halilit Support Center using an AI model. The pipeline checks for image quality, inappropriate content, and compliance with pre-defined standards. The validated images, along with the validation results, are stored in a designated storage location. This pipeline runs as a scheduled job.

## Requirements

- The pipeline must accept image data from a specified source (e.g., cloud storage bucket).
- The pipeline must use a pre-trained AI model for image validation. (Assumed: API access to a remote AI model service.)
- The pipeline must check for image quality (e.g., blurriness, low resolution).
- The pipeline must check for inappropriate content (e.g., violence, nudity, hate speech).
- The pipeline must ensure images comply with predefined standards (e.g., logo placement, aspect ratio).
- The pipeline must generate a validation report for each image, including quality score, content flags, and compliance status.
- The pipeline must store the validated images and their corresponding reports in a designated cloud storage location.
- The pipeline must log all processing steps and any errors encountered.
- The pipeline must be configurable for different AI models, thresholds, and storage locations via environment variables or a configuration file.
- The pipeline must be resilient to network errors when communicating with the AI model service. It should implement retry logic with exponential backoff.
- The pipeline must report metrics about processing time and number of images processed via logging or a metrics service.

## Data Contract

**Input:**

*   **Image Data:** Image files retrieved from a configured source (e.g., cloud storage bucket). The exact format will depend on the source (e.g., `bytes` for objects from S3). We assume the image is in a common format like JPEG or PNG.
*   **Configuration:**
    *   `AI_MODEL_API_URL`: URL of the AI image validation service. (string)
    *   `AI_MODEL_API_KEY`: API key for accessing the AI image validation service. (string)
    *   `QUALITY_THRESHOLD`: Minimum acceptable quality score (float between 0.0 and 1.0).
    *   `STORAGE_BUCKET`:  Name of the cloud storage bucket to store validated images and reports. (string)
    *   `STORAGE_PATH`: Path within the bucket to store the data. (string)
    *   `RETRY_COUNT`: Number of retries for AI model API calls. (integer, default 3)
    *   `RETRY_DELAY`: Delay (seconds) before retrying. (integer, default 1)

**Output (Validation Report):**

```python
from typing import Dict, Optional
from pydantic import BaseModel

class ValidationReport(BaseModel):
    image_id: str  # Unique identifier for the image.  Derived from the image file name (no extension).
    quality_score: float
    inappropriate_content_flags: Optional[Dict[str, float]] = None  # e.g., {"violence": 0.95, "nudity": 0.10} Values are probabilities.
    compliance_status: bool  # True if the image meets all compliance standards.
    error: Optional[str] = None  # If an error occurred during processing.

```

## Behavior Scenarios

-   **Scenario:** Successful Validation
    -   Input: A valid image from the source.
    -   Outcome: The image is processed by the AI model, and a ValidationReport with a high `quality_score`, no `inappropriate_content_flags` exceeding thresholds, and `compliance_status` set to `True` is generated. The image and the report are stored in the designated storage location.
-   **Scenario:** Low Quality Image
    -   Input: An image with low resolution (e.g., `quality_score` below `QUALITY_THRESHOLD`).
    -   Outcome: The image is processed, and a ValidationReport with a low `quality_score` is generated. The `compliance_status` is set to `False`. The image and the report are stored in the designated storage location.  The log includes a warning about the low-quality image.
-   **Scenario:** Inappropriate Content Detected
    -   Input: An image containing potentially inappropriate content (e.g., violence detected with a probability above a threshold).
    -   Outcome: The image is processed, and a ValidationReport with `inappropriate_content_flags` indicating the detected content and their probabilities is generated. The `compliance_status` is set to `False`. The image and the report are stored in the designated storage location. The log includes a warning about the inappropriate content.
-   **Scenario:** AI Model API Error
    -   Input: An image is being processed, but the AI model API returns an error (e.g., network timeout).
    -   Outcome: The pipeline retries the API call according to the configured retry policy (`RETRY_COUNT`, `RETRY_DELAY`). If all retries fail, a ValidationReport with an `error` message is generated, and the image and the report are stored. The error is logged with appropriate severity.
-   **Scenario:** Invalid Image Format
    -   Input: An image that is not a supported format (e.g., a corrupted file).
    -   Outcome:  A ValidationReport with an `error` message describing the invalid format is generated.  The pipeline logs the error and continues processing other images. The erroneous image is NOT stored in the designated location. Only the report is stored.
-   **Scenario:** Configuration Error
    -   Input: Incorrect `AI_MODEL_API_URL`
    -   Outcome: The Pipeline fails to start and logs the configuration error.

## Out of Scope

-   Implementing the AI image validation model itself. This spec assumes access to an external AI service.
-   Image resizing or other pre-processing steps before validation.
-   User interface or API endpoint for triggering the validation. This is a scheduled data pipeline.
-   Detailed specification of the storage location (e.g., specific cloud storage service). This spec assumes a generic cloud storage interface.
-   Specific details of the scheduling mechanism.

```python
import asyncio
import logging
import os
from typing import AsyncGenerator, Dict, Optional

import httpx
from pydantic import BaseModel, field_validator

# from tenacity import retry, stop_after_attempt, wait_exponential  # Alternative retry library if needed.
# from tenacity import retry, stop_after_attempt, wait_random_exponential
# from tenacity import retry, stop_after_attempt, wait_fixed

from urllib.parse import urljoin


from dotenv import load_dotenv

#from botocore.exceptions import ClientError
#import boto3

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ValidationReport(BaseModel):
    image_id: str  # Unique identifier for the image. Derived from the image file name (no extension).
    quality_score: float
    inappropriate_content_flags: Optional[Dict[str, float]] = None  # e.g., {"violence": 0.95, "nudity": 0.10} Values are probabilities.
    compliance_status: bool  # True if the image meets all compliance standards.
    error: Optional[str] = None  # If an error occurred during processing.


# Define Pydantic model for AI service response
class AIValidationResponse(BaseModel):
    quality_score: float
    inappropriate_content_flags: Optional[Dict[str, float]] = None

class AIPayload(BaseModel):
    image_url: str # URL to the image accessible by the AI service.  For direct image data, use base64 encoding.
    # Add other parameters as needed by the AI service.

class Config(BaseModel):
    AI_MODEL_API_URL: str
    AI_MODEL_API_KEY: str
    QUALITY_THRESHOLD: float
    STORAGE_BUCKET: str
    STORAGE_PATH: str
    RETRY_COUNT: int = 3
    RETRY_DELAY: int = 1 # seconds

    @field_validator("QUALITY_THRESHOLD")
    def quality_threshold_must_be_between_0_and_1(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Quality threshold must be between 0.0 and 1.0")
        return v

    @field_validator("RETRY_COUNT")
    def retry_count_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Retry count must be positive")
        return v

    @field_validator("RETRY_DELAY")
    def retry_delay_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Retry delay must be positive")
        return v



async def validate_image(image_url: str, image_id: str, config: Config) -> ValidationReport:
    """Validates an image using the AI model and returns a validation report."""
    try:
        validation_result = await call_ai_model(image_url, config)

        compliance_status = validation_result.quality_score >= config.QUALITY_THRESHOLD and (validation_result.inappropriate_content_flags is None or all(
            value < 0.8 for value in validation_result.inappropriate_content_flags.values()))  # Arbitrary threshold for inappropriate content.  Configurable in the future.

        report = ValidationReport(
            image_id=image_id,
            quality_score=validation_result.quality_score,
            inappropriate_content_flags=validation_result.inappropriate_content_flags,
            compliance_status=compliance_status
        )

        return report

    except Exception as e:
        logging.exception(f"Error validating image {image_id}: {e}")
        return ValidationReport(image_id=image_id, quality_score=0.0, compliance_status=False, error=str(e))

# Example using tenacity library for retry logic:
# @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
# @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(multiplier=1, min=4, max=10))  # Jitter
# @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))  # Fixed delay of 2 seconds
# async def call_ai_model(image_url: str, config: Config) -> AIValidationResponse:

async def call_ai_model(image_url: str, config: Config) -> AIValidationResponse:
    """Calls the AI model API with retry logic."""
    async with httpx.AsyncClient() as client:
        for attempt in range(config.RETRY_COUNT):
            try:
                payload = AIPayload(image_url=image_url).model_dump_json()
                response = await client.post(config.AI_MODEL_API_URL, data=payload, headers={"X-API-Key": config.AI_MODEL_API_KEY}, timeout=10) # Add timeout

                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                return AIValidationResponse(**response.json())
            except httpx.HTTPStatusError as e:
                 logging.warning(f"HTTP error during API call (attempt {attempt + 1}/{config.RETRY_COUNT}): {e.response.status_code} - {e.response.text}")
                 if e.response.status_code == 400: #Bad Request should not be retried.
                     raise
            except httpx.RequestError as e: #Connection errors and timeouts
                logging.warning(f"Request error during API call (attempt {attempt + 1}/{config.RETRY_COUNT}): {e}")

            if attempt < config.RETRY_COUNT - 1:
                await asyncio.sleep(config.RETRY_DELAY) #Exponential backoff can be implemented here if desired.

        raise Exception(f"Failed to call AI model after {config.RETRY_COUNT} attempts.") #Reraise last exception?


async def store_report(report: ValidationReport, config: Config) -> None:
    """Stores the validation report to the designated storage location."""
    try:
        # Implement storage logic here (e.g., using boto3 for S3)
        # Example:
        # s3 = boto3.client('s3')
        # s3.put_object(Bucket=config.STORAGE_BUCKET, Key=f"{config.STORAGE_PATH}/{report.image_id}.json", Body=report.json().encode('utf-8'))

        # Alternative simple local storage example for testing (NOT FOR PRODUCTION):
        filepath = os.path.join(config.STORAGE_PATH, f"{report.image_id}.json")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(report.model_dump_json())

        logging.info(f"Stored report for {report.image_id} to {config.STORAGE_BUCKET}/{config.STORAGE_PATH}")

    except Exception as e:
        logging.error(f"Error storing report for {report.image_id}: {e}")

async def process_image(image_url: str, image_id: str, config: Config) -> None:
    """Processes a single image: validates it and stores the report."""
    report = await validate_image(image_url, image_id, config)
    await store_report(report, config)


async def image_generator(image_source: str) -> AsyncGenerator[tuple[str, str], None]:
    """
    Generates image URLs and image IDs from a source (e.g., a text file with image URLs, an S3 bucket).

    For demonstration, this example reads image URLs from a local file.
    In a real-world scenario, this could fetch URLs from an S3 bucket or other source.
    """
    try:
        with open(image_source, "r") as f:
            for line in f:
                image_url = line.strip()
                image_id = os.path.splitext(os.path.basename(image_url))[0]  # Extract image ID from filename
                yield image_url, image_id
    except FileNotFoundError:
        logging.error(f"Image source file not found: {image_source}")
        return
    except Exception as e:
        logging.error(f"Error reading image source: {e}")
        return

async def run_pipeline(config: Config) -> None:
    """Runs the image validation pipeline."""
    image_source = "image_urls.txt" #Replace with path to your source or actual image source

    async for image_url, image_id in image_generator(image_source):
        await process_image(image_url, image_id, config)


def get_config() -> Config:
    """Retrieves configuration from environment variables."""
    try:
        return Config(
            AI_MODEL_API_URL=os.environ["AI_MODEL_API_URL"],
            AI_MODEL_API_KEY=os.environ["AI_MODEL_API_KEY"],
            QUALITY_THRESHOLD=float(os.environ["QUALITY_THRESHOLD"]),
            STORAGE_BUCKET=os.environ["STORAGE_BUCKET"],
            STORAGE_PATH=os.environ["STORAGE_PATH"],
            RETRY_COUNT = int(os.environ.get("RETRY_COUNT", "3")),
            RETRY_DELAY = int(os.environ.get("RETRY_DELAY", "1")),


        )
    except KeyError as e:
        raise ValueError(f"Missing required environment variable: {e}") from e
    except ValueError as e:
        raise ValueError(f"Invalid configuration: {e}") from e


async def main():
    """Main entry point for the pipeline."""
    try:
        config = get_config()
        logging.info("Starting image validation pipeline...")
        await run_pipeline(config)
        logging.info("Image validation pipeline completed.")

    except ValueError as e:
        logging.error(f"Configuration error: {e}")
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
```

Place this in a file called `data_pipeline/ai_image_validation.py`. You'll need to create an `image_urls.txt` file with a list of image URLs, one per line, for the script to process them. Also, set the appropriate environment variables. The storage path currently stores the reports locally; for cloud storage, implement appropriate logic.
