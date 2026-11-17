from pathlib import Path

try:
    import platformdirs
    _HAS_PLATFORMDIRS = True
except ImportError:
    _HAS_PLATFORMDIRS = False


def get_braidpipe_home() -> Path:
    if _HAS_PLATFORMDIRS:
        # Linux: ~/.config/braidpipe
        # macOS: ~/Library/Application Support/braidpipe
        # Windows: %LOCALAPPDATA%\braidpipe
        path = Path(platformdirs.user_config_dir("braidpipe", ensure_exists=True))
    else:
        path = Path.home() / ".braidpipe"
        path.mkdir(parents=True, exist_ok=True)
    return path


def get_braids_dir() -> Path:
    p = Path.home() / "braids"
    p.mkdir(parents=True, exist_ok=True)
    return p
