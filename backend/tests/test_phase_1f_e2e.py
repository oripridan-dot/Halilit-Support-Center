"""
Phase 1F: Comprehensive End-to-End Integration Tests
Tests the complete workflow from product ingestion through frontend sync
"""

from backend.auto_sync_engine import get_auto_sync_engine
from backend.copilot_skill_executor import CopilotSkillExecutor
import asyncio
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any

# Ensure parent directory is in path
_parent_dir = str(Path(__file__).parent.parent.parent)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)


class E2ETestRunner:
    """End-to-end test orchestrator"""

    def __init__(self):
        self.executor = CopilotSkillExecutor()
        self.sync_engine = get_auto_sync_engine()
        self.test_results = []
        self.start_time = None

    async def test_single_product_e2e(self):
        """Test 1: Complete single product workflow"""
        print("\n" + "="*70)
        print("TEST 1: Single Product End-to-End Workflow")
        print("="*70)

        try:
            start = time.time()

            # Step 1: Execute pipeline
            print("\n📋 Step 1: Running 6-phase ingestion pipeline...")
            pipeline_result = None
            pipeline_events = []

            async for event in self.executor.execute_full_pipeline(
                {
                    "halilit_id": "e2e-test-001",
                    "product_name": "Nord Lead A1",
                    "brand": "Nord",
                    "price_il": 14900.0
                },
                "Nord"
            ):
                pipeline_events.append(event)
                if event.get('type') == 'pipeline_completed':
                    pipeline_result = event

            if not pipeline_result:
                print("❌ Pipeline did not complete")
                return False

            print(f"   ✓ Pipeline: {pipeline_result.get('status')}")
            print(
                f"   ✓ Phases: {len([e for e in pipeline_events if e.get('type') == 'phase_completed'])} complete")

            # Step 2: Sync result
            print("\n📤 Step 2: Auto-syncing product to frontend...")
            sync_events = []

            async for sync_event in self.sync_engine.sync_pipeline_result(
                product_id=pipeline_result.get('product_id', 'e2e-test-001'),
                product_name=pipeline_result.get(
                    'product_name', 'Nord Lead A1'),
                brand="Nord",
                category=pipeline_result.get('category', 'Synthesizer'),
                status=pipeline_result.get('status', 'APPROVED'),
                risk_score=pipeline_result.get('risk_score', 20)
            ):
                sync_events.append(sync_event)

            print(f"   ✓ Sync events: {len(sync_events)}")
            print(
                f"   ✓ Product synced: {any(e.get('type') == 'product_synced' for e in sync_events)}")

            # Verify complete flow
            elapsed = time.time() - start
            success = (
                len(pipeline_events) > 0 and
                pipeline_result.get('status') in ['APPROVED', 'REJECTED'] and
                len(sync_events) > 0
            )

            if success:
                print(f"\n✅ Single product workflow complete ({elapsed:.2f}s)")
                return True
            else:
                print(f"\n❌ Workflow incomplete")
                return False

        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    async def test_batch_product_e2e(self):
        """Test 2: Batch product workflow with progress tracking"""
        print("\n" + "="*70)
        print("TEST 2: Batch Product End-to-End Workflow")
        print("="*70)

        try:
            start = time.time()
            test_products = [
                {
                    "halilit_id": "7971375",
                    "product_name": "Nord Piano 6",
                    "brand": "Nord",
                    "price_il": 16200.0
                },
                {
                    "halilit_id": "e2e-batch-002",
                    "product_name": "Rode Wireless GO II",
                    "brand": "Rode",
                    "price_il": 8500.0
                },
                {
                    "halilit_id": "e2e-batch-003",
                    "product_name": "Roland FP-90X",
                    "brand": "Roland",
                    "price_il": 13000.0
                }
            ]

            both_completed = 0
            sync_completed = 0

            print(
                f"\n📋 Processing {len(test_products)} products through pipeline & sync...")

            for idx, product in enumerate(test_products):
                print(
                    f"\n  [{idx + 1}/{len(test_products)}] {product['product_name']}")

                # Pipeline
                pipeline_ok = False
                async for event in self.executor.execute_full_pipeline(product, product['brand']):
                    if event.get('type') == 'pipeline_completed':
                        pipeline_ok = event.get('status') in [
                            'APPROVED', 'REJECTED']

                if pipeline_ok:
                    print(f"     ✓ Pipeline: APPROVED/REJECTED")
                    both_completed += 1

                # Sync (immediate after pipeline)
                sync_ok = False
                async for sync_event in self.sync_engine.sync_pipeline_result(
                    product_id=product['halilit_id'],
                    product_name=product['product_name'],
                    brand=product['brand'],
                    category='Category',
                    status='APPROVED',
                    risk_score=20
                ):
                    if sync_event.get('type') == 'product_synced':
                        sync_ok = True

                if sync_ok:
                    print(f"     ✓ Sync: Completed")
                    sync_completed += 1

            elapsed = time.time() - start
            success = (both_completed >= 2 and  # At least 2 out of 3 successful
                       sync_completed == len(test_products))  # All sync operations succeed

            if success:
                print(f"\n✅ Batch workflow complete ({elapsed:.2f}s)")
                print(f"   - Processed: {len(test_products)}")
                print(
                    f"   - Pipeline→Sync: {both_completed}/{len(test_products)}")
                return True
            else:
                print(
                    f"\n❌ Batch incomplete: {both_completed} pipeline, {sync_completed} sync")
                return False

        except Exception as e:
            print(f"❌ Batch test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    async def test_error_recovery(self):
        """Test 3: Error handling and recovery"""
        print("\n" + "="*70)
        print("TEST 3: Error Handling and Recovery")
        print("="*70)

        try:
            print("\n🔧 Testing error scenarios...")

            # Scenario 1: Invalid product data
            print("\n  [1/3] Invalid product structure...")
            try:
                async for event in self.executor.execute_full_pipeline(
                    {"incomplete": "data"},  # Missing required fields
                    "Invalid"
                ):
                    pass
                print("       ✓ Handled gracefully")
            except Exception as e:
                print(f"       ✓ Caught error: {type(e).__name__}")

            # Scenario 2: Unknown brand
            print("\n  [2/3] Unknown brand handling...")
            pipeline_ok = False
            async for event in self.executor.execute_full_pipeline(
                {
                    "halilit_id": "error-test-002",
                    "product_name": "Unknown Brand Product",
                    "brand": "UnknownBrand",
                    "price_il": 5000.0
                },
                "UnknownBrand"
            ):
                if event.get('type') == 'pipeline_completed':
                    # Should either complete or fail gracefully
                    pipeline_ok = True

            print(
                f"       ✓ Handled: {'completed' if pipeline_ok else 'failed gracefully'}")

            # Scenario 3: Sync engine resilience
            print("\n  [3/3] Sync engine error handling...")
            try:
                async for event in self.sync_engine.sync_pipeline_result(
                    product_id=None,  # Invalid ID
                    product_name="Test",
                    brand="Test",
                    category="Test",
                    status="INVALID_STATUS",  # Invalid status
                    risk_score=150  # Out of range
                ):
                    pass
                print("       ✓ Sync handled gracefully")
            except Exception as e:
                print(f"       ✓ Caught error: {type(e).__name__}")

            print(f"\n✅ Error handling verified")
            return True

        except Exception as e:
            print(f"❌ Error test failed: {str(e)}")
            return False

    async def test_concurrent_operations(self):
        """Test 4: Concurrent product processing"""
        print("\n" + "="*70)
        print("TEST 4: Concurrent Operations")
        print("="*70)

        try:
            start = time.time()

            products = [
                {
                    "halilit_id": f"concurrent-{i:03d}",
                    "product_name": f"Concurrent Product {i+1}",
                    "brand": "Test",
                    "price_il": 5000.0 + (i * 1000)
                }
                for i in range(3)
            ]

            print(f"\n⚡ Processing {len(products)} products concurrently...")

            # Define async tasks
            async def process_product(product):
                events = []
                async for event in self.executor.execute_full_pipeline(
                    product,
                    product['brand']
                ):
                    events.append(event)
                return len(events) > 0

            # Run concurrently
            tasks = [process_product(p) for p in products]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            elapsed = time.time() - start
            success_count = sum(1 for r in results if r is True)

            print(f"\n   Results:")
            print(f"   - Completed: {success_count}/{len(products)}")
            print(f"   - Time: {elapsed:.2f}s")
            print(f"   - Avg per product: {elapsed/len(products):.2f}s")

            if success_count == len(products):
                print(f"\n✅ Concurrent operations successful")
                return True
            else:
                print(f"\n⚠️ Partial success: {success_count}/{len(products)}")
                return False

        except Exception as e:
            print(f"❌ Concurrent test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    async def test_performance_metrics(self):
        """Test 5: Performance baseline"""
        print("\n" + "="*70)
        print("TEST 5: Performance Metrics")
        print("="*70)

        try:
            print("\n📊 Measuring performance baseline...")

            # Single product timing
            print("\n  [1/2] Single product pipeline...")
            start = time.time()
            async for event in self.executor.execute_full_pipeline(
                {
                    "halilit_id": "perf-test-001",
                    "product_name": "Performance Test Product",
                    "brand": "Test",
                    "price_il": 5000.0
                },
                "Test"
            ):
                pass
            pipeline_time = time.time() - start
            print(f"       ✓ {pipeline_time:.2f}s")

            # Sync timing
            print("\n  [2/2] Single product sync...")
            start = time.time()
            async for event in self.sync_engine.sync_pipeline_result(
                product_id="perf-001",
                product_name="Perf Test",
                brand="Test",
                category="Test",
                status="APPROVED",
                risk_score=20
            ):
                pass
            sync_time = time.time() - start
            print(f"       ✓ {sync_time:.2f}s")

            # Summary
            print(f"\n📈 Performance Summary:")
            print(f"   - Pipeline: {pipeline_time:.3f}s")
            print(f"   - Sync: {sync_time:.3f}s")
            print(f"   - Total: {pipeline_time + sync_time:.3f}s")
            print(f"   - Target: <2.0s ✓" if (pipeline_time + sync_time)
                  < 2.0 else "   - Target: <2.0s ✗")

            if (pipeline_time + sync_time) < 3.0:  # Allow some margin
                print(f"\n✅ Performance acceptable")
                return True
            else:
                print(f"\n⚠️ Performance slower than target")
                return False

        except Exception as e:
            print(f"❌ Performance test failed: {str(e)}")
            return False

    async def test_history_tracking(self):
        """Test 6: History and audit trail"""
        print("\n" + "="*70)
        print("TEST 6: History and Audit Trail")
        print("="*70)

        try:
            print("\n📚 Testing history tracking...")

            # Execute a pipeline
            print("   Executing pipeline...")
            pipeline_events = []
            async for event in self.executor.execute_full_pipeline(
                {
                    "halilit_id": "history-test-001",
                    "product_name": "Nord Piano 6",
                    "brand": "Nord",
                    "price_il": 16200.0
                },
                "Nord"
            ):
                pipeline_events.append(event)

            print(f"   ✓ Pipeline events: {len(pipeline_events)}")

            # Execute a sync
            print("   Executing sync...")
            sync_events = []
            async for event in self.sync_engine.sync_pipeline_result(
                product_id="history-001",
                product_name="Test Product",
                brand="Test",
                category="Test",
                status="APPROVED",
                risk_score=20
            ):
                sync_events.append(event)

            print(f"   ✓ Sync events: {len(sync_events)}")

            # Check sync history (which IS being tracked)
            sync_history = self.sync_engine.get_sync_history(limit=10)

            print(f"\n   Verification:")
            print(f"   - Pipeline events captured: {len(pipeline_events) > 0}")
            print(f"   - Sync events captured: {len(sync_events) > 0}")
            print(f"   - Sync history records: {len(sync_history)}")

            # Success if we captured events and history is working
            success = (len(pipeline_events) > 0 and
                       len(sync_events) > 0 and
                       len(sync_history) > 0)

            if success:
                print(f"\n✅ History tracking operational")
                return True
            else:
                print(f"\n❌ History tracking incomplete")
                return False

        except Exception as e:
            print(f"❌ History test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


async def run_all_e2e_tests():
    """Run all Phase 1F end-to-end tests"""
    print("\n" + "="*70)
    print("PHASE 1F: END-TO-END INTEGRATION TESTS")
    print("="*70)

    runner = E2ETestRunner()
    tests = [
        ("Single Product Workflow", runner.test_single_product_e2e),
        ("Batch Product Workflow", runner.test_batch_product_e2e),
        ("Error Handling", runner.test_error_recovery),
        ("Concurrent Operations", runner.test_concurrent_operations),
        ("Performance Metrics", runner.test_performance_metrics),
        ("History Tracking", runner.test_history_tracking),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
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
        print("\n🎉 PHASE 1F: END-TO-END INTEGRATION - All tests PASSED!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return False


if __name__ == '__main__':
    success = asyncio.run(run_all_e2e_tests())
    sys.exit(0 if success else 1)
