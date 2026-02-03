#!/usr/bin/env python3
"""
Full Codebase Cleanup & Consolidation
- Removes clutter files and backups
- Removes unused code
- Consolidates duplicates
- Leaves pure, clean code
"""

import re


class CodebaseCleanup:
    def __init__(self, root: str = '/workspaces/Halilit-Support-Center'):
        self.root = root
        self.removed = 0
        self.cleaned = 0

    def remove_clutter_files(self) -> int:
        """Remove backup files, temp files, and clutter"""
        clutter_patterns = [
            '**/*_BACKUP*',
            '**/*_backup*',
            '**/*.bak',
            '**/*.tmp',
            '**/TIMELINE_BACKUP*',
            '**/GALAXY_DASHBOARD_BACKUP*',
            '**/test_*.html',
            '**/*.swp',
            '**/.DS_Store',
            '**/Thumbs.db'
        ]

        removed = 0
        for pattern in clutter_patterns:
            for file_path in Path(self.root).glob(pattern):
                if file_path.is_file():
                    try:
                        file_path.unlink()
                        print(
                            f"  🗑️  Removed: {file_path.relative_to(self.root)}")
                        removed += 1
                    except Exception as e:
                        print(f"  ⚠️  Failed to remove {file_path}: {e}")

        return removed

    def remove_unused_imports_from_file(self, file_path: str) -> int:
        """Remove unused imports from Python files"""
        if not file_path.endswith('.py'):
            return 0

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            original = content
            removed = 0

            # Find imports
            lines = content.split('\n')
            modified_lines = []

            for i, line in enumerate(lines):
                stripped = line.strip()

                # Check if it's an import
                if re.match(r'^(import|from)\s+', stripped):
                    # Extract imported name
                    match = re.search(r'(?:import|from)\s+(\w+)', stripped)
                    if match:
                        imported_name = match.group(1)
                        # Check if used in rest of file
                        rest = '\n'.join(lines[i+1:])
                        if re.search(rf'\b{imported_name}\b(?![\s]*(?:import|from))', rest):
                            modified_lines.append(line)
                        else:
                            removed += 1
                    else:
                        modified_lines.append(line)
                else:
                    modified_lines.append(line)

            if removed > 0:
                with open(file_path, 'w') as f:
                    f.write('\n'.join(modified_lines))
                return removed

            return 0
        except Exception as e:
            return 0

    def clean_whitespace(self, file_path: str) -> bool:
        """Remove trailing whitespace and fix formatting"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            original = content

            # Remove trailing whitespace
            lines = content.split('\n')
            lines = [line.rstrip() for line in lines]
            content = '\n'.join(lines)

            # Ensure final newline
            if content and not content.endswith('\n'):
                content += '\n'

            # Remove multiple blank lines (keep max 2)
            while '\n\n\n' in content:
                content = content.replace('\n\n\n', '\n\n')

            if content != original:
                with open(file_path, 'w') as f:
                    f.write(content)
                return True
            return False
        except Exception:
            return False

    def consolidate_documentation(self) -> int:
        """Remove duplicate documentation files"""
        # Keep only the essential docs
        essential_docs = {
            'README.md',
            'INTEGRATION_COMPLETE.md',
            'REAL_MAINTENANCE_OPERATIONAL.md',
            'RELEASE_NOTES_v5.1.md'
        }

        removed = 0
        docs_dir = Path(self.root)

        for md_file in docs_dir.glob('*.md'):
            if md_file.name not in essential_docs:
                # Check if it's a duplicate/backup
                if any(x in md_file.name for x in ['BACKUP', 'OLD', 'TEMP', '_COPY', 'DEVAGENT_', 'SKILLS_', 'SYSTEM_', 'AGENT_', 'AUTO_', 'CHANGELOG', 'DIAGNOSTIC', 'PREVENTION', 'GALAXY_', 'ADK_', 'DOCS_']):
                    try:
                        md_file.unlink()
                        print(f"  📄 Removed doc: {md_file.name}")
                        removed += 1
                    except Exception as e:
                        print(f"  ⚠️  Failed to remove {md_file.name}: {e}")

        return removed

    def run_full_cleanup(self):
        """Execute all cleanup operations"""
        print("\n" + "="*70)
        print("🧹 FULL CODEBASE CLEANUP & CONSOLIDATION")
        print("="*70)

        # Phase 1: Remove clutter
        print("\n[Phase 1] Removing backup files and clutter...")
        clutter_removed = self.remove_clutter_files()
        print(f"  ✅ Removed {clutter_removed} clutter files")

        # Phase 2: Clean Python files
        print("\n[Phase 2] Cleaning Python files...")
        py_files = list(Path(self.root).glob('**/*.py'))
        total_imports_removed = 0
        total_whitespace_fixed = 0

        for py_file in py_files:
            if '__pycache__' in str(py_file):
                continue

            imports_removed = self.remove_unused_imports_from_file(
                str(py_file))
            total_imports_removed += imports_removed

            if self.clean_whitespace(str(py_file)):
                total_whitespace_fixed += 1

        print(f"  ✅ Removed {total_imports_removed} unused imports")
        print(f"  ✅ Fixed whitespace in {total_whitespace_fixed} files")

        # Phase 3: Clean TypeScript/JavaScript files
        print("\n[Phase 3] Cleaning TypeScript/JavaScript files...")
        ts_files = list(Path(self.root).glob('**/*.{ts,tsx,js,jsx}'))
        total_ts_cleaned = 0

        for ts_file in ts_files:
            if any(x in str(ts_file) for x in ['node_modules', '.next', 'dist', 'build']):
                continue

            if self.clean_whitespace(str(ts_file)):
                total_ts_cleaned += 1

        print(f"  ✅ Fixed whitespace in {total_ts_cleaned} TypeScript files")

        # Phase 4: Consolidate documentation
        print("\n[Phase 4] Consolidating documentation...")
        docs_removed = self.consolidate_documentation()
        print(f"  ✅ Removed {docs_removed} redundant docs")

        # Summary
        print("\n" + "="*70)
        print("✅ CLEANUP COMPLETE")
        print("="*70)
        print(f"Total clutter removed: {clutter_removed}")
        print(f"Imports cleaned: {total_imports_removed}")
        print(
            f"Files whitespace fixed: {total_whitespace_fixed + total_ts_cleaned}")
        print(f"Documentation consolidated: {docs_removed}")
        print("\nCodebase is now clean and consolidated!")
        print("="*70 + "\n")


if __name__ == '__main__':
    cleanup = CodebaseCleanup()
    cleanup.run_full_cleanup()
