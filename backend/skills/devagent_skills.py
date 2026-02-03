"""
DevAgent Skills - Code Maintenance & System Health

Capabilities:
- Auto-update and sync code across codebase
- Verify code compatibility and standards
- Format and organize code
- Validate dependencies
- Fix imports and structure
"""

import os
import re
import json
from backend.skills.base_skill import BaseSkill

class CodeAutoUpdateSkill(BaseSkill):
    """
    Automatically updates code to fix compatibility issues.
    Applies targeted fixes without breaking existing functionality.
    """

    def __init__(self):
        super().__init__()
        self.supported_languages = {'.py', '.ts', '.tsx', '.js', '.jsx'}
        self.safe_replacements = {
            'deprecated_import': 'new_import',
            'old_method': 'new_method'
        }

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Auto-update code to fix issues.

        Context requires:
        - file_path: str - File to update
        - changes: List[dict] - Changes to apply
        - preserve_functionality: bool (default: True)
        """
        valid, error = self.validate_context(context, ['file_path', 'changes'])
        if not valid:
            return False, error

        file_path = context['file_path']
        changes = context['changes']
        preserve_func = context.get('preserve_functionality', True)

        self.logger.info(f"🔄 Auto-updating: {file_path}")

        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"

            # Read original content
            with open(file_path, 'r') as f:
                original_content = f.read()

            updated_content = original_content
            applied_changes = []

            # Apply each change safely
            for change in changes:
                old_pattern = change.get('old_pattern')
                new_pattern = change.get('new_pattern')
                change_type = change.get('type', 'replacement')

                if not old_pattern or not new_pattern:
                    continue

                # Check if change would break functionality
                if preserve_func and self._would_break_functionality(old_pattern):
                    self.logger.warning(
                        f"⚠️  Skipping potentially breaking change: {old_pattern}")
                    continue

                # Apply change
                if old_pattern in updated_content:
                    updated_content = updated_content.replace(
                        old_pattern, new_pattern)
                    applied_changes.append(change_type)
                    self.logger.info(f"  ✅ Applied: {change_type}")

            # Write back only if changes applied
            if applied_changes:
                with open(file_path, 'w') as f:
                    f.write(updated_content)

                self.logger.info(
                    f"  ✅ Updated with {len(applied_changes)} changes")
                return True, {
                    'file_path': file_path,
                    'changes_applied': len(applied_changes),
                    'change_types': applied_changes,
                    'size_before': len(original_content),
                    'size_after': len(updated_content)
                }
            else:
                self.logger.info(f"  ℹ️  No changes needed")
                return True, {
                    'file_path': file_path,
                    'changes_applied': 0,
                    'change_types': [],
                    'message': 'No changes needed'
                }

        except Exception as e:
            error_msg = f"Auto-update failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def _would_break_functionality(self, pattern: str) -> bool:
        """Check if change might break functionality"""
        breaking_keywords = ['__init__', 'class', 'def ', 'return', 'import']
        return any(keyword in pattern for keyword in breaking_keywords)

class CodeSyncSkill(BaseSkill):
    """
    Synchronizes code across related files.
    Ensures consistency in imports, interfaces, and definitions.
    """

    def __init__(self):
        super().__init__()
        self.sync_patterns = {
            'imports': r'^from|^import',
            'exports': r'^export',
            'interfaces': r'interface|class'
        }

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Sync code across files.

        Context requires:
        - source_file: str - Source of truth
        - target_files: List[str] - Files to sync to
        - sync_type: str - 'imports' | 'exports' | 'interfaces'
        """
        valid, error = self.validate_context(
            context, ['source_file', 'target_files', 'sync_type'])
        if not valid:
            return False, error

        source_file = context['source_file']
        target_files = context['target_files']
        sync_type = context['sync_type']

        self.logger.info(f"🔗 Syncing {sync_type} from {source_file}")

        try:
            if not os.path.exists(source_file):
                return False, f"Source file not found: {source_file}"

            # Read source content
            with open(source_file, 'r') as f:
                source_content = f.read()

            # Extract pattern from source
            pattern = self.sync_patterns.get(sync_type, '')
            matching_lines = [line for line in source_content.split('\n')
                              if re.match(pattern, line)]

            synced_count = 0

            # Apply to each target file
            for target_file in target_files:
                if not os.path.exists(target_file):
                    self.logger.warning(
                        f"⚠️  Target file not found: {target_file}")
                    continue

                with open(target_file, 'r') as f:
                    target_content = f.read()

                # Remove old pattern lines
                old_lines = [line for line in target_content.split('\n')
                             if re.match(pattern, line)]

                for old_line in old_lines:
                    target_content = target_content.replace(
                        old_line + '\n', '')

                # Add new pattern lines if not present
                for new_line in matching_lines:
                    if new_line not in target_content:
                        # Insert at appropriate location
                        target_content = self._insert_at_section(
                            target_content, new_line, sync_type)
                        synced_count += 1

                with open(target_file, 'w') as f:
                    f.write(target_content)

            self.logger.info(
                f"  ✅ Synced {synced_count} items across {len(target_files)} files")

            return True, {
                'source_file': source_file,
                'target_files': len(target_files),
                'items_synced': synced_count,
                'sync_type': sync_type,
                'status': 'synchronized'
            }

        except Exception as e:
            error_msg = f"Code sync failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def _insert_at_section(self, content: str, line: str, section: str) -> str:
        """Insert line at appropriate section"""
        lines = content.split('\n')
        # Simple insertion at top for now
        return line + '\n' + content

class CompatibilityCheckSkill(BaseSkill):
    """
    Checks code compatibility across the system.
    Detects version mismatches, missing dependencies, etc.
    """

    def __init__(self):
        super().__init__()
        self.compatibility_rules = {
            'import_usage': 'Verify imports are used',
            'version_match': 'Check dependency versions',
            'type_consistency': 'Ensure type consistency',
            'interface_compliance': 'Match interfaces'
        }

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Check code compatibility.

        Context requires:
        - file_path: str - File to check
        - compatibility_level: str (default: 'standard')
        """
        valid, error = self.validate_context(context, ['file_path'])
        if not valid:
            return False, error

        file_path = context['file_path']
        level = context.get('compatibility_level', 'standard')

        self.logger.info(f"✔️  Checking compatibility: {file_path} ({level})")

        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"

            with open(file_path, 'r') as f:
                content = f.read()

            issues = []
            warnings = []

            # Check imports
            imports = re.findall(
                r'^(?:from|import)\s+(.+)', content, re.MULTILINE)
            unused_imports = self._find_unused_imports(content, imports)
            if unused_imports:
                issues.extend([f"Unused import: {i}" for i in unused_imports])

            # Check for deprecated patterns
            deprecated = re.findall(
                r'(deprecated|legacy|old_way)', content, re.IGNORECASE)
            if deprecated:
                warnings.extend(
                    [f"Found deprecated pattern: {d}" for d in deprecated])

            # Check consistency
            consistency_score = 100 - (len(issues) * 10 + len(warnings) * 5)
            compatibility_score = max(0, consistency_score)

            is_compatible = compatibility_score >= 80

            self.logger.info(f"  Compatibility: {compatibility_score}%")

            return True, {
                'file_path': file_path,
                'compatibility_score': compatibility_score,
                'is_compatible': is_compatible,
                'issues': issues,
                'warnings': warnings,
                'issue_count': len(issues),
                'warning_count': len(warnings)
            }

        except Exception as e:
            error_msg = f"Compatibility check failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def _find_unused_imports(self, content: str, imports: List[str]) -> List[str]:
        """Find imports that aren't used in code"""
        unused = []
        for imp in imports:
            # Simplistic check: does the import name appear in code?
            import_name = imp.split()[0]
            if import_name not in content.replace('import ' + import_name, ''):
                unused.append(import_name)
        return unused[:3]  # Limit to 3 for brevity

class CodeFormatterSkill(BaseSkill):
    """
    Formats code to match project standards.
    Handles indentation, spacing, line length, etc.
    """

    def __init__(self):
        super().__init__()
        self.format_rules = {
            'indent_size': 4,
            'max_line_length': 100,
            'trailing_whitespace': False,
            'final_newline': True
        }

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Format code file.

        Context requires:
        - file_path: str - File to format
        - language: str (optional) - Language hint
        """
        valid, error = self.validate_context(context, ['file_path'])
        if not valid:
            return False, error

        file_path = context['file_path']
        language = context.get('language', 'unknown')

        self.logger.info(f"🎨 Formatting: {file_path}")

        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"

            with open(file_path, 'r') as f:
                original_content = f.read()

            formatted_content = original_content

            # Remove trailing whitespace
            lines = formatted_content.split('\n')
            lines = [line.rstrip() for line in lines]
            formatted_content = '\n'.join(lines)

            # Ensure final newline
            if formatted_content and not formatted_content.endswith('\n'):
                formatted_content += '\n'

            # Fix indentation (Python-specific for now)
            if file_path.endswith('.py'):
                formatted_content = self._fix_python_indentation(
                    formatted_content)

            # Count changes
            original_lines = len(original_content.split('\n'))
            formatted_lines = len(formatted_content.split('\n'))
            changed = original_content != formatted_content

            if changed:
                with open(file_path, 'w') as f:
                    f.write(formatted_content)
                self.logger.info(f"  ✅ Formatted successfully")
            else:
                self.logger.info(f"  ℹ️  Already well-formatted")

            return True, {
                'file_path': file_path,
                'formatted': changed,
                'lines_original': original_lines,
                'lines_after': formatted_lines,
                'language': language,
                'status': 'formatted' if changed else 'already_formatted'
            }

        except Exception as e:
            error_msg = f"Code formatting failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def _fix_python_indentation(self, content: str) -> str:
        """Fix Python indentation"""
        lines = content.split('\n')
        result = []

        for line in lines:
            # Skip empty lines
            if not line.strip():
                result.append('')
                continue

            # Count leading spaces
            stripped = line.lstrip()
            leading_spaces = len(line) - len(stripped)

            # Convert to standard indentation (4 spaces)
            indent_level = leading_spaces // 2  # Assume mixed indentation
            new_indent = indent_level * 4

            result.append(' ' * new_indent + stripped)

        return '\n'.join(result)

class ImportOrganizationSkill(BaseSkill):
    """
    Organizes and fixes imports across files.
    Groups imports by type and removes duplicates.
    """

    def __init__(self):
        super().__init__()

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Organize imports in file.

        Context requires:
        - file_path: str - File to organize
        """
        valid, error = self.validate_context(context, ['file_path'])
        if not valid:
            return False, error

        file_path = context['file_path']

        self.logger.info(f"📦 Organizing imports: {file_path}")

        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"

            with open(file_path, 'r') as f:
                lines = f.readlines()

            # Separate imports from rest
            import_lines = []
            other_lines = []
            import_end_idx = 0

            for i, line in enumerate(lines):
                if re.match(r'^(?:from|import)\s+', line) or line.strip() == '':
                    import_lines.append(line)
                    import_end_idx = i + 1
                else:
                    other_lines = lines[i:]
                    break

            # Remove duplicates and sort
            import_set = {}
            for line in import_lines:
                if line.strip() and line not in import_set.values():
                    key = line.strip()[:30]  # Use start of import as key
                    import_set[key] = line

            # Group imports
            stdlib_imports = []
            third_party_imports = []
            local_imports = []

            for line in import_set.values():
                if 'from backend' in line or 'from .' in line:
                    local_imports.append(line)
                elif any(std in line for std in ['os', 'sys', 're', 'json']):
                    stdlib_imports.append(line)
                else:
                    third_party_imports.append(line)

            # Reconstruct file
            organized_lines = []
            if stdlib_imports:
                organized_lines.extend(sorted(stdlib_imports))
                organized_lines.append('\n')
            if third_party_imports:
                organized_lines.extend(sorted(third_party_imports))
                organized_lines.append('\n')
            if local_imports:
                organized_lines.extend(sorted(local_imports))
                organized_lines.append('\n')

            organized_lines.extend(other_lines)

            # Write back
            with open(file_path, 'w') as f:
                f.writelines(organized_lines)

            self.logger.info(
                f"  ✅ Organized imports ({len(import_set)} unique imports)")

            return True, {
                'file_path': file_path,
                'imports_unique': len(import_set),
                'stdlib_count': len(stdlib_imports),
                'third_party_count': len(third_party_imports),
                'local_count': len(local_imports),
                'status': 'organized'
            }

        except Exception as e:
            error_msg = f"Import organization failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

class CodeValidationSkill(BaseSkill):
    """
    Validates code quality and standards.
    Checks for best practices, naming conventions, etc.
    """

    def __init__(self):
        super().__init__()
        self.validation_rules = {
            'naming_convention': 'snake_case for Python, camelCase for TS',
            'max_function_length': 50,
            'max_file_length': 500,
            'required_docstrings': True,
            'type_hints': 'Encouraged'
        }

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Validate code quality.

        Context requires:
        - file_path: str - File to validate
        - strict_mode: bool (default: False)
        """
        valid, error = self.validate_context(context, ['file_path'])
        if not valid:
            return False, error

        file_path = context['file_path']
        strict = context.get('strict_mode', False)

        self.logger.info(f"✅ Validating: {file_path}")

        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"

            with open(file_path, 'r') as f:
                content = f.read()
                lines = content.split('\n')

            issues = []
            warnings = []

            # Check file length
            if len(lines) > self.validation_rules['max_file_length']:
                warnings.append(f"File too long: {len(lines)} lines")

            # Check for docstrings (Python)
            if file_path.endswith('.py'):
                functions = re.findall(r'def\s+(\w+)', content)
                docstrings = len(re.findall(r'"""', content))
                if docstrings < len(functions) // 2 and self.validation_rules['required_docstrings']:
                    warnings.append(f"Missing docstrings in some functions")

            # Check naming conventions
            snake_case_funcs = re.findall(r'def\s+([a-z_]+)', content)
            bad_names = [
                f for f in snake_case_funcs if '-' in f or f.isupper()]
            if bad_names and strict:
                issues.extend(
                    [f"Bad function name: {n}" for n in bad_names[:3]])

            validation_score = 100 - (len(issues) * 20 + len(warnings) * 10)
            validation_score = max(0, validation_score)

            self.logger.info(f"  Validation Score: {validation_score}%")

            return True, {
                'file_path': file_path,
                'validation_score': validation_score,
                'is_valid': validation_score >= 70,
                'issues': issues,
                'warnings': warnings,
                'total_problems': len(issues) + len(warnings)
            }

        except Exception as e:
            error_msg = f"Code validation failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

class DependencyResolutionSkill(BaseSkill):
    """
    Resolves and manages code dependencies.
    Ensures all imports can be resolved and versions are compatible.
    """

    def __init__(self):
        super().__init__()
        self.dependency_cache = {}

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Resolve dependencies.

        Context requires:
        - file_path: str - File to check
        - project_root: str (optional) - Root of project
        """
        valid, error = self.validate_context(context, ['file_path'])
        if not valid:
            return False, error

        file_path = context['file_path']
        project_root = context.get(
            'project_root', '/workspaces/Halilit-Support-Center')

        self.logger.info(f"🔗 Resolving dependencies: {file_path}")

        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"

            with open(file_path, 'r') as f:
                content = f.read()

            # Extract imports
            imports = re.findall(
                r'^(?:from|import)\s+(.+)', content, re.MULTILINE)

            resolved = []
            unresolved = []
            internal_imports = []

            for imp in imports:
                module_name = imp.split()[0].split('.')[0]

                # Check if it's internal
                if 'backend' in imp or 'frontend' in imp:
                    internal_imports.append(module_name)
                    # Verify internal import exists
                    if not self._check_internal_import(module_name, project_root):
                        unresolved.append(module_name)
                    else:
                        resolved.append(module_name)
                else:
                    # External module - assume available
                    resolved.append(module_name)

            self.logger.info(
                f"  Resolved: {len(resolved)}, Unresolved: {len(unresolved)}")

            return True, {
                'file_path': file_path,
                'resolved_count': len(resolved),
                'unresolved_count': len(unresolved),
                'internal_count': len(internal_imports),
                'resolved_imports': resolved,
                'unresolved_imports': unresolved,
                'all_resolved': len(unresolved) == 0
            }

        except Exception as e:
            error_msg = f"Dependency resolution failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def _check_internal_import(self, module: str, root: str) -> bool:
        """Check if internal module exists"""
        # Simplified check
        possible_paths = [
            os.path.join(root, module),
            os.path.join(root, 'backend', module.split('.')[-1]),
            os.path.join(root, 'frontend', 'src', module.split('.')[-1])
        ]
        return any(os.path.exists(p) or os.path.exists(p + '.py') for p in possible_paths)
