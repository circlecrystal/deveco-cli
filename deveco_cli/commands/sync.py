from __future__ import annotations

from pathlib import Path

from .._config import get_config
from .._runner import run_cmd
from .._output import progress

_SYNC_FLAGS = ["--sync", "--analyze=normal", "--parallel", "--incremental", "--no-daemon"]


def project_sync(
    project: Path | str,
    product: str = "default",
    skip_ohpm: bool = False,
    log_path: Path | None = None,
) -> dict:
    config = get_config(project)

    if not skip_ohpm:
        progress("执行 ohpm install...")
        ohpm = run_cmd(
            [config.ohpm, "install", "--all",
             "--registry", "https://ohpm.openharmony.cn/ohpm/",
             "--strict_ssl", "true"],
            cwd=config.project_path,
        )
        if not ohpm.ok:
            return {
                "status": "error", "command": "sync",
                "error_type": "ohpm_failed",
                "message": f"ohpm install 失败（退出码 {ohpm.returncode}）",
                "detail": (ohpm.stderr or ohpm.stdout)[:2000],
            }

    progress("执行 hvigorw --sync...")
    sync = run_cmd(
        [config.node, config.hvigorw_js] + _SYNC_FLAGS + ["-p", f"product={product}"],
        cwd=config.project_path,
        env_extra={"DEVECO_SDK_HOME": str(config.sdk_home)},
        timeout=300,
    )

    if log_path:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        Path(log_path).write_text(sync.stdout + "\n" + sync.stderr)

    if not sync.ok:
        return {
            "status": "error", "command": "sync",
            "error_type": "sync_failed",
            "message": f"hvigorw --sync 失败（退出码 {sync.returncode}）",
            "detail": (sync.stderr or sync.stdout)[:2000],
        }

    return {"status": "ok", "command": "sync", "message": "项目同步成功"}
