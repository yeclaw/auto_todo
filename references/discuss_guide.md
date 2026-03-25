# Discuss Phase Guide

## Purpose

The discuss phase exists to capture the **irreducible uncertainty** before spending subagent budget on research and planning.

Without discuss: Research makes wrong assumptions → Plan addresses wrong problem → Implement builds wrong thing.

With discuss: 5 minutes of questions → Research knows exactly what to investigate → Plan is actionable.

## When to Skip Discuss

- **Urgent known tasks**: "rm -rf node_modules and reinstall" — no discuss needed
- **Continuation of prior task**: Already discussed, just resuming
- **Quick exploratory**: `/quick` mode skips discuss by default

When in doubt, do discuss. 2 minutes now saves 20 minutes of rework.

## Discuss Protocol

Spend 3-5 minutes answering these three questions:

### 1. Scope — What is in, what is out?

Ask the user to explicitly state:
- What we're building (1 sentence)
- What's definitely NOT part of this task
- What's ambiguous (let the user decide or defer)

### 2. Constraints — What must be true?

- Tech stack (language, framework, library versions)
- Environment (local dev, production, embedded)
- Quality bar (MVP vs polished)
- Deadlines or time constraints

### 3. Risks — What could go wrong?

- What we don't know that we don't know
- External dependencies (APIs, third parties, other teams)
- Edge cases already anticipated vs unknown unknowns

## Output Format

After discuss, write 3-5 sentences to STATE.md:

```markdown
## Discuss Output
discuss_summary: |
  Building a Redis caching layer for the /api/products endpoint.
  MVP only — no cache invalidation strategy yet.
  Tech: Node.js + ioredis, running on existing API server.
  Key risk: cache stampede on cold start.
```

This feeds directly into Research (knows what to investigate) and Plan (knows what's locked).

## Common Discuss Mistakes

### Asking too many questions
> "Should we use Redis or Memcached? If Redis, cluster mode or sentinel? What TTL?..." 

→ User gets decision fatigue. Pick 1-2 most impactful questions.

### Not writing down decisions
> Discussed orally, forgot by the time Plan phase starts.

→ Always write discuss_summary to STATE.md immediately.

### Treating discuss as commitment
> "If I say yes to X, are we locked in?"

→ Discuss is scope-setting, not contracts. Plans can revisit decisions if new information emerges.
