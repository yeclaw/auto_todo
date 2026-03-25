#!/usr/bin/env python3
"""
STATE.md read/write utilities for auto-todo skill.
Usage:
  python3 state_manager.py read              # print current STATE.md
  python3 state_manager.py init <task_name>  # create new STATE.md
  python3 state_manager.py set_phase <phase>  # update current_phase
  python3 state_manager.py add_step <step>   # mark step complete
  python3 state_manager.py add_blocker <text> # add blocker
  python3 state_manager.py add_decision <key>:<val> # record decision
  python3 state_manager.py current_step       # print first incomplete step
  python3 state_manager.py next             # print next action recommendation
  python3 state_manager.py archive           # archive to STATE.bak
"""

import os
import sys
import json
import re
import datetime

STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "STATE.md")
STATE_BACKUP = os.path.join(os.path.dirname(__file__), "..", "STATE.bak")

def read_state():
    """Read and parse STATE.md into a dict."""
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE) as f:
        content = f.read()
    return parse_state_content(content)

def parse_state_content(content):
    """Parse STATE.md content into a structured dict."""
    state = {
        "task_id": None,
        "task_name": None,
        "created": None,
        "last_updated": None,
        "goal": None,
        "current_phase": None,
        "current_step": None,
        "current_wave": None,
        "completed_steps": [],
        "discuss_summary": None,
        "blockers": [],
        "decisions": {},
        "waves": {},
        "raw": content,
    }

    # Parse completed steps
    step_matches = re.findall(r'- \[x\]\s*(.+?)\s*@(.+?)(?:\n|$)', content)
    state["completed_steps"] = [(s.strip(), t.strip()) for s, t in step_matches]

    # Parse blockers
    blocker_matches = re.findall(r'-\s*(.+?)\s*@(.+?)(?:\n|$)', content)
    for b, t in blocker_matches:
        b = b.strip()
        if b and not b.startswith('[') and not b.startswith('•'):
            if b not in [s for s,_ in state["completed_steps"]]:
                state["blockers"].append((b, t.strip()))

    # Parse decisions
    decision_matches = re.findall(r'-\s*(.+?):\s*(.+?)\s*@', content)
    for k, v in decision_matches:
        state["decisions"][k.strip()] = v.strip()

    # Parse waves
    wave_sections = re.findall(r'(## Wave \d+)', content)
    state["waves"]["sections"] = wave_sections

    # Simple field extraction
    field_map = {
        "task_id": r'task_id:\s*(.+)',
        "task_name": r'task_name:\s*(.+)',
        "created": r'created:\s*(.+)',
        "last_updated": r'last_updated:\s*(.+)',
        "goal": r'## Goal\s*\n(.+?)(?=\n##|\Z)',
        "current_phase": r'current_phase:\s*(.+)',
        "current_step": r'current_step:\s*(.+)',
        "current_wave": r'current_wave:\s*(.+)',
        "discuss_summary": r'discuss_summary:\s*\|\s*\n(.+?)(?=\n##|\Z)',
    }
    for key, pattern in field_map.items():
        m = re.search(pattern, content, re.DOTALL)
        if m:
            val = m.group(1).strip()
            if key in ("task_id", "task_name", "current_phase", "current_step", "current_wave"):
                state[key] = val
            else:
                state[key] = val

    return state

def write_state(state):
    """Write state dict back to STATE.md."""
    now = datetime.datetime.now().isoformat()
    if state.get("last_updated"):
        state["last_updated"] = now

    lines = [
        "# STATE.md",
        "",
        "## Task",
        f"task_id: {state.get('task_id') or 'unset'}",
        f"task_name: {state.get('task_name') or 'unset'}",
        f"created: {state.get('created') or now}",
        f"last_updated: {now}",
        "",
        "## Goal",
        state.get('goal') or '_no goal set_',
        "",
        "## Phase",
        f"current_phase: {state.get('current_phase') or 'discuss'}",
        f"current_step: {state.get('current_step') or 'unset'}",
        f"current_wave: {state.get('current_wave') or '1'}",
        "",
        "## Progress",
        "completed_steps:",
    ]

    for step, ts in state.get("completed_steps", []):
        lines.append(f"  - [x] {step} @ {ts}")

    lines.append("")
    waves = state.get("waves", {})
    if waves:
        lines.append("## Waves")
        for wave_num in sorted(waves.keys(), key=lambda x: (isinstance(x, str), x)):
            items = waves[wave_num]
            lines.append(f"wave_{wave_num}:")
            for item in items:
                lines.append(f"  - [ ] {item}")

    if state.get("blockers"):
        lines.extend(["", "## Blockers"])
        for blocker, ts in state["blockers"]:
            lines.append(f"- {blocker} @ {ts}")

    if state.get("decisions"):
        lines.extend(["", "## Decisions"])
        for k, v in state["decisions"].items():
            lines.append(f"- {k}: {v} @ {now}")

    if state.get("discuss_summary"):
        lines.extend(["", "## Discuss Output", "discuss_summary: |", state["discuss_summary"]])

    with open(STATE_FILE, "w") as f:
        f.write("\n".join(lines))

def cmd_read():
    state = read_state()
    if not state:
        print("No STATE.md found. Run 'init <task_name>' first.")
        return
    print(state.get("raw") or "STATE.md is empty. Run 'init <task_name>' first.")

def cmd_init(task_name):
    import uuid
    state = {
        "task_id": str(uuid.uuid4())[:8],
        "task_name": task_name,
        "created": datetime.datetime.now().isoformat(),
        "last_updated": datetime.datetime.now().isoformat(),
        "goal": "_not yet discussed_",
        "current_phase": "discuss",
        "current_step": "run discuss phase",
        "current_wave": "1",
        "completed_steps": [],
        "discuss_summary": None,
        "blockers": [],
        "decisions": {},
        "waves": {},
    }
    write_state(state)
    print(f"STATE.md created for task: {task_name} (id: {state['task_id']})")

def cmd_set_phase(phase):
    state = read_state()
    if not state:
        print("No STATE.md found.")
        return
    state["current_phase"] = phase
    write_state(state)
    print(f"Phase set to: {phase}")

def cmd_add_step(step):
    state = read_state()
    if not state:
        print("No STATE.md found.")
        return
    ts = datetime.datetime.now().isoformat()
    state["completed_steps"].append((step, ts))
    state["current_step"] = "_unknown_"
    write_state(state)
    print(f"Step marked complete: {step}")

def cmd_add_blocker(text):
    state = read_state()
    if not state:
        print("No STATE.md found.")
        return
    ts = datetime.datetime.now().isoformat()
    state["blockers"].append((text, ts))
    write_state(state)
    print(f"Blocker added: {text}")

def cmd_add_decision(decision_str):
    if ':' not in decision_str:
        print("Format: key:value")
        return
    key, val = decision_str.split(':', 1)
    state = read_state()
    if not state:
        print("No STATE.md found.")
        return
    state["decisions"][key.strip()] = val.strip()
    write_state(state)
    print(f"Decision recorded: {key.strip()}: {val.strip()}")

def cmd_current_step():
    state = read_state()
    if not state:
        print("No active task. STATE.md not found.")
        return
    print(f"Phase: {state.get('current_phase')}")
    print(f"Step: {state.get('current_step')}")
    print(f"Wave: {state.get('current_wave')}")
    if state.get("completed_steps"):
        print(f"Completed: {len(state['completed_steps'])} steps")
    if state.get("blockers"):
        print(f"Blockers: {len(state['blockers'])}")

def cmd_next():
    state = read_state()
    if not state:
        print("No active task.")
        return
    phase = state.get("current_phase")
    step = state.get("current_step")
    blockers = state.get("blockers", [])

    if blockers:
        print(f"⚠️ BLOCKER: {blockers[-1][0]}")
        print("Resolve this before proceeding.")
        return

    if phase == "complete":
        print("✅ Task is complete. No next step.")
        return

    print(f"Current: Phase={phase}, Step={step}, Wave={state.get('current_wave')}")
    print()
    print(f"Next action: {step or phase}")
    print(f"Reason: {phase} phase is active, {step or 'step not set'}")

    # Show completed steps
    completed = state.get("completed_steps", [])
    if completed:
        print(f"\nAlready done ({len(completed)}):")
        for s, t in completed[-3:]:
            print(f"  ✓ {s}")

def cmd_archive():
    if not os.path.exists(STATE_FILE):
        print("No STATE.md to archive.")
        return
    ts = datetime.datetime.now().isoformat().replace(":", "-")
    backup = os.path.join(os.path.dirname(STATE_FILE), f"STATE.bak.{ts}")
    import shutil
    shutil.copy(STATE_FILE, backup)
    os.remove(STATE_FILE)
    print(f"Archived to: {os.path.basename(backup)}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "read":
        cmd_read()
    elif cmd == "init" and len(sys.argv) >= 3:
        cmd_init(" ".join(sys.argv[2:]))
    elif cmd == "set_phase" and len(sys.argv) >= 3:
        cmd_set_phase(sys.argv[2])
    elif cmd == "add_step" and len(sys.argv) >= 3:
        cmd_add_step(" ".join(sys.argv[2:]))
    elif cmd == "add_blocker" and len(sys.argv) >= 3:
        cmd_add_blocker(" ".join(sys.argv[2:]))
    elif cmd == "add_decision" and len(sys.argv) >= 3:
        cmd_add_decision(sys.argv[2])
    elif cmd == "current_step":
        cmd_current_step()
    elif cmd == "next":
        cmd_next()
    elif cmd == "archive":
        cmd_archive()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == "__main__":
    main()
