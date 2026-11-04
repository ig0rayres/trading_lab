import json
from datetime import datetime
from pathlib import Path

p = Path("/media/igor/windows_part/Cursor/trading lab/.cursorsession")
data = json.loads(p.read_text())
now = datetime.now().astimezone().isoformat(timespec="seconds")
for t in data.get("sprint_tasks", []):
    if t["id"] in ("N9.1", "N9.2", "N9.3", "N9.4", "N9.5"):
        t["status"] = "done"
    elif t["id"] == "N9.6":
        t["status"] = "todo"
front = data.get("front") or {}
front.update(
    {
        "slug": "n9-easypanel-homolog",
        "worktree": "/media/igor/windows_part/Cursor/trading lab",
        "branch": "front/n9-easypanel-homolog",
    }
)
data["front"] = front
cp = data.setdefault("checkpoint", {})
cp.update(
    {
        "last_completed_task": "N9.5",
        "current_task": "N9.6",
        "timestamp": now,
    }
)
data["proximos_passos"] = [
    "Operador: runbook HOMOLOGATION itens 3–7 no EasyPanel",
    "Preencher TEST-EVIDENCE tabela N9",
    "/qa validar N9 → PR → merge",
]
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
