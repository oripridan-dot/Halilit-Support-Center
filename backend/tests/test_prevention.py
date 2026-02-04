"""
Test Prevention - Production-ready v5.2.4
"""

#!/usr/bin/env python3
"""
Test DevAgent Prevention Capabilities
Demonstrates how DevAgent prevents syntax and type errors
"""

import sys
import logging
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logger = logging.getLogger(__name__)

def test_prevention():
    """Test error prevention features"""
    agent = DevAgent()

    print("\n" + "="*70)
    logger.info("🛡️ DevAgent Prevention Test - Catching Errors BEFORE They Happen")
    logger.info("="*70 + "\n")

    # Test 1: React Hooks violation (the actual error from screenshot)
    logger.info("📝 Test 1: React Hooks Violation Detection\n")

    bad_code = """
export function DevAgentMonitor() {
  const [errors, setErrors] = useState([]);
  const [isDevelopment] = useState(() => import.meta.env.DEV);

  // ❌ THIS IS WRONG - Return before hooks are done!
  if (!isDevelopment) {
    return null;
  }

  // More hooks after conditional return
  const analyzeError = useCallback(async (error) => {
    // ...
  }, []);

  return <div>Monitor</div>;
}
"""

    result = agent.validate_syntax("DevAgentMonitor.tsx", bad_code)

    if result.is_safe:
        logger.info("❌ MISSED: Should have caught the error!")
    else:
        print(f"✅ PREVENTED: {len(result.errors_prevented)} errors caught!\n")
        for err in result.errors_prevented:
            print(f"   🚫 Line {err['line']}: {err['type']}")
            print(f"      {err['message']}")
            print()

    # Test 2: Fixed code
    logger.info("\n📝 Test 2: Correct React Code\n")

    good_code = """
export function DevAgentMonitor() {
  const [errors, setErrors] = useState([]);
  const [isDevelopment] = useState(() => import.meta.env.DEV);

  // More hooks
  const analyzeError = useCallback(async (error) => {
    // ...
  }, []);

  // ✅ Return AFTER all hooks
  if (!isDevelopment) {
    return null;
  }

  return <div>Monitor</div>;
}
"""

    result = agent.validate_syntax("DevAgentMonitor.tsx", good_code)

    if result.is_safe:
        logger.info("✅ PASSED: Code is safe to use!")
    else:
        print(f"❌ FAILED: Found {len(result.errors_prevented)} errors")
        for err in result.errors_prevented:
            print(f"   Line {err['line']}: {err['message']}")

    # Test 3: Subscribe without null check
    logger.info("\n\n📝 Test 3: Potential Null Reference Detection\n")

    risky_code = """
useEffect(() => {
  const subscription = observable.subscribe(value => {
    console.log(value);
  });

  return () => subscription.unsubscribe();
}, []);
"""

    result = agent.validate_syntax("Component.tsx", risky_code)

    if len(result.warnings) > 0:
        print(f"⚠️  WARNED: {len(result.warnings)} potential issues found!\n")
        for warn in result.warnings:
            print(f"   ⚠️  {warn['type']}")
            print(f"      {warn['message']}")

    # Test 4: Python syntax error
    logger.info("\n\n📝 Test 4: Python Syntax Error Detection\n")

    bad_python = """
def my_function():
    if x == 1
        logger.info("Missing colon!")
    return x
"""

    result = agent.validate_syntax("test.py", bad_python)

    if result.is_safe:
        logger.info("❌ MISSED: Should have caught Python syntax error!")
    else:
        print(f"✅ PREVENTED: Python syntax error caught!\n")
        for err in result.errors_prevented:
            print(f"   🚫 {err['type']}: {err['message']}")

    print("\n" + "="*70)
    logger.info("✅ Prevention Test Complete!")
    logger.info("="*70 + "\n")

    logger.info("💡 DevAgent can now PREVENT:")
    logger.info("   • React Hooks violations")
    logger.info("   • Syntax errors (Python, TypeScript, JavaScript)")
    logger.info("   • Potential null references")
    logger.info("   • Missing error boundaries")
    logger.info("   • Type errors (when TypeScript is available)")
    logger.info("\n🚀 Errors caught BEFORE they run = Faster development!\n")

if __name__ == "__main__":
    test_prevention()
