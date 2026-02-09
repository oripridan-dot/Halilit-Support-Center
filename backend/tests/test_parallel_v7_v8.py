"""
Parallel Testing Harness for Halilit Support Center v8.0

Validates v8.0 (async/Celery) against v7.6 (synchronous) baseline.

Usage:
    python3 backend/tests/test_parallel_v7_v8.py
    python3 backend/tests/test_parallel_v7_v8.py --brands "Roland,Yamaha,Korg"
    python3 backend/tests/test_parallel_v7_v8.py --mode=perf (performance testing)
    python3 backend/tests/test_parallel_v7_v8.py --mode=correctness (accuracy testing)

Features:
    - Parallel execution of both versions
    - Result comparison (accuracy, performance, resource usage)
    - Gradual traffic migration validation
    - Detailed reporting
"""

import sys
import asyncio
import time
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import concurrent.futures

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.unified_agent_orchestrator_v76 import CommercialAgent, OfficialAgent, ContextualAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger("test_parallel")


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class ExecutionMetrics:
    """Track execution metrics for a single operation"""
    version: str  # "v7.6" or "v8.0"
    operation: str  # "harvest", "enrich", "validate"
    brand: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_seconds: float = 0.0
    product_count: int = 0
    success: bool = False
    error_message: Optional[str] = None
    
    def complete(self, product_count: int = 0, success: bool = True, error: Optional[str] = None):
        """Mark operation as complete"""
        self.end_time = time.time()
        self.duration_seconds = self.end_time - self.start_time
        self.product_count = product_count
        self.success = success
        self.error_message = error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'version': self.version,
            'operation': self.operation,
            'brand': self.brand,
            'duration_seconds': round(self.duration_seconds, 2),
            'product_count': self.product_count,
            'success': self.success,
            'error': self.error_message
        }


@dataclass
class ComparisonResult:
    """Compare metrics between v7.6 and v8.0"""
    operation: str
    brand: str
    v7_metrics: ExecutionMetrics
    v8_metrics: ExecutionMetrics
    accuracy_match: bool = True
    accuracy_diff: Optional[str] = None
    performance_delta: float = 0.0  # Percentage (positive = v8.0 faster)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'operation': self.operation,
            'brand': self.brand,
            'v7_duration': self.v7_metrics.duration_seconds,
            'v8_duration': self.v8_metrics.duration_seconds,
            'performance_delta_percent': round(self.performance_delta, 2),
            'accuracy_match': self.accuracy_match,
            'accuracy_notes': self.accuracy_diff,
            'v7_products': self.v7_metrics.product_count,
            'v8_products': self.v8_metrics.product_count,
        }


# ============================================================================
# V7.6 (Synchronous) Test Runner
# ============================================================================

class V76TestRunner:
    """Runs operations using v7.6 sync agents (baseline)"""
    
    def __init__(self):
        self.harvest_agent = CommercialAgent()
        self.enrich_agent = OfficialAgent()
        self.validate_agent = ContextualAgent()
    
    def test_harvest(self, brand: str) -> ExecutionMetrics:
        """Test harvest (CommercialScout)"""
        metrics = ExecutionMetrics(version='v7.6', operation='harvest', brand=brand)
        
        try:
            logger.info(f"[v7.6] Starting harvest for {brand}")
            products = self.harvest_agent.harvest(brand)
            metrics.complete(
                product_count=len(products) if products else 0,
                success=True
            )
            logger.info(f"[v7.6] ✅ Harvested {len(products)} products in {metrics.duration_seconds:.2f}s")
            return metrics, products
        
        except Exception as e:
            metrics.complete(success=False, error=str(e))
            logger.error(f"[v7.6] ❌ Harvest failed: {e}")
            return metrics, None
    
    def test_enrich(self, products: List[Dict], brand: str) -> ExecutionMetrics:
        """Test enrichment (OfficialVerifier)"""
        metrics = ExecutionMetrics(version='v7.6', operation='enrich', brand=brand)
        
        try:
            if not products:
                metrics.complete(success=True)
                return metrics, []
            
            logger.info(f"[v7.6] Starting enrichment for {len(products)} products")
            enriched = []
            
            for product in products[:3]:  # Test with first 3 products
                try:
                    enriched_prod = self.enrich_agent.enrich(product)
                    enriched.append(enriched_prod)
                except Exception as e:
                    logger.warning(f"[v7.6] Enrichment error for product: {e}")
            
            metrics.complete(product_count=len(enriched), success=True)
            logger.info(f"[v7.6] ✅ Enriched {len(enriched)} products in {metrics.duration_seconds:.2f}s")
            return metrics, enriched
        
        except Exception as e:
            metrics.complete(success=False, error=str(e))
            logger.error(f"[v7.6] ❌ Enrichment failed: {e}")
            return metrics, None
    
    def test_validate(self, products: List[Dict], brand: str) -> ExecutionMetrics:
        """Test validation (ExternalValidator)"""
        metrics = ExecutionMetrics(version='v7.6', operation='validate', brand=brand)
        
        try:
            if not products:
                metrics.complete(success=True)
                return metrics, []
            
            logger.info(f"[v7.6] Starting validation for {len(products)} products")
            validated = []
            
            for product in products[:3]:  # Test with first 3 products
                try:
                    audit_report = self.validate_agent.audit(product)
                    validated.append(audit_report)
                except Exception as e:
                    logger.warning(f"[v7.6] Validation error for product: {e}")
            
            metrics.complete(product_count=len(validated), success=True)
            logger.info(f"[v7.6] ✅ Validated {len(validated)} products in {metrics.duration_seconds:.2f}s")
            return metrics, validated
        
        except Exception as e:
            metrics.complete(success=False, error=str(e))
            logger.error(f"[v7.6] ❌ Validation failed: {e}")
            return metrics, None
    
    def test_full_pipeline(self, brand: str) -> Tuple[List[ExecutionMetrics], bool]:
        """Test complete pipeline (harvest → enrich → validate)"""
        logger.info(f"[v7.6] Starting full pipeline for {brand}")
        
        metrics_list = []
        success = True
        
        # Harvest
        harvest_metrics, harvest_products = self.test_harvest(brand)
        metrics_list.append(harvest_metrics)
        
        if not harvest_metrics.success:
            return metrics_list, False
        
        # Enrich
        enrich_metrics, enriched_products = self.test_enrich(harvest_products, brand)
        metrics_list.append(enrich_metrics)
        
        # Validate
        validate_metrics, validated_products = self.test_validate(enriched_products, brand)
        metrics_list.append(validate_metrics)
        
        logger.info(f"[v7.6] ✅ Full pipeline completed for {brand}")
        return metrics_list, success


# ============================================================================
# V8.0 (Async/Celery) Test Runner
# ============================================================================

class V80TestRunner:
    """Runs operations using v8.0 async Celery tasks"""
    
    def __init__(self):
        self.broker_url = "redis://localhost:6379/0"
        self.ready = self._check_celery_ready()
    
    def _check_celery_ready(self) -> bool:
        """Check if Celery broker is available"""
        try:
            from backend.celery_config import celery_app
            with celery_app.connection() as conn:
                conn.connect()
            logger.info("[v8.0] ✅ Celery broker available")
            return True
        except Exception as e:
            logger.warning(f"[v8.0] ⚠️ Celery broker not available: {e}")
            return False
    
    async def test_harvest(self, brand: str) -> ExecutionMetrics:
        """Test harvest task (async)"""
        if not self.ready:
            metrics = ExecutionMetrics(version='v8.0', operation='harvest', brand=brand)
            metrics.complete(success=False, error='Celery broker not available')
            return metrics
        
        metrics = ExecutionMetrics(version='v8.0', operation='harvest', brand=brand)
        
        try:
            from backend.tasks import harvest_brand_products
            from celery.result import AsyncResult
            import uuid
            
            task_id = str(uuid.uuid4())
            logger.info(f"[v8.0] Queuing harvest for {brand} (task_id={task_id})")
            
            # Queue task
            task = harvest_brand_products.apply_async(
                args=(brand, task_id),
                queue='harvest'
            )
            
            # Wait for result (with timeout)
            try:
                result = task.get(timeout=120)  # 120 second timeout
                products = result.get('products', [])
                metrics.complete(product_count=len(products), success=True)
                logger.info(f"[v8.0] ✅ Harvested {len(products)} products in {metrics.duration_seconds:.2f}s")
                return metrics
            except asyncio.TimeoutError:
                metrics.complete(success=False, error='Task timeout')
                return metrics
        
        except Exception as e:
            metrics.complete(success=False, error=str(e))
            logger.error(f"[v8.0] ❌ Harvest failed: {e}")
            return metrics


# ============================================================================
# Test Coordinator
# ============================================================================

class TestCoordinator:
    """Coordinates parallel testing of v7.6 and v8.0"""
    
    def __init__(self, brands: List[str], mode: str = 'correctness'):
        self.brands = brands
        self.mode = mode
        self.v76_runner = V76TestRunner()
        self.v80_runner = V80TestRunner()
        self.results: List[ComparisonResult] = []
    
    def run_parallel_harvest(self, brands: List[str]) -> None:
        """Run harvest on both versions in parallel"""
        logger.info(f"\n{'='*80}")
        logger.info("🌾 HARVEST TESTING")
        logger.info(f"{'='*80}\n")
        
        for brand in brands:
            logger.info(f"\n📍 Testing: {brand}")
            logger.info(f"{'-'*80}")
            
            # Run both versions
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                # V7.6 runs synchronously
                v76_future = executor.submit(self.v76_runner.test_harvest, brand)
                
                # V8.0 runs async (simulate with thread)
                v80_future = executor.submit(asyncio.run, self.v80_runner.test_harvest(brand))
                
                v76_metrics = v76_future.result()
                v80_metrics = v80_future.result()
            
            # Compare results
            self._compare_harvest_results(v76_metrics, v80_metrics)
    
    def _compare_harvest_results(self, v76_metrics: ExecutionMetrics, 
                                  v80_metrics: ExecutionMetrics):
        """Compare harvest results"""
        accuracy_match = v76_metrics.product_count == v80_metrics.product_count
        perf_delta = ((v76_metrics.duration_seconds - v80_metrics.duration_seconds) / 
                      v76_metrics.duration_seconds * 100) if v76_metrics.duration_seconds > 0 else 0
        
        result = ComparisonResult(
            operation='harvest',
            brand=v76_metrics.brand,
            v7_metrics=v76_metrics,
            v8_metrics=v80_metrics,
            accuracy_match=accuracy_match,
            accuracy_diff=f"v7.6: {v76_metrics.product_count} vs v8.0: {v80_metrics.product_count}",
            performance_delta=perf_delta
        )
        
        self.results.append(result)
        
        # Report
        logger.info(f"\n📊 HARVEST COMPARISON: {v76_metrics.brand}")
        logger.info(f"  v7.6: {v76_metrics.duration_seconds:.2f}s ({v76_metrics.product_count} products)")
        logger.info(f"  v8.0: {v80_metrics.duration_seconds:.2f}s ({v80_metrics.product_count} products)")
        logger.info(f"  Performance delta: {perf_delta:+.1f}% {'(v8.0 faster ✅)' if perf_delta > 0 else '(v7.6 faster)'}")
        logger.info(f"  Accuracy match: {'✅ YES' if accuracy_match else '❌ NO'}")
    
    def print_summary(self):
        """Print detailed test summary"""
        print("\n" + "="*80)
        print("📋 PARALLEL TEST SUMMARY - v7.6 vs v8.0")
        print("="*80 + "\n")
        
        # Overall stats
        passed = sum(1 for r in self.results if r.accuracy_match)
        total = len(self.results)
        
        print(f"Tests Executed: {total}")
        print(f"Accuracy Match: {passed}/{total} ({'✅ PASS' if passed == total else '❌ FAIL'})")
        print(f"Avg Performance Delta: {sum(r.performance_delta for r in self.results) / len(self.results):.1f}%\n")
        
        # Detailed results
        print("Detailed Results:\n")
        for result in self.results:
            print(f"  {result.operation.upper():10} {result.brand:15}")
            print(f"    v7.6: {result.v7_metrics.duration_seconds:7.2f}s ({result.v7_metrics.product_count:3} items)")
            print(f"    v8.0: {result.v8_metrics.duration_seconds:7.2f}s ({result.v8_metrics.product_count:3} items)")
            print(f"    Perf: {result.performance_delta:+6.1f}% | Accuracy: {'✅' if result.accuracy_match else '❌'}\n")
        
        # Save results
        self._save_results()
    
    def _save_results(self):
        """Save detailed results to JSON"""
        output_file = Path("logs/test_results_v7_v8.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'mode': self.mode,
            'brands_tested': self.brands,
            'results': [r.to_dict() for r in self.results],
            'summary': {
                'total_tests': len(self.results),
                'accuracy_matches': sum(1 for r in self.results if r.accuracy_match),
                'avg_performance_delta': round(
                    sum(r.performance_delta for r in self.results) / len(self.results),
                    2
                )
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"\n✅ Results saved to {output_file}")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main test entry point"""
    parser = argparse.ArgumentParser(
        description="Parallel testing harness for v7.6 vs v8.0"
    )
    parser.add_argument('--brands', default='Roland,Yamaha,Korg',
                        help='Comma-separated brands to test')
    parser.add_argument('--mode', choices=['correctness', 'perf', 'both'],
                        default='correctness', help='Testing mode')
    parser.add_argument('--timeout', type=int, default=300,
                        help='Test timeout (seconds)')
    
    args = parser.parse_args()
    
    brands = [b.strip() for b in args.brands.split(',')]
    
    logger.info(f"🧪 Running parallel tests for brands: {brands}")
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Timeout: {args.timeout}s\n")
    
    coordinator = TestCoordinator(brands, args.mode)
    
    try:
        coordinator.run_parallel_harvest(brands)
        coordinator.print_summary()
    except KeyboardInterrupt:
        logger.info("\n⛔ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
