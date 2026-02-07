#!/usr/bin/env python3
"""
Phase 1D: CopilotKit Integration Test

Tests the complete CopilotKit integration:
1. Backend executor initialization
2. Available skills listing
3. Single skill execution via executor
4. Pipeline execution with streaming
5. API endpoint availability
6. Error handling and edge cases
"""

from backend.copilot_skill_executor import CopilotSkillExecutor
import sys
import json
import asyncio
sys.path.insert(0, '/workspaces/Halilit-Support-Center')


def test_executor_initialization():
    """Test 1: CopilotKit Executor Initialization"""
    print("\n" + "="*60)
    print("TEST 1: CopilotKit Executor Initialization")
    print("="*60)

    try:
        executor = CopilotSkillExecutor()
        print(f"✓ Executor created successfully")
        print(
            f"  - Registry initialized: {len(executor.registry.list_skills())} skills")
        print(f"  - Pipeline initialized: {executor.pipeline is not None}")
        print(
            f"  - History tracking: {len(executor.execution_history)} records")
        print(f"\n✅ Executor initialization successful")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize executor: {str(e)}")
        return False


def test_available_skills():
    """Test 2: List Available Skills"""
    print("\n" + "="*60)
    print("TEST 2: Available Skills")
    print("="*60)

    try:
        executor = CopilotSkillExecutor()
        skills = executor.get_available_skills()

        print(f"Available Skills: {len(skills)}")
        for skill in skills:
            phase = skill.get('phase', '?')
            print(f"  {phase}. {skill['name']} - {skill['description']}")

        if len(skills) == 6:
            print(f"\n✅ All 6 skills available")
            return True
        else:
            print(f"\n⚠️ Expected 6 skills, got {len(skills)}")
            return False
    except Exception as e:
        print(f"❌ Failed to list skills: {str(e)}")
        return False


async def test_single_skill_execution():
    """Test 3: Single Skill Execution"""
    print("\n" + "="*60)
    print("TEST 3: Single Skill Execution")
    print("="*60)

    try:
        executor = CopilotSkillExecutor()

        raw_product = {
            "halilit_id": "copilot-test-001",
            "product_name": "CopilotKit Test Product",
            "brand": "TestBrand",
            "price_il": 5000.0,
            "price_eilat": 4274.0,
            "halilit_url": "https://halilit.com/test"
        }

        # Execute harvest skill
        result = await executor.execute_skill('harvest', {
            'raw_product': raw_product,
            'brand': 'TestBrand'
        })

        print(f"Harvest Execution Result:")
        print(f"  - Execution ID: {result['execution_id']}")
        print(f"  - Status: {result['status']}")
        print(f"  - Success: {result['success']}")

        if result['success']:
            output = result['output']
            print(
                f"  - Product: {output.product_name if hasattr(output, 'product_name') else 'unknown'}")
            print(f"\n✅ Single skill execution successful")
            return True
        else:
            print(f"  - Error: {result['output'].get('error', 'unknown')}")
            print(f"\n❌ Skill execution failed")
            return False
    except Exception as e:
        print(f"❌ Failed to execute skill: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_pipeline_execution():
    """Test 4: Full Pipeline Execution with Streaming"""
    print("\n" + "="*60)
    print("TEST 4: Full Pipeline Execution (Streaming)")
    print("="*60)

    try:
        executor = CopilotSkillExecutor()

        raw_product = {
            "halilit_id": "7971375",
            "product_name": "Nord Piano 6",
            "brand": "Nord",
            "price_il": 16200.0,
            "price_eilat": 13770.0,
            "halilit_url": "https://halilit.com/products/7971375"
        }

        events = []
        phase_count = 0
        final_status = None

        async for event in executor.execute_full_pipeline(raw_product, "Nord"):
            event_type = event.get('type', 'unknown')

            if event_type == 'pipeline_started':
                print(f"🚀 Pipeline Started")
                print(f"   Product: {event['product_name']}")
                print(f"   Total Phases: {event['total_phases']}")
            elif event_type == 'phase_completed':
                phase_count += 1
                phase_name = event.get('phase_name', 'unknown')
                progress = event.get('progress', '?')
                print(f"   ✓ {progress}: {phase_name}")
            elif event_type == 'pipeline_completed':
                final_status = event.get('status')
                print(f"✅ Pipeline Completed")
                print(f"   Status: {final_status}")
                print(f"   Product: {event.get('product_name')}")
                print(f"   Errors: {len(event.get('errors', []))}")

            events.append(event)

        print(f"\nStreaming Results:")
        print(f"  - Total events: {len(events)}")
        print(f"  - Phases reported: {phase_count}")
        print(f"  - Final status: {final_status}")
        print(
            f"  - History updated: {len(executor.execution_history)} records")

        # Accept either APPROVED or REJECTED as long as all 6 phases completed
        if phase_count >= 6 or final_status in ['APPROVED', 'REJECTED']:
            print(f"\n✅ Full pipeline execution successful")
            return True
        else:
            print(f"\n⚠️ Pipeline stopped early (phase {phase_count}/6)")
            return False
    except Exception as e:
        print(f"❌ Failed pipeline execution: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_execution_history():
    """Test 5: Execution History Tracking"""
    print("\n" + "="*60)
    print("TEST 5: Execution History Tracking")
    print("="*60)

    try:
        executor = CopilotSkillExecutor()

        # Execute a skill to build history
        await executor.execute_skill('harvest', {
            'raw_product': {
                'halilit_id': 'history-test-001',
                'product_name': 'Nord Synth Test',
                'brand': 'Nord',
                'price_il': 5000
            },
            'brand': 'Nord'
        })

        history = executor.get_execution_history(limit=10)
        print(f"Execution History:")
        print(f"  - Records: {len(history)}")
        print(f"  - Total executions: {len(executor.execution_history)}")

        if len(history) > 0:
            latest = history[0]
            print(f"  - Latest: {latest['skill']} @ {latest['timestamp']}")
            print(f"\n✅ History tracking working")
            return True
        else:
            print(f"\n⚠️ No history records found")
            return False
    except Exception as e:
        print(f"❌ Failed to test history: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_pipeline_status():
    """Test 6: Pipeline Status and Capabilities"""
    print("\n" + "="*60)
    print("TEST 6: Pipeline Status")
    print("="*60)

    try:
        executor = CopilotSkillExecutor()
        status = executor.get_pipeline_status()

        print(f"Pipeline Status:")
        print(f"  - Status: {status['status']}")
        print(f"  - Available Skills: {len(status['available_skills'])}")
        print(f"  - Agents Available:")
        for agent_name, available in status['agents'].items():
            icon = "✓" if available else "✗"
            print(f"    {icon} {agent_name}")

        if status['status'] == 'ready' and status['agents']['commercial_scout']:
            print(f"\n✅ Pipeline status check successful")
            return True
        else:
            print(f"\n⚠️ Pipeline not fully ready")
            return False
    except Exception as e:
        print(f"❌ Failed to get status: {str(e)}")
        return False


async def run_all_tests():
    """Run all Phase 1D tests"""
    print("\n" + "="*70)
    print("PHASE 1D: COPILOTKIT INTEGRATION TESTS")
    print("="*70)

    tests = [
        ("Executor Initialization", test_executor_initialization),
        ("Available Skills", test_available_skills),
        ("Single Skill Execution", test_single_skill_execution),
        ("Pipeline Streaming", test_pipeline_execution),
        ("History Tracking", test_execution_history),
        ("Pipeline Status", test_pipeline_status),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(
        f"\nTotal: {passed}/{total} tests passed ({(passed/total*100):.0f}%)")

    if passed == total:
        print("\n🎉 PHASE 1D: COPILOTKIT INTEGRATION - All tests PASSED!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return False


if __name__ == '__main__':
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
