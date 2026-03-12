Commit all staged and unstaged changes in this project.

1. Run `git status` and `git diff` to review what has changed.
2. Stage relevant files (avoid .env, secrets, or large binaries).
3. Write a concise commit message that explains *why* the change was made, not just what.
4. Commit using:
```
git commit -m "$(cat <<'EOF'
<message here>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```
5. Show the result of `git log --oneline -5` after committing.

Do NOT push. Do NOT use --no-verify. Do NOT amend unless explicitly asked.
