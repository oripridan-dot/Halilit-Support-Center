# Spec: Responsive Image Generation Pipeline
**Target:** data_pipeline/responsive_image_generation.py

## Overview
This data pipeline service automatically generates responsive image renditions (different sizes and formats) from source images uploaded to cloud storage.  This ensures optimal image delivery across various devices and network conditions for the Halilit Support Center Dark Factory website, reducing bandwidth consumption and improving page load times. The pipeline is triggered upon new image uploads to a designated cloud storage bucket.

## Requirements
- [x] Listen for new image upload events in the designated cloud storage bucket (`halilit-dark-factory-images`).
- [x] Support the following image formats: `jpeg`, `png`, `webp`, `avif`.
- [x] Generate the following image sizes (width in pixels): `320`, `640`, `960`, `1280`, `1920`.  Height should be automatically adjusted to maintain aspect ratio.
- [x] Convert all images to `webp` format for all sizes, and retain the original format if it is `avif`.
- [x] Store the generated images in a designated output bucket (`halilit-dark-factory-images-resized`) with a directory structure that reflects the original image's path and filename.
- [x] Maintain the original filename (except for the webp extension), and add a suffix indicating the width. Example: `original_image.jpg` becomes `original_image-320.webp`, `original_image-640.webp`, etc.  If the original image is `avif`, retain the avif format.
- [x] Implement error handling and logging for failed image processing attempts, including notifying a designated monitoring service (e.g., Sentry).
- [x] The pipeline should be idempotent; re-processing the same source image should not result in errors or data corruption.
- [x] Configuration (bucket names, monitoring service DSN) should be externally configurable via environment variables.

## Data Contract

**Input (Cloud Storage Event):**
```python
class CloudStorageEvent(BaseModel):
    bucket: str
    name: str  # Path to the image in the bucket (e.g., "products/image1.jpg")
    metageneration: str # Used for idempotency. Process only the latest generation.
    resourceState: str # "exists" or "not_exists".  Only process when "exists"
    contentType: str # Mimetype of the file. e.g. "image/jpeg"

```

**Output (Generated Images):**
Stored in `halilit-dark-factory-images-resized` bucket.  Directory structure mimics the source bucket. Filenames are modified to include size suffix (e.g., `image-320.webp`).

## Behavior Scenarios

- **Scenario:** New JPEG image uploaded
  - Input: A new file `products/shirts/blue_shirt.jpg` is uploaded to `halilit-dark-factory-images`. `contentType` is `image/jpeg`.
  - Outcome: The following files are generated in `halilit-dark-factory-images-resized/products/shirts/`: `blue_shirt-320.webp`, `blue_shirt-640.webp`, `blue_shirt-960.webp`, `blue_shirt-1280.webp`, `blue_shirt-1920.webp`.

- **Scenario:** New PNG image uploaded
  - Input: A new file `marketing/banners/summer_sale.png` is uploaded to `halilit-dark-factory-images`. `contentType` is `image/png`.
  - Outcome: The following files are generated in `halilit-dark-factory-images-resized/marketing/banners/`: `summer_sale-320.webp`, `summer_sale-640.webp`, `summer_sale-960.webp`, `summer_sale-1280.webp`, `summer_sale-1920.webp`.

- **Scenario:** New AVIF image uploaded
  - Input: A new file `marketing/hero/new_product.avif` is uploaded to `halilit-dark-factory-images`. `contentType` is `image/avif`.
  - Outcome: The following files are generated in `halilit-dark-factory-images-resized/marketing/hero/`: `new_product-320.avif`, `new_product-640.avif`, `new_product-960.avif`, `new_product-1280.avif`, `new_product-1920.avif`.

- **Scenario:** Re-upload of existing image
  - Input: The file `products/shirts/blue_shirt.jpg` is re-uploaded to `halilit-dark-factory-images` with a new `metageneration` value, but the same content.
  - Outcome: The pipeline re-processes the image, overwriting the existing resized images in `halilit-dark-factory-images-resized/products/shirts/`.  The processing should complete without errors.

- **Scenario:** Upload of non-image file
  - Input: A new file `documents/report.pdf` is uploaded to `halilit-dark-factory-images`. `contentType` is `application/pdf`.
  - Outcome: The pipeline ignores the file and logs the event, but does not attempt to process it. No error is raised.

- **Scenario:** Image processing fails (e.g., corrupt image data)
  - Input: A corrupt JPEG file `products/shirts/corrupt.jpg` is uploaded to `halilit-dark-factory-images`.
  - Outcome: The pipeline catches the exception, logs the error (including the filename and error message), reports the error to the monitoring service, and does NOT create any resized images. The pipeline continues to listen for new events.

## Out of Scope
- [Image optimization techniques beyond resizing and format conversion (e.g., advanced compression, metadata stripping).]
- [Watermarking or other image manipulation features.]
- [Direct integration with the website's image delivery system (CDN integration is handled separately).]
- [Automatic deletion of source images after processing.]
