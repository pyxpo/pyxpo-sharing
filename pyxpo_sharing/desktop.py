"""Desktop backend for `pyxpo run desktop`: shows the files in Finder or Explorer (or copies the message) instead of a share sheet."""
from __future__ import annotations

import subprocess
import sys
from typing import Any, Dict, List


def _path(f: str) -> str:
    """A local path from a path or a file:// URI (file:///C:/x on Windows is C:/x)."""
    if not f.startswith("file://"):
        return f
    p = f[7:]
    if sys.platform == "win32" and len(p) > 2 and p[0] == "/" and p[2] == ":":
        p = p[1:]
    return p


def share(files: List[str], message: str, mime: str, title: str) -> Dict[str, str]:
    paths = [_path(f) for f in files or []]
    if sys.platform == "darwin":
        if paths:
            subprocess.run(["open", "-R"] + paths, check=True)
        elif message:
            subprocess.run(["pbcopy"], input=message.encode(), check=True)
    elif sys.platform == "win32":
        if paths:  # Explorer selects one file per window
            subprocess.run(["explorer", "/select,", paths[0].replace("/", "\\")])
        elif message:
            subprocess.run(["clip"], input=b"\xff\xfe" + message.encode("utf-16-le"), check=True)  # BOM: clip reads UTF-16
    return {"action": "sharedAction"}


def call(method: str, args: List[Any]) -> Any:
    if method == "share":
        return share(*args)
    raise ValueError("unknown Share method %r" % method)
