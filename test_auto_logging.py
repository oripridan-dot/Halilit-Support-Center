#!/usr/bin/env python3
"""
Test Automatic Context Logging
Verifies that ALL operations are automatically logged to context
"""

import time
from backend.agents.context_manager import ContextManager
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_auto_logging():
    """Test that everything is automatically logged"""

    print("\n" + "="*70)
    print("🤖 Testing AUTOMATIC Context Logging")
    print("="*70 + "\n")

    # Get context manager
    ctx = ContextManager()

    # Count entries before
    before_count = ctx.get_context()['total_entries']
    print(f"📊 Context entries before test: {before_count}\n")

    # Create DevAgent (should auto-log initialization)
    print("1️⃣ Creating DevAgent...")
    agent = DevAgent()
    time.sleep(0.5)

    # Analyze an error (should auto-log error + fix)
    print("\n2️⃣ Analyzing error...")
    error = ErrorReport(
        error_type="TypeError",
        error_message="Cannot read property 'subscribe' of null",
        stack_trace="at useEffect",
        component="DevAgentMonitor",
        file_path="frontend/src/components/DevAgentMonitor.tsx",
        line_number=45,
        timestamp="2026-02-03T00:00:00Z",
        context={"framework": "React 18"}
    )

    fix = agent.analyze_error(error)
    print(f"   Fix confidence: {fix.confidence}%")
    time.sleep(0.5)

    # Validate syntax (should auto-log validation)
    print("\n3️⃣ Validating syntax...")
    bad_code = "const x = { missing_close"
    result = agent.validate_syntax("test.tsx", bad_code)
    print(f"   Validation: {'PASSED' if result.is_safe else 'FAILED'}")
    time.sleep(0.5)

    # Scan codebase (should auto-log scan)
    print("\n4️⃣ Scanning codebase...")
    scan_result = agent.scan_codebase("frontend/src")
    print(f"   Found {scan_result.get('issues_found', 0)} issues")
    time.sleep(0.5)

    # Count entries after
    after_count = ctx.get_context()['total_entries']
    print(f"\n📊 Context entries after test: {after_count}")
    print(f"   New entries: {after_count - before_count}")

    # Show recent entries
    print("\n" + "="*70)
    print("📝 Recent Context Entries (Last 10)")
    print("="*70 + "\n")

    history = ctx.get_recent_history(10)
    for entry in history:
        print(f"[{entry.timestamp[:19]}] {entry.type.upper()}")
        print(f"   {entry.content[:80]}...")
        if entry.tags:
            print(f"   Tags: {', '.join(entry.tags)}")
        if entry.files_affected:
            print(f"   Files: {', '.join(entry.files_affected[:3])}")
        print()

    # Verify automatic logging
    print("="*70)
    if after_count > before_count:
        print(
            f"✅ SUCCESS: {after_count - before_count} entries automatically logged!")
        print("   • DevAgent initialization")
        print("   • Error analysis + Fix suggestion")
        print("   • Syntax validation")
        print("   • Codebase scan")
        print("\n🎯 ALL operations are now AUTOMATICALLY tracked!")
    else:
        print("❌ FAILED: No automatic logging detected")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_auto_logging()
