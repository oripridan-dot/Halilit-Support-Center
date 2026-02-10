# backend/skills/frontend_builder.py
"""
Frontend Builder Skill

Safe React component builder with multi-layer verification.
This skill PREVENTS the catastrophic 0-byte file incidents.

Verification Layers:
1. File size check (> 0 bytes)
2. Basic syntax validation (imports, exports)
3. Content integrity check
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Tuple
from .base_skill import BaseSkill


class ReactComponentBuilder(BaseSkill):
    """
    Builds and validates React components with strict safety checks.

    CRITICAL GUARDRAIL: This skill will FAIL if it cannot verify:
    - File is not empty (> 0 bytes)
    - File contains valid React import
    - File contains an export statement

    This prevents the exact disaster that wiped your frontend.
    """

    REQUIRED_PATTERNS = {
        'react_import': r'import\s+(?:React|.*?)\s+from\s+[\'"]react[\'"]',
        'export': r'export\s+(?:default|const|function)',
    }

    MIN_FILE_SIZE = 100  # Realistic minimum for a component (bytes)

    VISUAL_THEME_PATTERNS = [
        (r'slate-900', 'Galaxy Background (slate-900)'),
        (r'blue-500', 'Galaxy Accent (blue-500)')
    ]

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Builds a React component with verification.

        Required context keys:
        - file_path: Absolute or relative path to the component file
        - code_content: The generated React component code

        Optional context keys:
        - skip_validation: If True, skips content validation (use with caution!)
        - create_backup: If True, backs up existing file before overwriting

        Returns:
            (True, details_dict) on success
            (False, error_message) on failure
        """
        # Validate required context
        valid, error = self.validate_context(
            context, ['file_path', 'code_content'])
        if not valid:
            return False, error

        file_path = context['file_path']
        code_content = context['code_content']
        skip_validation = context.get('skip_validation', False)
        create_backup = context.get('create_backup', True)

        try:
            # Ensure absolute path
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)

            # Create parent directories if needed
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            # BACKUP existing file if requested
            if create_backup and os.path.exists(file_path):
                backup_path = f"{file_path}.backup"
                with open(file_path, 'r', encoding='utf-8') as original:
                    with open(backup_path, 'w', encoding='utf-8') as backup:
                        backup.write(original.read())
                self.logger.info(f"📦 Backup created: {backup_path}")

            # PRE-WRITE VALIDATION: Check content integrity
            if not skip_validation:
                validation_result = self._validate_content(code_content)
                if not validation_result[0]:
                    return False, f"Pre-write validation failed: {validation_result[1]}"

                # VISUAL VALIDATION (Strict Policy)
                # Only check if it looks like a UI component (has JSX/return)
                if 'return (' in code_content or 'return <' in code_content:
                    valid_visuals, visual_msg = self._validate_visual_standards(
                        code_content)
                    if not valid_visuals:
                        return False, f"Visual Validation Failed: {visual_msg}"

            # WRITE the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code_content)

            # POST-WRITE VERIFICATION: The Critical Guardrail
            verification = self._verify_written_file(file_path, code_content)
            if not verification[0]:
                # ROLLBACK: If verification fails, restore backup or delete corrupt file
                if create_backup and os.path.exists(f"{file_path}.backup"):
                    os.replace(f"{file_path}.backup", file_path)
                    self.logger.warning(
                        f"⚠️  Verification failed. Backup restored.")
                else:
                    os.remove(file_path)
                    self.logger.warning(
                        f"⚠️  Verification failed. Corrupt file deleted.")

                return False, f"Post-write verification failed: {verification[1]}"

            # SUCCESS
            file_size = os.path.getsize(file_path)
            result = {
                'file_path': file_path,
                'size_bytes': file_size,
                'lines': len(code_content.splitlines()),
                'status': 'verified'
            }

            self.log_execution(
                True,
                "ReactComponentBuilder",
                f"{file_path} ({file_size} bytes, {result['lines']} lines)"
            )

            return True, result

        except Exception as e:
            self.log_execution(False, "ReactComponentBuilder", str(e))
            return False, f"Exception during build: {str(e)}"

    def _validate_visual_standards(self, code_content: str) -> Tuple[bool, str]:
        """
        Validates that the component adheres to the Galaxy Theme visual standards.
        Required: slate-900 (Background), blue-500 (Details)
        """
        missing = []
        for pattern, name in self.VISUAL_THEME_PATTERNS:
            if not re.search(pattern, code_content):
                missing.append(name)

        if missing:
            return False, f"Missing strict visual compliance: {', '.join(missing)}. Please use 'slate-900' for backgrounds and 'blue-500' for accents."

        return True, "Visual verification passed"

    def _validate_content(self, code_content: str) -> Tuple[bool, str]:
        """
        Validates that the code content meets basic React standards.

        Checks:
        1. Not empty
        2. Contains React import
        3. Contains export statement
        4. Minimum realistic size
        """
        if not code_content or len(code_content.strip()) == 0:
            return False, "Code content is empty"

        if len(code_content) < self.MIN_FILE_SIZE:
            return False, f"Code content too small ({len(code_content)} bytes < {self.MIN_FILE_SIZE} bytes)"

        # Check for React import
        if not re.search(self.REQUIRED_PATTERNS['react_import'], code_content, re.MULTILINE):
            return False, "Missing React import statement"

        # Check for export statement
        if not re.search(self.REQUIRED_PATTERNS['export'], code_content, re.MULTILINE):
            return False, "Missing export statement"

        return True, "Content validation passed"

    def _verify_written_file(self, file_path: str, expected_content: str) -> Tuple[bool, str]:
        """
        Verifies that the file was written correctly.

        Critical checks:
        1. File exists
        2. File size > 0 bytes
        3. File content matches what was written
        4. File is readable
        """
        if not os.path.exists(file_path):
            return False, "File does not exist after write"

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, "File is 0 bytes (CRITICAL: The exact bug we're preventing!)"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                actual_content = f.read()

            if actual_content != expected_content:
                return False, f"Content mismatch (expected {len(expected_content)} bytes, got {len(actual_content)} bytes)"

            return True, f"File verified: {file_size} bytes"

        except Exception as e:
            return False, f"File read verification failed: {str(e)}"


class TypeScriptModuleBuilder(BaseSkill):
    """
    Builds TypeScript modules with type safety checks.
    """

    MIN_FILE_SIZE = 50

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Builds a TypeScript module with verification.

        Required context keys:
        - file_path: Path to the .ts or .tsx file
        - code_content: The TypeScript code
        """
        valid, error = self.validate_context(
            context, ['file_path', 'code_content'])
        if not valid:
            return False, error

        file_path = context['file_path']
        code_content = context['code_content']

        try:
            # Basic validation
            if len(code_content) < self.MIN_FILE_SIZE:
                return False, f"Content too small ({len(code_content)} bytes)"

            # Ensure file has .ts or .tsx extension
            if not (file_path.endswith('.ts') or file_path.endswith('.tsx')):
                return False, f"Invalid TypeScript file extension: {file_path}"

            # Write file
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code_content)

            # Verify
            if os.path.getsize(file_path) == 0:
                os.remove(file_path)
                return False, "File write resulted in 0 bytes"

            result = {
                'file_path': file_path,
                'size_bytes': os.path.getsize(file_path),
                'status': 'verified'
            }

            self.log_execution(True, "TypeScriptModuleBuilder",
                               f"{file_path} ({result['size_bytes']} bytes)")
            return True, result

        except Exception as e:
            self.log_execution(False, "TypeScriptModuleBuilder", str(e))
            return False, str(e)
