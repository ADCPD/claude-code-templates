---
name: review-changes
description: Review code changes in any git repository, whatever the language or framework — local uncommitted work, a branch against its base, a single commit or a commit range. Use this skill whenever the user wants feedback on code changes — "review my code", "check my changes", "review before commit", "review this branch", "review commit abc123", "is this ready to merge?", "relis mon code", "revue avant commit", "vérifie mes modifs", "review de ma branche" — even if they don't explicitly say "review". Reports findings only; never modifies code.
argument-hint: "[--staged | --branch [base] | <commit> | <from>..<to>] [-- path...]"
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git branch:*), Bash(git log:*), Bash(git show:*), Bash(git ls-files:*), Bash(git rev-parse:*), Bash(git merge-base:*), Bash(git symbolic-ref:*), Bash(grep:*), Read, Grep, Glob, Task
---

# Review Changes

Review a set of code changes, report findings, and stop. This skill is project-agnostic: it discovers the stack, tooling and conventions of the repository instead of assuming them. It never modifies, formats, stages, commits or pushes anything.

## Context

- Branch: !`git branch --show-current`
- Status: !`git status --short`
- Last commits: !`git log --oneline -5 2>/dev/null`

Arguments: `$ARGUMENTS`

## Step 1 — Determine the review scope

Pick the mode from the arguments. Paths after `--` restrict any mode to those paths.

| Argument | Mode | Diff command |
|---|---|---|
| *(none)* | Local: staged + unstaged + untracked | `git diff HEAD` (fallback `git diff --cached` if the repo has no commit) + untracked files |
| `--staged` | What will actually be committed | `git diff --cached` |
| `--branch [base]` | Branch vs its base | `git diff $(git merge-base <base> HEAD)...HEAD` |
| `<commit>` | A single commit | `git show <commit> --format=fuller` |
| `<from>..<to>` | A commit range | `git diff <from>..<to>` + `git log <from>..<to> --oneline` |

**Resolving the base branch** for `--branch` without an explicit base: try `git symbolic-ref refs/remotes/origin/HEAD`, then `main`, `master`, `develop`. If none exists, ask the user.

**Local mode specifics:**

- Always include untracked files (`git ls-files --others --exclude-standard`), not only when the diff is empty — new files often hold the most important code. Diff each one with `git diff --no-index /dev/null <file>` so line numbers stay consistent.
- Compare `git diff --cached --name-only` and `git diff --name-only`. If files are partially staged, or relevant changes are unstaged, note it in the report: what gets committed may differ from what was reviewed.

**Exclude from the review** (list them in the report as "not reviewed"): lock files (`*.lock`, `package-lock.json`, `pnpm-lock.yaml`, `go.sum`…), minified or built assets, vendored dependencies, binary files, snapshots and generated code.

If nothing remains to review, say so ("No changes to review in this scope.") and **stop**.

## Step 2 — Discover the project

The review is only as good as its understanding of the project. Spend a few tool calls here, not more.

**Conventions** — read, if present: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `.editorconfig`, and any `docs/` page on coding standards. Project rules found there take precedence over the generic guidance in this skill.

**Stack and tooling** — detect from manifest files at the repo root (and in the changed files' nearest parent folders for monorepos):

| Manifest | Stack | Read-only checks to consider |
|---|---|---|
| `composer.json` | PHP | `phpstan`/`psalm` analyse, `php-cs-fixer fix --dry-run`, `phpcs` |
| `package.json` | JS/TS | `eslint`, `tsc --noEmit`, `prettier --check` |
| `pyproject.toml` / `setup.cfg` / `requirements*.txt` | Python | `ruff check`, `mypy`, `black --check` |
| `go.mod` | Go | `go vet`, `staticcheck`, `gofmt -l` |
| `Cargo.toml` | Rust | `cargo clippy`, `cargo fmt --check` |
| `pom.xml` / `build.gradle*` | Java/Kotlin | project lint task if quick |
| `Gemfile` | Ruby | `rubocop` |

Prefer the project's own entry points when they exist (`Makefile` targets, `composer`/`npm` scripts like `lint`, `typecheck`, `cs:check`), since they carry the project's configuration.

**Intent** — the review is better when it knows what the change is meant to do:

- Extract a ticket ID from the branch name or commit messages if one matches a common pattern (`ABC-1234`, `#123`, `GH-123`), plus the descriptive slug.
- Use commit messages in scope as additional intent.
- Do not fetch tickets from external trackers unless the user asks.

## Step 3 — Cheap deterministic checks

Run these before the agent, on changed files only. They catch obvious issues for free and let the agent focus on logic.

**On added lines only** (lines starting with `+` in the diff):

- Debug leftovers for the detected languages, e.g. `dump(`, `dd(`, `var_dump(`, `console.log(`, `debugger`, `print(` in non-CLI Python, `fmt.Println` used for debugging, `dbg!(`, `binding.pry`.
- Newly introduced `TODO` / `FIXME` / `XXX`.
- Secrets: hardcoded tokens, passwords, API keys, private keys, internal URLs, real values in `.env*` files that are not examples/templates.

**Consistency checks**, adapted to the detected stack:

- Schema/ORM model changed but no new migration (Doctrine `migrations/`, Django `*/migrations/`, Rails `db/migrate/`, Laravel `database/migrations/`, Prisma `prisma/migrations/`, Alembic `versions/`…) → flag it.
- Dependency manifest changed without its lock file, or the reverse → flag it.
- Production code changed with no test file touched → mention it (not a blocker on its own).
- Public API contracts changed (OpenAPI/GraphQL schema, exported types, DTOs) → highlight for backward-compatibility review.

**Tooling** detected in Step 2: run only what is installed and configured, only in read-only/check mode, only on the changed files when the tool allows it. Never run a fixer or formatter in write mode. If a tool is missing, slow (> ~1 min) or fails to start, skip it and say so in the report rather than retrying or installing anything.

## Step 4 — Review via agent

Launch a **`code-reviewer` agent** with the Task tool. Give it the diff and the file list, not full files: the agent has `Read` and will open the surrounding code itself, which keeps the main context small.

Prompt:

> Review these code changes.
>
> **Scope**: [mode — local / staged / branch vs <base> / commit <sha> / range]
> **Stack**: [languages and frameworks detected]
> **Project conventions**: [short summary of rules found in Step 2, or "none found"]
> **Intent**: [ticket + slug, commit messages, or "unknown"]
> **Files changed**: [list with status A/M/D/R]
> **Automated checks already done**: [Step 3 results — do not repeat them]
>
> Read the full content of each modified file, and any caller or callee you need, before judging — do not review the diff in isolation.
>
> Focus on: correctness and edge cases, security (injection, authn/authz, data exposure, unsafe deserialization), error handling, concurrency and resource leaks, performance (N+1 queries, unbounded loops or result sets), backward compatibility of public APIs, schemas and data, tests covering the new behaviour, and consistency with the project's existing conventions and patterns.
>
> For each finding give `file:line` (line in the new version), a severity (blocker / major / minor), why it matters, and a concrete fix. When unsure, say so instead of asserting. Do not report style issues that the project's linters or formatters would catch.
>
> **Diff**:
> [diff]

**Large changes** (roughly > 1,500 changed lines or > 25 files): split files into coherent groups (by module, package or layer) and launch one agent per group in parallel, then merge and deduplicate the results.

**If no `code-reviewer` agent is available**, perform the review yourself with the same instructions.

## Step 5 — Report

Write the report in the language the user is writing in. Use this template, and drop empty sections rather than writing "none".

```markdown
## Code review — <scope description>

### Summary
<2-3 sentences: what changes and why, based on the intent>

### What's good
- ...

### Findings

#### 🔴 Blockers
- **`file:line`** — <title>
  <why it matters>
  → Suggestion: <concrete fix>

#### 🟠 Major
- ...

#### 🟡 Minor
- ...

### Automated checks
- Leftovers / secrets: <result>
- <tool>: <result, or "not run (reason)">
- Migrations / dependencies / tests: <result>

### Not reviewed
- <excluded files; staged/unstaged mismatch if any>

### Verdict: <one of the three below>
```

Pick exactly **one** verdict, worded for the scope (commit for local/staged, merge for branch/range, "acceptable" for an already-merged commit):

- ✅ **Ready** — no blocker, no major.
- 🟡 **Minor changes suggested** — no blocker; majors or minors worth considering.
- 🔴 **Changes required** — at least one blocker.

### Severity guide

- **Blocker**: bug, data loss, security issue, broken build or tests, leaked secret, debug leftover, breaking change without migration or versioning.
- **Major**: missing edge case or error handling, missing test for new behaviour, performance trap, clear violation of project conventions.
- **Minor**: readability, naming, small simplification.

## Constraints

- Be constructive; explain *why*, not just *what*.
- Order by importance (blocker > major > minor); merge duplicates.
- Stay within the scope of the changes — no refactoring suggestions on untouched code, unless the change makes an existing problem worse.
- If the code is good, say so briefly. Do not invent problems to fill the report.
- Read-only: do NOT modify, format, stage, commit, push, install dependencies or call external services.
