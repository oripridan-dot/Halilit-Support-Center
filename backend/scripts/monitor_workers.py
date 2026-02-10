#!/usr/bin/env python3
"""
Monitor Celery Workers & Queues for Halilit Support Center v8.2

Usage:
    python3 backend/scripts/monitor_workers.py
    python3 backend/scripts/monitor_workers.py --json
    python3 backend/scripts/monitor_workers.py --watch (continuous monitoring)

Features:
    - Real-time worker status
    - Queue depths
    - Task state distribution
    - Performance metrics
    - Alert thresholds
"""

from backend.celery_config import celery_app
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# Colors for terminal output

class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'


def color(text: str, color_code: str) -> str:
    """Add color to terminal output"""
    return f"{color_code}{text}{Colors.RESET}"


def get_worker_stats() -> Dict[str, Any]:
    """Get current worker statistics"""
    try:
        inspect = celery_app.control.inspect()

        if inspect is None:
            return {'error': 'No workers available'}

        # Get various stats
        stats = inspect.stats()
        active_tasks = inspect.active()
        active_queue = inspect.active_queues()
        registered = inspect.registered()

        return {
            'stats': stats or {},
            'active_tasks': active_tasks or {},
            'active_queues': active_queue or {},
            'registered': registered or {}
        }

    except Exception as e:
        return {'error': str(e)}


def analyze_tasks() -> Dict[str, int]:
    """Analyze task state distribution"""
    try:
        inspect = celery_app.control.inspect()

        if inspect is None:
            return {}

        active = inspect.active() or {}

        # Count tasks by state
        task_states = defaultdict(int)

        for worker, tasks in active.items():
            for task in tasks:
                task_id = task.get('id', 'unknown')
                # Try to get task state from result backend
                # For now, just count as "ACTIVE"
                task_states['ACTIVE'] += 1

        return dict(task_states)

    except Exception as e:
        return {}


def check_thresholds(data: Dict[str, Any]) -> List[str]:
    """Check alert thresholds"""
    alerts = []

    if 'error' in data:
        alerts.append(f"❌ {data['error']}")

    # Check worker count
    worker_count = len(data.get('stats', {}))
    if worker_count == 0:
        alerts.append(f"⚠️  NO WORKERS AVAILABLE")
    elif worker_count < 3:
        alerts.append(f"⚠️  Low worker count: {worker_count} (expected 4+)")

    # Check queue depths (future integration with monitoring DB)

    return alerts


def format_table(headers: List[str], rows: List[List[str]], widths: Optional[List[int]] = None) -> str:
    """Format data as ASCII table"""
    if not widths:
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(str(cell)))

    # Header
    header_line = " | ".join(
        str(h).ljust(w) for h, w in zip(headers, widths)
    )
    sep_line = "-+-".join("-" * w for w in widths)

    # Rows
    table_lines = [sep_line, header_line, sep_line]
    for row in rows:
        table_lines.append(" | ".join(
            str(cell).ljust(w) for cell, w in zip(row, widths)
        ))
    table_lines.append(sep_line)

    return "\n".join(table_lines)


def print_status(data: Dict[str, Any], json_output: bool = False):
    """Print formatted status report"""

    if json_output:
        print(json.dumps(data, indent=2, default=str))
        return

    print("\n" + color("═" * 80, Colors.BLUE))
    print(color("🚀 Celery Worker Monitor - Halilit Support Center v8.2", Colors.BLUE))
    print(color("═" * 80, Colors.BLUE))
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Check for errors
    if 'error' in data:
        print(color(f"❌ ERROR: {data['error']}", Colors.RED))
        return

    # Worker Status
    stats = data.get('stats', {})
    active_tasks = data.get('active_tasks', {})
    active_queues = data.get('active_queues', {})

    print(color("📦 WORKER STATUS", Colors.CYAN) + "\n")

    worker_rows = []
    total_active = 0

    for worker_name, worker_stats in stats.items():
        # Extract info
        pool_size = worker_stats.get('pool', {}).get('max-concurrency', 0)
        active_count = len(active_tasks.get(worker_name, []))
        total_active += active_count

        # Queue list
        queues = active_queues.get(worker_name, [])
        queue_names = ", ".join(q.get('name', 'unknown') for q in queues)

        # Status indicator
        if active_count > 0:
            status = color("✅ ACTIVE", Colors.GREEN)
        else:
            status = color("⏸️  IDLE", Colors.YELLOW)

        worker_rows.append([
            worker_name.split('@')[0][:15],  # Worker name
            status,
            str(pool_size),
            str(active_count),
            queue_names[:40]
        ])

    print(format_table(
        ["Worker", "Status", "Pool", "Active", "Queues"],
        worker_rows
    ))

    print(f"\nTotal workers: {len(stats)}")
    print(f"Total active tasks: {total_active}")

    # Queue Information
    print("\n" + color("📊 QUEUE STATUS", Colors.CYAN) + "\n")

    queue_rows = []
    for worker_name, queues in active_queues.items():
        for queue in queues:
            queue_name = queue.get('name', 'unknown')
            queue_rows.append([
                worker_name.split('@')[0][:15],
                queue_name,
                str(queue.get('exchange', {}).get('name', 'N/A')),
                str(queue.get('routing_key', 'N/A'))
            ])

    if queue_rows:
        print(format_table(
            ["Worker", "Queue", "Exchange", "Routing Key"],
            queue_rows
        ))
    else:
        print("No active queues")

    # Alerts
    alerts = check_thresholds(data)
    if alerts:
        print("\n" + color("⚠️  ALERTS", Colors.YELLOW) + "\n")
        for alert in alerts:
            print(f"  {alert}")
    else:
        print("\n" + color("✅ All systems healthy", Colors.GREEN))

    print("")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Monitor Celery workers and queues"
    )
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--watch', action='store_true',
                        help='Continuous monitoring')
    parser.add_argument('--interval', type=int, default=5,
                        help='Update interval (seconds)')

    args = parser.parse_args()

    try:
        if args.watch:
            print(
                color("Starting continuous monitoring (Ctrl+C to stop)...\n", Colors.BLUE))
            while True:
                data = get_worker_stats()
                # Clear screen (Unix only)
                print("\033[2J\033[H")
                print_status(data, args.json)
                time.sleep(args.interval)
        else:
            data = get_worker_stats()
            print_status(data, args.json)

    except KeyboardInterrupt:
        print("\n" + color("Monitoring stopped", Colors.YELLOW))
        sys.exit(0)
    except Exception as e:
        print(color(f"❌ Error: {e}", Colors.RED), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
