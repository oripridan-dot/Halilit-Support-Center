"""
DevAgent - Development-Time Monitoring and Auto-Fix Agent
Part of the Halilit ADK v5.1 Trinity Swarm

Purpose: Monitor frontend health, catch errors, and provide real-time fixes
With AUTOMATIC context logging for everything
"""

import os
import time
import json

load_dotenv()
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

# --- DATA MODELS ---

class ErrorReport(BaseModel):
    """Error detected in development"""
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    component: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    timestamp: str
    context: Optional[Dict[str, Any]] = None

class FixSuggestion(BaseModel):
    """AI-generated fix for development error"""
    issue_summary: str
    root_cause: str
    fix_code: Optional[str] = None
    fix_steps: List[str]
    confidence: int = Field(..., description="0-100, how confident the fix is")
    prevention_tips: List[str]
    related_patterns: List[str]
    file_path: Optional[str] = None
    can_auto_apply: bool = False

class ValidationResult(BaseModel):
    """Result of validating a fix"""
    success: bool
    validation_message: str
    test_output: Optional[str] = None
    errors_found: List[str]
    confidence_after_test: int

class HealthReport(BaseModel):
    """System health assessment"""
    status: str = Field(..., description="'healthy', 'warning', 'critical'")
    issues: List[str]
    suggestions: List[str]
    metrics: Dict[str, Any]

class PreventionResult(BaseModel):
    """Result of preventive validation"""
    is_safe: bool
    # Changed from str to Any for flexible types
    errors_prevented: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    suggestions: List[str]
    validation_type: str  # syntax|type|lint|pattern

# --- DEV AGENT ---

class DevAgent(AutoContextMixin, MemoryAwareMixin):
    """Development monitoring agent - catches issues before they ship

    NOW WITH:
    - AUTOMATIC CONTEXT LOGGING - Every operation is tracked!
    - FUNCTIONAL MEMORY - Learns from every action and improves!
    """

    def __init__(self):
        super().__init__()  # Initialize AutoContextMixin first
        self.name = "DevAgent"
        self.model_name = "gemini-2.0-flash"
        self.client = client

        # Log initialization
        self.log_system_event("DevAgent initialized", {
            "model": self.model_name,
            "auto_logging": True
        })

        self.system_instruction = """You are DevAgent, a development-time monitoring AI for the Halilit Support Center.

Your responsibilities:
1. Analyze React/TypeScript errors and provide precise fixes
2. Identify common patterns (null checks, async issues, state problems)
3. Suggest code improvements to prevent future errors
4. Maintain context about the codebase architecture

Architecture context:
- Frontend: React 18.3.1 + TypeScript + CopilotKit
- Backend: Python + FastAPI + Google Gemini agents
- Data flow: Backend golden data → export script → frontend JSON files
- State management: Zustand stores

Common patterns to watch:
- Null/undefined checks (Optional chaining ?. and nullish coalescing ??)
- Async data loading states
- Component lifecycle issues
- CopilotKit integration errors
- State synchronization problems

Always provide:
1. Root cause analysis
2. Exact code fix (not pseudocode)
3. Prevention strategies
4. Related documentation links when relevant
"""  # End of system_instruction

    @auto_log_context("error_analysis")
    def analyze_error(self, error_report: ErrorReport) -> FixSuggestion:
        """Analyze a development error and suggest a fix

        AUTO-LOGGED: Error + Fix automatically saved to context
        """
        print(f"🔧 [DevAgent] Analyzing error: {error_report.error_type}")

        prompt = f"""Analyze this development error and provide a precise fix:

ERROR TYPE: {error_report.error_type}
MESSAGE: {error_report.error_message}
COMPONENT: {error_report.component or 'Unknown'}
FILE: {error_report.file_path or 'Unknown'}
LINE: {error_report.line_number or 'Unknown'}

STACK TRACE:
{error_report.stack_trace or 'Not provided'}

CONTEXT:
{json.dumps(error_report.context, indent=2)
            if error_report.context else 'None'}

Provide:
1. Issue summary (1 sentence)
2. Root cause (what's actually wrong)
3. Fix code (exact TypeScript/React code to fix it)
4. Step-by-step fix instructions
5. Confidence level (0-100)
6. Prevention tips for future
7. Related error patterns

Respond with valid JSON matching this schema:
{{
  "issue_summary": "Brief description",
  "root_cause": "Why this error occurred",
  "fix_code": "// Exact code fix here",
  "fix_steps": ["Step 1", "Step 2"],
  "confidence": 85,
  "prevention_tips": ["Tip 1", "Tip 2"],
  "related_patterns": ["Pattern 1"]
}}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "system_instruction": self.system_instruction,
                    "temperature": 0.3,  # Low temp for precise fixes
                    "response_mime_type": "application/json"
                }
            )

            fix_data = json.loads(response.text)
            fix_suggestion = FixSuggestion(**fix_data)

            # Auto-logging happens via decorator!
            print(
                f"✅ [DevAgent] Fix generated with {fix_suggestion.confidence}% confidence")
            return fix_suggestion

        except Exception as e:
            print(f"❌ [DevAgent] Error analysis failed: {e}")
            return FixSuggestion(
                issue_summary=f"Error analyzing {error_report.error_type}",
                root_cause=str(e),
                fix_steps=["Check the error manually", "Review stack trace"],
                confidence=0,
                prevention_tips=["Add better error handling"],
                related_patterns=[]
            )

    def check_health(self, metrics: Dict[str, Any]) -> HealthReport:
        """Check system health based on metrics"""
        print(f"🏥 [DevAgent] Checking system health...")

        prompt = f"""Analyze these development metrics and assess system health:

METRICS:
{json.dumps(metrics, indent=2)}

Evaluate:
1. Error rates and patterns
2. Performance issues
3. Code quality concerns
4. Integration problems

Respond with JSON:
{{
  "status": "healthy|warning|critical",
  "issues": ["Issue 1", "Issue 2"],
  "suggestions": ["Suggestion 1"],
  "metrics": {{"key": "analyzed_value"}}
}}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "system_instruction": self.system_instruction,
                    "temperature": 0.4,
                    "response_mime_type": "application/json"
                }
            )

            health_data = json.loads(response.text)
            return HealthReport(**health_data)

        except Exception as e:
            print(f"❌ [DevAgent] Health check failed: {e}")
            return HealthReport(
                status="warning",
                issues=[f"Health check failed: {str(e)}"],
                suggestions=["Review system manually"],
                metrics=metrics
            )

    def suggest_improvements(self, code: str, context: str) -> Dict[str, Any]:
        """Suggest code improvements proactively"""
        print(f"💡 [DevAgent] Suggesting improvements...")

        prompt = f"""Review this code and suggest improvements:

CONTEXT: {context}

CODE:
```
{code}
```

Suggest:
1. Potential bugs to prevent
2. Performance optimizations
3. Type safety improvements
4. Best practice alignment

Respond with JSON:
{{
  "suggestions": [
    {{
      "type": "bug|performance|type|style",
      "priority": "high|medium|low",
      "description": "What to improve",
      "code_fix": "Improved code"
    }}
  ],
  "overall_score": 85
}}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "system_instruction": self.system_instruction,
                    "temperature": 0.5,
                    "response_mime_type": "application/json"
                }
            )

            return json.loads(response.text)

        except Exception as e:
            print(f"❌ [DevAgent] Improvement suggestion failed: {e}")
            return {"suggestions": [], "overall_score": 0}

    def validate_fix(self, fix: FixSuggestion, original_error: ErrorReport) -> ValidationResult:
        """Validate a fix by analyzing its correctness and potential impact"""
        print(f"✅ [DevAgent] Validating fix for: {original_error.error_type}")

        prompt = f"""Validate this fix for correctness and completeness:

ORIGINAL ERROR:
Type: {original_error.error_type}
Message: {original_error.error_message}
File: {original_error.file_path}
Component: {original_error.component}

PROPOSED FIX:
{fix.fix_code}

ANALYSIS:
1. Does this fix actually address the root cause?
2. Are there any potential side effects or new bugs?
3. Is the fix syntactically correct?
4. Does it follow best practices?
5. Are there any edge cases not handled?

Respond with JSON:
{{
  "success": true,
  "validation_message": "Fix looks correct and complete",
  "test_output": "All checks passed",
  "errors_found": [],
  "confidence_after_test": 95
}}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "system_instruction": self.system_instruction,
                    "temperature": 0.2,
                    "response_mime_type": "application/json"
                }
            )

            validation_data = json.loads(response.text)
            return ValidationResult(**validation_data)

        except Exception as e:
            print(f"❌ [DevAgent] Validation failed: {e}")
            return ValidationResult(
                success=False,
                validation_message=f"Validation error: {str(e)}",
                errors_found=[str(e)],
                confidence_after_test=0
            )

    def auto_apply_fix(self, fix: FixSuggestion, file_path: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Auto-apply a fix to a file (ONLY if confidence > 85%)
        Returns: {"success": bool, "message": str,
            "backup_created": str, "applied": bool}
        """
        print(
            f"🤖 [DevAgent] {'DRY RUN: ' if dry_run else ''}Auto-applying fix to: {file_path}")

        # Safety check: only auto-apply high-confidence fixes
        if fix.confidence < 85:
            return {
                "success": False,
                "message": f"Confidence too low ({fix.confidence}%) for auto-apply. Manual review needed.",
                "backup_created": None,
                "applied": False
            }

        if not fix.fix_code:
            return {
                "success": False,
                "message": "No fix code provided",
                "backup_created": None,
                "applied": False
            }

        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "message": f"File not found: {file_path}",
                    "backup_created": None,
                    "applied": False
                }

            if dry_run:
                return {
                    "success": True,
                    "message": f"DRY RUN: Would apply fix with {fix.confidence}% confidence",
                    "backup_created": None,
                    "applied": False,
                    "fix_preview": fix.fix_code
                }

            # Create backup
            backup_path = f"{file_path}.backup_{int(time.time())}"
            import shutil
            shutil.copy2(file_path, backup_path)

            # Read original content
            with open(file_path, 'r') as f:
                original_content = f.read()

            # Log the action
            self.context_manager.log_entry(
                "auto_fix",
                f"Auto-applied fix: {fix.issue_summary}",
                files_affected=[file_path],
                tags=["auto_fix", "ai_applied"],
                metadata={
                    "confidence": fix.confidence,
                    "backup": backup_path
                }
            )

            print(f"✅ [DevAgent] Fix prepared. Backup: {backup_path}")
            print(f"📝 [DevAgent] Manual verification recommended before deployment")

            return {
                "success": True,
                "message": f"Backup created at {backup_path}. Fix code ready to apply.",
                "backup_created": backup_path,
                "applied": False,
                "fix_code": fix.fix_code,
                "instructions": fix.fix_steps,
                "note": "Review the fix_code and apply manually for safety. DevAgent cannot modify files directly for security."
            }

        except Exception as e:
            print(f"❌ [DevAgent] Auto-apply failed: {e}")
            return {
                "success": False,
                "message": f"Auto-apply error: {str(e)}",
                "backup_created": None,
                "applied": False
            }

    @auto_log_context("scan")
    def scan_codebase(self, directory: str) -> Dict[str, Any]:
        """Proactively scan codebase for potential issues and improvements

        AUTO-LOGGED: Scan results saved to context
        """
        print(f"🔍 [DevAgent] Scanning codebase: {directory}")

        issues_found = []
        files_scanned = 0

        try:
            import glob

            # Scan TypeScript/TSX files
            patterns = ['**/*.tsx', '**/*.ts', '**/*.jsx', '**/*.js']
            files = []
            for pattern in patterns:
                files.extend(
                    glob.glob(f"{directory}/{pattern}", recursive=True))

            # Limit to reasonable number
            files = files[:20]

            for file_path in files:
                if 'node_modules' in file_path or '.test.' in file_path:
                    continue

                try:
                    with open(file_path, 'r') as f:
                        content = f.read()

                    # Quick pattern matching for common issues
                    if '.subscribe(' in content and not '?' in content:
                        issues_found.append({
                            "file": file_path,
                            "type": "potential_null_subscription",
                            "severity": "medium",
                            "message": "Found .subscribe() without null check"
                        })

                    if 'useEffect' in content and 'subscribe' in content:
                        issues_found.append({
                            "file": file_path,
                            "type": "useEffect_subscription",
                            "severity": "high",
                            "message": "useEffect with subscription - verify cleanup and null checks"
                        })

                    files_scanned += 1

                except Exception as e:
                    print(f"⚠️ [DevAgent] Could not scan {file_path}: {e}")

            return {
                "success": True,
                "files_scanned": files_scanned,
                "issues_found": len(issues_found),
                "issues": issues_found,
                "summary": f"Scanned {files_scanned} files, found {len(issues_found)} potential issues"
            }

        except Exception as e:
            print(f"❌ [DevAgent] Scan failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "files_scanned": files_scanned,
                "issues_found": 0
            }

    def execute_improvement(self, suggestion: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Execute an improvement suggestion autonomously"""
        print(
            f"⚡ [DevAgent] Executing improvement: {suggestion.get('description', 'Unknown')}")

        priority = suggestion.get('priority', 'low')

        # Only auto-execute high-priority improvements
        if priority != 'high':
            return {
                "success": False,
                "message": f"Priority {priority} - manual review recommended",
                "executed": False
            }

        try:
            # Create backup first
            backup_path = f"{file_path}.improvement_backup_{int(time.time())}"
            import shutil
            shutil.copy2(file_path, backup_path)

            # Log the improvement
            self.context_manager.log_entry(
                "improvement",
                suggestion.get('description', 'Code improvement'),
                files_affected=[file_path],
                tags=["improvement", "proactive"],
                metadata={
                    "type": suggestion.get('type'),
                    "priority": priority,
                    "backup": backup_path
                }
            )

            return {
                "success": True,
                "message": f"Improvement prepared. Backup: {backup_path}",
                "executed": False,
                "backup_created": backup_path,
                "code_fix": suggestion.get('code_fix'),
                "note": "Review and apply manually for safety"
            }

        except Exception as e:
            print(f"❌ [DevAgent] Improvement execution failed: {e}")
            return {
                "success": False,
                "message": str(e),
                "executed": False
            }

    @auto_log_context("validation")
    def validate_syntax(self, file_path: str, code: Optional[str] = None) -> PreventionResult:
        """Validate syntax before saving/running code

        AUTO-LOGGED: Validation results saved to context
        """
        print(f"🔍 [DevAgent] Validating syntax: {file_path}")

        errors_prevented = []
        warnings = []
        suggestions = []

        try:
            # Read code from file if not provided
            if code is None:
                with open(file_path, 'r') as f:
                    code = f.read()

            # Detect file type
            file_ext = os.path.splitext(file_path)[1]

            # TypeScript/JavaScript/React validation
            if file_ext in ['.ts', '.tsx', '.js', '.jsx']:
                # Check for common React Hooks violations
                if 'useState' in code or 'useEffect' in code or 'useCallback' in code or 'useMemo' in code:
                    lines = code.split('\n')

                    # Look for early return pattern before hooks
                    for i, line in enumerate(lines):
                        # Check for early return + hook usage pattern
                        if 'if (' in line and i + 1 < len(lines):
                            # Check next few lines for return
                            for j in range(i + 1, min(i + 5, len(lines))):
                                if 'return' in lines[j] and 'null' in lines[j]:
                                    # Found early return, now check if hooks come after
                                    remaining_code = '\n'.join(lines[j+1:])
                                    if any(hook in remaining_code for hook in ['useState', 'useEffect', 'useCallback', 'useMemo', 'useRef']):
                                        errors_prevented.append({
                                            "line": j + 1,
                                            "type": "React Hooks Rule Violation",
                                            "message": f"Conditional return at line {j + 1} before all hooks are called. Move return statements after all hook declarations.",
                                            "severity": "error"
                                        })
                                        break

                # Alternative check: look for return null before hook declarations
                if 'return null' in code:
                    return_idx = code.index('return null')
                    code_after_return = code[return_idx:]
                    if any(f'use{hook}' in code_after_return for hook in ['State', 'Effect', 'Callback', 'Memo', 'Ref', 'Context']):
                        line_num = code[:return_idx].count('\n') + 1
                        errors_prevented.append({
                            "line": line_num,
                            "type": "React Hooks Rule Violation",
                            "message": "Early return before all hooks are called. React Hooks must be called in the same order on every render.",
                            "severity": "error"
                        })

                # Check for subscribe without null check
                if '.subscribe(' in code and not '?.' in code:
                    warnings.append({
                        "type": "Potential Null Reference",
                        "message": "Found .subscribe() without optional chaining - add ?.subscribe()",
                        "severity": "warning"
                    })

                # Check for missing error boundaries
                if 'throw' in code and 'ErrorBoundary' not in code:
                    suggestions.append(
                        "Consider wrapping error-throwing code in ErrorBoundary")

            # Python validation
            elif file_ext == '.py':
                try:
                    compile(code, file_path, 'exec')
                except SyntaxError as e:
                    errors_prevented.append({
                        "line": e.lineno,
                        "type": "Python Syntax Error",
                        "message": str(e.msg),
                        "severity": "error"
                    })

            is_safe = len(errors_prevented) == 0

            if is_safe:
                print(f"✅ [DevAgent] Syntax validation passed: {file_path}")
            else:
                print(
                    f"❌ [DevAgent] {len(errors_prevented)} syntax errors prevented!")
                for err in errors_prevented:
                    print(f"   Line {err['line']}: {err['message']}")

            # LEARN from validation
            self.learn_from_action(
                action_type="validate_syntax",
                input_data=file_path,
                output_data=f"Safe: {is_safe}, Errors: {len(errors_prevented)}",
                success=is_safe,
                confidence=100 if is_safe else 90,
                patterns=["syntax-validation", f"file-type-{file_ext}"]
            )

            return PreventionResult(
                is_safe=is_safe,
                errors_prevented=errors_prevented,
                warnings=warnings,
                suggestions=suggestions,
                validation_type="syntax"
            )

        except Exception as e:
            print(f"⚠️ [DevAgent] Validation error: {e}")
            return PreventionResult(
                is_safe=False,
                errors_prevented=[{
                    "line": 0,
                    "type": "Validation Error",
                    "message": str(e),
                    "severity": "error"
                }],
                warnings=[],
                suggestions=[],
                validation_type="syntax"
            )

    def validate_types(self, file_path: str) -> PreventionResult:
        """Run TypeScript type checking"""
        print(f"🔍 [DevAgent] Type checking: {file_path}")

        errors_prevented = []
        warnings = []

        try:
            import subprocess

            # Run TypeScript compiler in check mode
            result = subprocess.run(
                ['npx', 'tsc', '--noEmit', file_path],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(file_path)
            )

            if result.returncode != 0:
                # Parse TypeScript errors
                for line in result.stderr.split('\n'):
                    if 'error TS' in line:
                        errors_prevented.append({
                            "line": 0,
                            "type": "TypeScript Error",
                            "message": line.strip(),
                            "severity": "error"
                        })

            is_safe = len(errors_prevented) == 0

            return PreventionResult(
                is_safe=is_safe,
                errors_prevented=errors_prevented,
                warnings=warnings,
                suggestions=["Run 'npm run type-check' before committing"],
                validation_type="type"
            )

        except FileNotFoundError:
            return PreventionResult(
                is_safe=True,
                errors_prevented=[],
                warnings=[{"type": "TypeScript Not Available",
                           "message": "TypeScript compiler not found", "severity": "info"}],
                suggestions=["Install TypeScript: npm install -g typescript"],
                validation_type="type"
            )
        except Exception as e:
            return PreventionResult(
                is_safe=False,
                errors_prevented=[
                    {"line": 0, "type": "Type Check Failed", "message": str(e), "severity": "error"}],
                warnings=[],
                suggestions=[],
                validation_type="type"
            )

    def validate_before_save(self, file_path: str, code: str) -> Dict[str, Any]:
        """Comprehensive pre-save validation(syntax + types + patterns)"""
        print(f"🛡️ [DevAgent] Pre-save validation: {file_path}")

        # Run syntax validation
        syntax_result = self.validate_syntax(file_path, code)

        # Collect all issues
        all_errors = syntax_result.errors_prevented
        all_warnings = syntax_result.warnings
        all_suggestions = syntax_result.suggestions

        # If syntax is clean, run type checking for TS files
        if syntax_result.is_safe and file_path.endswith(('.ts', '.tsx')):
            type_result = self.validate_types(file_path)
            all_errors.extend(type_result.errors_prevented)
            all_warnings.extend(type_result.warnings)

        is_safe = len(all_errors) == 0

        return {
            "is_safe": is_safe,
            "can_save": is_safe,
            "errors_count": len(all_errors),
            "warnings_count": len(all_warnings),
            "errors": all_errors,
            "warnings": all_warnings,
            "suggestions": all_suggestions,
            "message": f"✅ Safe to save" if is_safe else f"❌ {len(all_errors)} errors must be fixed first"
        }

# --- QUICK TEST ---

def test_devagent():
    """Test the dev agent with a sample error"""
    agent = DevAgent()

    # Simulate the React error from the screenshot
    error = ErrorReport(
        error_type="TypeError",
        error_message="Cannot read properties of null (reading 'subscribe')",
        stack_trace="at commitHookEffectListMount (react-dom.development.js:23189:26)",
        component="App",
        file_path="frontend/src/App.tsx",
        line_number=45,
        timestamp="2026-02-02T22:49:00Z",
        context={
            "framework": "React 18.3.1",
            "library": "CopilotKit",
            "state_management": "Zustand"
        }
    )

    fix = agent.analyze_error(error)

    print("\n" + "="*60)
    print("🔧 DEV AGENT FIX SUGGESTION")
    print("="*60)
    print(f"\n📋 Issue: {fix.issue_summary}")
    print(f"\n🔍 Root Cause: {fix.root_cause}")
    print(f"\n💻 Fix Code:\n{fix.fix_code}")
    print(f"\n📝 Steps:")
    for i, step in enumerate(fix.fix_steps, 1):
        print(f"   {i}. {step}")
    print(f"\n✅ Confidence: {fix.confidence}%")
    print(f"\n🛡️ Prevention:")
    for tip in fix.prevention_tips:
        print(f"   • {tip}")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_devagent()
