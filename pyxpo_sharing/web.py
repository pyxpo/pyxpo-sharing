"""Web backend for `pyxpo build web`: the Web Share API (the system share sheet) where the browser has it; otherwise
files download and a message goes to the clipboard."""
from __future__ import annotations

from typing import Any, Dict, List

from pyxpo.renderers.web.browser import download, file_blob


async def share(files: List[str], message: str, mime: str, title: str) -> Dict[str, str]:
    import js  # type: ignore[import-not-found]
    from pyodide.ffi import JsException, to_js  # type: ignore[import-not-found]

    data: Dict[str, Any] = {}
    if files:
        data["files"] = [file_blob(f) for f in files]
    if message:
        data["text"] = message
    if title:
        data["title"] = title
    nav = js.navigator
    payload = to_js(data, dict_converter=js.Object.fromEntries)
    if hasattr(nav, "share") and (not hasattr(nav, "canShare") or nav.canShare(payload)):
        try:
            await nav.share(payload)
            return {"action": "sharedAction"}
        except JsException as e:
            if "AbortError" in str(e):
                return {"action": "dismissedAction"}
            if "NotAllowedError" not in str(e):
                raise
    for f in files or []:
        download(f)
    if message and not files:
        await nav.clipboard.writeText(message)
    return {"action": "sharedAction"}


def call(method: str, args: List[Any]) -> Any:
    if method == "share":
        return share(*args)
    raise ValueError("unknown Share method %r" % method)
