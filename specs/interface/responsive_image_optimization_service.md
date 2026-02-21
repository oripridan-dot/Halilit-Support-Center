# Spec: Responsive Image Optimization Service

**Target:** backend/services/image_optimization.py

## Overview

This service provides an API endpoint for optimizing images uploaded to the Halilit Support Center Dark Factory. The optimization includes resizing the image to a set of predefined sizes to ensure responsiveness across various devices and screen resolutions. The service should use lossless compression techniques to reduce file size while preserving image quality.  The service will return URLs pointing to the optimized images stored in the object store.

## Requirements

- The service must accept image files via a POST request.
- The service must support JPEG, PNG, and WebP image formats.
- The service must resize the image to the following widths: 320px, 640px, 1024px, and 1920px, preserving aspect ratio.
- The service must use lossless compression during resizing.
- The service must store the optimized images in the Halilit object store, using a naming convention based on the original filename and resolution (e.g., `original_filename_320w.jpg`, `original_filename_640w.png`).
- The service must return a JSON response containing a dictionary of URLs for each generated image size, keyed by width.
- The service must handle potential errors gracefully, returning appropriate HTTP status codes and error messages.
- The service must be secured using API key authentication. API keys must be managed centrally and validated upon each request.
- The service must be able to handle requests concurrently without performance degradation.
- The service must log all requests and errors for monitoring and debugging purposes.
- The service must validate image dimensions before resizing. If either width or height are greater than 4096px, the request must be rejected.
- The object store interactions must be abstracted using a configuration-driven interface that allows for easy swapping between different object store implementations.

## Data Contract

**Request (POST /images/optimize)**

*   Headers:
    *   `X-API-Key`: String (Required)
    *   `Content-Type`: `multipart/form-data`
*   Body:
    *   `image`: File (Required) - The image file to optimize.

**Response (200 OK)**

```json
{
  "320": "https://halilit-object-store.example.com/images/original_filename_320w.jpg",
  "640": "https://halilit-object-store.example.com/images/original_filename_640w.jpg",
  "1024": "https://halilit-object-store.example.com/images/original_filename_1024w.jpg",
  "1920": "https://halilit-object-store.example.com/images/original_filename_1920w.jpg"
}
```

**Response (400 Bad Request - Invalid Image)**

```json
{
  "detail": "Invalid image format or dimensions."
}
```

**Response (401 Unauthorized)**

```json
{
  "detail": "Invalid API Key"
}
```

**Response (500 Internal Server Error)**

```json
{
  "detail": "An unexpected error occurred."
}
```

## Behavior Scenarios

- **Scenario:** Successful Image Optimization
  - Input: POST request to `/images/optimize` with a valid JPEG image and a valid API key.
  - Outcome: Returns a 200 OK response with a JSON payload containing URLs for the resized images. The images are stored in the object store.

- **Scenario:** Invalid Image Format
  - Input: POST request to `/images/optimize` with a non-image file (e.g., a text file).
  - Outcome: Returns a 400 Bad Request response with the message "Invalid image format or dimensions.".

- **Scenario:** Image Dimensions Too Large
  - Input: POST request to `/images/optimize` with a valid image file, but either width or height exceeds 4096px.
  - Outcome: Returns a 400 Bad Request response with the message "Invalid image format or dimensions.".

- **Scenario:** Invalid API Key
  - Input: POST request to `/images/optimize` with a valid image file but an invalid API key.
  - Outcome: Returns a 401 Unauthorized response with the message "Invalid API Key".

- **Scenario:** Missing API Key
  - Input: POST request to `/images/optimize` with a valid image file but a missing API key.
  - Outcome: Returns a 401 Unauthorized response with the message "Invalid API Key".

- **Scenario:** Internal Server Error (Object Store Failure)
  - Input: POST request to `/images/optimize` with a valid image file, but the object store is unavailable.
  - Outcome: Returns a 500 Internal Server Error response with the message "An unexpected error occurred.". The error is logged.

## Out of Scope

- Image format conversion (e.g., converting all images to WebP).  This will be handled by a separate service, pre-ingestion.
- Advanced image manipulation (e.g., watermarking, face detection).
- Dynamic resizing based on user-specified dimensions.
- Monitoring and alerting for the service (handled by separate infrastructure).
- API Key creation and management (handled by separate admin service).
