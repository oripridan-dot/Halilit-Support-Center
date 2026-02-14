#!/bin/bash

# Script to delete unwanted branches
# Keep only: main, v8.4, v8.6
# This script documents the branches to be deleted

echo "=== Branch Cleanup Script ==="
echo "Branches to keep: main, v8.4, v8.6"
echo ""

# List of branches to delete
BRANCHES_TO_DELETE=(
    "copilot/fix-codespace-start-issue"
    "copilot/update-devcontainer-settings"
    "v4.0"
    "v4.1-3d"
    "v4.6.1"
    "v5.0"
    "v5.1-taxonomy"
    "v5.2-adk"
    "v5.2.4-google-conductor"
    "v5.4"
    "v6.0"
    "v6.1.1"
    "v8.0"
    "v8.3-mcp"
    "v8.5"
)

echo "Branches to be deleted (${#BRANCHES_TO_DELETE[@]} total):"
for branch in "${BRANCHES_TO_DELETE[@]}"; do
    echo "  - $branch"
done
echo ""

# Note: copilot/delete-unwanted-branches will be deleted after this PR is merged
echo "Note: Branch 'copilot/delete-unwanted-branches' (current PR branch) will be deleted after merge"
echo ""

# Check if user wants to proceed
read -p "Do you want to delete these branches? (yes/no): " confirm

if [ "$confirm" = "yes" ]; then
    echo ""
    echo "Deleting branches..."
    
    for branch in "${BRANCHES_TO_DELETE[@]}"; do
        echo "Deleting remote branch: $branch"
        git push origin --delete "$branch" 2>&1
        
        # Also delete local branch if it exists
        if git show-ref --verify --quiet refs/heads/"$branch"; then
            echo "Deleting local branch: $branch"
            git branch -D "$branch" 2>&1
        fi
        echo ""
    done
    
    echo "=== Branch deletion complete ==="
    echo ""
    echo "Remaining branches:"
    git branch -r | grep -v "HEAD"
else
    echo "Branch deletion cancelled."
fi
