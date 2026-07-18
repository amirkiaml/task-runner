import json
from pathlib import Path
from datetime import datetime, timezone

DATA_PATH = Path(__file__).resolve().parent / "tasks.json"

def _load_all() -> list:
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def _save_all(tasks: list) -> None:
    with open(DATA_PATH, "w") as f:
        json.dump(tasks, f, indent=2)

def save_task(user_input: str, final_output: str, tools_used: list, trace: list) -> int:
    tasks = _load_all()
    task_id = (tasks[-1]["id"] + 1) if tasks else 1
    tasks.append({
        "id": task_id,
        "user_input": user_input,
        "final_output": final_output,
        "tools_used": tools_used,
        "trace": trace,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    _save_all(tasks)
    return task_id

def list_tasks() -> list:
    return list(reversed(_load_all()))

def clear_all_tasks() -> None:
    _save_all([])