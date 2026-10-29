# pyxpo-sharing

The system share sheet for [pyxpo](https://github.com/pyxpo/pyxpo) apps, written in Python: send a link, a message or a
file to Messages, Mail, Drive, Quick Share and every other app on the phone. It offers the react-native `Share` shape
and the expo-sharing `Sharing` shape.

<p align="center">
  <img src="https://raw.githubusercontent.com/pyxpo/pyxpo-sharing/main/docs/images/hero.png" width="820" alt="The sharing module on Android and iOS: the system share sheet open with a message and a link">
</p>

```python
from pyxpo_sharing import Share

result = await Share.share({"message": "Made with pyxpo", "url": "https://github.com/pyxpo/pyxpo"})
```

## Features

- **One call** opens the native sheet: the Android chooser or the iOS activity sheet.
- **Links, messages and files:** a link is added to the message, a local path is shared as a file.
- **Several items at once** with `urls`.
- **Safe on Android:** files go through a `FileProvider`, so no `file://` path leaks out. The module declares it for you.
- **No permissions** and no Info.plist keys.
- **Never two sheets:** a second call while a sheet is open raises instead of stacking sheets.
- **Works on the web and desktop:** the Web Share API where the browser has it, otherwise a download or the clipboard.
  On the desktop window it reveals the file in Finder or Explorer.
- **Typed:** ships `py.typed`. Both camelCase and snake_case names work (`Sharing.shareAsync`, `Sharing.share_async`).

## Contents

| If you are... | Start here |
| --- | --- |
| Sharing a link or a message | [Quick start](#quick-start) |
| Sharing a photo or a PDF you made | [Sharing files](#sharing-files) |
| Following expo-sharing | [`Sharing`](#sharing-expo-sharing-shape) |
| Wondering what you get back | [Result](#result) |
| Targeting the web or a desktop window | [Web and desktop](#web-and-desktop) |
| Looking for exact signatures | [API reference](#api-reference) · [Errors](#errors) |
| Seeing it in a real app | [Recipe: share a drawing](#recipe-share-a-drawing) |
| Stuck | [Testing](#testing) · [Troubleshooting](#troubleshooting) · [FAQ](#faq) |

## Platform support

| Target | What works |
| --- | --- |
| Android, API 24+ | The system chooser. Files must be in the app's own cache or files folder (shared through a `FileProvider`). `dialogTitle` sets the chooser title. |
| iOS 15+ | The system activity sheet. It has no title option. |
| Web page (`pyxpo build web`) | The Web Share API where available (most phone browsers). Otherwise files are downloaded and a message goes to the clipboard. |
| Desktop window | Reveals the files in Finder or Explorer, or copies the message to the clipboard. There is no share sheet. |

Requires Python 3.9+ and `pyxpo>=0.1.0a1`.

## Install

```sh
pip install pyxpo-sharing
```

```toml
[tool.pyxpo]
modules = ["sharing"]
```

Rebuild the app after adding the module (`pyxpo run android` or `pyxpo run ios`). There are no permissions, no prompts
and no module options. On Android the build merges a `FileProvider` into your manifest.

## Quick start

```python
from pyxpo import Button, Text, View, component, use_async, use_state
from pyxpo_sharing import Share


@component
def ShareApp():
    taps, set_taps = use_state(0)
    last, set_last = use_state("")

    async def share():
        if taps == 0:
            return
        result = await Share.share(
            {"message": "Made with pyxpo", "url": "https://github.com/pyxpo/pyxpo"},
            {"dialogTitle": "Share pyxpo"},
        )
        set_last(result["action"])

    use_async(share, [taps])
    return View(Text(last or "Not shared yet"), Button("Share a link", lambda: set_taps(taps + 1)))
```

> **Tip:** a handler such as `lambda: Share.share(...)` creates a coroutine that nobody awaits, so nothing opens. Start
> async work from `use_async` with a counter in state, as above.

<p align="center">
  <img src="https://raw.githubusercontent.com/pyxpo/pyxpo-sharing/main/docs/images/sheet.png" width="720" alt="The share sheet on Android and iOS">
</p>

## Sharing text and links

```python
await Share.share({"message": "Look at this"})
await Share.share({"url": "https://example.com"})
await Share.share({"message": "Look", "url": "https://example.com"})   # the link follows the message
```

| `content` key | Meaning |
| --- | --- |
| `message` | Text to share. |
| `url` | One local path or one `http(s)` link. |
| `urls` | A list of paths and links. |

Links (anything starting with `http://` or `https://`) are appended to the message on both systems, so Android and iOS
behave the same. Paths are shared as files. At least one of `message`, `url` or `urls` is needed.

## Sharing files

```python
import os
from pyxpo_sharing import Share

await Share.share({"url": os.path.join(cache_dir, "drawing.png")})
await Share.share({"urls": [path_a, path_b], "message": "Two photos"})
```

On Android, the files must be inside your app's own cache or files folder (for example where `pyxpo-file-system` puts
`Paths.cache` or `Paths.document`). Copy a file there first if it lives elsewhere.

## `Sharing`, expo-sharing shape

```python
from pyxpo_sharing import Sharing

if await Sharing.is_available_async():
    await Sharing.share_async(path, {"mimeType": "image/png", "dialogTitle": "Share drawing"})
```

| Function | Meaning |
| --- | --- |
| `is_available_async()` (`isAvailableAsync`) | `True` when the module is linked. Both phones always have a share sheet. |
| `share_async(url, options=None)` (`shareAsync`) | Shares one local file. `options`: `mimeType` and `dialogTitle`, Android only (iOS reads both from the file). A link or an empty path raises `ValueError`. Returns `None`. |

## Result

`Share.share` returns `{"action": "sharedAction" | "dismissedAction"}`.

| Platform | What you can rely on |
| --- | --- |
| iOS | `"dismissedAction"` when the user closes the sheet without choosing. |
| Android | Always `"sharedAction"`, as in react-native, because Android does not report the outcome. |
| Web | `"dismissedAction"` when the user cancels the browser's sheet. |

Do not count shares by this value on Android.

## Errors

| Error | When | What to do |
| --- | --- | --- |
| `ValueError` | `Share.share` with no `url`, `urls` or `message`, or `Sharing.share_async` with a link or empty path. | Pass something to share. Use `Share.share` for links. |
| `RuntimeError("a share sheet is already open")` | A second share while one is open. | Ignore the second tap, or disable the button until the first call returns. |
| `ModuleNotLinkedError` (from `pyxpo.module_api`) | Built without `"sharing"` in `modules`. | Add it and rebuild. |

## Config

There are no module options and no config plugin. The module adds only a `FileProvider` on Android.

## Web and desktop

| Environment | Behavior |
| --- | --- |
| Web with the Web Share API | The browser's own sheet opens. Files go through `navigator.share`. A cancel returns `"dismissedAction"`. |
| Web without it (many desktop browsers) | Files download. A message with no file is copied to the clipboard. The result is `"sharedAction"`. |
| Desktop window, macOS | Files are revealed in Finder. A message is copied with `pbcopy`. |
| Desktop window, Windows | The first file is selected in Explorer. A message is copied to the clipboard. |

Browsers need a user gesture (a tap) to open a share sheet, so call `Share.share` from a button press.

## Recipe: share a drawing

Draw, export, and share the PNG from one button.

```python
from pyxpo import Button, View, component, use_async, use_state
from pyxpo_sharing import Sharing


@component
def Export(path: str):
    taps, set_taps = use_state(0)
    busy, set_busy = use_state(False)

    async def send():
        if taps == 0 or busy:
            return
        set_busy(True)
        try:
            if await Sharing.is_available_async():
                await Sharing.share_async(path, {"mimeType": "image/png", "dialogTitle": "Share drawing"})
        finally:
            set_busy(False)

    use_async(send, [taps])
    return View(Button("Share", lambda: set_taps(taps + 1), disabled=busy))
```

`path` is a PNG in your app's cache folder.

## Production checklist

- [ ] Share files only from the app's cache or files folder.
- [ ] The share button is disabled while a sheet is open.
- [ ] You do not rely on `"sharedAction"` to count shares on Android.
- [ ] A message always makes sense without the link, and with it.
- [ ] You tested on a real phone with Messages, Mail and a file app.
- [ ] On the web, `Share.share` runs from a tap.

## Testing

Unit tests run on the desktop host. Replace the native call and check what you sent:

```python
import asyncio

import pyxpo_sharing as S


def test_link_goes_into_message(monkeypatch):
    seen = []

    async def fake_call(*args, **kwargs):
        seen.append(args)
        return {"action": "sharedAction"}

    monkeypatch.setattr(S, "call", fake_call)
    monkeypatch.setattr(S, "require_linked", lambda *a, **k: None)

    res = asyncio.run(S.Share.share({"message": "Hi", "url": "https://example.com"}))
    assert res == {"action": "sharedAction"}
    assert seen[0][2:4] == ([], "Hi\nhttps://example.com")
```

## Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| Nothing happens on tap | The coroutine was never awaited. Start it from `use_async`. |
| Android: the share fails for a file | The file is outside the app's cache or files folder. Copy it in first. |
| `ValueError: Share.share needs a url, urls or message` | An empty content dict. |
| `a share sheet is already open` | A double tap. Disable the button while it runs. |
| iOS: no title in the sheet | iOS has no title option. `dialogTitle` is Android only. |
| Browser downloads instead of sharing | The browser has no Web Share API for that content. This is the fallback. |
| `ModuleNotLinkedError` | Add `"sharing"` to `modules` and rebuild. |

## FAQ

**Can I choose which app opens?** No. The user chooses from the system sheet.

**Can I share an image from memory?** Write it to a file in your cache folder, then share the path.

**Does it need a permission?** No.

**Why is the Android result always `sharedAction`?** Android does not tell the app what the user did. This matches
react-native.

**Can I share to a specific friend?** No. Use the app's own API for that.

## API reference

### `Share`

| Function | Returns |
| --- | --- |
| `Share.share(content, options=None)` | `{"action": "sharedAction" or "dismissedAction"}`. `content`: `message`, `url`, `urls`. `options`: `dialogTitle`. |

### `Sharing`

| Function | Returns |
| --- | --- |
| `Sharing.is_available_async()` (`isAvailableAsync`) | `bool` |
| `Sharing.share_async(url, options=None)` (`shareAsync`) | `None`. `options`: `mimeType`, `dialogTitle`. |

## License

MIT
