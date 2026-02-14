# Branch Cleanup Documentation

## Task
Delete all branches except `main`, `v8.4`, and `v8.6`

## Current Branch Status

### Branches to KEEP (3)
- `main` - Main development branch
- `v8.4` - Version 8.4 release
- `v8.6` - Version 8.6 release

### Branches to DELETE (16)
1. `copilot/fix-codespace-start-issue` - Old feature branch
2. `copilot/update-devcontainer-settings` - Old feature branch
3. `v4.0` - Old version
4. `v4.1-3d` - Old version
5. `v4.6.1` - Old version
6. `v5.0` - Old version
7. `v5.1-taxonomy` - Old version
8. `v5.2-adk` - Old version
9. `v5.2.4-google-conductor` - Old version
10. `v5.4` - Old version
11. `v6.0` - Old version
12. `v6.1.1` - Old version
13. `v8.0` - Old version
14. `v8.3-mcp` - Old version
15. `v8.5` - Old version
16. `copilot/delete-unwanted-branches` - This PR branch (delete after merge)

## How to Execute

### Option 1: Using GitHub Actions Workflow (RECOMMENDED)
1. Go to https://github.com/oripridan-dot/Halilit-Support-Center/actions/workflows/delete-old-branches.yml
2. Click "Run workflow"
3. Type "DELETE" in the confirmation field
4. Click "Run workflow" button
5. Wait for the workflow to complete
6. Verify results in the workflow logs

### Option 2: Using the provided script
```bash
./delete_branches.sh
```

### Option 3: Manual deletion via git commands
```bash
# Delete each branch remotely
git push origin --delete <branch-name>

# Delete local branch if exists
git branch -D <branch-name>
```

### Option 4: Via GitHub Web Interface
1. Go to https://github.com/oripridan-dot/Halilit-Support-Center/branches
2. Click the delete (trash) icon next to each branch listed above

## Post-cleanup Verification
After deletion, verify only 3 branches remain:
```bash
git branch -r
```

Expected output:
```
origin/main
origin/v8.4
origin/v8.6
```
