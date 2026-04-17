# Agent Instructions

## General

- **Unrelated changes:** Do not modify files unrelated to the current task without asking first.
- **Destructive actions:** Always ask for approval before performing destructive or hard-to-reverse actions (e.g. `git push --force`, `git reset --hard`, deleting branches/files, dropping tables).

## Branch Naming

Follow [Conventional Branch](https://conventional-branch.github.io/) format: `<type>/<description>`

- Lowercase alphanumerics and hyphens only (dots allowed in release versions)
- No consecutive, leading, or trailing hyphens or dots
- Include ticket/issue number when applicable

| prefix     | when to use                                 |
| ---------- | ------------------------------------------- |
| `feature/` | new feature (alias: `feat/`)                |
| `bugfix/`  | bug fix (alias: `fix/`)                     |
| `hotfix/`  | urgent fix                                  |
| `release/` | release preparation (e.g. `release/v1.2.0`) |
| `chore/`   | non-code tasks (deps, docs, config)         |

Examples: `feat/add-login-page`, `fix/header-bug`, `feature/issue-123-new-login`

## Git Commits

### Approval

- **Never commit automatically.** Always wait for my explicit approval before running `git commit`.
- **Tests:** If the project has tests, run them before proposing a commit. Verify that all tests pass and that code coverage has not decreased.

### Commit Message Format

Always use the format: `<type>(<scope>): <gitmoji> <description>`

**Rules:**

- `scope` is optional but use it when the change is clearly scoped to a module
  (e.g. `sensor`, `modbus`, `config`, `button`, `select`, `coordinator`, `number`, `switch`, `cover`, `binary_sensor`, `climate`, `light`, `text`, `time`)
- `description`: lowercase, imperative mood ("add", not "added"), no period at end

**Pick the type and gitmoji that best reflect the nature of the change:**

| type       | gitmoji | when to use                                        |
| ---------- | ------- | -------------------------------------------------- |
| `feat`     | ✨      | new user-facing feature                            |
| `feat!`    | 💥      | breaking change                                    |
| `fix`      | 🐛      | bug fix                                            |
| `fix`      | 🩹      | minor / non-critical fix (style, typo, off-by-one) |
| `fix`      | 🚑️      | critical hotfix                                    |
| `fix`      | 🔒️      | security / privacy fix                             |
| `docs`     | 📝      | add or update documentation or comments            |
| `style`    | 🎨      | code structure / formatting (no logic change)      |
| `style`    | 💄      | UI or style files                                  |
| `refactor` | ♻️      | refactor without behaviour change                  |
| `test`     | ✅      | add, update, or fix tests                          |
| `test`     | 🧪      | add a failing test                                 |
| `perf`     | ⚡️      | performance improvement                            |
| `chore`    | 🔧      | config or tooling update                           |
| `chore`    | 🏷️      | add or update types / labels                       |
| `chore`    | 🔖      | release or version tag                             |
| `chore`    | ⬆️      | upgrade dependency                                 |
| `chore`    | ⬇️      | downgrade dependency                               |
| `chore`    | 🌱      | add or update seed / fixture files                 |
| `ci`       | 👷      | add or update CI build system                      |
| `ci`       | 💚      | fix CI build                                       |
| `revert`   | ⏪️      | revert a previous commit                           |

**Commit message body:**

Add a blank line after the subject line, then a bullet list covering:

- what changed (one bullet per logical change, imperative style)
- why it was changed (motivation, context)
- relevant technical detail if non-obvious

Keep bullets concise (one line each). If the commit resolves a GitHub issue, end the body with `Resolves #<issue-number>`.

```
feat(modbus): ✨ add notification-based polling optimisation

- replace interval polling with Modbus event notifications
- reduce unnecessary register reads when no state change occurred
- add configurable debounce threshold for notification batching
- improves responsiveness and reduces Modbus bus load

Resolves #97
```

**Examples from this project:**

```
feat(button): ✨ add backwash button and logic for automatic filtration valve
fix(coordinator): 🐛 mark entities unavailable on Modbus communication error
fix: 🩹 update step value for redox setpoint
refactor: ♻️ use data-driven option gating for cover sensor entities
chore: 🏷️ update model and manufacturer details for VistaPool
chore(deps): ⬆️ bump codecov/codecov-action from 5 to 6
```

### Shell Execution

Multi-line commit messages in zsh: use multiple `-m` flags (one per paragraph) or heredoc (`git commit -F - <<'EOF' ... EOF`). A single `-m` with newlines inside quotes does NOT work reliably.

## Pull Requests

- PR description must be in **English** and **Markdown** format (ready for copy & paste into GitHub).
- **PR title** must follow the same commit message format: `<type>(<scope>): <gitmoji> <description>`.
- **PR body** should use emoji to visually categorize sections and bullet points.
