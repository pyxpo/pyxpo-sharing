"""System share sheet: react-native `Share` and expo-sharing shapes. Shares local files, links and an optional message."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pyxpo.module_api import call, require_linked, snake_aliases

__version__ = "0.1.0a1"

_in_flight = False


def _is_link(s: str) -> bool:
    return s.lower().startswith(("http://", "https://"))


async def _share(files: List[str], message: str, mime: str, title: str) -> Dict[str, str]:
    """One share sheet at a time; a second call while one is open raises instead of stacking sheets."""
    global _in_flight
    if _in_flight:
        raise RuntimeError("a share sheet is already open")
    _in_flight = True
    try:
        res = await call("Share", "share", files, message, mime, title, reply=True)
    finally:
        _in_flight = False
    return {"action": (res or {}).get("action", "dismissedAction")}


@snake_aliases
class Share:
    @staticmethod
    async def share(content: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Opens the system share sheet. `content`: `{"url": path_or_link}` or `{"urls": [...]}`, plus optional `message`.
        Local paths are shared as files; http(s) links are appended to the message, the same on both OSes.
        `options`: `{"dialogTitle": str}` (Android chooser title; iOS has none).
        Returns `{"action": "sharedAction" | "dismissedAction"}` (Android always reports sharedAction, as react-native does).
        Android shares files from the app's own cache and files folders."""
        require_linked("Share", "sharing", package="pyxpo-sharing")
        items = [str(u) for u in (content.get("urls") or ([content["url"]] if content.get("url") else []))]
        files = [u for u in items if not _is_link(u)]
        message = "\n".join([m for m in [content.get("message") or ""] + [u for u in items if _is_link(u)] if m])
        if not files and not message:
            raise ValueError("Share.share needs a url, urls or message")
        return await _share(files, message, "", str((options or {}).get("dialogTitle") or ""))


@snake_aliases
class Sharing:
    """expo-sharing shape."""

    @staticmethod
    async def isAvailableAsync() -> bool:
        """True when the share sheet module is linked (both iOS and Android always have a share sheet)."""
        try:
            require_linked("Share", "sharing", package="pyxpo-sharing")
        except Exception:  # noqa: BLE001 - not linked means unavailable, not an error
            return False
        return True

    @staticmethod
    async def shareAsync(url: str, options: Optional[Dict[str, Any]] = None) -> None:
        """Shares one local file. `options`: `mimeType` and `dialogTitle` (Android only; iOS derives both from the file)."""
        require_linked("Share", "sharing", package="pyxpo-sharing")
        if not url or _is_link(str(url)):
            raise ValueError("Sharing.shareAsync needs a local file path; use Share.share for links")
        o = options or {}
        await _share([str(url)], "", str(o.get("mimeType") or ""), str(o.get("dialogTitle") or ""))
