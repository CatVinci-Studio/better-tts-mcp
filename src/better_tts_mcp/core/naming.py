"""Naming helpers for audio output files."""

import os
import re
from datetime import datetime


def sanitize_filename(text: str, max_len: int = 20) -> str:
    """Convert arbitrary text into a filesystem-safe filename fragment.

    Args:
        text: Raw input text to derive a filename from.
        max_len: Maximum length of the sanitized fragment.

    Returns:
        Sanitized filename fragment. Falls back to ``audio`` when empty.
    """
    safe = re.sub(r"[^\w\s\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]", "", text)
    safe = safe.strip().replace(" ", "_")
    if len(safe) > max_len:
        safe = safe[:max_len]
    return safe or "audio"


def make_output_path(text: str, output_dir: str, suffix: str) -> str:
    """Generate a timestamped output path and ensure the target directory exists.

    Args:
        text: Source text used to derive a readable filename fragment.
        output_dir: Directory where output files should be stored.
        suffix: File extension, including the leading dot (for example ``.mp3``).

    Returns:
        Relative path to a new output file under ``output_dir``.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fragment = sanitize_filename(text)
    filename = f"{timestamp}_{fragment}{suffix}"
    return os.path.join(output_dir, filename)
