# Spec: Evolution Proposal Acceptance Button

**Target:** src/components/strategy/EvolutionProposalAcceptanceButton.tsx

## Overview
This component provides a button that allows authorized users to accept an evolution proposal within the Halilit Support Center's Dark Factory interface. Upon acceptance, the backend is notified to execute the proposed evolution, and the UI updates to reflect the change in status.

## Requirements
- The button should be visually distinct and clearly labeled "Accept Evolution Proposal".
- The button should be disabled unless the user has the necessary permissions (specifically, the `factory.evolve` permission).
- Clicking the button should trigger a confirmation modal.
- Upon confirmation, an API call should be made to the backend to initiate the evolution.
- The button should display a loading state while the API call is in progress.
- On successful evolution, a success message should be displayed to the user, and the button should be disabled.
- On failed evolution, an error message should be displayed to the user, and the button should remain enabled.
- The component should gracefully handle API errors, displaying informative messages to the user.
- The component should refresh the evolution proposal data after successful acceptance.

## Data Contract

**Props:**

```typescript
interface EvolutionProposalAcceptanceButtonProps {
  proposalId: string; // The ID of the evolution proposal.
  onSuccess: () => void; // Callback function to execute after successful evolution (e.g., to refresh data).
}
```

**Backend Endpoint (Example - `/api/evolution/{proposalId}/accept`):**

*   **Method:** POST
*   **Request Body:** (Empty - acceptance is triggered by the POST request itself)
*   **Response (Success - HTTP 200 OK):**

    ```json
    {
      "status": "accepted",
      "message": "Evolution proposal successfully executed.",
      "new_state": {
        "factory_version": "1.2.3" // Example data reflecting the new factory state
      }
    }
    ```

*   **Response (Failure - HTTP 400 Bad Request):**

    ```json
    {
      "status": "error",
      "message": "Failed to execute evolution proposal: Insufficient permissions.",
      "error_code": "INSUFFICIENT_PERMISSIONS" // Example error code
    }
    ```

*   **Response (Failure - HTTP 500 Internal Server Error):**

    ```json
    {
      "status": "error",
      "message": "Internal Server Error: Database connection failed.",
      "error_code": "DATABASE_ERROR"
    }
    ```

## Behavior Scenarios

- **Scenario:** User does not have `factory.evolve` permission.
  - Input: Component renders.
  - Outcome: The "Accept Evolution Proposal" button is disabled.

- **Scenario:** User has `factory.evolve` permission and clicks "Accept Evolution Proposal".
  - Input: User clicks the button.
  - Outcome: A confirmation modal appears, asking the user to confirm the action.

- **Scenario:** User confirms the evolution proposal.
  - Input: User clicks "Confirm" in the modal.
  - Outcome:
    - The button enters a loading state (e.g., displaying a spinner).
    - An API call is made to `/api/evolution/{proposalId}/accept`.

- **Scenario:** API call to `/api/evolution/{proposalId}/accept` is successful.
  - Input: API returns a 200 OK response with `status: "accepted"`.
  - Outcome:
    - A success message is displayed (e.g., "Evolution proposal successfully executed.").
    - The button is disabled.
    - The `onSuccess` callback is executed.

- **Scenario:** API call to `/api/evolution/{proposalId}/accept` returns a 400 Bad Request with `status: "error"`.
  - Input: API returns an error response.
  - Outcome:
    - An error message is displayed (e.g., "Failed to execute evolution proposal: Insufficient permissions.").
    - The button remains enabled.

- **Scenario:** API call to `/api/evolution/{proposalId}/accept` returns a 500 Internal Server Error with `status: "error"`.
  - Input: API returns a server error response.
  - Outcome:
    - An error message is displayed (e.g., "Internal Server Error: Please try again later.").
    - The button remains enabled.

- **Scenario:** User cancels the evolution proposal confirmation.
  - Input: User clicks "Cancel" in the modal.
  - Outcome:
    - The modal closes.
    - The button remains enabled.
    - No API calls are made.

## Out of Scope
- Implementation of the permission system itself. This spec assumes a helper function or React Context exists to determine user permissions.
- The confirmation modal component itself. This spec assumes a reusable modal component is available.
- The specific styling of the success and error messages (only the content is specified).
-  Detailed backend implementation of the evolution process after receiving the acceptance signal.
