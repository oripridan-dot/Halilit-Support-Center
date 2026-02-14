"""
Agent Memory — Learning history and pattern analysis.
Split from unified_quality_gates.py Section 5.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any

from backend.quality.models import LearningRecord, AgentInsight, MemoryQuery

logger = logging.getLogger(__name__)


class AgentMemory:
    """Functional memory system for agent learning and improvement."""

    def __init__(self, memory_dir: str = ".agent_memory"):
        self.memory_dir = memory_dir
        self.memory_file = os.path.join(memory_dir, "learning_history.jsonl")
        self.insights_file = os.path.join(memory_dir, "insights.json")
        os.makedirs(memory_dir, exist_ok=True)
        self.insights_cache: Dict[str, List[AgentInsight]] = {}
        self._load_insights()

        # Lazy LLM access
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            try:
                from backend.llm import get_llm
                self._llm = get_llm()
            except Exception as exc:
                logger.debug("LLM not available: %s", exc)
        return self._llm

    def _load_insights(self):
        if os.path.exists(self.insights_file):
            with open(self.insights_file, 'r') as f:
                data = json.load(f)
                for agent, insights in data.items():
                    self.insights_cache[agent] = [
                        AgentInsight(**i) for i in insights]

    def _save_insights(self):
        data = {
            agent: [i.model_dump() for i in insights]
            for agent, insights in self.insights_cache.items()
        }
        with open(self.insights_file, 'w') as f:
            json.dump(data, f, indent=2)

    def record_action(self, record: LearningRecord) -> None:
        with open(self.memory_file, 'a') as f:
            f.write(record.model_dump_json() + '\n')

    def recall_relevant(self, query: MemoryQuery) -> List[LearningRecord]:
        if not os.path.exists(self.memory_file):
            return []
        records = []
        with open(self.memory_file, 'r') as f:
            for line in f:
                if line.strip():
                    record = LearningRecord(**json.loads(line))
                    if record.agent_name == query.agent_name:
                        if query.action_type is None or record.action_type == query.action_type:
                            records.append(record)
        records.sort(key=lambda r: r.timestamp, reverse=True)
        return records[:query.limit]

    def analyze_patterns(self, agent_name: str,
                         min_frequency: int = 3) -> List[AgentInsight]:
        records = self.recall_relevant(
            MemoryQuery(agent_name=agent_name, limit=100))
        if len(records) < 3 or not self.llm:
            return []

        records_summary = [
            {"action": r.action_type, "success": r.success,
             "confidence": r.confidence,
             "input": r.input_summary[:200],
             "output": r.output_summary[:200],
             "patterns": r.patterns_learned}
            for r in records
        ]

        prompt = (
            f"Analyze these {len(records)} agent actions and extract patterns:\n"
            f"{json.dumps(records_summary, indent=2)}\n\n"
            f"Return JSON array of insights with structure:\n"
            f'[{{"pattern": "name", "frequency": N, "success_rate": 0.0-1.0, '
            f'"contexts": ["ctx"], "recommended_approach": "...", '
            f'"anti_patterns": ["..."]}}]\n'
            f"Focus on patterns appearing at least {min_frequency} times."
        )

        data, ok = self.llm.call_json("AgentMemory", prompt)
        if ok and isinstance(data, list):
            insights = [AgentInsight(**i) for i in data]
            self.insights_cache[agent_name] = insights
            self._save_insights()
            return insights
        return []

    def get_contextual_advice(self, agent_name: str,
                              current_task: str) -> str:
        records = self.recall_relevant(
            MemoryQuery(agent_name=agent_name, limit=20))
        insights = self.insights_cache.get(agent_name, [])

        if not records and not insights:
            return "No prior learning available. Proceed with best judgment."
        if not self.llm:
            return "AI client not available. Use cached insights."

        context_data = {
            "recent_successes": [r.output_summary for r in records if r.success][:5],
            "recent_failures": [r.output_summary for r in records if not r.success][:3],
            "learned_patterns": [i.pattern for i in insights][:5],
            "anti_patterns": [ap for i in insights for ap in i.anti_patterns][:5],
        }

        prompt = (
            f"Agent: {agent_name}\nTask: {current_task}\n"
            f"Context:\n{json.dumps(context_data, indent=2)}\n\n"
            f"Provide 2-3 sentences of specific, actionable advice."
        )

        text, ok = self.llm.call("AgentMemory", prompt)
        return text.strip() if ok else "Proceed with caution."

    def suggest_improvements(self, agent_name: str) -> List[str]:
        insights = self.insights_cache.get(agent_name, [])
        if not insights:
            insights = self.analyze_patterns(agent_name)
        if not insights:
            return ["Continue gathering learning data for meaningful insights"]

        improvements = []
        for insight in insights:
            if insight.success_rate < 0.8:
                improvements.append(
                    f"Improve {insight.pattern} (success: {insight.success_rate:.0%}) "
                    f"- {insight.recommended_approach}")

        records = self.recall_relevant(
            MemoryQuery(agent_name=agent_name, limit=50))
        if records:
            avg_conf = sum(r.confidence for r in records) / len(records)
            if avg_conf < 85:
                improvements.append(
                    f"Increase decision confidence (avg: {avg_conf:.0f}%)")
        return improvements[:5]

    def validate_outcome(self, record_id: str, quality: int) -> None:
        if not os.path.exists(self.memory_file):
            return
        records = []
        with open(self.memory_file, 'r') as f:
            for line in f:
                if line.strip():
                    record = LearningRecord(**json.loads(line))
                    if record.id == record_id:
                        record.outcome_quality = quality
                    records.append(record)
        with open(self.memory_file, 'w') as f:
            for record in records:
                f.write(record.model_dump_json() + '\n')

    def get_stats(self, agent_name: str) -> Dict[str, Any]:
        records = self.recall_relevant(
            MemoryQuery(agent_name=agent_name, limit=1000))
        if not records:
            return {"total_actions": 0, "success_rate": 0,
                    "avg_confidence": 0, "insights_count": 0}
        successes = sum(1 for r in records if r.success)
        avg_conf = sum(r.confidence for r in records) / len(records)
        insights = self.insights_cache.get(agent_name, [])
        return {
            "total_actions": len(records),
            "success_rate": successes / len(records),
            "avg_confidence": avg_conf,
            "insights_count": len(insights),
            "recent_patterns": [i.pattern for i in insights][:3],
        }


class MemoryAwareMixin:
    """Mixin to add memory capabilities to any agent."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory = AgentMemory()
        self.agent_name = getattr(self, 'name', self.__class__.__name__)

    def learn_from_action(self, action_type: str, input_data: Any,
                          output_data: Any, success: bool,
                          confidence: int,
                          patterns: List[str] = None) -> None:
        record = LearningRecord(
            id=f"{self.agent_name}_{datetime.now().isoformat()}",
            timestamp=datetime.now().isoformat(),
            agent_name=self.agent_name, action_type=action_type,
            input_summary=str(input_data)[:500],
            output_summary=str(output_data)[:500],
            success=success, confidence=confidence,
            patterns_learned=patterns or [],
        )
        self.memory.record_action(record)

    def get_advice_for(self, task: str) -> str:
        return self.memory.get_contextual_advice(self.agent_name, task)

    def analyze_my_patterns(self) -> List[AgentInsight]:
        return self.memory.analyze_patterns(self.agent_name)

    def my_improvement_suggestions(self) -> List[str]:
        return self.memory.suggest_improvements(self.agent_name)

    def my_stats(self) -> Dict[str, Any]:
        return self.memory.get_stats(self.agent_name)
