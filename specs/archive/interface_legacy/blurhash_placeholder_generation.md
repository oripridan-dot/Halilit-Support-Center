# Spec: BlurHash Placeholder Generation
**Target:** data_pipeline/blurhash_placeholder_generation.py

## Overview
This script generates BlurHash strings for images stored in our Halilit Support Center's asset storage. These BlurHashes will be used as low-resolution placeholders while the full-resolution images load, improving perceived performance and user experience. The script will process images in batches, using a configurable concurrency level for faster processing.

## Requirements
- The script must accept an input directory containing images and an output file path for storing the JSON with image paths and corresponding BlurHashes.
- The script must efficiently process images in parallel using a configurable number of worker processes.
- The script must use the BlurHash algorithm to generate placeholder strings.
- The script must handle common image formats (JPEG, PNG, GIF).
- The script must log errors and exceptions during processing, without crashing the script.
- The generated BlurHash strings should be of reasonable quality (e.g., use a resolution of 4x3).
- The script should be re-runnable, only processing images that do not already have an entry in the existing output file (if it exists).
- The script must be configurable via command-line arguments.

## Data Contract

**Input:**

- `input_dir`:  Path to the directory containing images.
- `output_file`: Path to the JSON file where BlurHash data will be stored.  The file should contain a JSON object where keys are file paths (relative to the input directory) and values are their respective BlurHash strings.
- `num_workers`: Number of worker processes to use for parallel processing (integer).
- `blurhash_x`: The x component for the BlurHash algorithm (integer).
- `blurhash_y`: The y component for the BlurHash algorithm (integer).

**Output (JSON file):**

```json
{
  "path/to/image1.jpg": "UFMVC5n20M0000000000t6WB-oIp",
  "path/to/image2.png": "L35k:W00004n4T00000000j[xt",
  "...": "..."
}
```

## Behavior Scenarios

- **Scenario: New Image Directory**
  - Input: `input_dir` contains a directory with JPEG and PNG images; `output_file` does not exist; `num_workers` is 4; `blurhash_x` is 4; `blurhash_y` is 3.
  - Outcome: All images in `input_dir` are processed, BlurHashes are generated, and a new `output_file` is created containing the image paths and their BlurHashes. The script outputs logs showing progress, and any errors encountered.

- **Scenario: Existing Output File with Some Images Processed**
  - Input: `input_dir` contains JPEG and PNG images; `output_file` exists, containing BlurHashes for some of the images; `num_workers` is 2; `blurhash_x` is 4; `blurhash_y` is 3.
  - Outcome: Only images in `input_dir` that are *not* already present in `output_file` are processed. New BlurHashes are appended to the existing `output_file`, without altering pre-existing entries.  The script outputs logs showing progress, specifically mentioning how many files were skipped, and any errors encountered.

- **Scenario: Invalid Image File**
  - Input: `input_dir` contains a valid JPEG image and an invalid file (e.g., a text file with a `.jpg` extension); `output_file` does not exist; `num_workers` is 1; `blurhash_x` is 4; `blurhash_y` is 3.
  - Outcome: The valid JPEG image is processed and a BlurHash is generated. The script logs an error message for the invalid file, indicating that it could not be processed, but the script continues processing other files. The `output_file` contains only the valid image and its blurhash.

- **Scenario: Empty Input Directory**
  - Input: `input_dir` is an empty directory; `output_file` does not exist; `num_workers` is 1; `blurhash_x` is 4; `blurhash_y` is 3.
  - Outcome: The script logs a message indicating that the input directory is empty and exits gracefully, creating an empty `output_file` (an empty JSON object `{}`).

## Out of Scope

- This script does *not* handle image resizing or other image manipulations beyond what is necessary for BlurHash generation.
- This script does *not* include error handling for filesystem permissions issues.  It is assumed that the script has read access to the input directory and write access to the output file.
- The script does not perform validation of image file extensions or content to ensure that an extension is truly reflective of file type. The Pillow library should handle cases where the file format can be autodetected. If Pillow throws an exception, we consider the file invalid.
- The script does not generate thumbnails or other derivative image formats.

```python
# data_pipeline/blurhash_placeholder_generation.py
import os
import json
import argparse
from PIL import Image
import blurhash
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_blurhash(image_path: str, x_components: int, y_components: int) -> str:
    """Generates a BlurHash string for a given image."""
    try:
        image = Image.open(image_path)
        return blurhash.encode(x_components, y_components, *image.convert("RGB").resize((32, 32)).getdata(), width=image.width, height=image.height)
    except Exception as e:
        logging.error(f"Error processing {image_path}: {e}")
        return None

def process_image(image_path: str, x_components: int, y_components: int, input_dir: str) -> tuple[str, str] | None:
    """Processes a single image and returns its path and BlurHash."""
    try:
        relative_path = os.path.relpath(image_path, input_dir)
        blurhash_str = generate_blurhash(image_path, x_components, y_components)
        if blurhash_str:
            return relative_path, blurhash_str
        else:
            return None
    except Exception as e:
        logging.error(f"Error processing {image_path}: {e}")
        return None


def main(input_dir: str, output_file: str, num_workers: int, blurhash_x: int, blurhash_y: int):
    """Main function to process images and generate BlurHashes."""
    logging.info(f"Starting BlurHash generation for images in {input_dir} using {num_workers} workers.")

    image_paths = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                image_paths.append(os.path.join(root, file))

    if not image_paths:
        logging.info("No images found in the input directory.")
        with open(output_file, 'w') as f:
            json.dump({}, f) # Create an empty file
        return

    # Load existing BlurHashes
    existing_data: Dict[str, str] = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            logging.warning(f"Output file {output_file} is corrupt. Overwriting.")

    # Filter out already processed images
    images_to_process = [
        image_path for image_path in image_paths
        if os.path.relpath(image_path, input_dir) not in existing_data
    ]

    num_skipped = len(image_paths) - len(images_to_process)
    if num_skipped > 0:
        logging.info(f"Skipping {num_skipped} already processed images.")

    if not images_to_process:
        logging.info("All images already processed.")
        return

    # Process images in parallel
    new_data: Dict[str, str] = {}
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(process_image, image_path, blurhash_x, blurhash_y, input_dir) for image_path in images_to_process]
        for future in as_completed(futures):
            result = future.result()
            if result:
                relative_path, blurhash_str = result
                new_data[relative_path] = blurhash_str

    # Merge new data with existing data
    updated_data = {**existing_data, **new_data}

    # Write updated data to file
    with open(output_file, 'w') as f:
        json.dump(updated_data, f, indent=2)

    logging.info(f"BlurHash generation complete. Results saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate BlurHash placeholders for images.")
    parser.add_argument("input_dir", help="Path to the directory containing images.")
    parser.add_argument("output_file", help="Path to the JSON file to store BlurHash data.")
    parser.add_argument("--num_workers", type=int, default=4, help="Number of worker processes to use.")
    parser.add_argument("--blurhash_x", type=int, default=4, help="The x component for the BlurHash algorithm.")
    parser.add_argument("--blurhash_y", type=int, default=3, help="The y component for the BlurHash algorithm.")

    args = parser.parse_args()

    main(args.input_dir, args.output_file, args.num_workers, args.blurhash_x, args.blurhash_y)
```