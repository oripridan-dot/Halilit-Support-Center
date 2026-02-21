# Spec: AI Image Validation Data Pipeline

**Target:** data_pipeline/ai_image_validation.py

## Overview
This data pipeline script validates images uploaded to the Halilit Support Center using an AI-powered image analysis service. It receives image paths as input, submits them to the validation service, and updates the support ticket database with the validation results. This ensures that only valid and appropriate images are stored and displayed, improving the quality and safety of the support center content.

## Requirements
- The script must accept a list of image file paths as input.
- The script must interact with an external AI image validation service (e.g., using an API). Assume the existence of an `AIImageValidator` class with an `async def validate_image(image_path: str) -> ValidationResult` method.
- The script must update the support ticket database with the image validation results, indicating whether each image is valid or invalid.  Assume the existence of a `SupportTicketDatabase` class with an `async def update_image_validation(image_path: str, is_valid: bool, validation_reason: str | None) -> None` method.
- The script must handle potential errors during image validation (e.g., network issues, invalid image formats, service unavailability) gracefully.
- The script must log all validation attempts and results, including any errors encountered. Use the `logging` module.
- The `ValidationResult` from the AI validation service is a Pydantic model with the following attributes: `is_valid: bool`, and `reason: str | None`.  `reason` is populated only if the image is invalid.
- The script must be asynchronous.

## Data Contract

**Input:**

```python
from typing import List

image_paths: List[str]
```

**Output:**

The script does not directly return a value. Its output is reflected in the support ticket database and the log file.

**AIImageValidator.validate_image Return Type:**

```python
from pydantic import BaseModel

class ValidationResult(BaseModel):
    is_valid: bool
    reason: str | None = None
```

## Behavior Scenarios

- **Scenario: Valid Image**
  - Input: `image_paths = ["/path/to/valid_image.jpg"]`
  - Outcome:
    - The image is successfully validated by the `AIImageValidator`.
    - The `SupportTicketDatabase` is updated with `is_valid=True` and `validation_reason=None` for `/path/to/valid_image.jpg`.
    - A log entry indicating successful validation is created.

- **Scenario: Invalid Image**
  - Input: `image_paths = ["/path/to/invalid_image.png"]`
  - Outcome:
    - The image is successfully validated by the `AIImageValidator`.
    - The `AIImageValidator` returns a `ValidationResult` with `is_valid=False` and `reason="Contains inappropriate content"`.
    - The `SupportTicketDatabase` is updated with `is_valid=False` and `validation_reason="Contains inappropriate content"` for `/path/to/invalid_image.png`.
    - A log entry indicating failed validation with the corresponding reason is created.

- **Scenario: AI Validation Service Unavailable**
  - Input: `image_paths = ["/path/to/image.gif"]` and the `AIImageValidator` raises an exception (e.g., `ConnectionError`) during validation.
  - Outcome:
    - The exception is caught and logged.
    - The `SupportTicketDatabase` is updated with `is_valid=False` and `validation_reason="AI Validation Service Unavailable"` for `/path/to/image.gif`.
    - A log entry indicating the error and the image path is created.

- **Scenario: Image File Not Found**
  - Input: `image_paths = ["/path/to/nonexistent_image.bmp"]`
  - Outcome:
    - A `FileNotFoundError` is raised during the `AIImageValidator.validate_image` call.
    - The exception is caught and logged.
    - The `SupportTicketDatabase` is updated with `is_valid=False` and `validation_reason="Image File Not Found"` for `/path/to/nonexistent_image.bmp`.
    - A log entry indicating the error and the image path is created.

## Out of Scope
- Implementation details of the `AIImageValidator` class.
- Implementation details of the `SupportTicketDatabase` class.
- Definition of specific validation rules used by the AI image validation service.
- Retry mechanisms for failed validation attempts.
- Handling of different image file types beyond basic validation (e.g., resizing, format conversion).
