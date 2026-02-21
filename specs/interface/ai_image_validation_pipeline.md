# Spec: AI Image Validation Pipeline

**Target:** data_pipeline/ai_image_validation.py

## Overview
This script defines a data pipeline to validate images uploaded by users of the Halilit Support Center, ensuring they adhere to quality and content standards before being used in support tickets or knowledge base articles. It leverages an AI model to check image dimensions, file size, and the presence of inappropriate content.

## Requirements
- [x] The script must accept an image file path as input.
- [x] The script must load the image from the specified file path.
- [x] The script must validate the image dimensions against a minimum resolution of 256x256 pixels.
- [x] The script must validate the image file size against a maximum limit of 5MB.
- [x] The script must integrate with an AI-powered content moderation service to detect inappropriate content (e.g., violence, nudity, hate speech).
- [x] The script must return a JSON object indicating the validation status (pass/fail) and reasons for failure, if any.
- [x] The script must log all validation attempts and results, including timestamps.
- [x] The script must handle potential errors gracefully, such as invalid file paths, unsupported image formats, and service unavailability of the AI content moderation service.
- [x] The script should be configurable via environment variables for parameters like minimum resolution, maximum file size, and AI service API key.
- [x] The AI content moderation service should be abstracted through an interface to allow for easy swapping of providers (e.g., Sightengine, Amazon Rekognition).

## Data Contract

**Input:**

```python
{
    "image_path": str  # Absolute path to the image file.
}
```

**Output:**

```python
{
    "is_valid": bool,  # True if the image passes all validation checks, False otherwise.
    "errors": List[str] # A list of error messages, empty if the image is valid.
}
```

## Behavior Scenarios

- **Scenario:** Valid Image
  - Input: `image_path`: "/path/to/valid_image.jpg" (256x256 pixels, 4MB, no inappropriate content)
  - Outcome: `{"is_valid": True, "errors": []}` and a log entry indicating successful validation.

- **Scenario:** Image Too Small
  - Input: `image_path`: "/path/to/small_image.png" (128x128 pixels, 1MB, no inappropriate content)
  - Outcome: `{"is_valid": False, "errors": ["Image dimensions are below the minimum resolution of 256x256 pixels."]}` and a log entry indicating failure due to image dimensions.

- **Scenario:** Image Too Large
  - Input: `image_path`: "/path/to/large_image.jpeg" (512x512 pixels, 6MB, no inappropriate content)
  - Outcome: `{"is_valid": False, "errors": ["Image file size exceeds the maximum limit of 5MB."]}` and a log entry indicating failure due to file size.

- **Scenario:** Inappropriate Content Detected
  - Input: `image_path`: "/path/to/inappropriate_image.gif" (256x256 pixels, 2MB, inappropriate content)
  - Outcome: `{"is_valid": False, "errors": ["Inappropriate content detected by content moderation service."]}` and a log entry indicating failure due to inappropriate content.

- **Scenario:** Invalid File Path
  - Input: `image_path`: "/path/to/nonexistent_image.bmp"
  - Outcome: `{"is_valid": False, "errors": ["Invalid file path or unsupported image format."]}` and a log entry indicating failure due to file path.

- **Scenario:** AI Service Unavailable
  - Input: `image_path`: "/path/to/valid_image.jpg" (256x256 pixels, 4MB, no inappropriate content) when the AI content moderation service is unavailable.
  - Outcome: `{"is_valid": False, "errors": ["Content moderation service unavailable. Please try again later."]}` and a log entry indicating failure due to service unavailability.

## Out of Scope
- [Implementation of the AI content moderation service itself.]
- [Detailed error handling beyond logging and basic error messages.]
- [Specific AI content moderation service provider. The implementation uses an interface that can be configured to connect to multiple providers.]
