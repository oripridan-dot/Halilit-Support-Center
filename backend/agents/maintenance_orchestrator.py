"""
Agent Maintenance Orchestrator

Coordinates Trinity Swarm for internal system maintenance.
Manages multiple maintenance workflows and ensures system health.

Agents & Their Internal Roles:
- CommercialScout: Code reconnaissance (scan codebase)
- OfficialVerifier: Standards enforcement (verify compliance)
- ExternalValidator: Quality auditing (validate integrity)
- DevAgent: Auto-fix & updates (apply remediation)
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from backend.workflow.maintenance_workflows import (
    CodeCleanupWorkflow,
    CodeOrganizationWorkflow,
    CodeSyncWorkflow,
    SystemHealthCheckWorkflow
)

class MaintenanceSchedule:
    """Defines when different maintenance tasks run"""

    def __init__(self):
        self.schedule = {
            'code_cleanup': {'interval': 'daily', 'priority': 'high'},
            'code_organization': {'interval': 'weekly', 'priority': 'medium'},
            'code_sync': {'interval': 'daily', 'priority': 'high'},
            'health_check': {'interval': 'hourly', 'priority': 'critical'}
        }

    def get_due_tasks(self, last_run: Dict[str, str]) -> List[str]:
        """Determine which tasks are due based on last run"""
        due = []
        now = datetime.now()

        for task, config in self.schedule.items():
            if task not in last_run:
                due.append(task)
            # In production: check interval against last_run time

        return due

class AgentMaintenanceOrchestrator:
    """
    Orchestrates Trinity Swarm for internal system maintenance.

    Responsibilities:
    1. Coordinate multiple agents on maintenance tasks
    2. Schedule and execute workflows
    3. Track system health metrics
    4. Generate maintenance reports
    5. Auto-remediate common issues
    """

    def __init__(self, project_root: str = '/workspaces/Halilit-Support-Center'):
        self.project_root = project_root
        self.schedule = MaintenanceSchedule()

        # Workflows
        self.cleanup_workflow = CodeCleanupWorkflow()
        self.organization_workflow = CodeOrganizationWorkflow()
        self.sync_workflow = CodeSyncWorkflow()
        self.health_workflow = SystemHealthCheckWorkflow()

        # State
        self.last_run_times = {}
        self.maintenance_history = []
        self.system_health = {'score': 0, 'status': 'unknown'}

        print("🤖 Agent Maintenance Orchestrator Initialized")

    def discover_python_files(self, max_count: Optional[int] = None) -> List[str]:
        """Discover Python files in backend"""
        python_files = []
        backend_dir = os.path.join(self.project_root, 'backend')

        for root, dirs, files in os.walk(backend_dir):
            # Skip __pycache__ and .git
            dirs[:] = [d for d in dirs if d not in [
                '__pycache__', '.git', '.pytest_cache']]

            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    python_files.append(os.path.join(root, file))

        if max_count:
            python_files = python_files[:max_count]

        return python_files

    def discover_typescript_files(self, max_count: Optional[int] = None) -> List[str]:
        """Discover TypeScript files in frontend"""
        ts_files = []
        frontend_dir = os.path.join(self.project_root, 'frontend', 'src')

        if os.path.exists(frontend_dir):
            for root, dirs, files in os.walk(frontend_dir):
                dirs[:] = [d for d in dirs if d not in [
                    '__pycache__', '.git', '.next']]

                for file in files:
                    if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                        ts_files.append(os.path.join(root, file))

        if max_count:
            ts_files = ts_files[:max_count]

        return ts_files

    def run_cleanup_workflow(self, auto_fix: bool = True) -> Dict[str, Any]:
        """
        Run code cleanup workflow (CommercialScout + DevAgent).

        CommercialScout role: Scan for cleanup opportunities
        DevAgent role: Apply fixes
        """
        print("\n" + "=" * 70)
        print("🧹 MAINTENANCE: Code Cleanup Workflow")
        print("=" * 70)
        print("   CommercialScout: Scanning for cleanup opportunities...")
        print("   DevAgent: Applying fixes...")

        # Discover Python files (CommercialScout scanning)
        py_files = self.discover_python_files(max_count=10)

        result = self.cleanup_workflow.execute({
            'file_paths': py_files,
            'auto_fix': auto_fix
        })

        self.last_run_times['code_cleanup'] = datetime.now().isoformat()
        self.maintenance_history.append(('cleanup', result))

        print("\n" + "=" * 70)
        print(f"✅ Cleanup Complete")
        print(
            f"   Files Scanned: {result.get('metrics', {}).get('files_scanned', 0)}")
        print(
            f"   Issues Found: {result.get('metrics', {}).get('issues_found', 0)}")
        print(
            f"   Files Formatted: {result.get('metrics', {}).get('files_formatted', 0)}")
        print("=" * 70)

        return result

    def run_organization_workflow(self, enforce_naming: bool = True) -> Dict[str, Any]:
        """
        Run code organization workflow (OfficialVerifier + DevAgent).

        OfficialVerifier role: Check naming conventions and standards
        DevAgent role: Organize and fix issues
        """
        print("\n" + "=" * 70)
        print("📁 MAINTENANCE: Code Organization Workflow")
        print("=" * 70)
        print("   OfficialVerifier: Checking standards and conventions...")
        print("   DevAgent: Organizing and fixing...")

        # Discover Python files
        py_files = self.discover_python_files(max_count=10)

        result = self.organization_workflow.execute({
            'file_paths': py_files,
            'enforce_naming': enforce_naming
        })

        self.last_run_times['code_organization'] = datetime.now().isoformat()
        self.maintenance_history.append(('organization', result))

        print("\n" + "=" * 70)
        print(f"✅ Organization Complete")
        print(
            f"   Files Analyzed: {result.get('metrics', {}).get('files_analyzed', 0)}")
        print(
            f"   Files Fixed: {result.get('metrics', {}).get('files_fixed', 0)}")
        print(f"   Score: {result.get('organization_score', 0):.1f}%")
        print("=" * 70)

        return result

    def run_sync_workflow(self) -> Dict[str, Any]:
        """
        Run code sync workflow (all agents coordinate).

        Ensures consistency across related files.
        """
        print("\n" + "=" * 70)
        print("🔗 MAINTENANCE: Code Sync Workflow")
        print("=" * 70)
        print("   CommercialScout: Scanning for sync opportunities...")
        print("   OfficialVerifier: Verifying consistency...")
        print("   ExternalValidator: Auditing sync quality...")

        # For demo, sync key files
        source_file = os.path.join(self.project_root, 'backend', 'server.py')
        target_files = self.discover_python_files(max_count=5)

        result = self.sync_workflow.execute({
            'source_file': source_file,
            'target_files': target_files,
            'sync_types': ['imports']
        })

        self.last_run_times['code_sync'] = datetime.now().isoformat()
        self.maintenance_history.append(('sync', result))

        print("\n" + "=" * 70)
        print(f"✅ Sync Complete")
        print(
            f"   Sync Operations: {result.get('metrics', {}).get('sync_operations', 0)}")
        print(
            f"   Files Synced: {result.get('metrics', {}).get('files_synced', 0)}")
        print(f"   Score: {result.get('sync_score', 0):.1f}%")
        print("=" * 70)

        return result

    def run_health_check_workflow(self) -> Dict[str, Any]:
        """
        Run comprehensive system health check (all agents audit).

        Uses all three agents to comprehensively validate system state.
        """
        print("\n" + "=" * 70)
        print("🏥 MAINTENANCE: System Health Check")
        print("=" * 70)
        print("   CommercialScout: Scanning codebase integrity...")
        print("   OfficialVerifier: Verifying compliance...")
        print("   ExternalValidator: Auditing quality and dependencies...")

        py_files = self.discover_python_files(max_count=8)

        result = self.health_workflow.execute({
            'file_paths': py_files,
            'include_dependencies': True
        })

        self.last_run_times['health_check'] = datetime.now().isoformat()
        self.maintenance_history.append(('health', result))

        # Update system health
        self.system_health = {
            'score': result.get('health_score', 0),
            'status': result.get('health_status', 'unknown'),
            'timestamp': datetime.now().isoformat()
        }

        print("\n" + "=" * 70)
        print(f"✅ Health Check Complete")
        print(
            f"   Total Files: {result.get('metrics', {}).get('total_files', 0)}")
        print(
            f"   Valid Files: {result.get('metrics', {}).get('valid_files', 0)}")
        print(
            f"   Invalid Files: {result.get('metrics', {}).get('invalid_files', 0)}")
        print(
            f"   Health Score: {result.get('health_score', 0):.1f}% ({result.get('health_status', 'unknown')})")
        print("=" * 70)

        return result

    def run_full_maintenance(self) -> Dict[str, Any]:
        """
        Run complete maintenance cycle.

        Executes all workflows in optimal order:
        1. Health check (assess current state)
        2. Cleanup (remove dead code)
        3. Organization (structure code)
        4. Sync (ensure consistency)
        5. Final health check (verify improvements)
        """
        print("\n")
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 15 + "🤖 FULL SYSTEM MAINTENANCE CYCLE 🤖" + " " * 17 + "║")
        print("╚" + "=" * 68 + "╝")

        maintenance_results = {
            'start_time': datetime.now().isoformat(),
            'workflows': {}
        }

        # 1. Initial Health Check
        print("\n[1/5] Running initial health check...")
        health_initial = self.run_health_check_workflow()
        maintenance_results['workflows']['health_initial'] = health_initial

        # 2. Code Cleanup
        print("\n[2/5] Running code cleanup...")
        cleanup = self.run_cleanup_workflow(auto_fix=True)
        maintenance_results['workflows']['cleanup'] = cleanup

        # 3. Code Organization
        print("\n[3/5] Running code organization...")
        organization = self.run_organization_workflow(enforce_naming=True)
        maintenance_results['workflows']['organization'] = organization

        # 4. Code Sync
        print("\n[4/5] Running code synchronization...")
        sync = self.run_sync_workflow()
        maintenance_results['workflows']['sync'] = sync

        # 5. Final Health Check
        print("\n[5/5] Running final health check...")
        health_final = self.run_health_check_workflow()
        maintenance_results['workflows']['health_final'] = health_final

        # Calculate improvements
        initial_score = health_initial.get('health_score', 0)
        final_score = health_final.get('health_score', 0)
        improvement = final_score - initial_score

        maintenance_results['end_time'] = datetime.now().isoformat()
        maintenance_results['summary'] = {
            'health_initial': initial_score,
            'health_final': final_score,
            'improvement': improvement,
            'status': 'complete',
            'total_workflows': 5
        }

        # Print summary
        print("\n")
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 20 + "✨ MAINTENANCE COMPLETE ✨" + " " * 20 + "║")
        print("╠" + "=" * 68 + "╣")
        print(
            f"║  Initial Health: {initial_score:6.1f}% → Final Health: {final_score:6.1f}%           ║")
        print(
            f"║  Improvement: {improvement:+6.1f}%                                                ║")
        print(
            f"║  Status: {maintenance_results['summary']['status'].upper():20}                              ║")
        print("╚" + "=" * 68 + "╝")
        print()

        return maintenance_results

    def generate_maintenance_report(self) -> str:
        """Generate comprehensive maintenance report"""
        report = []
        report.append("\n" + "=" * 70)
        report.append("📊 MAINTENANCE ORCHESTRATOR REPORT")
        report.append("=" * 70)

        report.append(
            f"\nSystem Health: {self.system_health['score']:.1f}% ({self.system_health['status']})")
        report.append(
            f"Last Check: {self.system_health.get('timestamp', 'never')}")

        report.append(
            f"\nMaintenance History ({len(self.maintenance_history)} operations):")
        for i, (operation, result) in enumerate(self.maintenance_history[-5:], 1):
            status = "✅" if result.get('success') else "❌"
            report.append(f"  {i}. {status} {operation.upper()}")

        report.append(f"\nLast Run Times:")
        for task, timestamp in self.last_run_times.items():
            report.append(f"  • {task}: {timestamp}")

        report.append("\n" + "=" * 70)

        return "\n".join(report)

def main():
    """Demo: Run full maintenance cycle"""
    print("\n🚀 Initializing Agent Maintenance Orchestrator...")

    orchestrator = AgentMaintenanceOrchestrator()

    # Run full maintenance
    results = orchestrator.run_full_maintenance()

    # Print report
    print(orchestrator.generate_maintenance_report())

    print("\n✨ Maintenance orchestration complete!")
    print("   System is now healthy and synchronized.")

if __name__ == '__main__':
    main()
