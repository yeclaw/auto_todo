# Wave Execution Guide

## Concept

Wave execution means: identify which tasks are independent, run them in parallel, then run dependent tasks sequentially.

## When Waves Matter

- **5+ tasks** — waves save significant time
- **Independent sub-tasks** — API + DB + UI are independent if they don't share state
- **Long tasks** — research-heavy tasks benefit most

## How to Identify Waves

Look at dependencies in your plan:

```
Wave 1 (parallel):
  - [ ] Setup database schema
  - [ ] Build auth API endpoint
  - [ ] Create frontend component library

Wave 2 (sequential):
  - [ ] Connect API to DB
  - [ ] Wire frontend to API

Wave 3 (sequential):
  - [ ] End-to-end integration test
```

**Rule of thumb:**
- If task B requires output from task A → B is in a later wave
- If task A and B are completely independent → same wave (parallel)

## Spawning Parallel Subagents

Within a wave, use `sessions_spawn` for each task:

```python
subagent_a = sessions_spawn(
    task="Implement Task A: ...",
    mode="run",
    runTimeoutSeconds=180,
)
subagent_b = sessions_spawn(
    task="Implement Task B: ...",
    mode="run",
    runTimeoutSeconds=180,
)
# Both run simultaneously
# Wait for both to complete
```

## After Wave Completes

1. Verify each task independently
2. Update STATE.md: mark each task complete
3. Check Wave 2 tasks: are their dependencies satisfied?
4. Proceed to next wave

## Anti-Patterns

- **Vertical slices are better than horizontal**: Instead of "all models, then all APIs, then all UIs", prefer "User feature end-to-end, then Product feature end-to-end"
- **Don't over-parallelize**: 2-3 tasks per wave is manageable, 10 is chaos
- **Don't parallelize dependent tasks**: Running B before A finishes guarantees rework
