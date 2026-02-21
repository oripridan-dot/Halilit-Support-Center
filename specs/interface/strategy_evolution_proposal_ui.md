# Spec: Strategy Evolution Proposal UI

**Target:** src/components/strategy/StrategyEvolutionProposal.tsx

## Overview
This React component allows users to propose new evolution steps for a production strategy in the "Halilit Support Center — Dark Factory" application. It presents a form where users can input details about the proposed evolution, including a description, justification, and estimated impact. Upon submission, the proposal is sent to the backend for review and approval.

## Requirements
- The component must be implemented in React 18 with TypeScript and styled using Tailwind CSS, adhering to the dark theme and using the slate-900/blue-500 palette.
- The component must include input fields for the following:
  - Proposal Title (text input, required)
  - Description (text area, required)
  - Justification (text area, required)
  - Estimated Impact (select dropdown with options: "Low", "Medium", "High", required)
- The component must include a submit button labeled "Submit Proposal".
- The component must display validation errors for required fields.
- On successful submission, the component should display a success message to the user for 3 seconds.
- The component must call a backend API endpoint to submit the proposal data.
- The component should handle potential errors from the backend API (e.g., network errors, validation errors) and display appropriate error messages to the user.
- The input fields must be clearly labeled and accessible.
- The component must implement loading state on submission, disabling the button and displaying a loading indicator.

## Data Contract
**API Endpoint:** `POST /api/strategy/evolution/proposals`

**Request Body (JSON):**

```typescript
interface EvolutionProposalRequest {
  title: string;
  description: string;
  justification: string;
  estimated_impact: "Low" | "Medium" | "High";
}
```

**Response (JSON):**

*Success:*
```typescript
interface EvolutionProposalSuccessResponse {
  id: string; // UUID of the created proposal
  message: string; // "Proposal submitted successfully"
}
```

*Error:*
```typescript
interface EvolutionProposalErrorResponse {
  detail: string | object; // Error message or validation errors
}
```

**Component Props:**
None.

## Behavior Scenarios
- **Scenario:** Successful Proposal Submission
  - Input: User fills out the form with valid data and clicks "Submit Proposal".
  - Outcome:
    - The button is disabled and a loading indicator is displayed.
    - A `POST` request is sent to `/api/strategy/evolution/proposals` with the proposal data.
    - Upon receiving a successful response from the backend, a success message "Proposal submitted successfully" is displayed for 3 seconds.
    - The form fields are cleared.

- **Scenario:** Validation Error
  - Input: User clicks "Submit Proposal" without filling out required fields.
  - Outcome:
    - Validation errors are displayed next to the empty required fields, indicating that they are required.
    - The form submission is prevented.

- **Scenario:** Backend API Error (e.g., 500 Internal Server Error)
  - Input: User fills out the form and clicks "Submit Proposal", but the backend returns an error.
  - Outcome:
    - An error message is displayed to the user indicating that there was an error submitting the proposal.
    - The error message should not reveal sensitive information about the backend.
    - The button is re-enabled.

- **Scenario:** Backend API Validation Error (e.g., invalid data format)
  - Input: User fills out the form with invalid data (e.g., a title that is too long) and clicks "Submit Proposal", and the backend returns validation errors.
  - Outcome:
    - Specific error messages from the backend are displayed next to the corresponding form fields.
    - The button is re-enabled.

## Out of Scope
- Authentication and authorization (assuming the user is already authenticated).
- Management of the proposal review and approval process (handled by a separate service).
- Displaying existing proposals.
- UI styling beyond the basic dark theme and color palette specified.
