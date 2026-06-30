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

Create a pull request for every completed task unless explicitly told not to.

PR descriptions should include:
- Summary
- Changes
- Testing
- Notes