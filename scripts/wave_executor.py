#!/usr/bin/env python3
"""
Wave-based parallel execution orchestrator for auto-todo.
Reads plan.md from stdin (or file), identifies waves, spawns subagents.

Usage:
  python3 wave_executor.py --plan plan.md
  python3 wave_executor.py --interactive
"""

import json
import re
import sys
import os

def parse_plan_waves(plan_content):
    """Extract wave structure from plan.md."""
    waves = []
    current_wave = None
    wave_num = 0

    for line in plan_content.split('\n'):
        # Detect new wave
        wave_m = re.match(r'#{2,3}\s*Wave\s+(\d+)(?:\s*\(parallel\))?', line)
        if wave_m:
            wave_num = int(wave_m.group(1))
            waves.append({
                "wave": wave_num,
                "parallel": "parallel" in line.lower(),
                "tasks": []
            })
            continue

        # Detect task lines: - [ ] **Task Name**:
        task_m = re.match(r'- \[ \]\s+\*\*(.+?)\*\*:', line)
        if task_m and waves:
            task_name = task_m.group(1).strip()
            waves[-1]["tasks"].append({
                "name": task_name,
                "done": False,
                "output": None
            })

    return waves

def format_waves_summary(waves):
    """Format wave structure for display."""
    lines = []
    for w in waves:
        parallel_tag = "parallel" if w["parallel"] else "sequential"
        lines.append(f"Wave {w['wave']} ({parallel_tag}):")
        for t in w["tasks"]:
            lines.append(f"  - {t['name']}")
        lines.append("")
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--plan":
        plan_path = sys.argv[2]
        with open(plan_path) as f:
            content = f.read()
        waves = parse_plan_waves(content)
        print(format_waves_summary(waves))
        print(f"Total waves: {len(waves)}")
        total_tasks = sum(len(w["tasks"]) for w in waves)
        print(f"Total tasks: {total_tasks}")
        print("\nIn Wave 1 (parallel):")
        if waves:
            for t in waves[0]["tasks"]:
                print(f"  → {t['name']}")
    else:
        print(__doc__)
        print("\nExample plan structure:")
        print("""## Wave 1 (parallel)
- [ ] **Task A**: do X → verify by running Y
- [ ] **Task B**: do Z → verify by checking W

## Wave 2 (sequential)
- [ ] **Task C**: do W → verify by running Z
""")
