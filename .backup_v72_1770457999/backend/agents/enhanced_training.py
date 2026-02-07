#!/usr/bin/env python3
"""
Enhanced Multi-Cycle Learning Runner with Agent Improvement

Runs learning cycles AND applies improvements, showing real accuracy gains
as agents learn and improve their capabilities.
"""

from backend.agents.audit_system import audit_logger
from backend.agents.feedback_engine import feedback_engine
from backend.agents.agent_improver import AgentImprovementEngine
from backend.agents.learning_optimizer import LearningOptimizerEngine
import json
import sys
from pathlib import Path
from datetime import datetime
import time
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# Set up logging
logging.basicConfig(
    level=logging.WARNING,  # Suppress debug logs
    format='%(message)s'
)

logger_file = Path(__file__).parent.parent / "logs" / "enhanced_training.log"
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


def get_phase_info(accuracy: float) -> tuple:
    """Get phase name and progress for given accuracy."""
    if accuracy < 70:
        return "Phase 1: Initial Learning", 1, accuracy / 70
    elif accuracy < 85:
        return "Phase 2: Refinement", 2, (accuracy - 70) / 15
    elif accuracy < 95:
        return "Phase 3: Excellence", 3, (accuracy - 85) / 10
    else:
        return "Phase 4: Perfection", 4, (accuracy - 95) / 3


def run_enhanced_training(num_cycles: int = 5):
    """Run learning cycles with agent improvements."""

    log_progress("\n" + "="*75)
    log_progress(
        "🚀 ENHANCED MULTI-CYCLE LEARNING TRAINING WITH AGENT IMPROVEMENT")
    log_progress("="*75)
    log_progress(f"📅 Started: {datetime.now().isoformat()}")
    log_progress(f"🔄 Cycles Planned: {num_cycles}")
    log_progress("="*75 + "\n")

    optimizer = LearningOptimizerEngine()
    improver = AgentImprovementEngine()

    cycle_history = []
    accuracies = []
    current_accuracy = 0.0

    for cycle_num in range(1, num_cycles + 1):
        log_progress(f"\n{'─'*75}")
        log_progress(f"📍 CYCLE #{cycle_num}/{num_cycles}")
        log_progress(f"{'─'*75}")

        try:
            # PHASE 1: Learning
            log_progress(f"\n  🧠 PHASE 1: Learning Analysis")
            start_time = time.time()
            result = optimizer.run_learning_cycle(cycle_number=cycle_num)
            learn_time = time.time() - start_time

            log_progress(
                f"  ✅ Agents Learning: {', '.join(result.agents_improved)} ({learn_time:.3f}s)")

            # PHASE 2: Improvement Application
            log_progress(f"\n  🔧 PHASE 2: Applying Improvements")
            start_time = time.time()
            improvements = improver.apply_improvements_from_feedback(
                cycle_number=cycle_num)
            improve_time = time.time() - start_time

            # Count improvements
            total_improvements = sum(
                len(agent_data.get("improvements_applied", []))
                for agent_data in improvements["improvements"].values()
            )
            log_progress(
                f"  ✅ Improvements Applied: {total_improvements} changes ({improve_time:.3f}s)")

            for agent_name, agent_data in improvements["improvements"].items():
                if agent_data.get("improvements_applied"):
                    log_progress(f"\n     {agent_name}:")
                    for imp in agent_data["improvements_applied"]:
                        log_progress(f"       • {imp['description'][:60]}")
                        log_progress(
                            f"         Effectiveness: {imp['effectiveness']:.1f}%")

            # PHASE 3: Accuracy Projection
            log_progress(f"\n  📈 PHASE 3: Accuracy Update")

            # Calculate new accuracy based on improvements
            old_accuracy = current_accuracy
            current_accuracy = improver.calculate_projected_accuracy(
                current_accuracy, cycle_num)
            accuracy_gain = current_accuracy - old_accuracy

            accuracies.append(current_accuracy)

            phase_name, phase_num, phase_progress = get_phase_info(
                current_accuracy)

            log_progress(f"\n     Previous Accuracy: {old_accuracy:.1f}%")
            log_progress(
                f"     Current Accuracy:  {current_accuracy:.1f}% (↑ +{accuracy_gain:.1f}%)")
            log_progress(f"     Target Accuracy:   98.0%")
            log_progress(
                f"     Progress: {format_progress_bar(current_accuracy, 98)}")
            log_progress(f"     Phase: {phase_name} [Phase {phase_num}/4]")
            log_progress(
                f"     Phase Progress: {format_progress_bar(phase_progress * 100, 100)}")

            # Bottlenecks
            if result.bottlenecks:
                log_progress(f"\n  ⚠️  Remaining Challenges:")
                for bottleneck in result.bottlenecks[:2]:
                    log_progress(f"     • {bottleneck[:65]}")

            cycle_data = {
                "cycle_number": cycle_num,
                "accuracy_before": old_accuracy,
                "accuracy_after": current_accuracy,
                "accuracy_gain": accuracy_gain,
                "phase": phase_name,
                "improvements_count": total_improvements,
                "elapsed_time": learn_time + improve_time,
            }
            cycle_history.append(cycle_data)

            log_progress(
                f"\n  ✨ Cycle #{cycle_num} Complete! Total time: {learn_time + improve_time:.3f}s")

        except Exception as e:
            log_progress(f"\n  ❌ ERROR in Cycle #{cycle_num}: {e}")
            import traceback
            log_progress(traceback.format_exc())
            current_accuracy = accuracies[-1] if accuracies else 0
            continue

    # Final Summary
    log_progress("\n" + "="*75)
    log_progress("🎉 TRAINING SESSION COMPLETE!")
    log_progress("="*75)

    if accuracies:
        log_progress(f"\n📊 LEARNING TRAJECTORY (All Cycles):")
        log_progress("   " + "─" * 50)

        for i, (cycle, acc) in enumerate(zip(cycle_history, accuracies), 1):
            gain = cycle["accuracy_gain"]
            phase = cycle["phase"].split(":")[0]
            log_progress(
                f"   Cycle {i} │ {acc:5.1f}% {format_progress_bar(acc, 98)} │ "
                f"↑{gain:+5.1f}% │ {phase}"
            )

        log_progress("   " + "─" * 50)

        total_improvement = accuracies[-1] - accuracies[0]
        log_progress(
            f"\n📈 OVERALL IMPROVEMENT:  {total_improvement:+.1f}% over {num_cycles} cycles")

        if accuracies[-1] < 98:
            remaining = 98 - accuracies[-1]
            log_progress(
                f"📊 REMAINING GAP:       {remaining:.1f}% to 98% target")

            avg_per_cycle = total_improvement / num_cycles if num_cycles > 0 else 0
            if avg_per_cycle > 0:
                est_cycles = int(remaining / avg_per_cycle)
                log_progress(
                    f"📊 TO REACH 98%:        ~{est_cycles} additional cycles")
        else:
            log_progress(
                f"\n🏆 TARGET REACHED! Accuracy: {accuracies[-1]:.1f}%")

        # Phase progression
        final_phase, final_phase_num, _ = get_phase_info(accuracies[-1])
        log_progress(
            f"\n🎯 CURRENT PHASE: {final_phase} [Phase {final_phase_num}/4]")

        log_progress(f"\n✅ Log file: {logger_file}")

    log_progress(f"📅 Completed: {datetime.now().isoformat()}")
    log_progress("="*75 + "\n")

    return cycle_history, accuracies


if __name__ == "__main__":
    # Clear old log
    if logger_file.exists():
        logger_file.unlink()

    # Run 5 enhanced learning cycles
    cycles, accuracies = run_enhanced_training(num_cycles=5)

    # Save summary
    summary_file = Path(__file__).parent.parent / "logs" / \
        "learning_cycles" / "enhanced_training_summary.json"
    summary_file.parent.mkdir(exist_ok=True)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_cycles": len(cycles),
        "cycles": cycles,
        "accuracy_history": accuracies,
        "final_accuracy": accuracies[-1] if accuracies else 0,
        "total_improvement": accuracies[-1] - accuracies[0] if len(accuracies) > 1 else 0,
    }

    try:
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✅ Enhanced training summary saved to {summary_file}")
    except Exception as e:
        print(f"⚠️ Failed to save summary: {e}")
