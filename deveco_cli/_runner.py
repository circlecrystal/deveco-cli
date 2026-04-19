from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CmdResult:
    returncode: int
    stdout: str
    stderr: str
    command: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def run_cmd(
    args: list[str | Path],
    cwd: Path | None = None,
    env_extra: dict[str, str] | None = None,
    timeout: int = 600,
) -> CmdResult:
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)

    str_args = [str(a) for a in args]
    result = subprocess.run(
        str_args,
        cwd=str(cwd) if cwd else None,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return CmdResult(
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
        command=" ".join(str_args),
    )


# hdc 的设计缺陷：无设备时 `hdc shell ...` 返回 exit 0，错误只出现在 stdout/stderr
# 里（`[Fail]ExecuteCommand need connect-key? please confirm a device by help info`）。
# 所有依赖 hdc shell 的命令在入口处先调这个函数做 gate，若无设备直接返回统一错误 dict。
_NO_DEVICE_MARKERS = (
    "need connect-key",
    "[Empty]",
)


def ensure_device(hdc: Path | str, device: str | None = None) -> dict | None:
    """若无设备返回 {"status":"error", "error_type":"no_device", ...}，否则返回 None。
    调用方应在命令开头: `err = ensure_device(hdc, device); if err: return err`。"""
    r = run_cmd([str(hdc), "list", "targets"], timeout=10)
    if not r.ok:
        return {
            "status": "error",
            "error_type": "hdc_list_failed",
            "message": (r.stderr or r.stdout).strip(),
        }
    lines = [t.strip() for t in r.stdout.strip().split("\n") if t.strip()]
    targets = [t for t in lines if t != "[Empty]"]
    if not targets:
        return {
            "status": "error",
            "error_type": "no_device",
            "message": "未发现已连接的设备，请连接真机或启动模拟器",
        }
    if device and device not in targets:
        return {
            "status": "error",
            "error_type": "device_not_found",
            "message": f"指定的设备 {device!r} 不在 hdc list targets 中：{targets}",
        }
    return None


def is_hdc_no_device_output(text: str) -> bool:
    """检查 stdout/stderr 里是否包含无设备信号（用于 shell 命令事后补检）。"""
    if not text:
        return False
    return any(m in text for m in _NO_DEVICE_MARKERS)
