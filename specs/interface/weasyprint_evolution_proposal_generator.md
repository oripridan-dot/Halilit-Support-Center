# Spec: Weasyprint Evolution Proposal Generator

**Target:** /src/backend/services/evolution_proposals.py

## Overview
This backend service generates an Evolution Proposal (EP) document based on Weasyprint's current state, justification for proposed changes, and usage guidelines for developers. The service takes a JSON payload containing the proposal details and returns a PDF document representing the EP.

## Requirements
- The service must accept a JSON payload containing the following fields:
    - `title`: Title of the Evolution Proposal (string).
    - `author`: Author of the Evolution Proposal (string).
    - `date`: Date of the proposal (YYYY-MM-DD string).
    - `current_state`: Description of Weasyprint's current state related to the proposal (string).
    - `justification`: Justification for the proposed changes (string).
    - `proposed_changes`: Detailed description of the proposed changes (string).
    - `usage_guidelines`: Guidelines for developers on how to use the new features or changes (string).
- The service must generate a PDF document from the provided data using Weasyprint.
- The PDF document should contain a title page with the title, author, and date.
- The PDF document should include sections for "Current State", "Justification", "Proposed Changes", and "Usage Guidelines", populated with the corresponding data from the JSON payload.
- The service must handle potential Weasyprint exceptions and return an appropriate error response.
- The service must use a consistent styling for the generated PDF using CSS. This styling should be defined within the service.
- The generated PDF should be named based on the title of the evolution proposal, replacing spaces with underscores and appending ".pdf".

## Data Contract

**Request (POST /evolution_proposals):**

```json
{
  "title": "string",
  "author": "string",
  "date": "YYYY-MM-DD",
  "current_state": "string",
  "justification": "string",
  "proposed_changes": "string",
  "usage_guidelines": "string"
}
```

**Response (200 OK):**

Returns a PDF file as a binary stream with `Content-Type: application/pdf` and `Content-Disposition: attachment; filename="{title.replace(' ', '_')}.pdf"`.

**Error Response (400 Bad Request):**

```json
{
  "detail": "string"  // Error message describing the problem
}
```

## Behavior Scenarios
- **Scenario:** Valid Evolution Proposal Data
  - Input:
    ```json
    {
      "title": "Improve CSS Grid Layout Support",
      "author": "Jane Doe",
      "date": "2024-10-27",
      "current_state": "Weasyprint's CSS Grid Layout support is currently incomplete, missing several key features.",
      "justification": "Improved Grid Layout support will significantly enhance Weasyprint's rendering capabilities and allow for more complex layouts.",
      "proposed_changes": "Implement support for `grid-template-areas`, `grid-auto-flow`, and more advanced grid placement properties.",
      "usage_guidelines": "Developers can now use the newly supported Grid Layout properties to create more flexible and responsive layouts. Refer to the Weasyprint documentation for detailed usage examples."
    }
    ```
  - Outcome: A PDF file named `Improve_CSS_Grid_Layout_Support.pdf` is generated and returned as a downloadable attachment.  The PDF contains a title page and sections for current state, justification, proposed changes, and usage guidelines, all populated with the input data.

- **Scenario:** Invalid Date Format
  - Input:
    ```json
    {
      "title": "Improve CSS Grid Layout Support",
      "author": "Jane Doe",
      "date": "2024/10/27",
      "current_state": "Weasyprint's CSS Grid Layout support is currently incomplete, missing several key features.",
      "justification": "Improved Grid Layout support will significantly enhance Weasyprint's rendering capabilities and allow for more complex layouts.",
      "proposed_changes": "Implement support for `grid-template-areas`, `grid-auto-flow`, and more advanced grid placement properties.",
      "usage_guidelines": "Developers can now use the newly supported Grid Layout properties to create more flexible and responsive layouts. Refer to the Weasyprint documentation for detailed usage examples."
    }
    ```
  - Outcome: The service returns a 400 Bad Request error with a JSON response containing a detailed error message, such as `{"detail": "Invalid date format.  Use YYYY-MM-DD."}`.

- **Scenario:** Weasyprint Fails to Generate PDF
  - Input: A valid JSON payload, but the content within leads to an error during Weasyprint PDF generation (e.g., invalid CSS within a generated HTML template).
  - Outcome: The service returns a 500 Internal Server Error with a JSON response containing a detailed error message from Weasyprint's exception, such as `{"detail": "Weasyprint error: ...[Weasyprint error message]..."}`.

## Out of Scope
- User authentication or authorization.
- Input data validation beyond basic type and format checking (Pydantic will handle the `date` format).
- Storage of generated PDFs. The service only generates and returns the PDF as a response.
- Advanced PDF customization options (e.g., specifying fonts, margins, or other styling options beyond the basic, pre-defined CSS).
