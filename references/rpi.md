# RPI Pattern — Full Reference

> **Note:** This RPI pattern is the backbone of auto-todo v2.
> State is persisted in `STATE.md` at the skill root — see SKILL.md for full schema.
> Wave parallelism is optional — use for tasks with 5+ independent sub-tasks.
> See `references/wave_execution.md` for wave execution details.

## Full Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    PHASE 0: DISCUSS (optional)                    │
│  1-2 turns in main session, clarify scope/constraints/risks    │
│  Output: discuss_summary written to STATE.md                    │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                     PHASE 1: RESEARCH                             │
│  sessions_spawn(mode="run", cleanup="keep", isolated=true)       │
│  Output: context_snapshot.md — facts only, no speculation        │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                       PHASE 2: PLAN                               │
│  sessions_spawn(mode="run", cleanup="keep", isolated=true)       │
│  Input: context_snapshot.md                                        │
│  Output: execution_checklist.md — exact steps, files, snippets    │
│                                                                  │
│  ⚠️ Assumptions check first: stop if assumptions are uncertain  │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                  PHASE 3: HUMAN REVIEW (blocking)                 │
│  Human answers 3 gate questions:                                  │
│    [ ] Correct goal?                                              │
│    [ ] Right order?                                               │
│    [ ] Edge cases covered?                                        │
│                                                                  │
│  ✓ All yes → proceed to Phase 4                                  │
│  ✗ Any no → return to Phase 2 with feedback                     │
│  [waved] → proceed without human (document why)                  │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                   PHASE 4: IMPLEMENT (main)                       │
│  Execute in main session per execution_checklist.md               │
│  Deviation rules during execution:                               │
│    R1: Auto-fix bugs (broken behavior, errors)                   │
│    R2: Auto-add missing critical (error handling, auth, validation)│
│    R3: Auto-fix blocking issues (missing deps, broken imports)   │
│    R4: Ask about architectural changes                            │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                    PHASE 5: VERIFY (main)                         │
│  Run verification commands per language table                     │
│  All pass → mark all steps [x] → "🎉 All tasks completed!"       │
│  Any fail → fix before marking done                              │
│  Persistent failure → gap output → new Phase 2 turn              │
└──────────────────────────────────────────────────────────────────┘
```

## Sub-Agent Spawn Syntax

```python
sessions_spawn(
    task="""[detailed task description]""",
    runtime="subagent",
    mode="run",
    cleanup="keep",          # keep output session for debugging
)
```

## Merging Multiple Research Snapshots (Multi-Agent Phase 1)

For large research tasks, spawn multiple agents in parallel:

```python
# Phase 1a: Spawn parallel research agents
agent_1 = sessions_spawn(task="Research X aspect...", runtime="subagent", ...)
agent_2 = sessions_spawn(task="Research Y aspect...", runtime="subagent", ...)
agent_3 = sessions_spawn(task="Research Z aspect...", runtime="subagent", ...)

# Wait for all → merge into single context_snapshot.md
# Then proceed to Phase 2 with the merged snapshot
```

Use the **multi-agent skill** for this pattern.

## Edge Cases

### Plan Rejection (Step 3 → "no")

```
Human: "No, step 5 should come before step 3"
→ Do NOT proceed to Phase 4
→ Spawn new Phase 2 with feedback
→ Receive revised execution_checklist.md
→ Re-enter Step 3 (Human Review)
```

### Sub-Agent Timeout or Crash

- Check if partial output exists (context_snapshot.md or execution_checklist.md)
- If partial and usable → continue with what exists
- If nothing useful → restart the phase

### Human Unavailable (wave the gate)

```markdown
> - [waved] Step 3: Human Review → unavailable, proceeding autonomously
>   Reason: [explain why human review was skipped]
> - [ ] Step 4: Implement...
```

Document the assumption being made. Retroactively validate when human is available.

## Before/After Example

### Task: "Add user authentication to the web app"

**Before RPI (bad):**
```
Step 1: Add auth endpoint
Step 2: Add login form
Step 3: Add auth middleware
→ User: "this isn't what I meant"
→ Wasted 3 turns
```

**After RPI (good):**

```
Phase 1: Research
→ context_snapshot.md:
  - Existing: Express.js, Prisma, React
  - Auth approach: JWT with httpOnly cookies
  - No existing auth middleware

Phase 2: Plan
→ execution_checklist.md:
  1. Add User model fields (passwordHash, salt)
  2. Add /auth/login endpoint (verify: returns JWT)
  3. Add /auth/logout endpoint
  4. Add auth middleware (verify: rejects unauthenticated)
  5. Wire middleware to protected routes (verify: 401 without cookie)

Phase 3: Human Review
→ Human: "Yes to all 3 gate questions"
→ Proceed

Phase 4: Implement (per checklist)
Phase 5: Verify (per command table)
→ 🎉 All tasks completed!
```
