# Spec: Agent Autonomy Improvements
**Target:** src/components/AgentAutonomyPanel.tsx

## Overview
This specification outlines the implementation of an enhanced "Agent Autonomy Panel" within the Halilit Support Center's Dark Factory interface. The panel allows authorized users to configure and monitor the level of autonomy granted to AI agents performing automated tasks. The UI component displays the agent's current autonomy level, provides controls to adjust it (within pre-defined limits), and logs any adjustments made, including the user who initiated the change and the timestamp.

## Requirements
- The panel must display the current autonomy level of a specified AI agent. Autonomy levels are defined as: `Limited`, `Moderate`, `High`, and `Full`.
- The panel must allow authorized users (determined via role-based access control, assumed to be handled elsewhere) to adjust the autonomy level of the agent using a controlled input mechanism (e.g., a select dropdown).
- Autonomy level adjustments must be validated against pre-defined, agent-specific limits (defined in the `AgentAutonomyLimits` data structure). Attempting to set an autonomy level outside these limits should trigger an error message.
- Any changes to the autonomy level should be logged to a backend service, including the agent ID, previous autonomy level, new autonomy level, user ID making the change, and a timestamp.
- The panel should display a success message upon successfully changing the autonomy level and an error message if the change fails.
- The panel should clearly indicate the agent being configured (display the agent ID).
- The panel should utilize a dark theme consistent with the Halilit Support Center's Dark Factory design.
- The component must be responsive and render correctly on various screen sizes.

## Data Contract

**AgentAutonomyLimits (backend, returned by /agents/{agent_id}/autonomy/limits endpoint)**:
```python
from typing import Literal
from pydantic import BaseModel

class AgentAutonomyLimits(BaseModel):
    agent_id: str
    allowed_levels: list[Literal["Limited", "Moderate", "High", "Full"]]
```

**AgentAutonomyState (backend, returned by /agents/{agent_id}/autonomy endpoint)**:
```python
from typing import Literal
from pydantic import BaseModel

class AgentAutonomyState(BaseModel):
    agent_id: str
    current_level: Literal["Limited", "Moderate", "High", "Full"]
```

**AutonomyLevelChangeRequest (frontend -> backend, POST /agents/{agent_id}/autonomy)**:
```typescript
interface AutonomyLevelChangeRequest {
  newLevel: "Limited" | "Moderate" | "High" | "Full";
}
```

**AutonomyLevelChangeResponse (backend, POST /agents/{agent_id}/autonomy)**:
```python
from typing import Literal
from pydantic import BaseModel

class AutonomyLevelChangeResponse(BaseModel):
    agent_id: str
    previous_level: Literal["Limited", "Moderate", "High", "Full"]
    new_level: Literal["Limited", "Moderate", "High", "Full"]
    user_id: str  # The ID of the user who made the change.
    timestamp: str # ISO 8601 Timestamp
```

**React Props for AgentAutonomyPanel:**

```typescript
interface AgentAutonomyPanelProps {
  agentId: string;
  userId: string; // Current user's ID
  onAutonomyChangeSuccess?: (message: string) => void; // Optional callback on successful autonomy change.
  onAutonomyChangeError?: (error: string) => void; // Optional callback on autonomy change error.
}
```

## Behavior Scenarios
- **Scenario:** Initial Load - Valid Agent
  - Input: `agentId` is "agent-123", valid credentials.
  - Outcome:
    - Component fetches current autonomy level for "agent-123" from `/agents/agent-123/autonomy`.
    - Component fetches allowed autonomy levels for "agent-123" from `/agents/agent-123/autonomy/limits`.
    - Component renders a select dropdown populated with the allowed autonomy levels.
    - Current autonomy level is pre-selected in the dropdown.
    - Agent ID ("agent-123") is displayed.

- **Scenario:** Initial Load - Invalid Agent
  - Input: `agentId` is "invalid-agent", which returns a 404 from both autonomy endpoints.
  - Outcome:
    - Component displays an error message: "Error loading agent autonomy data for invalid-agent."

- **Scenario:** Successful Autonomy Level Change
  - Input: User selects "High" from the dropdown, current level is "Moderate".
  - Outcome:
    - Component makes a POST request to `/agents/agent-123/autonomy` with `{ newLevel: "High" }`.
    - Backend returns a 200 with `AutonomyLevelChangeResponse` data.
    - The dropdown selection updates to "High".
    - A success message "Autonomy level updated to High" is displayed.
    - The optional `onAutonomyChangeSuccess` callback is triggered with the success message.

- **Scenario:** Unauthorized Autonomy Level Change
  - Input: User selects "Full" from the dropdown, but "Full" is not in `AgentAutonomyLimits.allowed_levels`.
  - Outcome:
    - Component prevents the POST request.
    - An error message "Autonomy level 'Full' not allowed for this agent." is displayed.
    - The dropdown selection reverts to the current level (before the change).

- **Scenario:** Backend Error during Autonomy Level Change
  - Input: User selects "High" from the dropdown, and the POST request to `/agents/agent-123/autonomy` returns a 500 error.
  - Outcome:
    - An error message "Error updating autonomy level. Please try again." is displayed.
    - The dropdown selection remains at the previous level.
    - The optional `onAutonomyChangeError` callback is triggered with the error message.

## Out of Scope
- User authentication and role-based access control. It's assumed the `userId` prop is derived from an existing authentication mechanism.
- Detailed logging implementation on the backend (beyond the `AutonomyLevelChangeResponse` data contract).
- Persistence of autonomy levels (handled by the backend).
