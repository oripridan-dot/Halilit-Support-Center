"""
Automatic Context Logging System
Wraps all DevAgent operations with automatic context tracking
"""

from functools import wraps
from typing import Callable, Optional
from backend.agents.context_manager import ContextManager

# Global context manager instance
_context_manager = None


def get_context_manager():
    """Get or create global context manager"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager


def auto_log_context(operation_type: str):
    """
    Decorator that automatically logs operations to context

    Usage:
        @auto_log_context("error_analysis")
        def analyze_error(self, error):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            ctx = get_context_manager()

            # Execute the function
            try:
                result = func(*args, **kwargs)

                # Log success
                if operation_type == "error_analysis":
                    error = args[1] if len(args) > 1 else kwargs.get('error')
                    if error:
                        ctx.log_entry(
                            "error",
                            f"{error.error_type}: {error.error_message}",
                            files_affected=[
                                error.file_path] if error.file_path else [],
                            tags=["error", "auto-logged"],
                            metadata={
                                "component": error.component,
                                "line": error.line_number
                            }
                        )

                        if hasattr(result, 'issue_summary'):
                            ctx.log_entry(
                                "fix",
                                result.issue_summary,
                                files_affected=[
                                    error.file_path] if error.file_path else [],
                                tags=["fix", "ai-generated", "auto-logged"],
                                metadata={
                                    "confidence": result.confidence,
                                    "root_cause": result.root_cause
                                }
                            )

                elif operation_type == "validation":
                    file_path = kwargs.get(
                        'file_path', args[1] if len(args) > 1 else 'unknown')
                    if hasattr(result, 'is_safe'):
                        ctx.log_entry(
                            "validation",
                            f"Code validation: {'PASSED' if result.is_safe else 'FAILED'}",
                            files_affected=[
                                file_path] if file_path != 'unknown' else [],
                            tags=["validation", "prevention", "auto-logged"],
                            metadata={
                                "errors_count": len(result.errors_prevented) if hasattr(result, 'errors_prevented') else 0,
                                "validation_type": result.validation_type if hasattr(result, 'validation_type') else 'unknown'
                            }
                        )

                elif operation_type == "scan":
                    if isinstance(result, dict) and 'issues_found' in result:
                        ctx.log_entry(
                            "scan",
                            f"Codebase scan: {result['issues_found']} issues found",
                            files_affected=[],
                            tags=["scan", "proactive", "auto-logged"],
                            metadata={
                                "files_scanned": result.get('files_scanned', 0),
                                "issues": result.get('issues', [])
                            }
                        )

                elif operation_type == "improvement":
                    ctx.log_entry(
                        "improvement",
                        f"Improvement suggestion executed",
                        files_affected=[kwargs.get('file_path', 'unknown')],
                        tags=["improvement", "proactive", "auto-logged"],
                        metadata=result if isinstance(result, dict) else {}
                    )

                return result

            except Exception as e:
                # Log failure
                ctx.log_entry(
                    "error",
                    f"Operation failed: {operation_type} - {str(e)}",
                    files_affected=[],
                    tags=["error", "operation-failure", "auto-logged"],
                    metadata={"operation": operation_type, "error": str(e)}
                )
                raise

        return wrapper
    return decorator


class AutoContextMixin:
    """
    Mixin to add automatic context logging to DevAgent
    Just inherit from this to get automatic logging
    """

    def __init__(self):
        self.context_manager = get_context_manager()
        super().__init__()

    def _auto_log(self, type: str, content: str, files: list = None, tags: list = None, metadata: dict = None):
        """Helper to log context"""
        self.context_manager.log_entry(
            type,
            content,
            files_affected=files or [],
            tags=(tags or []) + ["auto-logged"],
            metadata=metadata or {}
        )

    def log_user_action(self, action: str, details: dict = None):
        """Log user interactions"""
        self._auto_log(
            "user_action",
            action,
            tags=["user", "interaction"],
            metadata=details or {}
        )

    def log_copilot_message(self, message: str, response: str):
        """Log CopilotKit interactions"""
        self._auto_log(
            "copilot_chat",
            f"User: {message}",
            tags=["copilot", "chat"],
            metadata={"response": response}
        )

    def log_system_event(self, event: str, details: dict = None):
        """Log system-level events"""
        self._auto_log(
            "system_event",
            event,
            tags=["system", "event"],
            metadata=details or {}
        )
