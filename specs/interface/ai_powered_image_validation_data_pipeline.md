# Spec: AI-Powered Image Validation Data Pipeline
**Target:** data_pipeline/image_validation.py

## Overview
This data pipeline script leverages AI to automatically validate images uploaded to the Halilit Support Center. It checks for specific criteria such as image quality, presence of Halilit products, and adherence to brand guidelines. The pipeline outputs validation results that are stored for further processing and integration with the support ticket system.

## Requirements
- The script must process images in a scalable and efficient manner.
- The script must use an AI model to detect the presence of Halilit products within the image.
- The script must assess image quality metrics such as resolution, sharpness, and brightness.
- The script must check for adherence to brand guidelines (e.g., acceptable backgrounds, product angles).
- The script must output a structured report indicating validation success/failure and specific reasons for failure.
- The script must handle common image formats (JPEG, PNG, WebP).
- The script must be configurable to adjust validation thresholds (e.g., minimum confidence score for product detection, minimum acceptable resolution).
- The script must log all operations and errors to a central logging system.
- The script must be triggered automatically upon image upload (details of trigger mechanism are external to this spec).
- The script should retry failed image validations a configurable number of times.

## Data Contract

**Input:**

The script receives a dictionary containing image metadata and the image data itself.

```python
from typing import TypedDict, BinaryIO
from pydantic import BaseModel, HttpUrl, validator

class ImageValidationInput(BaseModel):
    image_url: HttpUrl
    image_data: bytes # Raw image data
    file_name: str

    @validator('image_data')
    def image_data_not_empty(cls, v):
        if not v:
            raise ValueError('Image data cannot be empty.')
        return v
```

**Output:**

The script returns a JSON-serializable dictionary containing the validation results.

```python
from typing import Optional
from pydantic import BaseModel

class ImageValidationResult(BaseModel):
    is_valid: bool
    reasons: list[str]
    halilit_product_detected: bool
    confidence_score: Optional[float] = None  # Confidence score of product detection (if applicable)
    image_quality_score: Optional[float] = None # Image quality (0-1 where 1.0 is perfect)
```

## Behavior Scenarios

- **Scenario:** Valid Halilit Product Image
  - Input: An image containing a clear, well-lit photo of a Halilit product against a neutral background.
  - Outcome: `is_valid: True`, `halilit_product_detected: True`, `confidence_score` > configured threshold, `reasons: []`

- **Scenario:** Invalid Halilit Product Image - Poor Quality
  - Input: A blurry, low-resolution image of a Halilit product.
  - Outcome: `is_valid: False`, `halilit_product_detected: True`, `confidence_score` > configured threshold, `reasons: ["Poor image quality (low resolution, blurry)"]`

- **Scenario:** Invalid Halilit Product Image - No Product Detected
  - Input: An image containing unrelated objects.
  - Outcome: `is_valid: False`, `halilit_product_detected: False`, `confidence_score: None`, `reasons: ["No Halilit product detected"]`

- **Scenario:** Invalid Halilit Product Image - Brand Guideline Violation
  - Input: An image of a Halilit product with a cluttered or distracting background.
  - Outcome: `is_valid: False`, `halilit_product_detected: True`, `confidence_score` > configured threshold, `reasons: ["Background violates brand guidelines"]`

- **Scenario:** Corrupted Image Data
  - Input: Corrupted or unreadable image data.
  - Outcome: Log an error, retry (if configured), and eventually return `is_valid: False`, `halilit_product_detected: False`, `confidence_score: None`, `reasons: ["Image data is corrupted or invalid"]`

## Out of Scope
-  The implementation of the AI model itself (this is assumed to be pre-trained and accessible via an API).
-  The specific mechanism for triggering the script upon image upload.
-  The storage and retrieval of images.
-  The specifics of the central logging system.
-  The UI for displaying validation results.
