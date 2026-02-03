#!/usr/bin/env python3
"""
System Sync & Verification Engine v5.2

Verifies and syncs:
1. Version consistency across all files
2. Dependency compatibility
3. File integrity and structure
4. Documentation accuracy
5. Functionality validation
"""

import os
import json
import re
import sys

class SystemVerifier:
    def __init__(self, root: str = '/workspaces/Halilit-Support-Center'):
        self.root = root
        self.errors = []
        self.warnings = []
        self.info = []
        self.version = "5.2.3"

    def log_error(self, msg: str):
        """Log critical error"""
        self.errors.append(f"❌ {msg}")

    def log_warning(self, msg: str):
        """Log warning"""
        self.warnings.append(f"⚠️  {msg}")

    def log_info(self, msg: str):
        """Log info"""
        self.info.append(f"ℹ️  {msg}")

    def verify_versions(self) -> bool:
        """Verify version consistency"""
        print("\n[1/6] Verifying Version Consistency...")

        versions_found = {}

        # Check backend/__init__.py
        init_file = os.path.join(self.root, 'backend', '__init__.py')
        if os.path.exists(init_file):
            with open(init_file) as f:
                content = f.read()
                match = re.search(
                    r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    versions_found['backend/__init__.py'] = match.group(1)

        # Check frontend/package.json
        pkg_file = os.path.join(self.root, 'frontend', 'package.json')
        if os.path.exists(pkg_file):
            with open(pkg_file) as f:
                data = json.load(f)
                versions_found['frontend/package.json'] = data.get('version')

        # Check README
        readme_file = os.path.join(self.root, 'README.md')
        if os.path.exists(readme_file):
            with open(readme_file) as f:
                content = f.read()
                match = re.search(r'v([\d.]+)', content)
                if match:
                    ver = match.group(1)
                    # Normalize to x.y.z if x.y format
                    if ver.count('.') == 1:
                        ver += '.0'
                    versions_found['README.md'] = ver

        # Verify all match
        all_match = len(set(versions_found.values())) == 1

        if all_match:
            version = list(versions_found.values())[0]
            self.log_info(f"✓ All versions consistent: {version}")
            return True
        else:
            for file, ver in versions_found.items():
                self.log_warning(f"Version mismatch in {file}: {ver}")
            return False

    def verify_dependencies(self) -> bool:
        """Verify dependencies are specified"""
        print("[2/6] Verifying Dependencies...")

        requirements = os.path.join(self.root, 'backend', 'requirements.txt')
        pkg_json = os.path.join(self.root, 'frontend', 'package.json')

        all_ok = True

        # Check backend requirements
        if os.path.exists(requirements):
            with open(requirements) as f:
                content = f.read()
                deps = [line.strip() for line in content.split(
                    '\n') if line.strip() and not line.startswith('#')]
                if deps:
                    self.log_info(
                        f"Backend requirements found: {len(deps)} dependencies")
                else:
                    self.log_warning("No backend dependencies found")
                    all_ok = False
        else:
            self.log_error("backend/requirements.txt not found")
            all_ok = False

        # Check frontend package.json
        if os.path.exists(pkg_json):
            with open(pkg_json) as f:
                data = json.load(f)
                deps = len(data.get('dependencies', {}))
                dev_deps = len(data.get('devDependencies', {}))
                self.log_info(
                    f"Frontend dependencies: {deps} deps, {dev_deps} dev-deps")
        else:
            self.log_error("frontend/package.json not found")
            all_ok = False

        return all_ok

    def verify_file_structure(self) -> bool:
        """Verify critical files exist"""
        print("[3/6] Verifying File Structure...")

        critical_files = [
            'backend/__init__.py',
            'backend/server.py',
            'backend/agents/trinity_swarm.py',
            'backend/workflow/engine.py',
            'backend/workflow/real_maintenance.py',
            'backend/skills/base_skill.py',
            'frontend/src/main.tsx',
            'frontend/src/App.tsx',
            'frontend/vite.config.ts',
            'frontend/package.json',
            'README.md',
            'MAINTENANCE_COMPLETE.md',
        ]

        missing = []
        for file in critical_files:
            path = os.path.join(self.root, file)
            if not os.path.exists(path):
                missing.append(file)
                self.log_error(f"Missing critical file: {file}")
            else:
                size = os.path.getsize(path)
                if size == 0:
                    self.log_error(f"Empty file: {file}")
                else:
                    self.log_info(f"✓ {file} ({size} bytes)")

        return len(missing) == 0

    def verify_documentation(self) -> bool:
        """Verify documentation is current"""
        print("[4/6] Verifying Documentation...")

        docs = [
            'README.md',
            'MAINTENANCE_COMPLETE.md',
            'RELEASE_NOTES_v5.1.md',
        ]

        all_ok = True
        for doc in docs:
            path = os.path.join(self.root, doc)
            if os.path.exists(path):
                with open(path) as f:
                    content = f.read()
                    if len(content) > 100:
                        self.log_info(f"✓ {doc} is complete")
                    else:
                        self.log_warning(f"{doc} seems too short")
                        all_ok = False
            else:
                self.log_warning(f"{doc} not found")
                all_ok = False

        return all_ok

    def verify_code_quality(self) -> bool:
        """Verify code has no obvious issues"""
        print("[5/6] Verifying Code Quality...")

        issues = []

        # Check for 0-byte files
        for root, dirs, files in os.walk(self.root):
            if any(x in root for x in ['.venv', '__pycache__', 'node_modules', '.git']):
                continue

            for file in files:
                if file.endswith(('.py', '.tsx', '.ts')):
                    path = os.path.join(root, file)
                    if os.path.getsize(path) == 0:
                        issues.append(f"Empty file: {path}")

        if issues:
            for issue in issues[:5]:  # Show first 5
                self.log_error(issue)
            return False
        else:
            self.log_info("✓ No empty source files detected")
            return True

    def verify_functionality(self) -> bool:
        """Verify key functionality exists"""
        print("[6/6] Verifying Functionality...")

        all_ok = True

        # Check for key functions/classes
        checks = [
            ('backend/agents/trinity_swarm.py',
             ['class TrinitySwarm', 'class ProductDraft']),
            ('backend/workflow/real_maintenance.py',
             ['class RealCodeCleanupWorkflow', 'class RealHealthCheckWorkflow']),
            ('backend/skills/base_skill.py', ['class BaseSkill']),
            ('frontend/src/App.tsx', ['export', 'function App']),
        ]

        for file_path, patterns in checks:
            full_path = os.path.join(self.root, file_path)
            if os.path.exists(full_path):
                with open(full_path) as f:
                    content = f.read()
                    found = [p for p in patterns if p.lower()
                             in content.lower()]
                    if len(found) == len(patterns):
                        self.log_info(
                            f"✓ {file_path}: All key components found")
                    else:
                        missing = [p for p in patterns if p.lower()
                                   not in content.lower()]
                        self.log_warning(f"{file_path}: Missing {missing}")
                        all_ok = False
            else:
                self.log_error(f"File not found: {file_path}")
                all_ok = False

        return all_ok

    def generate_report(self) -> str:
        """Generate verification report"""
        report = f"""
════════════════════════════════════════════════════════════════════════════════
                    SYSTEM VERIFICATION REPORT v{self.version}
════════════════════════════════════════════════════════════════════════════════

🔍 VERIFICATION RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{chr(10).join(self.info)}

⚠️  WARNINGS ({len(self.warnings)})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chr(10).join(self.warnings) if self.warnings else "✅ No warnings"}

❌ ERRORS ({len(self.errors)})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chr(10).join(self.errors) if self.errors else "✅ No errors"}

📊 SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
System Version:        {self.version}
Status:                {"✅ HEALTHY" if not self.errors else "❌ ISSUES FOUND"}
Errors:                {len(self.errors)}
Warnings:              {len(self.warnings)}
Info Messages:         {len(self.info)}

════════════════════════════════════════════════════════════════════════════════
"""
        return report

    def run_full_verification(self):
        """Run complete verification"""
        print("\n" + "="*80)
        print(" SYSTEM SYNC & VERIFICATION ENGINE v5.2")
        print("="*80)

        results = {
            'versions': self.verify_versions(),
            'dependencies': self.verify_dependencies(),
            'structure': self.verify_file_structure(),
            'documentation': self.verify_documentation(),
            'quality': self.verify_code_quality(),
            'functionality': self.verify_functionality(),
        }

        report = self.generate_report()
        print(report)

        # Overall status
        all_ok = all(results.values())
        status = "✅ PASS" if all_ok else "❌ FAIL"

        print(f"\n📋 VERIFICATION STATUS: {status}")
        print("="*80 + "\n")

        return results

if __name__ == '__main__':
    verifier = SystemVerifier()
    results = verifier.run_full_verification()

    # Exit with error if critical issues
    sys.exit(0 if all(results.values()) else 1)
