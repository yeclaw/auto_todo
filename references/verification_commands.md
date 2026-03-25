# Verification Commands — Extended Reference

## Core Principle

> If verification fails, the step is NOT complete. Fix the error before marking `[x]`.

Do not skip verification to "keep momentum." Technical debt compounds.

---

## By Language / Framework

### Python

| Check | Command |
|-------|---------|
| Syntax only | `python -m py_compile <file.py>` |
| Lint | `ruff check <file.py>` or `flake8 <file.py>` |
| Type check | `mypy <file.py>` |
| Format check | `black --check <file.py>` |
| Unit tests | `pytest <file.py> -v` |
| All tests | `pytest tests/ -v` |
| Import check | `python -c "import <module>"` |

**CI variant:** `python -m py_compile && ruff check . && mypy . && pytest`

### JavaScript / TypeScript

| Check | Command |
|-------|---------|
| Type check (TS) | `tsc --noEmit` |
| Syntax only (JS) | `node --check <file.js>` |
| Lint | `eslint <file.js>` or `eslint .` |
| Format check | `prettier --check .` |
| Unit tests (Jest) | `jest` or `jest <file.test.ts>` |
| Unit tests (Vitest) | `vitest run` or `vitest run <file.test.ts>` |
| All tests | `npm test` |
| Bundle check | `npm run build` (verify no build errors) |

**CI variant:** `tsc --noEmit && eslint . && vitest run`

### Go

| Check | Command |
|-------|---------|
| Build | `go build ./...` |
| Unit tests | `go test ./...` |
| Vet | `go vet ./...` |
| Format check | `gofmt -d .` |
| Test coverage | `go test -cover ./...` |

**CI variant:** `go build && go vet && go test -cover`

### Bash / Shell

| Check | Command |
|-------|---------|
| Syntax only | `bash -n <script.sh>` |
| ShellCheck | `shellcheck <script.sh>` |
| SC2154 (referenced but not assigned) | `shellcheck -a <script.sh>` |

### Rust

| Check | Command |
|-------|---------|
| Build | `cargo build` |
| Tests | `cargo test` |
| Clippy (lint) | `cargo clippy` |
| Format check | `cargo fmt --check` |

### Ruby

| Check | Command |
|-------|---------|
| Syntax | `ruby -c <file.rb>` |
| Tests | `rspec` or `rake spec` |
| Lint | `rubocop <file.rb>` |

### Java / Kotlin

| Check | Command |
|-------|---------|
| Compile | `javac <file.java>` (Java) / `kotlinc <file.kt>` |
| Build | `./gradlew build` (Gradle) / `mvn compile` (Maven) |
| Tests | `./gradlew test` / `mvn test` |

### Dockerfile / Container

| Check | Command |
|-------|---------|
| Syntax / lint | `hadolint <Dockerfile>` |
| Build dry-run | `docker build --dry-run .` |

---

## When Multiple Steps Share Verification

If a single verification command covers multiple files:

```markdown
- [ ] Step 3: Implement User model + auth endpoints
- [ ] [Step 3 Verify] ← `pytest tests/auth/ -v` covers both
```

Group verification at the most natural boundary — don't verify every micro-step.

---

## Verification Anti-Patterns

| Anti-pattern | Why bad | Fix |
|---|---|---|
| `git status` as "verification" | Doesn't prove code works | Run actual tests |
| `ls file.py` as "verification" | Only checks file exists | Check substantive content |
| No verification step | Bugs ship undetected | Add explicit verify step |
| Mark `[x]` after writing code, before running tests | Tests might fail | Run tests first, then mark |
