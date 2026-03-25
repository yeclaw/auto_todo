# auto-todo

Multi-step task execution framework for OpenClaw agents. Supports todo tracking, RPI (Research → Plan → Implement) workflow, wave-based parallelism, and persistent state across sessions.

**Trigger phrases:** auto todo, todo list, stepwise, 逐步, 建立todo, 任务清单, multi-step task, complex task, RPI, research plan implement, /next, /quick, discuss phase, 讨论阶段

## What's included

- `SKILL.md` — Core skill: STATE.md schema, phase flow, /next /quick /status /abort commands, wave execution
- `scripts/state_manager.py` — STATE.md read/write CLI utility
- `scripts/wave_executor.py` — Wave-based parallel execution parser
- `references/rpi.md` — Full RPI pattern: diagrams, sub-agent API, edge cases
- `references/wave_execution.md` — Wave parallelism guide
- `references/discuss_guide.md` — Discuss phase protocol
- `references/verification_commands.md` — Extended verification table (9 languages, CI variants)

## Install

```bash
clawhub install auto-todo
```

Or via skillhub (if your OpenClaw supports it).

## Key features

- **Persistent STATE.md** — task progress survives session resets, no context loss
- **Wave-based parallelism** — run independent sub-tasks in parallel, dependent tasks sequentially
- **Discuss phase** — clarify scope/constraints/risks before spending sub-agent budget
- **RPI workflow** — Research → Plan → Implement with sub-agent isolation
- **Todo tracking** — inline markdown format with per-step verification
- **/next, /quick, /status, /abort** — command shortcuts for common operations
- **Per-language verification** — concrete, executable verification for every code step

## Quick start

```
# Normal mode (full RPI)
> "帮我做 X" → discuss → research → plan → implement → verify → ship

# Quick mode (skip research)
> "/quick 帮我做 X" → discuss → plan → implement → verify

# Resume after session reset
> "继续上次的任务" → reads STATE.md → resumes from current step

# Check next step
> "/next" → reports first incomplete step with reasoning
```

## Phase flow

```
discuss (optional) → research → plan → implement → verify → ship
```

Each phase reads from and writes to `STATE.md` in the skill directory.
