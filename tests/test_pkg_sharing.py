from __future__ import annotations

import asyncio

import pytest

from pyxpo.apis import _bridge
from pyxpo_sharing import Share, Sharing


class FakeApp:
    """Records native calls and answers from `handlers[(module, method)]`."""

    loop = None

    def __init__(self, handlers):
        self.handlers = handlers
        self.calls = []

    def call(self, module, method, *args, reply=False):
        self.calls.append((module, method, args))
        fut = asyncio.get_event_loop().create_future()
        out = self.handlers[(module, method)](*args)
        if isinstance(out, Exception):
            fut.set_exception(out)
        else:
            fut.set_result(out)
        return fut


def run(handlers, coro_fn):
    app = FakeApp(handlers)
    old = _bridge.get_app()
    _bridge.set_app(app)
    try:
        return asyncio.run(coro_fn()), app
    finally:
        _bridge.set_app(old)


def test_share_links_go_into_message_and_sharing_shape():
    h = {("Share", "share"): lambda urls, msg, mime, title: {"action": "sharedAction"}}
    _, app = run(h, lambda: Share.share({"urls": ["/a.jpg", "https://x.dev/p"], "message": "hi"}, {"dialogTitle": "Send"}))
    assert app.calls[0][2] == (["/a.jpg"], "hi\nhttps://x.dev/p", "", "Send")
    _, app = run(h, lambda: Share.share({"url": "https://x.dev"}))
    assert app.calls[0][2] == ([], "https://x.dev", "", "")
    _, app = run(h, lambda: Sharing.shareAsync("/a.pdf", {"mimeType": "application/pdf", "dialogTitle": "T"}))
    assert app.calls[0][2] == (["/a.pdf"], "", "application/pdf", "T")
    with pytest.raises(ValueError):
        run(h, lambda: Sharing.shareAsync("https://x.dev"))


def test_share_rejects_second_sheet_and_resets_after_error():
    async def both():
        first = asyncio.ensure_future(Share.share({"url": "/a"}))
        await asyncio.sleep(0)
        with pytest.raises(RuntimeError, match="already open"):
            await Share.share({"url": "/b"})
        gate.set_result({"action": "dismissedAction"})
        return await first

    gate = None

    class SlowApp(FakeApp):
        def call(self, module, method, *args, reply=False):
            return gate

    async def go():
        nonlocal gate
        gate = asyncio.get_event_loop().create_future()
        return await both()

    old = _bridge.get_app()
    _bridge.set_app(SlowApp({}))
    try:
        assert asyncio.run(go()) == {"action": "dismissedAction"}
    finally:
        _bridge.set_app(old)
    out, _ = run({("Share", "share"): lambda *a: RuntimeError("boom")}, lambda: _boom())
    assert out == "boom"
    out, _ = run({("Share", "share"): lambda *a: {"action": "sharedAction"}}, lambda: Share.share({"url": "/a"}))
    assert out["action"] == "sharedAction"


async def _boom():
    try:
        await Share.share({"url": "/a"})
    except RuntimeError as e:
        return str(e)


def test_share_shape():
    out, app = run({("Share", "share"): lambda urls, msg, mime, title: {"action": "sharedAction"}},
                   lambda: Share.share({"urls": ["/a", "/b"]}))
    assert out == {"action": "sharedAction"} and app.calls[0][2] == (["/a", "/b"], "", "", "")
    with pytest.raises(ValueError):
        run({}, lambda: Share.share({}))
