"""
Memory Management Utilities

Provides memory monitoring, limits, and cleanup functions to prevent
excessive memory usage in the application.
"""

import gc
import logging
import os
import sys
import tracemalloc
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger("MemoryUtils")

# Memory limits (in bytes)
MAX_MEMORY_MB = int(os.getenv("MAX_MEMORY_MB", "2048"))  # Default 2GB
MEMORY_WARNING_THRESHOLD = 0.8  # Warn at 80% of max

# Track memory usage
_memory_snapshots: Dict[str, Dict[str, Any]] = {}
_tracemalloc_started = False


def start_memory_tracking():
    """Start tracking memory allocations."""
    global _tracemalloc_started
    if not _tracemalloc_started:
        try:
            tracemalloc.start()
            _tracemalloc_started = True
            logger.info("Memory tracking started")
        except Exception as e:
            logger.warning(f"Failed to start memory tracking: {e}")


def get_memory_usage() -> Dict[str, Any]:
    """
    Get current memory usage statistics.
    Returns dict with memory info in MB.
    """
    try:
        import psutil
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        
        return {
            "rss_mb": mem_info.rss / (1024 * 1024),  # Resident Set Size
            "vms_mb": mem_info.vms / (1024 * 1024),  # Virtual Memory Size
            "percent": process.memory_percent(),
            "available_mb": psutil.virtual_memory().available / (1024 * 1024),
            "total_mb": psutil.virtual_memory().total / (1024 * 1024),
        }
    except ImportError:
        logger.warning("psutil not installed — cannot get memory stats")
        return {}
    except Exception as e:
        logger.warning(f"Failed to get memory usage: {e}")
        return {}


def log_memory_snapshot(label: str):
    """Log a memory snapshot with a label."""
    mem = get_memory_usage()
    if mem:
        rss_mb = mem.get("rss_mb", 0)
        logger.info(f"Memory snapshot [{label}]: RSS={rss_mb:.1f}MB, {mem.get('percent', 0):.1f}%")
        
        if _tracemalloc_started:
            try:
                current, peak = tracemalloc.get_traced_memory()
                logger.info(f"  Traced: current={current / (1024*1024):.1f}MB, peak={peak / (1024*1024):.1f}MB")
            except Exception:
                pass
        
        _memory_snapshots[label] = {
            **mem,
            "timestamp": datetime.now().isoformat(),
        }


def check_memory_limit() -> bool:
    """
    Check if memory usage exceeds limits.
    Returns True if within limits, False if exceeded.
    """
    mem = get_memory_usage()
    if not mem:
        return True  # Can't check, assume OK
    
    rss_mb = mem.get("rss_mb", 0)
    if rss_mb > MAX_MEMORY_MB:
        logger.error(f"Memory limit exceeded: {rss_mb:.1f}MB > {MAX_MEMORY_MB}MB")
        return False
    
    if rss_mb > MAX_MEMORY_MB * MEMORY_WARNING_THRESHOLD:
        logger.warning(f"Memory usage high: {rss_mb:.1f}MB ({rss_mb/MAX_MEMORY_MB*100:.1f}% of limit)")
    
    return True


def force_garbage_collection():
    """Force Python garbage collection."""
    collected = gc.collect()
    logger.info(f"Forced GC: collected {collected} objects")
    return collected


def cleanup_large_caches():
    """
    Clean up large caches to free memory.
    Call this periodically or when memory is high.
    """
    try:
        # Clear catalog cache if memory is high
        mem = get_memory_usage()
        if mem and mem.get("rss_mb", 0) > MAX_MEMORY_MB * 0.7:
            import backend.server as srv
            if hasattr(srv, "_catalog_cache_dict"):
                # Keep compressed versions, clear dict
                srv._catalog_cache_dict = None
                logger.info("Cleared catalog cache dict to free memory")
        
        # Force GC
        force_garbage_collection()
        
    except Exception as e:
        logger.warning(f"Failed to cleanup caches: {e}")


def get_memory_report() -> Dict[str, Any]:
    """Get a comprehensive memory report."""
    mem = get_memory_usage()
    report = {
        "current": mem,
        "snapshots": _memory_snapshots,
        "limit_mb": MAX_MEMORY_MB,
        "within_limit": check_memory_limit(),
    }
    
    if _tracemalloc_started:
        try:
            current, peak = tracemalloc.get_traced_memory()
            report["traced"] = {
                "current_mb": current / (1024 * 1024),
                "peak_mb": peak / (1024 * 1024),
            }
        except Exception:
            pass
    
    return report
