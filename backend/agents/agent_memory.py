"""
Agent Memory System - Long-term learning and improvement for all agents
Part of Halilit ADK v5.1 Trinity Swarm

Purpose: Enable all agents to learn from every action and improve over time
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))


class LearningRecord(BaseModel):
    """Single learning instance from an agent action"""
    id: str
    timestamp: str
    agent_name: str
    action_type: str  # analyze|fix|validate|improve|scan
    input_summary: str
    output_summary: str
    success: bool
    confidence: int
    outcome_quality: Optional[int] = None  # 0-100, validated later
    patterns_learned: List[str] = Field(default_factory=list)
    mistakes_avoided: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentInsight(BaseModel):
    """Distilled insight from multiple learning records"""
    pattern: str
    frequency: int
    success_rate: float
    contexts: List[str]
    recommended_approach: str
    anti_patterns: List[str]


class MemoryQuery(BaseModel):
    """Query to retrieve relevant past learning"""
    agent_name: str
    action_type: Optional[str] = None
    context: Optional[str] = None
    limit: int = 10


class AgentMemory:
    """Functional memory system for agent learning and improvement"""

    def __init__(self, memory_dir: str = ".agent_memory"):
        self.memory_dir = memory_dir
        self.memory_file = os.path.join(memory_dir, "learning_history.jsonl")
        self.insights_file = os.path.join(memory_dir, "insights.json")
        self.client = client

        # Ensure directory exists
        os.makedirs(memory_dir, exist_ok=True)

        # Initialize insights cache
        self.insights_cache: Dict[str, List[AgentInsight]] = {}
        self._load_insights()

    def _load_insights(self):
        """Load existing insights from disk"""
        if os.path.exists(self.insights_file):
            with open(self.insights_file, 'r') as f:
                data = json.load(f)
                for agent, insights in data.items():
                    self.insights_cache[agent] = [
                        AgentInsight(**i) for i in insights
                    ]

    def _save_insights(self):
        """Save insights to disk"""
        data = {
            agent: [i.model_dump() for i in insights]
            for agent, insights in self.insights_cache.items()
        }
        with open(self.insights_file, 'w') as f:
            json.dump(data, f, indent=2)

    def record_action(self, record: LearningRecord) -> None:
        """Record an agent action for learning"""
        # Save to JSONL history
        with open(self.memory_file, 'a') as f:
            f.write(record.model_dump_json() + '\n')

        print(
            f"📚 [Memory] Recorded {record.agent_name} action: {record.action_type}")

    def recall_relevant(self, query: MemoryQuery) -> List[LearningRecord]:
        """Retrieve relevant past learning records"""
        if not os.path.exists(self.memory_file):
            return []

        records = []
        with open(self.memory_file, 'r') as f:
            for line in f:
                if line.strip():
                    record = LearningRecord(**json.loads(line))

                    # Filter by agent and action type
                    if record.agent_name == query.agent_name:
                        if query.action_type is None or record.action_type == query.action_type:
                            records.append(record)

        # Return most recent
        records.sort(key=lambda r: r.timestamp, reverse=True)
        return records[:query.limit]

    def analyze_patterns(self, agent_name: str, min_frequency: int = 3) -> List[AgentInsight]:
        """Analyze learning records to extract patterns using AI"""
        records = self.recall_relevant(MemoryQuery(
            agent_name=agent_name,
            limit=100
        ))

        if len(records) < 3:
            return []

        # Prepare data for AI analysis
        records_summary = []
        for r in records:
            records_summary.append({
                "action": r.action_type,
                "success": r.success,
                "confidence": r.confidence,
                "input": r.input_summary[:200],
                "output": r.output_summary[:200],
                "patterns": r.patterns_learned
            })

        # Use AI to extract insights
        prompt = f"""Analyze these {len(records)} agent actions and extract patterns:

{json.dumps(records_summary, indent=2)}

Identify:
1. Common successful patterns (things that work well)
2. Anti-patterns (approaches that fail)
3. Context-specific recommendations
4. Areas for improvement

Return JSON array of insights with this structure:
[
  {{
    "pattern": "Descriptive pattern name",
    "frequency": number_of_occurrences,
    "success_rate": 0.0_to_1.0,
    "contexts": ["context1", "context2"],
    "recommended_approach": "What to do",
    "anti_patterns": ["What to avoid"]
  }}
]

Focus on patterns that appear at least {min_frequency} times."""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )

            # Parse AI response
            insights_data = json.loads(response.text.strip())
            insights = [AgentInsight(**i) for i in insights_data]

            # Cache insights
            self.insights_cache[agent_name] = insights
            self._save_insights()

            print(
                f"🧠 [Memory] Extracted {len(insights)} patterns for {agent_name}")
            return insights

        except Exception as e:
            print(f"⚠️ [Memory] Pattern analysis failed: {e}")
            return []

    def get_contextual_advice(self, agent_name: str, current_task: str) -> str:
        """Get AI-powered advice based on past learning"""
        # Get recent records
        records = self.recall_relevant(MemoryQuery(
            agent_name=agent_name,
            limit=20
        ))

        # Get insights
        insights = self.insights_cache.get(agent_name, [])

        if not records and not insights:
            return "No prior learning available. Proceed with best judgment."

        # Build context for AI
        context_data = {
            "recent_successes": [
                r.output_summary for r in records if r.success
            ][:5],
            "recent_failures": [
                r.output_summary for r in records if not r.success
            ][:3],
            "learned_patterns": [i.pattern for i in insights][:5],
            "anti_patterns": [
                ap for i in insights for ap in i.anti_patterns
            ][:5]
        }

        prompt = f"""Based on this agent's learning history, provide advice for the current task.

Agent: {agent_name}
Current Task: {current_task}

Learning Context:
{json.dumps(context_data, indent=2)}

Provide specific, actionable advice in 2-3 sentences that:
1. References successful past patterns
2. Warns against known mistakes
3. Suggests optimal approach for this task"""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )

            advice = response.text.strip()
            print(f"💡 [Memory] Generated contextual advice for {agent_name}")
            return advice

        except Exception as e:
            print(f"⚠️ [Memory] Advice generation failed: {e}")
            return "Proceed with caution. No specific advice available."

    def suggest_improvements(self, agent_name: str) -> List[str]:
        """Suggest improvements based on learning patterns"""
        insights = self.insights_cache.get(agent_name, [])

        if not insights:
            # Trigger pattern analysis
            insights = self.analyze_patterns(agent_name)

        if not insights:
            return ["Continue gathering learning data for meaningful insights"]

        # Find patterns with low success rate
        improvements = []
        for insight in insights:
            if insight.success_rate < 0.8:
                improvements.append(
                    f"Improve {insight.pattern} (current success: {insight.success_rate:.0%}) - {insight.recommended_approach}"
                )

        # Add general improvements
        records = self.recall_relevant(MemoryQuery(
            agent_name=agent_name,
            limit=50
        ))

        if records:
            avg_confidence = sum(r.confidence for r in records) / len(records)
            if avg_confidence < 85:
                improvements.append(
                    f"Increase decision confidence (current avg: {avg_confidence:.0f}%) - Gather more context before acting"
                )

        return improvements[:5]  # Top 5 improvements

    def validate_outcome(self, record_id: str, quality: int) -> None:
        """Validate the quality of a past action's outcome"""
        # Read all records
        records = []
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                for line in f:
                    if line.strip():
                        record = LearningRecord(**json.loads(line))
                        if record.id == record_id:
                            record.outcome_quality = quality
                        records.append(record)

        # Rewrite file with updated record
        with open(self.memory_file, 'w') as f:
            for record in records:
                f.write(record.model_dump_json() + '\n')

        print(f"✅ [Memory] Validated outcome for {record_id}: {quality}/100")

    def get_stats(self, agent_name: str) -> Dict[str, Any]:
        """Get learning statistics for an agent"""
        records = self.recall_relevant(MemoryQuery(
            agent_name=agent_name,
            limit=1000
        ))

        if not records:
            return {
                "total_actions": 0,
                "success_rate": 0,
                "avg_confidence": 0,
                "insights_count": 0
            }

        successes = sum(1 for r in records if r.success)
        avg_confidence = sum(r.confidence for r in records) / len(records)
        insights = self.insights_cache.get(agent_name, [])

        return {
            "total_actions": len(records),
            "success_rate": successes / len(records),
            "avg_confidence": avg_confidence,
            "insights_count": len(insights),
            "recent_patterns": [i.pattern for i in insights][:3]
        }


# Memory-aware mixin for agents
class MemoryAwareMixin:
    """Mixin to add memory capabilities to any agent"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory = AgentMemory()
        self.agent_name = getattr(self, 'name', self.__class__.__name__)

    def learn_from_action(self,
                          action_type: str,
                          input_data: Any,
                          output_data: Any,
                          success: bool,
                          confidence: int,
                          patterns: List[str] = None) -> None:
        """Record learning from an action"""
        record = LearningRecord(
            id=f"{self.agent_name}_{datetime.now().isoformat()}",
            timestamp=datetime.now().isoformat(),
            agent_name=self.agent_name,
            action_type=action_type,
            input_summary=str(input_data)[:500],
            output_summary=str(output_data)[:500],
            success=success,
            confidence=confidence,
            patterns_learned=patterns or []
        )
        self.memory.record_action(record)

    def get_advice_for(self, task: str) -> str:
        """Get contextual advice for a task"""
        return self.memory.get_contextual_advice(self.agent_name, task)

    def analyze_my_patterns(self) -> List[AgentInsight]:
        """Analyze my own learning patterns"""
        return self.memory.analyze_patterns(self.agent_name)

    def my_improvement_suggestions(self) -> List[str]:
        """Get improvement suggestions for myself"""
        return self.memory.suggest_improvements(self.agent_name)

    def my_stats(self) -> Dict[str, Any]:
        """Get my learning statistics"""
        return self.memory.get_stats(self.agent_name)


# Test function
def test_agent_memory():
    """Test the memory system"""
    memory = AgentMemory()

    # Simulate some learning records
    for i in range(5):
        record = LearningRecord(
            id=f"test_{i}",
            timestamp=datetime.now().isoformat(),
            agent_name="DevAgent",
            action_type="fix",
            input_summary=f"Error: React hook violation {i}",
            output_summary=f"Fixed by moving hooks before return {i}",
            success=i < 4,  # 80% success rate
            confidence=85 + i * 2,
            patterns_learned=["hooks-before-return", "proper-dependency-array"]
        )
        memory.record_action(record)

    # Test retrieval
    records = memory.recall_relevant(MemoryQuery(
        agent_name="DevAgent",
        action_type="fix",
        limit=5
    ))

    print(f"\n✅ Retrieved {len(records)} records")

    # Test advice
    advice = memory.get_contextual_advice(
        "DevAgent",
        "Fix React hooks violation in UserProfile component"
    )
    print(f"\n💡 Advice: {advice}")

    # Test stats
    stats = memory.get_stats("DevAgent")
    print(f"\n📊 Stats: {json.dumps(stats, indent=2)}")


if __name__ == "__main__":
    test_agent_memory()
