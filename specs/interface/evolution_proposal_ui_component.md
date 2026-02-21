# Spec: Evolution Proposal UI Component
**Target:** src/components/strategy/EvolutionProposal.tsx

## Overview
This component provides a UI for displaying and interacting with an evolution proposal. It allows users to view the details of the proposal and optionally approve or reject it. The UI must be visually clear and easy to use, with a dark theme consistent with the overall application style.

## Requirements
- The component must fetch the evolution proposal data from a backend API endpoint.
- The component must display the following proposal details:
  - Proposal ID
  - Proposer ID
  - Timestamp of proposal
  - Current State Name
  - Next State Name
  - Justification for the transition
  - Attachments (list of files/links, if any)
  - Approval Status (Pending, Approved, Rejected)
- The component should display an error message if the data fetch fails.
- If the Approval Status is "Pending," display "Approve" and "Reject" buttons.
- Clicking "Approve" or "Reject" should send a request to the backend API.
- The UI should update to reflect the new approval status after a successful approval/rejection.
- The UI should display a loading indicator while fetching data or submitting approval/rejection.
- The component must be responsive and display correctly on various screen sizes.
- All text should be rendered with sufficient contrast to be easily readable.

## Data Contract

**API Endpoint:** `/api/evolution_proposal/{proposal_id}` (GET)

**Request Parameters:**
- `proposal_id`: string (UUID) - The ID of the evolution proposal to retrieve.

**Response Body (Successful - 200 OK):**

```json
{
  "proposal_id": "string",
  "proposer_id": "string",
  "timestamp": "string",
  "current_state_name": "string",
  "next_state_name": "string",
  "justification": "string",
  "attachments": [
    {
      "filename": "string",
      "url": "string"
    }
  ],
  "approval_status": "Pending" | "Approved" | "Rejected"
}
```

**Response Body (Error - 404 Not Found):**

```json
{
  "detail": "Evolution Proposal not found"
}
```

**API Endpoint:** `/api/evolution_proposal/{proposal_id}/approve` (POST)

**Request Parameters:**
- `proposal_id`: string (UUID) - The ID of the evolution proposal to approve.

**Response Body (Successful - 200 OK):**
```json
{
  "message": "Evolution proposal approved"
}
```

**API Endpoint:** `/api/evolution_proposal/{proposal_id}/reject` (POST)

**Request Parameters:**
- `proposal_id`: string (UUID) - The ID of the evolution proposal to reject.

**Response Body (Successful - 200 OK):**
```json
{
  "message": "Evolution proposal rejected"
}
```

**Error Handling:**
- The React component must gracefully handle 404 errors and other API errors.  Display a user-friendly error message.

## Behavior Scenarios

- **Scenario:** Initial Load - Proposal Exists and is Pending
  - Input: Component is mounted with `proposalId = "some_valid_uuid"`
  - Outcome:
    - A loading indicator is displayed.
    - A GET request is made to `/api/evolution_proposal/some_valid_uuid`.
    - Upon successful response (200 OK), the proposal details are rendered, including proposal ID, proposer ID, timestamp, current state, next state, justification, attachments, and approval status "Pending."
    - "Approve" and "Reject" buttons are visible.
    - The loading indicator is hidden.

- **Scenario:** Initial Load - Proposal Does Not Exist
  - Input: Component is mounted with `proposalId = "some_invalid_uuid"`
  - Outcome:
    - A loading indicator is displayed.
    - A GET request is made to `/api/evolution_proposal/some_invalid_uuid`.
    - Upon receiving a 404 error, an error message "Evolution Proposal not found" is displayed to the user.
    - The loading indicator is hidden.
    - "Approve" and "Reject" buttons are hidden.

- **Scenario:** Approve Proposal
  - Input: User clicks the "Approve" button.
  - Outcome:
    - A POST request is made to `/api/evolution_proposal/some_valid_uuid/approve`.
    - The "Approve" and "Reject" buttons are disabled and a loading indicator appears next to them.
    - Upon successful response (200 OK), the approval status is updated to "Approved" in the UI.
    - The "Approve" and "Reject" buttons are hidden.
    - The loading indicator next to buttons is hidden.

- **Scenario:** Reject Proposal
  - Input: User clicks the "Reject" button.
  - Outcome:
    - A POST request is made to `/api/evolution_proposal/some_valid_uuid/reject`.
    - The "Approve" and "Reject" buttons are disabled and a loading indicator appears next to them.
    - Upon successful response (200 OK), the approval status is updated to "Rejected" in the UI.
    - The "Approve" and "Reject" buttons are hidden.
    - The loading indicator next to buttons is hidden.

- **Scenario:** Proposal Already Approved
  - Input: Component is mounted with `proposalId = "some_valid_uuid"` and the proposal data returns with `"approval_status": "Approved"`
  - Outcome:
    - A GET request is made to `/api/evolution_proposal/some_valid_uuid`.
    - Upon successful response (200 OK), the proposal details are rendered, including proposal ID, proposer ID, timestamp, current state, next state, justification, attachments, and approval status "Approved."
    - "Approve" and "Reject" buttons are NOT visible.

- **Scenario:** Attachment List is Empty
  - Input: Component is mounted with `proposalId = "some_valid_uuid"` and the proposal data returns with `"attachments": []`
  - Outcome: The component renders the proposal details without displaying an attachments section.

## Out of Scope
- Authentication and authorization of users. This component assumes the user is already authenticated.
- Navigation to other pages.
- Complex UI elements beyond basic text display and button interactions.
- Real-time updates (e.g., using WebSockets). The component fetches the data only on mount and after approval/rejection actions.
