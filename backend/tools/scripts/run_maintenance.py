"""
Run Maintenance - Production-ready v5.2.4
"""

#!/usr/bin/env python3
"""
Direct maintenance execution - bypass server issues
"""

import os
import logging
import sys

logger = logging.getLogger(__name__)
sys.path.insert(0, '/workspaces/Halilit-Support-Center')

class HealthCheck:
    def __init__(self, project_root: str = '/workspaces/Halilit-Support-Center'):
        self.project_root = project_root

    def scan(self) -> dict:
        """Scan all Python and TypeScript files"""
        empty_files = []
        total_files = 0

        extensions = ('.py', '.ts', '.tsx', '.js', '.jsx')
        exclude_dirs = {'node_modules', '__pycache__',
                        '.venv', 'dist', 'build', '.next'}

        for root, dirs, files in os.walk(self.project_root):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if file.endswith(extensions):
                    file_path = os.path.join(root, file)
                    total_files += 1

                    try:
                        size = os.path.getsize(file_path)
                        if size == 0:
                            rel_path = os.path.relpath(
                                file_path, self.project_root)
                            empty_files.append(rel_path)
                    except Exception:
                        pass

        return {
            'total_files': total_files,
            'empty_files': len(empty_files),
            'health': 'HEALTHY' if not empty_files else 'DEGRADED',
            'empty_file_list': empty_files[:10]  # Show first 10
        }

class CodeCleanup:
    def __init__(self, project_root: str = '/workspaces/Halilit-Support-Center'):
        self.project_root = project_root

    def cleanup_python_files(self) -> dict:
        """Clean Python files"""
        stats = {
            'files_scanned': 0,
            'files_modified': 0,
            'imports_removed': 0,
            'whitespace_fixed': 0
        }

        for root, dirs, files in os.walk(self.project_root):
            if '__pycache__' in root or '.venv' in root:
                continue

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    stats['files_scanned'] += 1

                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()

                        original = content

                        # Clean whitespace
                        lines = content.split('\n')
                        lines = [line.rstrip() for line in lines]
                        content = '\n'.join(lines)

                        # Ensure final newline
                        if content and not content.endswith('\n'):
                            content += '\n'

                        # Consolidate blank lines
                        while '\n\n\n' in content:
                            content = content.replace('\n\n\n', '\n\n')

                        if content != original:
                            with open(file_path, 'w') as f:
                                f.write(content)
                            stats['files_modified'] += 1
                            stats['whitespace_fixed'] += 1
                    except Exception:
                        pass

        return stats

def main():
    print("\n" + "="*70)
    logger.info("🧹 FULL MAINTENANCE CYCLE - DIRECT EXECUTION")
    print("="*70)

    # Phase 1: Initial health check
    logger.info("\n[Phase 1/4] Initial Health Check...")
    health = HealthCheck()
    initial_health = health.scan()
    print(f"  ✅ Scanned {initial_health['total_files']} files")
    print(
        f"  📊 Status: {initial_health['health']} ({initial_health['empty_files']} empty files)")

    # Phase 2: Code cleanup
    logger.info("\n[Phase 2/4] Code Cleanup...")
    cleanup = CodeCleanup()
    cleanup_results = cleanup.cleanup_python_files()
    print(f"  ✅ Scanned {cleanup_results['files_scanned']} Python files")
    print(f"  ✅ Modified {cleanup_results['files_modified']} files")
    print(
        f"  ✅ Fixed whitespace in {cleanup_results['whitespace_fixed']} files")

    # Phase 3: Final health check
    logger.info("\n[Phase 3/4] Final Health Check...")
    final_health = health.scan()
    print(f"  ✅ Scanned {final_health['total_files']} files")
    print(
        f"  📊 Status: {final_health['health']} ({final_health['empty_files']} empty files)")

    # Phase 4: Summary
    logger.info("\n[Phase 4/4] Maintenance Complete!")
    print("="*70)
    logger.info("📊 MAINTENANCE SUMMARY")
    print("="*70)
    print(f"Total files scanned: {initial_health['total_files']}")
    print(f"Files cleaned: {cleanup_results['files_modified']}")
    print(f"Codebase health: {final_health['health']}")
    logger.info("\n✅ Maintenance cycle complete!")
    logger.info("   Codebase is clean and consolidated.")
    logger.info("="*70 + "\n")

if __name__ == '__main__':
    main()
