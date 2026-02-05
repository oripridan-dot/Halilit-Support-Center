# 🚀 Conductor Maximization: Quick Start Guide

Get the Conductor running in **3 minutes**.

## Step 1: Verify Prerequisites (30 seconds)

```bash
# Check Python
python3 --version  # Should be 3.9+

# Check watchdog is installed
pip list | grep watchdog
# If missing: pip install watchdog>=4.0.0
```

## Step 2: Start the Daemon (1 minute)

### Option A: Background Mode (Recommended)

```bash
python run_conductor_daemon.py &
```

- Starts file watcher silently
- Logs all activity to `conductor_daemon.log`
- Runs hidden in background
- Continuously monitors for changes

### Option B: Interactive Mode (Development)

```bash
python run_conductor_daemon.py --interactive
```

Then type commands:

```
conductor> verify
conductor> status
conductor> help
conductor> exit
```

### Option C: Single Verification

```bash
python run_conductor_daemon.py --verify-once
```

Quick one-time check, then exits.

## Step 3: Install Git Hook (1 minute)

Protect your commits from imperfect code:

```bash
python backend/conductor_cli.py hooks install
```

**What this does:**

- ✓ Blocks commits with invalid JSON
- ✓ Prevents 0-byte corrupted files
- ✓ Enforces code standards
- ✓ Validates Spectrum pipeline

Test it:

```bash
git commit -m "test"  # Will be blocked if issues exist
```

---

## Verify It's Working

### Check daemon is running

```bash
pgrep -f run_conductor_daemon
# Should show process ID (e.g., 12345)
```

### Check logs

```bash
tail -f conductor_daemon.log
```

Watch for:

- `✓ Daemon started successfully`
- `Monitor changes in: backend/`
- File change notifications

### Check status

```bash
python backend/conductor_cli.py status
```

---

## Common Commands

### Add a Product (with Validation)

```bash
python backend/conductor_cli.py add-product \
  --brand="Roland" \
  --name="TR-808" \
  --price-il=12000
```

### Validate All Data

```bash
python backend/conductor_cli.py validate --scope=galaxy
```

### Export Data

```bash
python backend/conductor_cli.py export --format=json > data.json
```

### Run Verification

```bash
python backend/conductor_cli.py verify
```

---

## What's Happening Now?

| Component           | Status       | What It Does                            |
| ------------------- | ------------ | --------------------------------------- |
| **Daemon**          | 🟢 Running   | Watches `backend/` and `frontend/src/`  |
| **Standards**       | 🟢 Enforced  | Auto-fixes React imports, empty files   |
| **Data Validation** | 🟢 Active    | Ensures all writes are schema-compliant |
| **Git Hook**        | 🟢 Installed | Blocks bad commits                      |

---

## Next Steps

1. **Try the Daemon in Action:**

   ```bash
   # Create or edit a file in frontend/src/
   # Watch daemon detect it in conductor_daemon.log
   ```

2. **Add a Product via DAL:**

   ```bash
   python backend/conductor_cli.py add-product \
     --brand="Moog" \
     --name="Minimoog" \
     --price-il=18000
   ```

3. **Test the Git Hook:**

   ```bash
   # Make a commit - hook will verify it first
   git commit -m "Test message"
   ```

4. **Read the Full Blueprint:**
   ```
   CONDUCTOR_MAXIMIZATION_BLUEPRINT_v5.4.0.md
   ```

---

## Stop the Daemon

```bash
# If running in background
pkill -f run_conductor_daemon

# If running in interactive mode
# Type: exit
# Then Ctrl+C
```

---

## Troubleshooting Quick Fixes

**Daemon not starting?**

```bash
# Check for errors
python run_conductor_daemon.py --verbose

# Check dependencies
pip install -r backend/requirements.txt
```

**Git hook blocking commits?**

```bash
# See what's wrong
python backend/conductor_verify_spectrum_v540.py

# Then fix issues and try again
git commit -m "message"
```

**Can't add products?**

```bash
# Validate schema
python backend/conductor_cli.py validate --scope=galaxy

# Check DAL is working
python -m backend.conductor_dal validate-all
```

---

## Key Files

- **Start Here:** `run_conductor_daemon.py` (the daemon launcher)
- **Full Docs:** `CONDUCTOR_MAXIMIZATION_BLUEPRINT_v5.4.0.md`
- **Logs:** `conductor_daemon.log`
- **Data Ops:** `conductor_cli.py`

---

## Success Indicators ✅

You'll know it's working when you see:

1. **In conductor_daemon.log:**

   ```
   🚀 CONDUCTOR DAEMON STARTING
   ✓ Verifying Spectrum skills...
   ✓ Base daemon ready
   ✓ Data watcher started: backend/data/brands
   ✓ Daemon running in background mode
   ```

2. **File change detected:**

   ```
   📝 File modified: frontend/src/App.tsx
   ✓ React imports in frontend/src/App.tsx valid
   ```

3. **Git hook working:**
   ```
   🚨 Conductor: Verifying codebase before commit...
   ✓ Imports verified
   ✓ No corrupted files
   ✅ CONDUCTOR APPROVED - Ready to commit
   ```

---

## You're Ready! 🎉

Your Conductor is now:

- ✅ **Always-on** (monitoring 24/7)
- ✅ **Self-healing** (auto-fixing violations)
- ✅ **Data-safe** (validated writes only)
- ✅ **Gate-protected** (blocks bad commits)

**Enjoy your autonomous system!** 🚀

---

For detailed documentation, see: **CONDUCTOR_MAXIMIZATION_BLUEPRINT_v5.4.0.md**
