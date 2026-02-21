# Spec: Evolution Plan Visualization
**Target:** src/components/EvolutionPlan/EvolutionPlan.tsx

## Overview
This component visualizes the evolution plan for a given Halilit support strategy. It displays the plan as a series of ordered steps, each with a description and relevant metadata. The component should be responsive and visually clear, allowing operators to quickly understand the intended progression of a support strategy.

## Requirements
- The component must fetch evolution plan data from the `/api/evolution_plan/{strategy_id}` endpoint.
- The component must handle loading states gracefully, displaying a placeholder or loading indicator while data is being fetched.
- The component must display error states gracefully, informing the user if the data cannot be loaded.
- Each step in the evolution plan should display the following information:
  - Step Number
  - Description
  - Estimated time to completion (if available)
  - Status (e.g., "Pending", "In Progress", "Completed", "Blocked")
- The component must use a dark theme with slate-900/blue-500 palette.
- The component should be responsive and adapt to different screen sizes.
- The component must use Tailwind CSS for styling.
- The component must be implemented as a React 18 component using TypeScript.

## Data Contract

**API Endpoint:** `GET /api/evolution_plan/{strategy_id}`

**Request:**
- Path Parameter: `strategy_id` (integer, required)

**Response (Success - 200 OK):**

```json
[
  {
    "step_number": 1,
    "description": "Initial assessment of the support request.",
    "estimated_completion_time": "2024-11-15T10:00:00Z",
    "status": "Completed"
  },
  {
    "step_number": 2,
    "description": "Gather additional information from the user.",
    "estimated_completion_time": "2024-11-15T12:00:00Z",
    "status": "In Progress"
  },
  {
    "step_number": 3,
    "description": "Escalate the request to a senior engineer.",
    "estimated_completion_time": null,
    "status": "Pending"
  }
]
```

**Response (Error - 400 Bad Request):**

```json
{
  "detail": "Invalid strategy ID."
}
```

**Response (Error - 404 Not Found):**

```json
{
  "detail": "Evolution plan not found for strategy ID {strategy_id}."
}
```

**TypeScript Interface:**

```typescript
interface EvolutionStep {
  step_number: number;
  description: string;
  estimated_completion_time: string | null; // ISO 8601 timestamp or null
  status: "Pending" | "In Progress" | "Completed" | "Blocked";
}

interface EvolutionPlanProps {
  strategyId: number;
}
```

## Behavior Scenarios
- **Scenario:** Loading State
  - Input: Component is mounted with `strategyId = 123` and data is being fetched.
  - Outcome: A loading indicator (e.g., a spinner) is displayed in place of the evolution plan steps.

- **Scenario:** Successful Data Load
  - Input: Component is mounted with `strategyId = 123` and the API returns a valid evolution plan (see Data Contract example).
  - Outcome: The evolution plan is rendered as a series of steps, each displaying the step number, description, estimated completion time (formatted appropriately), and status.

- **Scenario:** No Estimated Completion Time
  - Input: Component is mounted with `strategyId = 123` and the API returns an evolution plan where one step has `estimated_completion_time: null`.
  - Outcome: The step is rendered with a placeholder for the estimated completion time, such as "N/A" or "Not Available".

- **Scenario:** Error State (404 Not Found)
  - Input: Component is mounted with `strategyId = 456` and the API returns a 404 error.
  - Outcome: An error message is displayed to the user, such as "Evolution plan not found."

- **Scenario:** Responsiveness (Small Screen)
  - Input: Component is rendered on a small screen (e.g., mobile phone).
  - Outcome: The component adapts to the smaller screen size, ensuring that all information is still visible and readable, possibly using a vertical layout for the steps.  The estimated completion time and status may be displayed below the description.

## Out of Scope
- User interaction with the evolution plan (e.g., editing steps, changing status).
- Authentication and authorization.
- Real-time updates to the evolution plan.
- Detailed error logging beyond displaying a user-friendly error message.
- Complex date formatting. A simple `toLocaleDateString` is sufficient.
