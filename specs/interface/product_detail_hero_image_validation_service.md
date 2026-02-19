# Spec: Product Detail Hero Image Validation Service
**Target:** backend/services/product_image_validation.py

## Overview
This service validates that a given image URL is accessible and of an appropriate format for use as a hero image on the product detail page. It checks for image accessibility by attempting to retrieve the image and verifying the response code. It also validates the image file type and returns a boolean indicating whether the image is suitable.

## Requirements
- The service must accept an image URL as input.
- The service must verify that the image URL is reachable and returns a 200 OK response.
- The service must verify that the image file type is one of: JPEG, PNG, or WEBP.
- The service must return a boolean value indicating whether the image is valid.
- The service must handle network errors gracefully and return `False` if an image URL is unreachable after retries.
- The service must log any errors encountered during validation.
- The service must be implemented as a FastAPI endpoint.

## Data Contract

**Request:**

```json
{
  "image_url": "string"
}
```

**Response:**

```json
{
  "is_valid": "boolean"
}
```

Pydantic Models:

```python
from pydantic import BaseModel, HttpUrl

class ImageValidationRequest(BaseModel):
    image_url: HttpUrl

class ImageValidationResponse(BaseModel):
    is_valid: bool
```

## Behavior Scenarios

- **Scenario:** Valid JPEG Image
  - Input: `{"image_url": "https://example.com/valid_image.jpg"}` (where example.com serves a valid JPEG image with 200 OK)
  - Outcome: `{ "is_valid": true }`

- **Scenario:** Valid PNG Image
  - Input: `{"image_url": "https://example.com/valid_image.png"}` (where example.com serves a valid PNG image with 200 OK)
  - Outcome: `{ "is_valid": true }`

- **Scenario:** Valid WEBP Image
  - Input: `{"image_url": "https://example.com/valid_image.webp"}` (where example.com serves a valid WEBP image with 200 OK)
  - Outcome: `{ "is_valid": true }`

- **Scenario:** Invalid Image URL (404 Not Found)
  - Input: `{"image_url": "https://example.com/invalid_image.jpg"}` (where example.com returns a 404 error)
  - Outcome: `{ "is_valid": false }`

- **Scenario:** Invalid Image URL (Network Error)
  - Input: `{"image_url": "https://unreachable-domain.com/image.jpg"}` (where the domain does not exist)
  - Outcome: `{ "is_valid": false }`

- **Scenario:** Invalid Image Type (GIF)
  - Input: `{"image_url": "https://example.com/invalid_image.gif"}` (where example.com serves a GIF image with 200 OK)
  - Outcome: `{ "is_valid": false }`

- **Scenario:** Invalid Image URL (Not an Image)
  - Input: `{"image_url": "https://example.com/document.pdf"}` (where example.com serves a PDF document with 200 OK)
  - Outcome: `{ "is_valid": false }`

## Out of Scope
- Image resizing or other image manipulation.
- Authentication or authorization for the endpoint.
- Detailed error reporting beyond the boolean `is_valid` value (errors should be logged server-side).
- Checking image dimensions or file size.
