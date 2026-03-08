"""Parsers used by synthesis tools."""

import re


def parse_multi_voice_text(text: str, default_voice: str) -> list[tuple[str, str]]:
    """Parse multi-voice text using ``[voice]text`` markers.

    Args:
        text: Raw input, for example
            ``[zh-CN-XiaoxiaoNeural]你好[en-US-AriaNeural]Hello``.
        default_voice: Voice used when no marker exists in the input.

    Returns:
        Ordered ``(voice, segment_text)`` pairs. When no markers are found,
        returns a single pair using ``default_voice`` and the full input text.
    """
    pattern = r"\[([^\]]+)\]([^[]+)"
    matches = re.findall(pattern, text)
    if not matches:
        return [(default_voice, text)]
    return matches
