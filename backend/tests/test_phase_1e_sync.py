"""
Phase 1E: Auto-Sync Pipeline - Test Suite
Tests for real-time product synchronization to frontend data stores
"""

from backend.copilot_skill_executor import CopilotSkillExecutor
from backend.auto_sync_engine import AutoSyncEngine, get_auto_sync_engine, SyncBatch
import asyncio
import sys
import json
from pathlib import Path

# Ensure parent directory is in path
_parent_dir = str(Path(__file__).parent.parent.parent)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)


async def test_sync_engine_initialization():
    """Test 1: Auto-Sync Engine Initialization"""
    print("\n" + "="*60)
    print("TEST 1: Auto-Sync Engine Initialization")
    print("="*60)

    try:
        engine = AutoSyncEngine()

        print(f"✓ Engine created successfully")
        print(f"  - Sync enabled: {engine.sync_enabled}")
        print(f"  - History records: {len(engine.sync_history)}")
        print(f"  - Active batches: {len(engine.active_batches)}")

        print(f"\n✅ Auto-Sync engine initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize engine: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_single_product_sync():
    """Test 2: Single Product Sync Stream"""
    print("\n" + "="*60)
    print("TEST 2: Single Product Sync Stream")
    print("="*60)

    try:
        engine = AutoSyncEngine()

        events = []
        product_synced = False

        async for event in engine.sync_pipeline_result(
            product_id="test-001",
            product_name="Nord Piano 6",
            brand="Nord",
            category="Digital Piano",
            status="APPROVED",
            risk_score=15
        ):
            event_type = event.get('type')
            events.append(event)

            if event_type == 'sync_started':
                print(f"🚀 Sync started")
            elif event_type == 'sync_phase':
                print(f"  ⚙️  {event['phase']}: {event['message']}")
            elif event_type == 'product_synced':
                product_synced = True
                print(f"  ✓ Product synced: {event['product_name']}")
            elif event_type == 'sync_completed':
                print(f"✅ Sync completed")

        print(f"\nSync Results:")
        print(f"  - Total events: {len(events)}")
        print(f"  - Product synced: {product_synced}")
        print(f"  - History updated: {len(engine.sync_history)}")

        if len(events) >= 7 and product_synced:  # At least 7 events expected
            print(f"\n✅ Single product sync successful")
            return True
        else:
            print(f"\n⚠️ Expected at least 7 events, got {len(events)}")
            return False
    except Exception as e:
        print(f"❌ Failed single product sync: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_batch_sync_stream():
    """Test 3: Batch Sync with Progress Tracking"""
    print("\n" + "="*60)
    print("TEST 3: Batch Sync with Progress Tracking")
    print("="*60)

    try:
        engine = AutoSyncEngine()

        # Test batch with 3 products
        products = [
            {
                "product_id": "batch-001",
                "product_name": "Nord Piano 6",
                "brand": "Nord",
                "category": "Digital Piano",
                "status": "APPROVED",
                "risk_score": 15
            },
            {
                "product_id": "batch-002",
                "product_name": "Roland TR-808",
                "brand": "Roland",
                "category": "Drum Machine",
                "status": "APPROVED",
                "risk_score": 20
            },
            {
                "product_id": "batch-003",
                "product_name": "Shure SM7B",
                "brand": "Shure",
                "category": "Microphone",
                "status": "APPROVED",
                "risk_score": 10
            }
        ]

        events = []
        batch_completed = False
        progress_updates = 0

        async for event in engine.sync_batch(products, "Multi-Brand"):
            event_type = event.get('type')
            events.append(event)

            if event_type == 'batch_sync_started':
                batch_id = event['batch_id']
                print(
                    f"📦 Batch started: {batch_id} ({event['total_products']} products)")
            elif event_type == 'batch_progress':
                progress_updates += 1
                progress = event['percent_complete']
                product_name = event['product_name']
                print(
                    f"  ✓ {event['progress']}: {product_name} ({progress:.0f}%)")
            elif event_type == 'batch_sync_completed':
                batch_completed = True
                summary = event['summary']
                print(f"✅ Batch completed")
                print(f"  - Approved: {summary['approved']}")
                print(f"  - Rejected: {summary['rejected']}")
                print(f"  - Pending: {summary['pending']}")

        print(f"\nBatch Results:")
        print(f"  - Total events: {len(events)}")
        print(f"  - Progress updates: {progress_updates}")
        print(f"  - Batch completed: {batch_completed}")

        if batch_completed and progress_updates >= 3:
            print(f"\n✅ Batch sync successful")
            return True
        else:
            print(f"\n⚠️ Batch sync incomplete")
            return False
    except Exception as e:
        print(f"❌ Failed batch sync: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_sync_history():
    """Test 4: Sync History Management"""
    print("\n" + "="*60)
    print("TEST 4: Sync History Management")
    print("="*60)

    try:
        engine = AutoSyncEngine()

        # Generate some sync history
        async for _ in engine.sync_pipeline_result(
            product_id="history-001",
            product_name="Test Product",
            brand="Test",
            category="Test Category",
            status="APPROVED",
            risk_score=50
        ):
            pass

        async for _ in engine.sync_batch(
            [
                {"product_id": "h2", "product_name": "P2", "category": "C2",
                    "status": "APPROVED", "risk_score": 25},
                {"product_id": "h3", "product_name": "P3", "category": "C3",
                    "status": "REJECTED", "risk_score": 75}
            ],
            "Test"
        ):
            pass

        history = engine.get_sync_history(limit=10)

        print(f"History Results:")
        print(f"  - Total records: {len(engine.sync_history)}")
        print(f"  - Retrieved (limit 10): {len(history)}")

        if len(history) > 0:
            latest = history[0]
            print(f"  - Latest: {latest['product_name']}")

        # Test clearing history
        engine.clear_history()
        print(f"  - After clear: {len(engine.sync_history)} records")

        if len(history) > 0 and len(engine.sync_history) == 0:
            print(f"\n✅ Sync history tracking successful")
            return True
        else:
            print(f"\n⚠️ History tracking incomplete")
            return False
    except Exception as e:
        print(f"❌ Failed history test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_batch_status_tracking():
    """Test 5: Batch Status and Metadata"""
    print("\n" + "="*60)
    print("TEST 5: Batch Status and Metadata")
    print("="*60)

    try:
        engine = AutoSyncEngine()

        # Run a batch to generate status
        batch_id = None
        async for event in engine.sync_batch(
            [
                {"product_id": "s1", "product_name": "Synth 1",
                    "category": "Synth", "status": "APPROVED", "risk_score": 30},
                {"product_id": "s2", "product_name": "Synth 2",
                    "category": "Synth", "status": "APPROVED", "risk_score": 40}
            ],
            "Test"
        ):
            if event.get('type') == 'batch_sync_started':
                batch_id = event['batch_id']

        # Get batch status
        if batch_id:
            status = engine.get_batch_status(batch_id)

            if status:
                print(f"Batch Status:")
                print(f"  - Batch ID: {status['batch_id']}")
                print(f"  - Total: {status['total_products']}")
                print(f"  - Completed: {status['completed']}")
                print(f"  - Approved: {status['approved']}")
                print(f"  - Progress: {status['progress_percent']:.1f}%")

                if status['completed'] == status['total_products'] and status['progress_percent'] == 100:
                    print(f"\n✅ Batch status tracking successful")
                    return True

        print(f"\n⚠️ Batch status incomplete or not found")
        return False
    except Exception as e:
        print(f"❌ Failed batch status test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_sync_with_pipeline():
    """Test 6: Integration with CopilotKit Pipeline"""
    print("\n" + "="*60)
    print("TEST 6: Sync After Pipeline (Integration)")
    print("="*60)

    try:
        executor = CopilotSkillExecutor()
        sync_engine = AutoSyncEngine()

        # Execute pipeline
        pipeline_result = None
        async for event in executor.execute_full_pipeline(
            {
                "halilit_id": "integration-test-001",
                "product_name": "Nord Piano 6",
                "brand": "Nord",
                "price_il": 16200.0
            },
            "Nord"
        ):
            if event.get('type') == 'pipeline_completed':
                pipeline_result = event

        if not pipeline_result:
            print(f"⚠️ Pipeline did not complete")
            return False

        # Immediately sync the result
        sync_events = []
        async for sync_event in sync_engine.sync_pipeline_result(
            product_id=pipeline_result.get('product_id', 'test-001'),
            product_name=pipeline_result.get('product_name', 'Unknown'),
            brand="Nord",
            category=pipeline_result.get('category', 'Uncategorized'),
            status=pipeline_result.get('status', 'APPROVED'),
            risk_score=pipeline_result.get('risk_score', 50)
        ):
            sync_events.append(sync_event)

        print(f"Integration Results:")
        print(f"  - Pipeline status: {pipeline_result.get('status')}")
        print(f"  - Sync events generated: {len(sync_events)}")
        print(f"  - Pipeline → Sync flow: ✅")

        if len(sync_events) > 0 and pipeline_result.get('status') in ['APPROVED', 'REJECTED']:
            print(f"\n✅ Pipeline-to-sync integration successful")
            return True
        else:
            print(f"\n⚠️ Integration incomplete")
            return False
    except Exception as e:
        print(f"❌ Failed integration test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all Phase 1E tests"""
    print("\n" + "="*70)
    print("PHASE 1E: AUTO-SYNC PIPELINE - TEST SUITE")
    print("="*70)

    tests = [
        ("Sync Engine Initialization", test_sync_engine_initialization),
        ("Single Product Sync", test_single_product_sync),
        ("Batch Sync with Progress", test_batch_sync_stream),
        ("Sync History Management", test_sync_history),
        ("Batch Status Tracking", test_batch_status_tracking),
        ("Pipeline-to-Sync Integration", test_sync_with_pipeline),
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
        print("\n🎉 PHASE 1E: AUTO-SYNC PIPELINE - All tests PASSED!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return False


if __name__ == '__main__':
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
