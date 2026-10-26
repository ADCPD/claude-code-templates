---
name: rebase
description: Safely rebase the current branch on master with backup and conflict resolution. Use for "rebase", "rebase on master", "update my branch".
argument-hint: "[optional target branch, default: origin/<default branch>]"
---

# Safe Rebase

## Context

- Current branch: !`git branch --show-current`
- Default branch: !`git rev-parse --abbrev-ref origin/HEAD`
- Working tree status: !`git status --short`
- Upstream tracking: !`git rev-parse --abbrev-ref @{u} 2>/dev/null || echo "(no upstream)"`
- Commits ahead of default branch: !`git log --oneline origin/HEAD..HEAD 2>/dev/null`

## Step 1: Pre-flight checks

### 1.1 Clean working tree
If there are uncommitted changes:
- Warn the user: "You have uncommitted changes. Commit or stash them before rebasing."
- **STOP**. Do not proceed.

### 1.2 Determine the target
- If `$ARGUMENTS` is provided, use it as the rebase target (e.g., `origin/develop`)
- Otherwise, use the "Default branch" from Context above

### 1.3 Verify we're not on the default branch
```bash
current=$(git branch --show-current) && default=$(git rev-parse --abbrev-ref origin/HEAD) && default=${default#origin/} && if [ "$current" = "$default" ]; then echo "ERROR: you are on $default. Nothing to rebase."; exit 1; fi
```

## Step 2: Backup

Create a backup tag so we can rollback if needed:

```bash
git tag "backup/$(git branch --show-current)/$(date +%Y%m%d-%H%M%S)"
```

## Step 3: Fetch and rebase

```bash
git fetch origin
```

```bash
git rebase <target>
```

(Replace `<target>` with the branch determined in Step 1.2)

### If rebase succeeds (no conflicts):
- Skip to Step 5

### If rebase fails with conflicts:
- Continue to Step 4

## Step 4: Conflict resolution

1. List conflicting files:
   ```bash
   git diff --name-only --diff-filter=U
   ```

2. For each conflicting file:
   - Read the file with conflict markers
   - Analyze both sides of the conflict (ours vs theirs)
   - Propose a resolution explaining the reasoning
   - Ask the user via `AskUserQuestion`:
     - **Accept resolution**: apply the proposed fix
     - **Keep ours**: keep the current branch version
     - **Keep theirs**: keep the target branch version
     - **Manual**: let the user resolve manually

3. After resolving all conflicts in a file:
   ```bash
   git add <file>
   ```

4. After all files are resolved:
   ```bash
   git rebase --continue
   ```

5. If new conflicts appear, repeat from step 1.

### If the user wants to abort at any point:
```bash
git rebase --abort
```
Inform the user that the branch is back to its original state (the backup tag is still available).

## Step 5: Post-rebase

Display the result:

```
Rebase     : OK
Target     : <target branch>
Commits    : <number> commits rebased
Backup tag : backup/<branch>/<timestamp>
```

Then ask the user via `AskUserQuestion`:
- **Force push**: `git push --force-with-lease origin $(git branch --show-current)`
- **Skip push**: don't push yet
- **Abort**: undo the rebase via `git reset --hard` to the backup tag

## Constraints

- NEVER rebase without creating a backup tag first
- NEVER use `git push --force` — always use `--force-with-lease`
- NEVER rebase on the default branch itself
- NEVER auto-resolve conflicts without user confirmation
- If working tree is dirty, STOP and ask to commit/stash first
- Always fetch before rebase to ensure we have the latest remote
