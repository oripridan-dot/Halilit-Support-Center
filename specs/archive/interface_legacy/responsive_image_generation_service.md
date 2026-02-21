# Spec: Responsive Image Generation Service
**Target:** backend/services/image_generation.py

## Overview
This service provides an API endpoint for generating responsive images from a source image URL. It takes an image URL as input, resizes the image into multiple predefined sizes, and returns the URLs of the resized images. The resized images are stored in a cloud storage bucket (e.g., AWS S3 or Google Cloud Storage).

## Requirements
- The service must accept a valid image URL as input.
- The service must validate the image URL and ensure it points to a valid image file (JPEG, PNG, or WebP).
- The service must resize the image into the following sizes (width x height): 320x240, 640x480, 1024x768, 1920x1080.
- The resizing process must maintain the aspect ratio of the original image.  The height should be calculated from the requested width by keeping the aspect ratio.
- The resized images must be stored in a cloud storage bucket.  The specific bucket name is defined via environment variables.
- The service must return a JSON response containing the URLs of the resized images.
- The service must handle errors gracefully and return appropriate error messages.
- The service must be implemented using FastAPI and Pydantic.
- The service must be able to handle concurrent requests.
- The service must log all requests and errors.
- The service must implement appropriate rate limiting to prevent abuse.
- The image resizing should be done using a high-quality resizing algorithm (e.g., Lanczos resampling).
- Generated files must include the original filename + width in the cloud bucket.
- All the bucket paths must start with "images/".
- The service must utilize environment variables for cloud storage credentials and bucket name.

## Data Contract

**Request (POST /images/generate):**

```json
{
  "image_url": "string"
}
```

**Pydantic Model:**

```python
from pydantic import BaseModel, HttpUrl

class ImageGenerationRequest(BaseModel):
  image_url: HttpUrl
```

**Response (200 OK):**

```json
{
  "original_url": "string",
  "sizes": {
    "320": "string",
    "640": "string",
    "1024": "string",
    "1920": "string"
  }
}
```

**Pydantic Model:**

```python
from pydantic import BaseModel, HttpUrl

class ImageGenerationResponse(BaseModel):
    original_url: HttpUrl
    sizes: dict[str, HttpUrl]  # Key is width as string, value is URL
```

**Error Response (400 Bad Request, 500 Internal Server Error):**

```json
{
  "detail": "string"
}
```

## Behavior Scenarios

- **Scenario:** Valid Image URL
  - Input: `{"image_url": "https://example.com/image.jpg"}`
  - Outcome: The service resizes the image, stores the resized images in the cloud storage bucket, and returns a JSON response containing the URLs of the resized images.
- **Scenario:** Invalid Image URL (Non-image file)
  - Input: `{"image_url": "https://example.com/document.pdf"}`
  - Outcome: The service returns a 400 Bad Request error with the message "Invalid image URL: Not a valid image file."
- **Scenario:** Invalid Image URL (URL does not exist)
  - Input: `{"image_url": "https://example.com/nonexistent_image.jpg"}`
  - Outcome: The service returns a 400 Bad Request error with the message "Invalid image URL: Could not retrieve image."
- **Scenario:** Image Resizing Error
  - Input: `{"image_url": "https://example.com/image.jpg"}`
  - Outcome: If an error occurs during image resizing, the service returns a 500 Internal Server Error with a descriptive error message. The error should be logged.
- **Scenario:** Valid Image URL containing spaces
  - Input: `{"image_url": "https://example.com/image with spaces.jpg"}`
  - Outcome: The service correctly handles the URL, resizes the image, stores the resized images in the cloud storage bucket with spaces replaced (e.g., underscores), and returns a JSON response containing the URLs of the resized images.  The spaces should be converted to underscores in the cloud storage filename.
- **Scenario:** Correct cloud path
  - Input: `{"image_url": "https://example.com/image.jpg"}`
  - Outcome: The generated files must be uploaded to `images/image_320.jpg`, `images/image_640.jpg`, etc...

## Out of Scope
- Authentication and Authorization.
- Image format conversion (the service only handles JPEG, PNG and WebP).
- Advanced image manipulation features (e.g., watermarking, cropping).
- Monitoring and alerting.
- Detailed error reporting beyond a descriptive message.
