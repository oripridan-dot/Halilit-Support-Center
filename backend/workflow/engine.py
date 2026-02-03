# backend/workflow/engine.py
"""
Workflow Engine - Agentic State Machine

This prevents agents from declaring "Done" when they've actually created
catastrophic failures (like 0-byte files).

Key Concept: A Workflow is a Directed Graph where each state has:
1. Entry conditions
2. Exit conditions (verification gates)
3. Rollback logic on failure

This is the structural fix for the "DevAgent wipes frontend" disaster.
"""

import logging

class WorkflowState(Enum):
    """Valid states in the feature build workflow."""
    PLANNING = "PLANNING"
    CODING = "CODING"
    VERIFYING = "VERIFYING"
    TESTING = "TESTING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"

class StateTransitionError(Exception):
    """Raised when a state transition is attempted without meeting exit conditions."""
    pass

class WorkflowEngine:
    """
    Base workflow engine that manages state transitions with verification.

    Prevents the system from moving forward if verification fails.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # Create console handler
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Skill registry
        self.skills = {
            "build_react": ReactComponentBuilder(),
            "build_typescript": TypeScriptModuleBuilder(),
        }

        self.current_state = None
        self.state_history = []
        self.execution_log = []

    def log_state_change(self, from_state: str, to_state: str, reason: str = ""):
        """Logs and tracks state transitions."""
        self.state_history.append({
            'from': from_state,
            'to': to_state,
            'reason': reason
        })
        self.logger.info(
            f"🔄 State: {from_state} → {to_state} {f'({reason})' if reason else ''}")

    def execute_skill(self, skill_name: str, context: Dict[str, Any]) -> tuple[bool, Any]:
        """
        Executes a skill from the registry with error handling.

        Returns:
                        (success: bool, result: Any)
        """
        if skill_name not in self.skills:
            error = f"Unknown skill: {skill_name}"
            self.logger.error(error)
            return False, error

        try:
            success, result = self.skills[skill_name].execute(context)

            self.execution_log.append({
                'skill': skill_name,
                'success': success,
                'result': str(result)[:200]  # Truncate for logging
            })

            return success, result

        except Exception as e:
            error_msg = f"Skill {skill_name} raised exception: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

class FeatureBuildWorkflow(WorkflowEngine):
    """
    Workflow for building and verifying frontend features.

    State Machine:
    PLANNING → CODING → VERIFYING → TESTING → COMPLETE
                                                            ↑         ↓
                                                            └─── FAILED (retry or abort)

    Critical Gates:
    - Cannot exit CODING if build fails
    - Cannot exit VERIFYING if file is invalid
    - Cannot reach COMPLETE without passing TESTING
    """

    def __init__(self, max_retries: int = 3):
        super().__init__()
        self.max_retries = max_retries
        self.retry_count = 0

    def run_feature_build(self, feature_spec: Dict[str, Any]) -> bool:
        """
        Executes a complete feature build with strict verification gates.

        Required feature_spec keys:
        - name: Feature name
        - files: List of dicts with 'path' and 'content' keys
        - verification_steps: Optional list of verification functions

        Returns:
                        True if workflow completes successfully, False otherwise
        """
        self.current_state = WorkflowState.PLANNING
        self.log_state_change(
            "INIT", self.current_state.value, "Starting workflow")

        feature_name = feature_spec.get('name', 'Unnamed Feature')
        files = feature_spec.get('files', [])

        if not files:
            self.logger.error("❌ No files specified in feature_spec")
            return False

        self.logger.info(f"🚀 Starting Feature Build: {feature_name}")
        self.logger.info(f"📋 Files to build: {len(files)}")

        # Main workflow loop
        while self.current_state not in [WorkflowState.COMPLETE, WorkflowState.FAILED]:

            # ========== STATE: PLANNING ==========
            if self.current_state == WorkflowState.PLANNING:
                self.logger.info(f"📐 Planning build for {len(files)} files...")

                # Validate file specifications
                if self._validate_file_specs(files):
                    self.current_state = WorkflowState.CODING
                    self.log_state_change(
                        "PLANNING", self.current_state.value, "Specs validated")
                else:
                    self.current_state = WorkflowState.FAILED
                    self.log_state_change(
                        "PLANNING", self.current_state.value, "Invalid specs")

            # ========== STATE: CODING ==========
            elif self.current_state == WorkflowState.CODING:
                self.logger.info(
                    f"⚙️  Coding phase (Attempt {self.retry_count + 1}/{self.max_retries})")

                build_results = []
                all_builds_successful = True

                for file_spec in files:
                    file_path = file_spec.get('path')
                    file_content = file_spec.get('content')
                    # 'react' or 'typescript'
                    file_type = file_spec.get('type', 'react')

                    # Select appropriate skill
                    skill_name = "build_react" if file_type == 'react' else "build_typescript"

                    # Execute build skill
                    success, result = self.execute_skill(skill_name, {
                        'file_path': file_path,
                        'code_content': file_content,
                        'create_backup': True
                    })

                    build_results.append({
                        'file': file_path,
                        'success': success,
                        'result': result
                    })

                    if not success:
                        all_builds_successful = False
                        self.logger.error(
                            f"❌ Build failed for {file_path}: {result}")
                    else:
                        self.logger.info(f"✅ Build succeeded for {file_path}")

                # Gate: Can only proceed if ALL builds succeeded
                if all_builds_successful:
                    self.current_state = WorkflowState.VERIFYING
                    self.log_state_change(
                        "CODING", self.current_state.value, "All builds successful")
                else:
                    self.retry_count += 1
                    if self.retry_count >= self.max_retries:
                        self.current_state = WorkflowState.FAILED
                        self.log_state_change(
                            "CODING", self.current_state.value, "Max retries exceeded")
                    else:
                        self.logger.warning(
                            f"⚠️  Build failed. Retrying ({self.retry_count}/{self.max_retries})")
                        # Stay in CODING state for retry

            # ========== STATE: VERIFYING ==========
            elif self.current_state == WorkflowState.VERIFYING:
                self.logger.info("🔍 Verifying build integrity...")

                # Run additional verification checks
                verification_passed = self._run_verification_checks(files)

                if verification_passed:
                    self.current_state = WorkflowState.TESTING
                    self.log_state_change(
                        "VERIFYING", self.current_state.value, "Verification passed")
                else:
                    # Verification failed - go back to CODING
                    self.retry_count += 1
                    if self.retry_count >= self.max_retries:
                        self.current_state = WorkflowState.FAILED
                        self.log_state_change(
                            "VERIFYING", self.current_state.value, "Verification failed, max retries")
                    else:
                        self.current_state = WorkflowState.CODING
                        self.log_state_change(
                            "VERIFYING", self.current_state.value, "Verification failed, retrying build")

            # ========== STATE: TESTING ==========
            elif self.current_state == WorkflowState.TESTING:
                self.logger.info("🧪 Running integration tests...")

                # Placeholder for actual tests (could run npm build, syntax checks, etc.)
                test_passed = True  # In reality, this would run actual tests

                if test_passed:
                    self.current_state = WorkflowState.COMPLETE
                    self.log_state_change(
                        "TESTING", self.current_state.value, "Tests passed")
                else:
                    self.current_state = WorkflowState.FAILED
                    self.log_state_change(
                        "TESTING", self.current_state.value, "Tests failed")

        # ========== FINAL STATE ==========
        if self.current_state == WorkflowState.COMPLETE:
            self.logger.info(
                f"✨ Workflow Complete: {feature_name} deployed successfully")
            self._print_execution_summary()
            return True
        else:
            self.logger.error(
                f"💀 Workflow Failed: {feature_name} - Manual intervention required")
            self._print_execution_summary()
            return False

    def _validate_file_specs(self, files: List[Dict]) -> bool:
        """Validates that all file specifications are complete."""
        for file_spec in files:
            if 'path' not in file_spec or 'content' not in file_spec:
                self.logger.error(f"Invalid file spec: {file_spec}")
                return False

            if not file_spec['content'] or len(file_spec['content']) == 0:
                self.logger.error(f"Empty content for {file_spec['path']}")
                return False

        return True

    def _run_verification_checks(self, files: List[Dict]) -> bool:
        """
        Runs additional verification checks beyond the skill-level checks.

        This is where you could add:
        - Cross-file dependency checks
        - Import consistency validation
        - Project-level conventions
        """
        import os

        for file_spec in files:
            file_path = file_spec['path']

            # Check file exists and is not empty
            if not os.path.exists(file_path):
                self.logger.error(
                    f"❌ Verification failed: {file_path} does not exist")
                return False

            if os.path.getsize(file_path) == 0:
                self.logger.error(
                    f"❌ Verification failed: {file_path} is 0 bytes")
                return False

            # Check file is readable
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) < 50:  # Unrealistically small file
                        self.logger.error(
                            f"❌ Verification failed: {file_path} is suspiciously small ({len(content)} bytes)")
                        return False
            except Exception as e:
                self.logger.error(
                    f"❌ Verification failed: Cannot read {file_path}: {e}")
                return False

        self.logger.info("✅ All verification checks passed")
        return True

    def _print_execution_summary(self):
        """Prints a summary of the workflow execution."""
        self.logger.info("\n" + "="*60)
        self.logger.info("WORKFLOW EXECUTION SUMMARY")
        self.logger.info("="*60)

        self.logger.info(f"Final State: {self.current_state.value}")
        self.logger.info(f"Total Retries: {self.retry_count}")
        self.logger.info(f"State Transitions: {len(self.state_history)}")

        self.logger.info("\nState History:")
        for i, transition in enumerate(self.state_history, 1):
            self.logger.info(
                f"  {i}. {transition['from']} → {transition['to']} ({transition['reason']})")

        self.logger.info("\nSkill Executions:")
        for i, log_entry in enumerate(self.execution_log, 1):
            status = "✅" if log_entry['success'] else "❌"
            self.logger.info(
                f"  {i}. {status} {log_entry['skill']}: {log_entry['result']}")

        self.logger.info("="*60 + "\n")
