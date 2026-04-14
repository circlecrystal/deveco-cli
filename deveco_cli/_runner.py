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
