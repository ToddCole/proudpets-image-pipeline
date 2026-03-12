Push the current branch to the remote repository.

1. Run `git status` to confirm everything is committed (no uncommitted changes).
2. Run `git log --oneline origin/main..HEAD` to show what commits will be pushed.
3. Confirm the target branch is not `main` unless the user has explicitly asked to push to main.
4. Push with: `git push -u origin <branch>`
5. If pushing to main, warn the user first and ask for confirmation before proceeding.
6. Show the remote URL and confirm the push succeeded.

Do NOT force push. Do NOT skip hooks.
