"""
ContextManager - Development Context & History Management
Part of Halilit ADK v5.1 DevAgent

Purpose: Track, store, analyze, and maintain development context across sessions
"""

import os
import json
import time
from datetime import datetime

load_dotenv()
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

# --- DATA MODELS ---

class ContextEntry(BaseModel):
    """Single context entry in development history"""
    id: str
    timestamp: str
    type: str = Field(..., description="prompt|response|fix|refactor|decision")
    content: str
    files_affected: List[str] = []
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class DevelopmentContext(BaseModel):
    """Complete development context state"""
    project_name: str
    version: str
    last_updated: str
    total_entries: int
    active_patterns: List[str]
    recent_decisions: List[Dict[str, Any]]
    file_history: Dict[str, List[str]]  # file -> list of change ids
    consistency_rules: Dict[str, str]

class ContextAnalysis(BaseModel):
    """Analysis of current development context"""
    consistency_score: int = Field(..., description="0-100")
    patterns_detected: List[str]
    inconsistencies: List[str]
    suggestions: List[str]
    related_context: List[str]

class RefactoringPlan(BaseModel):
    """Automated refactoring plan"""
    priority: str = Field(..., description="high|medium|low")
    type: str = Field(..., description="consistency|pattern|optimization")
    description: str
    affected_files: List[str]
    suggested_changes: List[Dict[str, str]]
    reasoning: str

# --- CONTEXT MANAGER ---

class ContextManager:
    """Manages development context, history, and consistency"""

    def __init__(self, workspace_root: str = "/workspaces/Halilit-Support-Center"):
        self.workspace_root = workspace_root
        self.context_dir = os.path.join(workspace_root, ".devagent")
        self.history_file = os.path.join(self.context_dir, "history.jsonl")
        self.context_file = os.path.join(self.context_dir, "context.json")
        self.rules_file = os.path.join(
            self.context_dir, "consistency_rules.json")

        # Create context directory if not exists
        os.makedirs(self.context_dir, exist_ok=True)

        # Initialize context if needed
        if not os.path.exists(self.context_file):
            self._initialize_context()

        self.client = client
        self.model_name = "gemini-2.0-flash"

    def _initialize_context(self):
        """Initialize fresh development context"""
        context = DevelopmentContext(
            project_name="Halilit Support Center",
            version="5.1.0-v2",
            last_updated=datetime.now().isoformat(),
            total_entries=0,
            active_patterns=[
                "React 18 + TypeScript",
                "Python + FastAPI",
                "Pydantic v2 models",
                "ADK multi-agent architecture"
            ],
            recent_decisions=[],
            file_history={},
            consistency_rules={
                "naming": "Use camelCase for TypeScript, snake_case for Python",
                "imports": "Absolute imports for cross-module, relative for same directory",
                "errors": "All errors captured by DevAgent, never silent failures",
                "docs": "Update docs immediately after code changes",
                "testing": "Test new features before committing"
            }
        )

        with open(self.context_file, 'w') as f:
            json.dump(context.model_dump(), f, indent=2)

    def log_entry(self, entry_type: str, content: str, files_affected: List[str] = None,
                  tags: List[str] = None, metadata: Dict[str, Any] = None):
        """Log a development context entry"""
        entry = ContextEntry(
            id=f"{int(time.time() * 1000)}",
            timestamp=datetime.now().isoformat(),
            type=entry_type,
            content=content,
            files_affected=files_affected or [],
            tags=tags or [],
            metadata=metadata or {}
        )

        # Append to history
        with open(self.history_file, 'a') as f:
            f.write(json.dumps(entry.model_dump()) + '\n')

        # Update context
        self._update_context(entry)

        return entry.id

    def _update_context(self, entry: ContextEntry):
        """Update main context file with new entry"""
        context = self._load_context()

        context["last_updated"] = datetime.now().isoformat()
        context["total_entries"] += 1

        # Update file history
        for file_path in entry.files_affected:
            if file_path not in context["file_history"]:
                context["file_history"][file_path] = []
            context["file_history"][file_path].append(entry.id)

        # Track decisions
        if entry.type == "decision":
            context["recent_decisions"].insert(0, {
                "id": entry.id,
                "timestamp": entry.timestamp,
                "content": entry.content
            })
            # Keep only last 20 decisions
            context["recent_decisions"] = context["recent_decisions"][:20]

        with open(self.context_file, 'w') as f:
            json.dump(context, f, indent=2)

    def _load_context(self) -> Dict[str, Any]:
        """Load current context"""
        with open(self.context_file, 'r') as f:
            return json.load(f)

    def get_recent_history(self, limit: int = 10) -> List[ContextEntry]:
        """Get recent history entries"""
        entries = []
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                lines = f.readlines()
                for line in reversed(lines[-limit:]):
                    entry_data = json.loads(line.strip())
                    entries.append(ContextEntry(**entry_data))
        return entries

    def analyze_context(self) -> ContextAnalysis:
        """Analyze current development context for consistency"""
        print("🔍 [ContextManager] Analyzing development context...")

        context = self._load_context()
        recent_entries = self.get_recent_history(20)

        prompt = f"""Analyze this development context for consistency and patterns:

PROJECT CONTEXT:
{json.dumps(context, indent=2)}

RECENT HISTORY (last 20 entries):
{json.dumps([e.model_dump() for e in recent_entries], indent=2)}

Analyze:
1. Consistency score (0-100) - How consistent is the development?
2. Patterns detected - What patterns are emerging?
3. Inconsistencies - What breaks the rules or patterns?
4. Suggestions - How to improve consistency?
5. Related context - What previous decisions are relevant?

Respond with JSON:
{{
  "consistency_score": 85,
  "patterns_detected": ["Pattern 1", "Pattern 2"],
  "inconsistencies": ["Issue 1", "Issue 2"],
  "suggestions": ["Suggestion 1"],
  "related_context": ["Context 1"]
}}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "temperature": 0.3,
                    "response_mime_type": "application/json"
                }
            )

            analysis_data = json.loads(response.text)
            return ContextAnalysis(**analysis_data)

        except Exception as e:
            print(f"❌ [ContextManager] Analysis failed: {e}")
            return ContextAnalysis(
                consistency_score=0,
                patterns_detected=[],
                inconsistencies=[str(e)],
                suggestions=["Manual review needed"],
                related_context=[]
            )

    def suggest_refactoring(self, file_path: str = None) -> List[RefactoringPlan]:
        """Suggest refactoring based on context history"""
        print("💡 [ContextManager] Generating refactoring suggestions...")

        context = self._load_context()

        if file_path:
            # File-specific refactoring
            file_history = context.get("file_history", {}).get(file_path, [])
            recent_entries = [e for e in self.get_recent_history(50)
                              if file_path in e.files_affected]
        else:
            # Project-wide refactoring
            recent_entries = self.get_recent_history(50)

        prompt = f"""Based on this development history, suggest refactoring opportunities:

CONTEXT:
{json.dumps(context, indent=2)}

RECENT CHANGES:
{json.dumps([e.model_dump() for e in recent_entries], indent=2)}

Suggest refactoring for:
1. Consistency improvements
2. Pattern extraction
3. Code optimization
4. Documentation updates

Respond with JSON array:
[
  {{
    "priority": "high|medium|low",
    "type": "consistency|pattern|optimization",
    "description": "What needs refactoring",
    "affected_files": ["file1.py", "file2.ts"],
    "suggested_changes": [{{"file": "file.py", "change": "specific change"}}],
    "reasoning": "Why this refactoring is needed"
  }}
]
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "temperature": 0.4,
                    "response_mime_type": "application/json"
                }
            )

            plans_data = json.loads(response.text)
            return [RefactoringPlan(**plan) for plan in plans_data]

        except Exception as e:
            print(f"❌ [ContextManager] Refactoring suggestions failed: {e}")
            return []

    def update_documentation(self, change_description: str, files_affected: List[str]):
        """Auto-update documentation based on changes"""
        print("📝 [ContextManager] Updating documentation...")

        context = self._load_context()

        prompt = f"""Generate documentation update for this change:

CHANGE DESCRIPTION:
{change_description}

FILES AFFECTED:
{', '.join(files_affected)}

PROJECT CONTEXT:
{json.dumps(context, indent=2)}

Generate:
1. What documentation files need updates
2. Specific sections to update
3. New content to add

Respond with JSON:
{{
  "docs_to_update": [
    {{
      "file": "README.md",
      "section": "Section name",
      "content": "New content to add"
    }}
  ],
  "new_docs": [
    {{
      "file": "NEW_FEATURE.md",
      "content": "Full content for new doc"
    }}
  ]
}}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "temperature": 0.4,
                    "response_mime_type": "application/json"
                }
            )

            doc_updates = json.loads(response.text)

            # Log the documentation update intent
            self.log_entry(
                "documentation",
                f"Auto-documentation: {change_description}",
                files_affected=files_affected,
                tags=["auto-doc"],
                metadata=doc_updates
            )

            return doc_updates

        except Exception as e:
            print(f"❌ [ContextManager] Documentation update failed: {e}")
            return {"docs_to_update": [], "new_docs": []}

    def check_consistency(self, proposed_change: str, files: List[str]) -> Dict[str, Any]:
        """Check if proposed change is consistent with development context"""
        print("✅ [ContextManager] Checking consistency...")

        context = self._load_context()
        rules = context.get("consistency_rules", {})
        recent_decisions = context.get("recent_decisions", [])

        prompt = f"""Check if this proposed change is consistent with project context:

PROPOSED CHANGE:
{proposed_change}

AFFECTED FILES:
{', '.join(files)}

CONSISTENCY RULES:
{json.dumps(rules, indent=2)}

RECENT DECISIONS:
{json.dumps(recent_decisions[:10], indent=2)}

Evaluate:
1. Is this consistent with established patterns?
2. Does it violate any rules?
3. Does it conflict with recent decisions?
4. Should it be approved?

Respond with JSON:
{{
  "is_consistent": true,
  "consistency_score": 95,
  "violations": [],
  "conflicts": [],
  "recommendation": "approve|review|reject",
  "reasoning": "Why this recommendation"
}}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "temperature": 0.2,
                    "response_mime_type": "application/json"
                }
            )

            return json.loads(response.text)

        except Exception as e:
            print(f"❌ [ContextManager] Consistency check failed: {e}")
            return {
                "is_consistent": False,
                "consistency_score": 0,
                "violations": [str(e)],
                "recommendation": "review"
            }

    def get_context_summary(self) -> str:
        """Get formatted context summary"""
        context = self._load_context()
        recent = self.get_recent_history(5)

        summary = f"""
╔═══════════════════════════════════════════════════════════╗
║         DEVELOPMENT CONTEXT SUMMARY                       ║
╚═══════════════════════════════════════════════════════════╝

Project: {context['project_name']}
Version: {context['version']}
Last Updated: {context['last_updated']}
Total Entries: {context['total_entries']}

Active Patterns:
{chr(10).join(f"  • {p}" for p in context['active_patterns'])}

Recent Decisions:
{chr(10).join(f"  • {d['content']}" for d in context['recent_decisions'][:3])}

Files Under Management: {len(context['file_history'])}

Recent Activity:
{chr(10).join(f"  [{e.timestamp}] {e.type}: {e.content[:50]}..." for e in recent)}

═══════════════════════════════════════════════════════════
"""
        return summary

# --- QUICK TEST ---

def test_context_manager():
    """Test the context manager"""
    manager = ContextManager()

    # Log some test entries
    manager.log_entry(
        "prompt",
        "User requested DevAgent to manage development context",
        files_affected=["backend/agents/context_manager.py"],
        tags=["feature-request", "context-management"]
    )

    manager.log_entry(
        "response",
        "Created ContextManager class with full history tracking",
        files_affected=["backend/agents/context_manager.py"],
        tags=["implementation"]
    )

    # Analyze context
    analysis = manager.analyze_context()
    print("\n🔍 Context Analysis:")
    print(f"Consistency Score: {analysis.consistency_score}%")
    print(f"Patterns: {', '.join(analysis.patterns_detected)}")

    # Get summary
    print(manager.get_context_summary())

    print("\n✅ Context Manager test complete!")

if __name__ == "__main__":
    test_context_manager()
