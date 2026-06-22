"""轮询 Vgame 图谱来源，检测变化后自动重建设计仓库中的图谱。"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from vgame_paths import client_graph, config_datas


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "knowledge-graph" / "watchdog-state.json"
DATAS = config_datas()
CLIENT_GRAPH = client_graph()


def file_token(path: Path) -> str:
    if not path.exists():
        return "missing"
    stat = path.stat()
    return f"{stat.st_size}:{stat.st_mtime_ns}"


def tree_token(root: Path, pattern: str) -> str:
    digest = hashlib.sha256()
    if not root.exists():
        return "missing"
    for path in sorted(root.rglob(pattern)):
        if path.is_file():
            digest.update(path.relative_to(root).as_posix().encode("utf-8"))
            digest.update(file_token(path).encode("ascii"))
    return digest.hexdigest()


def snapshot() -> dict[str, str]:
    return {
        "client": file_token(CLIENT_GRAPH),
        "config": tree_token(DATAS, "*.xlsx"),
        "design": hashlib.sha256(
            "|".join(
                tree_token(ROOT / directory, "*.md")
                for directory in ("design", "proposals", "tasks", "plans", "harness")
            ).encode("ascii")
        ).hexdigest(),
    }


def save_state(state: dict[str, str]) -> None:
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def rebuild(changed: list[str]) -> None:
    command = [sys.executable, str(ROOT / "scripts" / "build_vgame_graph.py")]
    if "config" not in changed:
        command.append("--skip-config")
    else:
        command.append("--skip-cs-refs")
    print(f"[{datetime.now():%H:%M:%S}] 触发重建: {', '.join(changed)}")
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Watch Vgame graph sources")
    parser.add_argument("--interval", type=int, default=30, help="检查间隔（秒）")
    parser.add_argument("--once", action="store_true", help="只检查一次")
    args = parser.parse_args()

    previous = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else snapshot()
    save_state(previous)
    print(f"[INFO] Vgame 图谱监控已启动，间隔 {args.interval} 秒。Ctrl+C 停止。")

    while True:
        current = snapshot()
        changed = [name for name, token in current.items() if previous.get(name) != token]
        if changed:
            try:
                rebuild(changed)
                previous = current
                save_state(previous)
            except subprocess.CalledProcessError as exc:
                print(f"[ERROR] 重建失败，保留旧指纹以便下轮重试: {exc}")
        elif args.once:
            print("[INFO] 未检测到变化")
        if args.once:
            return
        time.sleep(max(args.interval, 5))


if __name__ == "__main__":
    main()
