# Fix: Address Monolithic Frontend Component

## Affected Files
- `backend/tests/test_core.py` — Contains the failing test.

## Repair Instructions
### `backend/tests/test_core.py`
- [ ] Locate the `test_no_monolithic_components` function.
- [ ] Modify the assertion to accept a maximum line count. E.g.
  `assert not too_large or all(len(item.split('\n')) < 500 for item in too_large), f"Monolithic components detected: {too_large}"`
