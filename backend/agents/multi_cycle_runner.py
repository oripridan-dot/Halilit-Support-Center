#!/usr/bin/env python3
"""
Multi-Cycle Learning Runner - Drives agents through improvement phases

Executes multiple learning cycles with detailed progress tracking,
showing how agents improve from 0% toward 98% accuracy.
"""

from backend.unified_quality_gates import audit_logger, feedback_engine
from backend.unified_learning_system import LearningOptimizerEngine
import json
import sys
from pathlib import Path
from datetime import datetime
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


logger_file = Path(__file__).parent.parent / \
    "logs" / "multi_cycle_training.log"
logger_file.parent.mkdir(exist_ok=True)


def log_progress(message: str):
    """Log to both console and file."""
    print(message)
    with open(logger_file, 'a') as f:
        f.write(f"{message}\n")


def format_progress_bar(current: float, target: float = 100) -> str:
    """Create a visual progress bar."""
    percent = (current / target) * 100 if target > 0 else 0
    filled = int(percent / 5)
    empty = 20 - filled
    return f"[{'█' * filled}{'░' * empty}] {percent:.1f}%"


def run_multi_cycle_training(num_cycles: int = 5):
    """Run multiple learning cycles with progress tracking."""

    log_progress("\n" + "="*70)
    log_progress("🚀 MULTI-CYCLE LEARNING TRAINING SESSION")
    log_progress("="*70)
    log_progress(f"📅 Started: {datetime.now().isoformat()}")
    log_progress(f"🔄 Cycles Planned: {num_cycles}")
    log_progress("="*70 + "\n")

    optimizer = LearningOptimizerEngine()

    cycle_history = []
    accuracies = []

    for cycle_num in range(1, num_cycles + 1):
        log_progress(f"\n{'─'*70}")
        log_progress(f"📍 CYCLE #{cycle_num}/{num_cycles}")
        log_progress(f"{'─'*70}")

        try:
            # Run learning cycle
            start_time = time.time()
            result = optimizer.run_learning_cycle(cycle_number=cycle_num)
            elapsed = time.time() - start_time

            # Extract metrics
            cycle_data = {
                "cycle_number": cycle_num,
                "timestamp": datetime.now().isoformat(),
                "elapsed_seconds": elapsed,
                "agents_improved": result.agents_improved,
                "accuracy_improvement": result.accuracy_improvement,
                "bottlenecks": result.bottlenecks,
                "next_focus_areas": result.next_focus_areas,
            }

            cycle_history.append(cycle_data)

            # Log agent improvements
            log_progress(
                f"\n✅ Agents Processed: {', '.join(result.agents_improved)}")
            log_progress(f"⏱️  Execution Time: {elapsed:.2f}s")

            # Get health report to show accuracy
            health = feedback_engine.get_pipeline_health_report()
            current_accuracy = health.get('pipeline_accuracy', 0)
            accuracies.append(current_accuracy)

            log_progress(f"\n📊 ACCURACY PROGRESSION:")
            log_progress(f"   Current: {current_accuracy:.1f}%")
            log_progress(f"   Target: 98.0%")
            log_progress(
                f"   Progress: {format_progress_bar(current_accuracy, 98)}")

            # Check which phase we're in
            if current_accuracy < 70:
                phase = "Phase 1: Initial Learning (0-70%)"
            elif current_accuracy < 85:
                phase = "Phase 2: Refinement (70-85%)"
            elif current_accuracy < 95:
                phase = "Phase 3: Excellence (85-95%)"
            else:
                phase = "Phase 4: Perfection (95-98%)"

            log_progress(f"   Phase: {phase}")

            # Show bottlenecks
            if result.bottlenecks:
                log_progress(f"\n⚠️  BOTTLENECKS:")
                for bottleneck in result.bottlenecks:
                    log_progress(f"   • {bottleneck}")

            # Show next focus areas
            log_progress(f"\n🎯 NEXT FOCUS AREAS:")
            for area in result.next_focus_areas:
                log_progress(f"   • {area}")

            log_progress(f"\n✨ Cycle #{cycle_num} Complete! ({elapsed:.2f}s)")

        except Exception as e:
            log_progress(f"\n❌ ERROR in Cycle #{cycle_num}: {e}")
            import traceback
            log_progress(traceback.format_exc())
            continue

    # Summary
    log_progress("\n" + "="*70)
    log_progress("🎉 TRAINING SESSION COMPLETE")
    log_progress("="*70)

    if accuracies:
        log_progress(f"\n📈 ACCURACY HISTORY:")
        for i, acc in enumerate(accuracies, 1):
            log_progress(
                f"   Cycle {i}: {acc:.1f}% {format_progress_bar(acc, 98)}")

        improvement = accuracies[-1] - accuracies[0]
        log_progress(
            f"\n📊 TOTAL IMPROVEMENT: +{improvement:.1f}% over {num_cycles} cycles")

        if len(accuracies) > 1 and improvement != 0:
            avg_improvement = improvement / (len(accuracies) - 1)
            log_progress(f"📊 AVERAGE PER CYCLE: +{avg_improvement:.1f}%")

            # Project to 98%
            if accuracies[-1] < 98 and avg_improvement > 0:
                remaining_gap = 98 - accuracies[-1]
                cycles_to_98 = max(1, int(remaining_gap / avg_improvement))
                log_progress(
                    f"📊 ESTIMATED CYCLES TO 98%: {cycles_to_98} cycles")
        elif improvement == 0:
            log_progress(f"📊 AVERAGE PER CYCLE: Awaiting agent updates...")
            log_progress(
                f"⏳ Note: Agents need to apply feedback to improve accuracy")

    log_progress(f"\n✅ Summary saved to: {logger_file}")
    log_progress(f"📅 Completed: {datetime.now().isoformat()}")
    log_progress("="*70 + "\n")

    return cycle_history, accuracies


if __name__ == "__main__":
    # Run 5 learning cycles
    cycles, accuracies = run_multi_cycle_training(num_cycles=5)

    # Save summary to JSON
    summary_file = Path(__file__).parent.parent / "logs" / \
        "learning_cycles" / "training_summary.json"
    summary_file.parent.mkdir(exist_ok=True)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_cycles": len(cycles),
        "cycles": cycles,
        "accuracy_history": accuracies,
        "final_accuracy": accuracies[-1] if accuracies else 0,
        "total_improvement": (accuracies[-1] - accuracies[0]) if len(accuracies) > 1 else 0,
    }

    try:
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✅ Training summary saved to {summary_file}")
    except Exception as e:
        print(f"⚠️ Failed to save summary: {e}")
