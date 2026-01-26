# 🛠️ 05_WORKFLOWS.md

## 🔄 Daily Dev Cycle

### 1. Start Environment
```bash
cd frontend
pnpm dev
```

### 2. Update Data (If Scrapers Changed)
```bash
cd backend
python3 forge_backbone.py
# Verify check:
# python3 system_architect.py
```

### 3. Deployment Build
```bash
cd frontend
pnpm build
# Upload 'dist/' folder to host
```

## 🚨 Troubleshooting
- **Missing Images?** Run `forge_backbone.py` to trigger Visual Factory.
- **Type Errors?** Run `npx tsc --noEmit` in frontend.
- **Stale Data?** Clear browser cache or run `window.__hscdev.clearCache()`.
