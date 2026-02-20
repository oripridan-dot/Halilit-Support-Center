# Spec: AI-Powered Image Validation Pipeline

**Target:** data_pipeline/src/image_validation.py

## Overview
This script implements an AI-powered image validation pipeline. It takes an image file path as input, performs a series of checks using a pre-trained AI model, and returns a validation report indicating whether the image is valid and any identified issues. The primary purpose is to automatically flag potentially problematic images uploaded to the Halilit Support Center, such as those containing inappropriate content, watermarks, or that fail to meet quality standards.

## Requirements
- The pipeline must accept an image file path as input.
- The pipeline must load and use a pre-trained AI model for image validation (specify model details below).
- The pipeline must perform checks for:
    - **Inappropriate content:** Identify and flag images containing nudity, violence, or hate speech.
    - **Watermarks:** Detect and flag images containing visible watermarks.
    - **Quality:** Assess image quality based on metrics like blurriness and resolution, flagging images below a minimum acceptable threshold.
- The pipeline must return a validation report in JSON format, indicating the overall validity of the image and any identified issues with specific confidence scores.
- The pipeline must log all validation attempts and results for auditing purposes.
- The AI model should be configurable for fine-tuning or replacement without significant code changes.
- The pipeline needs to handle common image file types: JPEG, PNG, GIF.
- The pipeline should be containerized using Docker for easy deployment.
- Error handling must be robust, with clear error messages logged for any failures during the process.

## Data Contract

**Input:**
```python
# data_pipeline/src/image_validation.py
from pydantic import BaseModel
from typing import Optional

class ImageValidationRequest(BaseModel):
    image_path: str
```

**Output:**
```python
# data_pipeline/src/image_validation.py
from pydantic import BaseModel
from typing import Optional, Dict

class ValidationReport(BaseModel):
    is_valid: bool
    issues: Dict[str, IssueDetails]
    overall_confidence: float  # Overall confidence score of the validation

class IssueDetails(BaseModel):
    description: str
    confidence: float  # Confidence score for the specific issue
    metadata: Optional[Dict] = None  # Additional metadata about the issue (e.g., coordinates of a watermark)

```

## Behavior Scenarios

- **Scenario:** Valid Image
  - Input: `image_path`: `/path/to/valid_image.jpg` (image of a Halilit product on a clean background)
  - Outcome: Returns a `ValidationReport` with `is_valid: True`, `issues: {}`, and `overall_confidence`: a high value (e.g., 0.95).

- **Scenario:** Image with Watermark
  - Input: `image_path`: `/path/to/watermarked_image.png` (image containing a visible watermark)
  - Outcome: Returns a `ValidationReport` with `is_valid: False`, `issues: {"watermark": IssueDetails(description="Image contains a watermark.", confidence=0.85, metadata={"coordinates": [10, 10, 100, 50]})}`, and `overall_confidence`: a medium value (e.g., 0.65).

- **Scenario:** Image with Inappropriate Content
  - Input: `image_path`: `/path/to/inappropriate_image.jpg` (image containing nudity)
  - Outcome: Returns a `ValidationReport` with `is_valid: False`, `issues: {"inappropriate_content": IssueDetails(description="Image contains inappropriate content.", confidence=0.92)}`, and `overall_confidence`: a low value (e.g., 0.1).

- **Scenario:** Low-Quality Image
  - Input: `image_path`: `/path/to/blurry_image.jpeg` (blurry image with low resolution)
  - Outcome: Returns a `ValidationReport` with `is_valid: False`, `issues: {"quality": IssueDetails(description="Image quality is below acceptable threshold.", confidence=0.75, metadata={"blurriness_score": 0.6, "resolution": "640x480"})}`, and `overall_confidence`: a medium value (e.g., 0.5).

- **Scenario:** Unsupported Image Format
  - Input: `image_path`: `/path/to/image.webp` (image in WebP format)
  - Outcome: Raises an exception (handled internally and logged) and returns a `ValidationReport` with `is_valid: False`, `issues: {"format": IssueDetails(description="Unsupported image format (WebP).", confidence=1.0)}`, and `overall_confidence`: a very low value (e.g., 0.05).

- **Scenario:** File Not Found
  - Input: `image_path`: `/path/to/nonexistent_image.jpg`
  - Outcome: Raises an exception (handled internally and logged) and returns a `ValidationReport` with `is_valid: False`, `issues: {"file": IssueDetails(description="Image file not found.", confidence=1.0)}`, and `overall_confidence`: a very low value (e.g., 0.05).

## Out of Scope
- User interface for viewing validation reports. This will be handled in a separate UI component.
- Retraining the AI model. Model retraining will be handled by a separate data science pipeline.
- Real-time video processing. This pipeline is designed for static images only.
- Image format conversion. The pipeline expects images to be in one of the supported formats.

## Implementation Details

- **AI Model:** The pipeline should use a pre-trained deep learning model for image classification and object detection.  Consider using a model like `DeepDetect/yolov5m-vision-detector` hosted on Hugging Face Hub or equivalent, fine-tuned for the specific requirements of Halilit Support Center.  The model should be loaded at startup to minimize latency. You can wrap this in a separate `ai_model.py` file for encapsulation.
- **Configuration:** The path to the AI model, the confidence thresholds for different types of issues, and other configuration parameters should be stored in a configuration file (e.g., `config.yaml`) and loaded at startup.
- **Logging:** Use Python's built-in `logging` module to log all validation attempts, results, and errors. Include timestamps and relevant details for debugging.
- **Error Handling:** Implement robust error handling using `try...except` blocks to catch potential exceptions (e.g., file not found, invalid image format, AI model errors). Log errors with sufficient detail to diagnose and resolve issues.
- **Containerization:** Create a Dockerfile to package the pipeline and its dependencies into a Docker image. This will ensure consistent deployment across different environments. Include `uvicorn` for the API entrypoint.
- **API Endpoint (FastAPI):**
    ```python
    # main.py
    from fastapi import FastAPI, HTTPException, status
    from data_pipeline.src.image_validation import ImageValidationRequest, ValidationReport, validate_image

    app = FastAPI()

    @app.post("/validate_image", response_model=ValidationReport)
    async def validate_image_endpoint(request: ImageValidationRequest):
        try:
            return validate_image(request.image_path)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    ```

## data_pipeline/src/image_validation.py Code Skeleton

```python
import logging
from typing import Dict, Optional
from pydantic import BaseModel
from PIL import Image
# from deepface import DeepFace  # If using DeepFace for content moderation - example
import yaml
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define Data Contracts
class ImageValidationRequest(BaseModel):
    image_path: str

class ValidationReport(BaseModel):
    is_valid: bool
    issues: Dict[str, 'IssueDetails']
    overall_confidence: float

class IssueDetails(BaseModel):
    description: str
    confidence: float
    metadata: Optional[Dict] = None

# Load configuration
try:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    logging.error("Configuration file not found. Using default values.")
    config = {}  # Provide default values if the config file is missing.  Critical.

def validate_image(image_path: str) -> ValidationReport:
    """
    Validates an image file based on configured checks.
    """
    logging.info(f"Validating image: {image_path}")
    report = ValidationReport(is_valid=True, issues={}, overall_confidence=1.0)

    try:
        img = Image.open(image_path)
        img.verify()  # Verify that it is actually an image
    except FileNotFoundError:
        logging.error(f"Image file not found: {image_path}")
        report.is_valid = False
        report.issues["file"] = IssueDetails(description="Image file not found.", confidence=1.0)
        report.overall_confidence = 0.05
        return report
    except Exception as e:
        logging.error(f"Error opening image: {e}")
        report.is_valid = False
        report.issues["format"] = IssueDetails(description="Invalid image format.", confidence=1.0)
        report.overall_confidence = 0.05
        return report

    # Perform checks (example - adjust based on chosen model/methods)
    try:
        # Example - Content moderation (replace with actual implementation using your chosen model)
        # result = DeepFace.analyze(img_path = image_path, actions = ['age', 'gender', 'race', 'emotion'])
        # if result['dominant_emotion'] == 'angry':
        #     report.is_valid = False
        #     report.issues["inappropriate_content"] = IssueDetails(description="Image potentially contains negative emotions.", confidence=0.7)
        #     report.overall_confidence *= 0.3

        # Example - Watermark detection (replace with actual implementation)
        if "WATERMARK" in image_path.upper(): # Mock watermark detection
           report.is_valid = False
           report.issues["watermark"] = IssueDetails(description="Image contains a watermark.", confidence=0.85, metadata={"coordinates": [10, 10, 100, 50]})
           report.overall_confidence *= 0.5

        # Example - Quality check (replace with actual implementation)
        width, height = img.size
        if width < config.get("min_width", 500) or height < config.get("min_height", 500):  # Access config values safely
            report.is_valid = False
            report.issues["quality"] = IssueDetails(description="Image resolution is too low.", confidence=0.7, metadata={"resolution": f"{width}x{height}"})
            report.overall_confidence *= 0.6

    except Exception as e:
        logging.error(f"Error during image checks: {e}")
        report.is_valid = False
        report.issues["processing_error"] = IssueDetails(description="Error during image processing.", confidence=0.9)
        report.overall_confidence = 0.1

    logging.info(f"Validation report: {report}")
    return report


if __name__ == '__main__':
    # Example Usage (for testing)
    image_path = "path/to/valid_image.jpg"  # Replace with an actual image path. MUST BE A VALID IMAGE for the code to run.
    report = validate_image(image_path)
    print(report)
```

**config.yaml example**:

```yaml
min_width: 500
min_height: 500
```
