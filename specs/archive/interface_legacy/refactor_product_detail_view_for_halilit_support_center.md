# Spec: Refactor Product Detail View for Halilit Support Center
**Target:** src/components/ProductDetail/ProductDetailView.tsx

## Overview
This specification details the refactoring of the Product Detail View within the Halilit Support Center "Dark Factory" to improve code maintainability, readability, and performance. The refactor includes adopting a component-based architecture, leveraging Tailwind CSS for styling, and ensuring a consistent dark theme. The view will display product information fetched from a backend API.

## Requirements
- The Product Detail View must display detailed information about a specific product, including its name, description, serial number (if available), associated documents (e.g., manuals, schematics), and troubleshooting guides.
- The view must fetch product data from a backend API endpoint `/products/{product_id}`.
- The view must implement proper error handling for API requests, displaying informative error messages to the user.
- The view must use React 18 functional components with TypeScript.
- The view must be styled using Tailwind CSS, adhering to the dark theme (slate-900 background, blue-500 accents).
- The view must implement responsive design for optimal viewing on different screen sizes.
- The view should be divided into logical sub-components for better organization and reusability. Suggested components: `ProductInfo`, `ProductDocuments`, `ProductTroubleshooting`.
- Implement skeleton loading state while data is being fetched from the API.

## Data Contract

**API Endpoint:** `/products/{product_id}` (GET)

**Request:**
- `product_id` (path parameter): Integer representing the unique identifier of the product.

**Response (Success - 200 OK):**
```json
{
  "id": int,
  "name": str,
  "description": str,
  "serial_number": str | None,
  "documents": list[dict],
  "troubleshooting_guides": list[dict]
}
```
Where:
- `id`: Integer, unique identifier of the product.
- `name`: String, name of the product.
- `description`: String, detailed description of the product.
- `serial_number`: String or null, the product's serial number (may be absent).
- `documents`: List of document objects. Each document object contains:
  ```json
  {
    "id": int,
    "name": str,
    "url": str,
    "type": str // e.g., "manual", "schematic"
  }
  ```
- `troubleshooting_guides`: List of troubleshooting guide objects. Each guide object contains:
  ```json
  {
    "id": int,
    "title": str,
    "steps": list[str]
  }
  ```

**Response (Error - 404 Not Found):**
```json
{
  "detail": "Product not found"
}
```

**Response (Error - 500 Internal Server Error):**
```json
{
  "detail": "Internal Server Error"
}
```

## Behavior Scenarios

- **Scenario:** Successful Product Load
  - Input: `product_id` = 123 (exists in the backend).
  - Outcome: The view displays the product's name, description, serial number (if available), associated documents as clickable links, and troubleshooting guides with their respective steps.  The loading indicator is removed.

- **Scenario:** Product Not Found
  - Input: `product_id` = 999 (does not exist in the backend).
  - Outcome: The view displays an error message "Product not found" to the user.

- **Scenario:** API Request Fails (e.g., network error)
  - Input: No `product_id` (or backend is unavailable).
  - Outcome: The view displays a generic error message "Failed to load product details. Please try again later."

- **Scenario:** Loading State
  - Input: Initial page load with `product_id` provided, while API request is in progress.
  - Outcome: The view displays a skeleton loading state, with placeholder elements for the product name, description, documents, and troubleshooting guides.

- **Scenario:** Product has no Serial Number
  - Input: `product_id` refers to a product with `serial_number` set to `null` in the database.
  - Outcome: The view displays the product information but omits the serial number field, or displays "Serial Number: Not Available".

## Out of Scope
- Authentication and authorization.
- Modification of product data (editing).
- Specific error reporting mechanisms (e.g., logging to a server). These errors should be displayed as user-friendly messages within the view.
- Implementing a search functionality for products.
