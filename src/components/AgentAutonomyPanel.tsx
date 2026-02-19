import React, { useState, useEffect } from 'react';

interface AgentAutonomyPanelProps {
  agentId: string;
  userId: string;
  onAutonomyChangeSuccess?: (message: string) => void;
  onAutonomyChangeError?: (error: string) => void;
}

interface AgentAutonomyLimits {
  agent_id: string;
  allowed_levels: ("Limited" | "Moderate" | "High" | "Full")[];
}

interface AgentAutonomyState {
  agent_id: string;
  current_level: "Limited" | "Moderate" | "High" | "Full";
}

interface AutonomyLevelChangeRequest {
  newLevel: "Limited" | "Moderate" | "High" | "Full";
}

interface AutonomyLevelChangeResponse {
  agent_id: string;
  previous_level: "Limited" | "Moderate" | "High" | "Full";
  new_level: "Limited" | "Moderate" | "High" | "Full";
  user_id: string;
  timestamp: string;
}

const AgentAutonomyPanel: React.FC<AgentAutonomyPanelProps> = ({ agentId, userId, onAutonomyChangeSuccess, onAutonomyChangeError }) => {
  const [autonomyLimits, setAutonomyLimits] = useState<AgentAutonomyLimits | null>(null);
  const [autonomyState, setAutonomyState] = useState<AgentAutonomyState | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isChanging, setIsChanging] = useState(false);

  useEffect(() => {
    const fetchAutonomyData = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const limitsResponse = await fetch(`/agents/${agentId}/autonomy/limits`);
        if (!limitsResponse.ok) {
          throw new Error(`Error fetching autonomy limits: ${limitsResponse.status}`);
        }
        const limitsData: AgentAutonomyLimits = await limitsResponse.json();
        setAutonomyLimits(limitsData);

        const stateResponse = await fetch(`/agents/${agentId}/autonomy`);
        if (!stateResponse.ok) {
          throw new Error(`Error fetching autonomy state: ${stateResponse.status}`);
        }
        const stateData: AgentAutonomyState = await stateResponse.json();
        setAutonomyState(stateData);
      } catch (err: any) {
        setError(`Error loading agent autonomy data for ${agentId}.`);
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    if (agentId) {
      fetchAutonomyData();
    }
  }, [agentId]);

  const handleChange = async (newLevel: "Limited" | "Moderate" | "High" | "Full") => {
    if (!autonomyLimits || !autonomyState) {
      return;
    }

    if (!autonomyLimits.allowed_levels.includes(newLevel)) {
      setError(`Autonomy level '${newLevel}' not allowed for this agent.`);
      return;
    }

    setIsChanging(true);
    setError(null);

    try {
      const requestBody: AutonomyLevelChangeRequest = { newLevel };
      const response = await fetch(`/agents/${agentId}/autonomy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`Error updating autonomy level: ${response.status}`);
      }

      const changeResponse: AutonomyLevelChangeResponse = await response.json();
      setAutonomyState({ ...autonomyState, current_level: newLevel });
      if (onAutonomyChangeSuccess) {
        onAutonomyChangeSuccess(`Autonomy level updated to ${newLevel}`);
      }
    } catch (err: any) {
      setError('Error updating autonomy level. Please try again.');
      console.error(err);
      if (onAutonomyChangeError) {
        onAutonomyChangeError('Error updating autonomy level. Please try again.');
      }
    } finally {
      setIsChanging(false);
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!autonomyLimits || !autonomyState) {
    return <div>Could not load autonomy data.</div>;
  }

  return (
    <div style={{ backgroundColor: 'var(--dark-background)', padding: '16px', borderRadius: '8px', color: 'var(--text-color)' }}>
      <h3>Agent Autonomy: {agentId}</h3>
      <p>Current Level: {autonomyState.current_level}</p>
      <div>
        <label htmlFor="autonomyLevel">Change Autonomy Level:</label>
        <select
          id="autonomyLevel"
          value={autonomyState.current_level}
          onChange={(e) => handleChange(e.target.value as "Limited" | "Moderate" | "High" | "Full")}
          disabled={isChanging}
        >
          {autonomyLimits.allowed_levels.map((level) => (
            <option key={level} value={level}>
              {level}
            </option>
          ))}
        </select>
        {isChanging && <span> Updating...</span>}
      </div>
    </div>
  );
};

export default AgentAutonomyPanel;