---
name: safe-python-change
description: Safely modify, extend, refactor, or fix Python source code and unittest tests in this repository. Use for Python feature work, bug fixes, validation changes, CLI behavior changes, and related test updates that require a minimal diff, full test verification, and protection against unrequested Git staging, commits, or merges.
---

# Safe Python Change

Follow this workflow for every Python change in this repository.

## Workflow

1. Check the current Git branch and run `git status`. Preserve unrelated or pre-existing changes.
2. Read the relevant Python source code and existing tests before editing.
3. Compare the requested behavior with the current behavior. State the specific gaps to address.
4. Make only the smallest changes needed to close those gaps. Avoid unrelated cleanup or refactoring.
5. Add or update automated tests for the changed behavior. Keep existing coverage intact.
6. Run the complete unittest suite with `python -m unittest -v`. Use the repository's available Python interpreter if `python` is not on PATH.
7. If any test fails, diagnose the cause, apply a scoped fix, and rerun the complete suite until it passes. Do not hide, skip, or weaken a failing test merely to obtain a pass.
8. Run `git diff` and `git status` to confirm the actual change scope. Ensure generated outputs and temporary files are absent or ignored.
9. Report the files changed, behavior implemented, full test result, and any remaining risks or unverified edge cases.
10. Do not run `git add`, create a commit, switch or merge branches, or otherwise alter Git history unless the user explicitly requests that Git action.

If a safe change cannot be completed without expanding scope, overwriting user work, or making an unrequested Git operation, stop and ask for direction.
