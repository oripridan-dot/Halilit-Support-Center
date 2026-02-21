# Spec: AI Image Validation Data Pipeline
**Target:** data_pipeline/ai_image_validation.py

## Overview
This data pipeline component validates images uploaded to the Halilit Support Center using an AI-powered image analysis service. It checks for various failure conditions (e.g., blurry images, irrelevant content, low resolution) and flags them accordingly in a structured format. This component retrieves images from cloud storage (S3), sends them to the AI validation service, and updates the corresponding records in the database.

## Requirements
- [x] Retrieve images from an S3 bucket. The bucket name and image keys are provided as input.
- [x] Communicate with a pre-existing AI image validation service via HTTP. The service endpoint and authentication details will be provided as environment variables.
- [x] Implement error handling for network errors, service outages, and invalid responses from the AI service.
- [x] Filter images based on pre-defined criteria, such as minimum resolution and maximum file size.
- [x] Store validation results in a database table (PostgreSQL).
- [x] Generate metrics for monitoring the pipeline's performance (e.g., processing time, failure rate).
- [x] Provide a configurable threshold for determining whether an image is considered invalid based on the AI service's confidence scores.
- [x] Integrate with the existing logging infrastructure.
- [x] Support batch processing of images.
- [x] Allow configurable retry attempts for failed image validations.
- [x]  Use asynchronous operations to efficiently handle I/O-bound tasks.
- [x]  Implement type checking with mypy.

## Data Contract

**Input:**

```python
from typing import List, Dict
from pydantic import BaseModel

class ImageMetadata(BaseModel):
    s3_bucket: str
    s3_key: str
    image_id: str  # Unique identifier for the image in the Halilit system.

class ImageValidationJob(BaseModel):
    images: List[ImageMetadata]
```

**Output (Database Record):**

```python
from typing import Optional
from pydantic import BaseModel

class ImageValidationResult(BaseModel):
    image_id: str  # Matches image_id from ImageMetadata
    is_valid: bool
    failure_reasons: Optional[List[str]] = None  # e.g., ["blurry", "low_resolution"]
    confidence_score: Optional[float] = None # AI Service's confidence in the validation result.
    validation_timestamp: str # ISO 8601 timestamp
```

**AI Service Request:**

```json
{
  "image_url": "s3://{s3_bucket}/{s3_key}"
}
```

**AI Service Response:**

```json
{
  "is_valid": true,
  "failure_reasons": ["blurry", "low_resolution"],
  "confidence_score": 0.95
}
```

## Behavior Scenarios

- **Scenario:** Successful Image Validation
  - Input: `ImageValidationJob(images=[ImageMetadata(s3_bucket="halilit-images", s3_key="image1.jpg", image_id="img_001")])`
  - Outcome: The image is retrieved from S3, sent to the AI validation service, and if the AI service reports `is_valid: true`, an `ImageValidationResult(image_id="img_001", is_valid=True, failure_reasons=None, confidence_score=0.95, validation_timestamp=...)` record is created in the database.

- **Scenario:** Failed Image Validation due to Blurriness
  - Input: `ImageValidationJob(images=[ImageMetadata(s3_bucket="halilit-images", s3_key="blurry.jpg", image_id="img_002")])`
  - Outcome: The image is retrieved from S3, sent to the AI validation service, and if the AI service reports `is_valid: false` and `failure_reasons=["blurry"]`, an `ImageValidationResult(image_id="img_002", is_valid=False, failure_reasons=["blurry"], confidence_score=0.2, validation_timestamp=...)` record is created in the database.

- **Scenario:** AI Service Unavailable
  - Input: `ImageValidationJob(images=[ImageMetadata(s3_bucket="halilit-images", s3_key="image1.jpg", image_id="img_001")])` and the AI service is down.
  - Outcome: The pipeline retries the request up to a configurable number of times. After the maximum number of retries is reached, an error log is created, and the `ImageValidationResult` record is created with `is_valid = False` and `failure_reasons=["ai_service_unavailable"]`.

- **Scenario:** Image Not Found in S3
  - Input: `ImageValidationJob(images=[ImageMetadata(s3_bucket="halilit-images", s3_key="nonexistent.jpg", image_id="img_003")])`
  - Outcome: The pipeline catches the S3 `NoSuchKey` exception, creates an error log, and stores an `ImageValidationResult(image_id="img_003", is_valid=False, failure_reasons=["s3_object_not_found"], confidence_score=None, validation_timestamp=...)` record in the database.

- **Scenario:** Image exceeds file size limits.
    - Input: `ImageValidationJob(images=[ImageMetadata(s3_bucket="halilit-images", s3_key="large.jpg", image_id="img_004")])` with `large.jpg` exceeding the configured maximum file size.
    - Outcome: The pipeline skips the AI validation service, creates a warning log, and stores an `ImageValidationResult(image_id="img_004", is_valid=False, failure_reasons=["file_size_exceeded"], confidence_score=None, validation_timestamp=...)` record in the database.

## Out of Scope
- [Training the AI image validation model is out of scope.]
- [Defining the exact criteria for image validity (e.g., acceptable blur levels, relevant content categories) is the responsibility of the AI service.]
- [This pipeline does not handle image uploads.]
