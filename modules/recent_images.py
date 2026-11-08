import json
import os
from typing import Any, Dict, List, Optional

RECENT_IMAGES_PATH = os.path.join(os.getcwd(), "recent_images.json")


def _normalize_path(path: str) -> str:
    if not path:
        return ""
    return os.path.abspath(os.path.expanduser(str(path).strip()))


def _read_state(path: Optional[str] = None) -> Dict[str, List[str]]:
    file_path = path or RECENT_IMAGES_PATH
    state: Dict[str, List[str]] = {"source": [], "background": []}
    try:
        if not os.path.exists(file_path):
            return state
        with open(file_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict):
            return state
        for key in ("source", "background"):
            items = payload.get(key, [])
            if isinstance(items, list):
                state[key] = [
                    _normalize_path(item)
                    for item in items
                    if isinstance(item, str) and _normalize_path(item)
                ]
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return state
    return state


def _write_state(state: Dict[str, List[str]], path: Optional[str] = None) -> None:
    file_path = path or RECENT_IMAGES_PATH
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2)


def get_recent_images(kind: str, limit: int = 8, path: Optional[str] = None) -> List[str]:
    kind_name = str(kind).strip().lower()
    if kind_name not in {"source", "background"}:
        return []
    state = _read_state(path)
    items = state.get(kind_name, [])
    unique: List[str] = []
    seen = set()
    for item in items:
        if not item or item in seen:
            continue
        unique.append(item)
        seen.add(item)
    return unique[:limit]


def record_recent_image(kind: str, image_path: str, limit: int = 8, path: Optional[str] = None) -> List[str]:
    kind_name = str(kind).strip().lower()
    normalized = _normalize_path(image_path)
    if kind_name not in {"source", "background"} or not normalized:
        return []

    state = _read_state(path)
    entries = state.setdefault(kind_name, [])
    filtered = [item for item in entries if item and item != normalized]
    filtered.insert(0, normalized)
    state[kind_name] = filtered[:limit]
    _write_state(state, path)
    return state[kind_name]
