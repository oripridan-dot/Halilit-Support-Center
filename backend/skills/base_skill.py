# backend/skills/base_skill.py
"""
Base Skill Interface

Every skill must:
1. Implement execute()
2. Return (success: bool, output: Any)
3. Include verification logic to prevent catastrophic failures
"""

import logging

class BaseSkill(ABC):
    """
    Abstract base class for all agent skills.

    Skills are standalone, verifiable capabilities that agents *use*, not *are*.
    This separation allows upgrading capabilities without modifying agent logic.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # Create console handler if not exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Executes the skill with the given context.

        Args:
            context: Dictionary containing all required parameters for the skill

        Returns:
            Tuple of (success: bool, output: Any)
            - success: True if operation completed without errors
            - output: Result data on success, error message on failure

        Example:
            success, result = skill.execute({'file_path': 'test.py', 'content': 'print("hi")'})
            if success:
                print(f"Success: {result}")
            else:
                print(f"Failed: {result}")
        """
        pass

    def validate_context(self, context: Dict[str, Any], required_keys: list) -> Tuple[bool, str]:
        """
        Helper method to validate that context contains all required keys.

        Args:
            context: The context dictionary to validate
            required_keys: List of required key names

        Returns:
            Tuple of (valid: bool, error_message: str)
        """
        missing = [key for key in required_keys if key not in context]
        if missing:
            error = f"Missing required context keys: {', '.join(missing)}"
            self.logger.error(error)
            return False, error
        return True, ""

    def log_execution(self, success: bool, operation: str, details: str = ""):
        """
        Standardized logging for skill execution.

        Args:
            success: Whether the operation succeeded
            operation: Name of the operation performed
            details: Additional context about the operation
        """
        if success:
            self.logger.info(f"✅ {operation} - {details}")
        else:
            self.logger.error(f"❌ {operation} - {details}")
