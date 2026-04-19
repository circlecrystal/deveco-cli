from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from .._config import get_config
from .._runner import ensure_device, run_cmd
from .._output import progress


def perform_ui_action(
    project: Path | str,
    action_type: str,
    device: Optional[str] = None,
    x: Optional[int] = None,
    y: Optional[int] = None,
    text: Optional[str] = None,
    direction: Optional[int] = None,
    velocity: Optional[int] = None,
    step_length: Optional[int] = None,
    key1: Optional[str] = None,
    key2: Optional[str] = None,
    key3: Optional[str] = None,
    save_path: Optional[str] = None,
    local_path: Optional[str] = None,
    display_id: Optional[int] = None,
) -> dict:
    config = get_config(project)
    hdc = str(config.hdc)
    err = ensure_device(hdc, device)
    if err is not None:
        return {**err, "command": "ui-action"}
    hdc_t = [hdc] + (["-t", device] if device else [])

    def _err(msg: str, detail: str = "") -> dict:
        r = {"status": "error", "command": "ui-action",
             "error_type": "action_failed", "message": msg}
        if detail:
            r["detail"] = detail[:2000]
        return r

    if action_type == "click":
        if x is None or y is None:
            return {"status": "error", "command": "ui-action",
                    "error_type": "missing_params", "message": "click 需要 --x 和 --y"}
        r = run_cmd([*hdc_t, "shell", "uitest", "uiInput", "click", str(x), str(y)])
        if not r.ok:
            return _err("click 操作失败", r.stderr)
        return {"status": "ok", "command": "ui-action", "action": "click", "x": x, "y": y}

    elif action_type == "inputText":
        if x is None or y is None or text is None:
            return {"status": "error", "command": "ui-action",
                    "error_type": "missing_params", "message": "inputText 需要 --x, --y, --text"}
        run_cmd([*hdc_t, "shell", "uitest", "uiInput", "click", str(x), str(y)])
        time.sleep(0.3)
        run_cmd([*hdc_t, "shell", "uitest", "uiInput", "keyEvent", "2072", "2017"])
        time.sleep(0.1)
        run_cmd([*hdc_t, "shell", "uitest", "uiInput", "keyEvent", "2071"])
        time.sleep(0.1)
        r = run_cmd([*hdc_t, "shell", "uitest", "uiInput", "inputText", text])
        if not r.ok:
            return _err("inputText 操作失败", r.stderr)
        return {"status": "ok", "command": "ui-action", "action": "inputText", "text": text}

    elif action_type == "directionalFling":
        d = str(direction if direction is not None else 0)
        v = str(velocity if velocity is not None else 600)
        s = str(step_length if step_length is not None else 200)
        r = run_cmd([*hdc_t, "shell", "uitest", "uiInput", "dircFling", d, v, s])
        if not r.ok:
            return _err("directionalFling 操作失败", r.stderr)
        return {"status": "ok", "command": "ui-action", "action": "directionalFling",
                "direction": d, "velocity": v, "step_length": s}

    elif action_type == "keyEvent":
        keys = [k for k in [key1, key2, key3] if k is not None]
        if not keys:
            return {"status": "error", "command": "ui-action",
                    "error_type": "missing_params", "message": "keyEvent 需要 --key1"}
        r = run_cmd([*hdc_t, "shell", "uitest", "uiInput", "keyEvent", *keys])
        if not r.ok:
            return _err("keyEvent 操作失败", r.stderr)
        return {"status": "ok", "command": "ui-action", "action": "keyEvent", "keys": keys}

    elif action_type == "screenshot":
        ts = int(time.time())
        remote = save_path or f"/data/local/tmp/screenshot_{ts}.png"
        local = Path(local_path) if local_path else config.project_path / "screenshot" / f"{ts}.png"
        local.parent.mkdir(parents=True, exist_ok=True)

        cmd = [*hdc_t, "shell", "snapshot_display", "-f", remote]
        if display_id is not None:
            cmd += ["-id", str(display_id)]

        progress("截图中...")
        r = run_cmd(cmd)
        if not r.ok:
            return _err("截图失败", r.stderr)

        recv = run_cmd([*hdc_t, "file", "recv", remote, str(local)])
        if not recv.ok:
            return _err("截图传输失败", recv.stderr)

        return {"status": "ok", "command": "ui-action", "action": "screenshot",
                "file": str(local), "message": f"截图已保存到 {local}"}

    else:
        return {"status": "error", "command": "ui-action",
                "error_type": "unknown_action",
                "message": f"未知操作类型: {action_type}。"
                           "支持: click, inputText, directionalFling, keyEvent, screenshot"}
