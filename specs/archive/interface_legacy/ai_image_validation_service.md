# Spec: AI Image Validation Service

**Target:** data_pipeline/services/ai_image_validation.py

## Overview
This service provides an endpoint for validating images uploaded to the Halilit Support Center using an AI model. The service receives an image and returns a validation score indicating the image's suitability for use in support documentation, specifically checking for clarity, appropriate content (e.g., not offensive or irrelevant), and Halilit product focus.

## Requirements
- [x] Implement a FastAPI endpoint at `/validate_image` that accepts an image file.
- [x] Integrate with a pre-trained AI model (details below) for image analysis.
- [x] Return a JSON response containing a `validation_score` (float between 0 and 1, higher is better) and a `reason` string (brief explanation of the score).
- [x] Implement error handling for invalid image formats, AI model failures, and other exceptions.
- [x] The AI model must be configurable via environment variables to allow for switching models and versions.
- [x] Include logging for all requests, responses, and errors.
- [x] Comply with Halilit's data privacy policy regarding image storage and processing. The service should **not** permanently store images.
- [x] Authenticate requests to the `/validate_image` endpoint using API key authentication.
- [x] Rate limit the `/validate_image` endpoint to prevent abuse.

## Data Contract

**Request Body (multipart/form-data):**
```json
{
  "image": "file" // Image file to be validated.  Supported formats: JPEG, PNG.
}
```

**Response (JSON):**
```json
{
  "validation_score": 0.85,
  "reason": "Image is clear, shows a Halilit product, and is relevant to support."
}
```

**Error Responses (JSON):**

*   `400 Bad Request`: Invalid image format.
    ```json
    {
      "detail": "Invalid image format. Supported formats are JPEG and PNG."
    }
    ```
*   `500 Internal Server Error`: AI model failure.
    ```json
    {
      "detail": "AI model failed to process the image."
    }
    ```
*   `401 Unauthorized`: Invalid API key.
    ```json
    {
      "detail": "Invalid API Key"
    }
    ```
*   `429 Too Many Requests`: Rate limit exceeded.
    ```json
    {
      "detail": "Rate limit exceeded. Please try again later."
    }
    ```

## Behavior Scenarios

- **Scenario:** Valid Image
  - Input: A clear JPEG image of a Halilit xylophone with a child playing it.
  - Outcome: Returns a JSON response with a high `validation_score` (e.g., 0.9) and a `reason` such as "Image is clear, shows a Halilit product, and is relevant to support."

- **Scenario:** Blurry Image
  - Input: A blurry PNG image of a Halilit maraca.
  - Outcome: Returns a JSON response with a medium `validation_score` (e.g., 0.5) and a `reason` such as "Image is somewhat blurry and could be clearer."

- **Scenario:** Offensive Image
  - Input: A JPEG image containing offensive content.
  - Outcome: Returns a JSON response with a low `validation_score` (e.g., 0.1) and a `reason` such as "Image contains inappropriate content."

- **Scenario:** Non-Halilit Product Image
  - Input: A PNG image of a non-Halilit musical instrument.
  - Outcome: Returns a JSON response with a low `validation_score` (e.g., 0.2) and a `reason` such as "Image does not contain a Halilit product."

- **Scenario:** Invalid Image Format
  - Input: A TIFF image.
  - Outcome: Returns a 400 Bad Request error with the message "Invalid image format. Supported formats are JPEG and PNG."

- **Scenario:** AI Model Failure
    - Input: A valid JPEG image, but the AI model throws an exception.
    - Outcome: Returns a 500 Internal Server Error with the message "AI model failed to process the image."

- **Scenario:** Unauthorized Request
    - Input: Valid JPEG Image, but no API key.
    - Outcome: Returns a 401 Unauthorized error with the message "Invalid API Key"

- **Scenario:** Rate Limit Exceeded
    - Input: Rapid consecutive requests within a short timeframe.
    - Outcome: Returns a 429 Too Many Requests error with the message "Rate limit exceeded. Please try again later."

## Out of Scope

- [Training or fine-tuning the AI model itself.]
- [Implementing a UI for uploading images.]
- [Detailed performance metrics beyond basic logging.]
- [Specific AI model selection (this will be handled separately, but the service must be configurable to use different models).]
