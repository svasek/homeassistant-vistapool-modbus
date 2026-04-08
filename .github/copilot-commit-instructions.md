Always use the format: `<type>(<scope>): <gitmoji> <description>`

**Rules:**
- `scope` is optional but use it when the change is clearly scoped to a module  
  (e.g. `sensor`, `modbus`, `config`, `button`, `select`, `coordinator`, `number`, `switch`, `cover`, `binary_sensor`, `climate`, `light`, `text`, `time`)
- `description`: lowercase, imperative mood ("add", not "added"), no period at end

**Pick the type and gitmoji that best reflect the nature of the change:**

| type       | gitmoji | when to use                                      |
|------------|---------|--------------------------------------------------|
| `feat`     | ✨      | new user-facing feature                          |
| `feat!`    | 💥      | breaking change                                  |
| `fix`      | 🐛      | bug fix                                          |
| `fix`      | 🩹      | minor / non-critical fix (style, typo, off-by-one) |
| `fix`      | 🚑️      | critical hotfix                                  |
| `fix`      | 🔒️      | security / privacy fix                           |
| `docs`     | 📝      | add or update documentation or comments          |
| `style`    | 🎨      | code structure / formatting (no logic change)    |
| `style`    | 💄      | UI or style files                                |
| `refactor` | ♻️      | refactor without behaviour change                |
| `test`     | ✅      | add, update, or fix tests                        |
| `test`     | 🧪      | add a failing test                               |
| `perf`     | ⚡️      | performance improvement                          |
| `chore`    | 🔧      | config or tooling update                         |
| `chore`    | 🏷️      | add or update types / labels                     |
| `chore`    | 🔖      | release or version tag                           |
| `chore`    | ⬆️      | upgrade dependency                               |
| `chore`    | ⬇️      | downgrade dependency                             |
| `chore`    | 🌱      | add or update seed / fixture files               |
| `ci`       | 👷      | add or update CI build system                    |
| `ci`       | 💚      | fix CI build                                     |
| `revert`   | ⏪️      | revert a previous commit                         |

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
