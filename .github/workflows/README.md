# GitHub Actions Workflows

## Delete Old Branches Workflow

**File**: `delete-old-branches.yml`

### Purpose
Automates the deletion of obsolete branches while preserving the main development branches.

### How to Run
1. Navigate to the [Actions tab](https://github.com/oripridan-dot/Halilit-Support-Center/actions)
2. Select "Delete Old Branches" from the workflow list
3. Click "Run workflow" button (on the right side)
4. Type `DELETE` in the confirmation field
5. Click "Run workflow"

### What It Does
- Deletes 15 old version and feature branches
- Preserves: `main`, `v8.4`, and `v8.6`
- Provides detailed logs of deletion results
- Verifies the final branch count

### Safety Features
- Requires manual trigger (workflow_dispatch)
- Requires typing "DELETE" to confirm
- Only runs if confirmation is provided
- Logs all actions for audit trail

### Expected Result
After successful execution:
- 15 branches will be deleted
- 4 branches will remain: `main`, `v8.4`, `v8.6`, and `copilot/delete-unwanted-branches`
- The PR branch (`copilot/delete-unwanted-branches`) should be deleted manually after merge

### Troubleshooting
If the workflow fails:
1. Check the workflow logs for specific error messages
2. Verify GitHub token has sufficient permissions
3. Ensure branches haven't been deleted manually already
4. Use alternative deletion methods documented in `BRANCH_CLEANUP.md`
