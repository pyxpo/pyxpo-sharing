# pyxpo-sharing

System share sheet for pyxpo apps (react-native Share shape).

This is an optional [pyxpo](https://github.com/ivishalchaubey/pyxpo) native module. Apps that do not
list it carry none of its code, permissions or dependencies.

## Install

```bash
pip install pyxpo-sharing
```

Then link it into your app in `pyproject.toml`:

```toml
[tool.pyxpo]
modules = ["sharing"]
```

and rebuild (`pyxpo run ios`, `pyxpo build android`, ...). The build copies the module's Swift and Kotlin
sources into the native project and its Python package into the app.

## Use

```python
from pyxpo_sharing import Share

await Share.share({"url": path, "message": "Made with pyxpo"})
```

Permissions and Info.plist keys: none (Android shares through a FileProvider declared in the module manifest).

## What is in the package

- `pyxpo_sharing/__init__.py`: the Python API.
- `pyxpo_sharing/pyxpo-module.json`: autolink metadata (bridge name, Swift and Kotlin classes, Android namespace and dependencies, Info.plist keys).
- `pyxpo_sharing/ios/`: Swift sources compiled into the iOS app.
- `pyxpo_sharing/android/src/main/`: Kotlin sources and the manifest merged into the Android app.
