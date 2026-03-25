---
name: auto-todo
description: "Multi-step task execution framework with persistent state and wave-based parallelism. Trigger: (auto todo, todo list, stepwise, 逐步, 建立todo, 任务清单, multi-step task, complex task, RPI, research plan implement, /next, /quick, discuss phase, 讨论阶段). Use for: any task requiring multiple steps, code development, spec-driven projects. Automatically breaks down tasks, tracks progress in STATE.md, supports wave-parallel subagent execution."
---

# Auto-Todo v2

Persistent multi-step task execution with state across sessions.

## Core Principle

**STATE.md is the source of truth.** All progress persists across session resets. Never assume a fresh context — always read STATE.md first.

## Phase Flow

```
discuss (optional) → research → plan → implement → verify → ship
```

Each phase reads from and writes to `STATE.md` in the skill directory.

---

## Quick Start

### Normal mode (full RPI)

> "帮我做 X" → auto-todo triggers → discuss → research → plan → implement → verify

### Quick mode (skip research)

> "/quick 帮我做 X" → discuss → plan → implement → verify (no subagent research)

### Resume after session reset

> "继续上次的任务" → read STATE.md → detect current step → resume

### Check next step

> "/next" → read STATE.md → report first incomplete step

---

## STATE.md Schema

Every task has a `STATE.md` in `~/.openclaw/workspace/skills/auto-todo/`:

```markdown
# STATE.md

## Task
task_id: <uuid>
task_name: <short name>
created: <ISO timestamp>
last_updated: <ISO timestamp>

## Goal
<1 sentence describing what this task aims to achieve>

## Phase
current_phase: discuss | research | plan | implement | verify | ship | complete

## Progress
completed_steps:
  - [step name] @ [timestamp]

current_step: [step name]
current_wave: [wave number]

## Waves
wave_1:
  - [ ] task A (parallel)
  - [ ] task B (parallel)
wave_2:
  - [ ] task C (depends on A,B)

## Blockers
blockers:
  - [description] @ [timestamp]

## Decisions
decisions:
  - [key: decision made] @ [timestamp]

## Discuss Output
discuss_summary: |
  <3-5 sentence summary from discuss phase>
```

---

## Commands

### /next

Read STATE.md → find first incomplete step → report:
- What the step is
- Why it's the next step
- Whether to proceed

### /quick [task description]

Same as normal mode but:
- Skips Research subagent (saves ~3 min, avoids timeout)
- Assumes context is already in main session
- If research was already done, this is always the right flag

### /status

Dump current STATE.md summary to conversation.

### /abort

Archive current STATE.md to `STATE.bak.<timestamp>`, start fresh. Does NOT delete history.

---

## Discuss Phase (optional, recommended)

Before spawning any subagent, spend 1-2 turns clarifying:

1. **Scope** — What is definitely in, what is definitely out?
2. **Constraints** — Tech stack, deadlines, quality bar?
3. **Risks** — What could go wrong, what do we not know?

Output: `discuss_summary` written to STATE.md. Even a 3-sentence summary dramatically improves Research quality.

---

## Research Phase (isolated subagent)

Spawn isolated subagent with:
- task goal + discuss_summary
- directories to investigate
- files to read

Output: `context_snapshot.md` in skill directory.

Key rule: subagent dies after output. Main session never inherits raw research context — only the snapshot.

---

## Plan Phase (isolated subagent)

Based on context_snapshot.md, output `plan.md`:

```markdown
# Plan: <task_name>

## Context
<2-3 sentences on what we're building and why>

## Wave Execution Plan

### Wave 1 (parallel — all independent)
- [ ] **Task A**: do X → verify by running Y
- [ ] **Task B**: do Z → verify by checking W

### Wave 2 (sequential — depends on Wave 1)
- [ ] **Task C**: do W → verify by running Z

## Decided
- Using [X] not [Y] because [reason]
- File structure: [description]

## Blockers
- None / [description]
```

---

## Implement Phase (main session)

### Wave execution:

```
Wave 1: spawn subagent A + subagent B in parallel
         ↓ both complete
Wave 2: spawn subagent C
         ↓ complete
Verify: run tests, syntax checks
```

### After each task:
1. Mark `[x]` in STATE.md
2. Run verification commands
3. If verify fails → document error, fix, re-verify
4. Git commit (if in git repo): `auto-todo: complete <task name>`

### Atomic commit rule:
Never leave implementation uncommitted. If something breaks later, git bisect makes recovery trivial.

---

## Verify Phase

For code tasks: run language-specific verification per task (not just at end).

| Language | Syntax | Test |
|----------|--------|------|
| Python | `python -m py_compile <file>` | `pytest` or manual |
| JS/TS | `tsc --noEmit` / `node --check` | `jest` / `vitest` |
| Go | `go build ./...` | `go test ./...` |
| Bash | `bash -n <script>` | ShellCheck |

If verify fails: document error in STATE.md blockers, fix, re-verify. Do not skip.

---

## Ship Phase

After all waves complete and verify passes:
1. Final git commit if not yet committed
2. Write completion summary to STATE.md
3. Archive STATE.md → `STATE.complete.<timestamp>`
4. Report: what was done, what changed, how to verify

---

## Common Patterns

### "Continue last task"
1. Read STATE.md
2. Detect `current_phase` and `current_step`
3. Resume from there

### "Start new task"
1. Create new STATE.md (archive old if exists)
2. Run discuss phase (30 seconds to 2 minutes)
3. Proceed to research

### "Task failed mid-execution"
1. Log error in STATE.md blockers
2. Do not skip or paper over
3. Fix before marking step complete

---

## Key Files

- `STATE.md` — Persistent task state (source of truth)
- `context_snapshot.md` — Research output (facts only, no speculation)
- `plan.md` — Execution plan with waves
- `references/rpi.md` — Full RPI pattern diagram
- `references/wave_execution.md` — Wave parallelism details
- `scripts/state_manager.py` — STATE.md read/write utilities

---

## Related Skills

- **effective-skills** — Skill design best practices (read before editing this skill)
- **multi-agent** — Parallel subagent orchestration; use in Wave 1 execution
- **skill-creator** — Technical init/package/validate

---

## Verification Is Not Optional

For code tasks, verification is mandatory per step — not deferred to the end. Do not mark `[x]` until verification passes or failure is explicitly documented.
