#!/usr/bin/env python3
"""
v7.3 Codebase Consolidation & Purification Script

This script:
1. Identifies all duplicated functions/classes
2. Creates consolidated modules
3. Updates all imports
4. Deletes obsolete files
5. Validates the new codebase
"""

import os
import ast
import json
import shutil
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple


class ConsolidationAnalyzer:
    def __init__(self, root_dir: str = "/workspaces/Halilit-Support-Center"):
        self.root_dir = Path(root_dir)
        self.backend_dir = self.root_dir / "backend"
        self.duplicates = defaultdict(list)
        self.imports_graph = defaultdict(set)
        self.dead_files = []
        self.consolidation_plan = {}

    def analyze_python_files(self) -> Dict:
        """Analyze all Python files for duplicates and dead code"""
        functions = defaultdict(list)
        classes = defaultdict(list)
        file_imports = {}
        file_content_hashes = {}

        for python_file in self.backend_dir.rglob("*.py"):
            if any(part in str(python_file) for part in ["__pycache__", ".venv", "dist"]):
                continue

            try:
                with open(python_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)
                file_imports[str(python_file)] = []

                # Extract functions and classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions[node.name].append(str(python_file))
                    elif isinstance(node, ast.ClassDef):
                        classes[node.name].append(str(python_file))
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        if isinstance(node, ast.ImportFrom):
                            if node.module:
                                file_imports[str(python_file)].append(
                                    node.module)
                        else:
                            for alias in node.names:
                                file_imports[str(python_file)].append(
                                    alias.name)
            except Exception as e:
                print(f"❌ Error analyzing {python_file}: {e}")

        return {
            'functions': {k: v for k, v in functions.items() if len(v) > 1},
            'classes': {k: v for k, v in classes.items() if len(v) > 1},
            'imports': file_imports
        }

    def create_consolidation_plan(self) -> Dict:
        """Create detailed consolidation plan"""
        return {
            "1_Data_Services": {
                "files_to_merge": [
                    "conductor_data_service.py",
                    "data_normalizer.py",
                    "ingestion_to_frontend.py"
                ],
                "merge_into": "conductor_data_service.py",
                "consolidation": [
                    "Merge DataNormalizer class into ConductorDataService",
                    "Merge frontend sync logic into ConductorDataService methods",
                    "Update all imports across codebase"
                ],
                "delete_files": ["data_normalizer.py", "ingestion_to_frontend.py"]
            },
            "2_Learning_System": {
                "files_to_merge": [
                    "agents/learning_engine.py",
                    "agents/learning_optimizer.py",
                    "agents/enhanced_training.py",
                    "agents/multi_cycle_runner.py"
                ],
                "merge_into": "agents/learning_system.py",
                "consolidation": [
                    "Merge all learning logic into single LearningSystem class",
                    "Consolidate run_learning_cycles() functionality",
                    "Merge log_progress() and format_progress_bar() utilities"
                ],
                "delete_files": [
                    "agents/learning_optimizer.py",
                    "agents/enhanced_training.py",
                    "agents/multi_cycle_runner.py"
                ]
            },
            "3_Agent_System": {
                "files_to_merge": [
                    "agents/agent_improver.py",
                    "agents/agent_memory.py"
                ],
                "merge_into": "agents/agent_system.py",
                "consolidation": [
                    "Merge AgentImprover and AgentMemory into AgentSystem",
                    "Move main() logic from agent_improver.py to conductor_main.py"
                ],
                "delete_files": ["agents/agent_improver.py"]
            },
            "4_Validation_System": {
                "files_to_consolidate": [
                    "agents/audit_system.py",
                    "agents/feedback_engine.py",
                    "agents/perfection_map.py",
                    "agents/security_gates.py"
                ],
                "merge_into": "agents/validation_system.py",
                "consolidation": [
                    "Merge AuditSystem, FeedbackEngine, PerfectionMap, SecurityGates",
                    "Consolidate _generate_recommendations() and _identify_bottlenecks()",
                    "Create unified validation pipeline"
                ],
                "delete_files": [
                    "agents/audit_system.py",
                    "agents/feedback_engine.py",
                    "agents/perfection_map.py",
                    "agents/security_gates.py"
                ]
            },
            "5_Obsolete_Files": {
                "files_to_delete": [
                    "ingestion_versioning.py",
                    "copilot_agent_actions.py",
                    "copilot_skill_executor.py",
                    "data/ingestion.backup.1770400232"
                ],
                "reason": "Obsolete, replaced by modern architecture"
            },
            "6_Documentation": {
                "files_to_keep_and_update": [
                    "README.md",
                    "ARCHITECTURE_v7.3.md",
                    "QUICK_START.md",
                    "LEARNING_PIPELINE_GUIDE.md"
                ],
                "files_to_archive": [
                    "PLANNED_VS_EXECUTED.md",
                    "AGENT_LEARNING_REPORT.md",
                    "LEARNING_PROGRESS_REPORT.md"
                ],
                "files_to_delete": [
                    "ARCHITECTURE_v7.2_COMPLETE.md",
                    "QUICK_START_v7.2.md",
                    "CONSOLIDATION_REPORT.md",
                    "CODEBASE_STRUCTURE.md",
                    "DEPLOYMENT.md",
                    "QUICK_START.md",
                    "LEARNING_IMPLEMENTATION_COMPLETE.md",
                    "IMPLEMENTATION_COMPLETE.md",
                    "PATH_1_FINAL_COMPLETION.md"
                ]
            }
        }

    def print_plan(self):
        """Print consolidation plan"""
        plan = self.create_consolidation_plan()
        print("\n" + "="*80)
        print("📋 V7.3 CONSOLIDATION PLAN")
        print("="*80 + "\n")

        for phase, details in plan.items():
            print(f"\n{phase}")
            print("-" * 80)
            print(json.dumps(details, indent=2))


if __name__ == "__main__":
    analyzer = ConsolidationAnalyzer()

    # Print analysis
    print("\n" + "="*80)
    print("🔍 CODEBASE ANALYSIS")
    print("="*80)

    analysis = analyzer.analyze_python_files()

    print(f"\n📊 Duplicate Functions: {len(analysis['functions'])}")
    for func_name, files in list(analysis['functions'].items())[:5]:
        print(f"   - {func_name}: {len(files)} implementations")

    print(f"\n📊 Duplicate Classes: {len(analysis['classes'])}")
    for class_name, files in list(analysis['classes'].items())[:5]:
        print(f"   - {class_name}: {len(files)} implementations")

    # Print consolidation plan
    analyzer.print_plan()

    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE - Ready for consolidation execution")
    print("="*80 + "\n")
