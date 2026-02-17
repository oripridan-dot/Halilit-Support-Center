# Memory Management Guide

## Overview

This document describes the memory management system implemented to prevent excessive memory usage (like the 19GB issue).

## Memory Monitoring

### Automatic Tracking
- Memory tracking starts automatically when the server starts
- Snapshots are logged at key points: startup, after MCP init, after catalog build, shutdown
- Memory usage is checked every 60 seconds

### Memory Limits
- Default limit: 2GB (configurable via `MAX_MEMORY_MB` environment variable)
- Warning threshold: 80% of limit
- When limit is exceeded, catalog dict cache is cleared from memory

## Optimizations

### Backend Catalog Cache
- **Before**: Catalog kept in memory as JSON bytes, gzip bytes, AND dict (triple memory usage)
- **After**: Dict only kept in memory when memory is available. When memory is high, dict is cleared and rebuilt from JSON when needed
- Catalog JSON and gzip remain in memory for fast API responses
- Dict is rebuilt on-demand from JSON when needed for endpoints that require it

### Periodic Cleanup
- Runs every 60 seconds
- Checks memory usage
- Clears large caches if memory usage exceeds 70% of limit
- Forces Python garbage collection

## Memory Utilities

Located in `backend/memory_utils.py`:

- `start_memory_tracking()` - Start tracemalloc tracking
- `get_memory_usage()` - Get current memory stats (RSS, VMS, percent)
- `log_memory_snapshot(label)` - Log memory usage with a label
- `check_memory_limit()` - Check if memory exceeds limits
- `force_garbage_collection()` - Force Python GC
- `cleanup_large_caches()` - Clean up large caches
- `get_memory_report()` - Get comprehensive memory report

## Monitoring Memory Usage

### Check Current Usage
```python
from backend.memory_utils import get_memory_usage, log_memory_snapshot

mem = get_memory_usage()
print(f"RSS: {mem['rss_mb']:.1f}MB")
print(f"Percent: {mem['percent']:.1f}%")

log_memory_snapshot("my_checkpoint")
```

### View Memory Report
```python
from backend.memory_utils import get_memory_report

report = get_memory_report()
print(report)
```

## Environment Variables

- `MAX_MEMORY_MB` - Maximum memory limit in MB (default: 2048)

## Best Practices

1. **Regular Monitoring**: Check memory snapshots in logs
2. **Cache Management**: Large caches are automatically cleared when memory is high
3. **Garbage Collection**: Forced GC runs periodically, but you can trigger manually if needed
4. **Memory Limits**: Set appropriate limits based on your server capacity

## Troubleshooting

### High Memory Usage
1. Check logs for memory snapshots
2. Verify catalog cache is being cleared when memory is high
3. Check for memory leaks in long-running processes
4. Consider reducing `MAX_MEMORY_MB` if server has limited RAM

### Memory Not Being Freed
1. Force garbage collection: `force_garbage_collection()`
2. Clear caches manually: `cleanup_large_caches()`
3. Check for circular references in data structures
4. Restart the server if memory continues to grow

## Future Improvements

- Add memory profiling endpoints for monitoring
- Implement LRU cache eviction for catalog data
- Add memory usage alerts
- Track memory usage per endpoint
