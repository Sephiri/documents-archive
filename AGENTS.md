# Agent instructions

## Git conventions

Use conventional branch names:

- `feat/{task-slug}` for new features
- `fix/{task-slug}` for bug fixes
- `refactor/{task-slug}` for internal code restructuring
- `docs/{task-slug}` for documentation-only changes
- `chore/{task-slug}` for maintenance, config, dependencies
- `test/{task-slug}` for tests
- `style/{task-slug}` for formatting-only changes
- `perf/{task-slug}` for performance improvements
- `ci/{task-slug}` for CI/CD changes

Use lowercase kebab-case.

Examples:
- `feat/add-document-search`
- `fix/pdf-iframe-rendering`
- `refactor/document-data-layer`
- `docs/update-readme-installation`

## Pull requests

Only create a pull request when the user explicitly asks for a PR or when a feature/fix/docs/refactor task is complete and ready to merge into main.

Never create a pull request for branch maintenance tasks such as rebasing, syncing with main, resolving rebase conflicts, updating dependencies only to unblock another branch, or pushing intermediate commits.

When asked to update a branch with main, only rebase the current branch onto origin/main and push the same branch with --force-with-lease. Then stop.

PR descriptions should include:
- Summary
- Changes
- Testing
- Notes