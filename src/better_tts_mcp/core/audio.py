"""Audio-related helpers built on edge-tts."""

from typing import Any

import edge_tts


def build_communicate(
    text: str,
    voice: str,
    rate: str | None = None,
    volume: str | None = None,
    pitch: str | None = None,
) -> edge_tts.Communicate:
    """Create an ``edge_tts.Communicate`` object with optional prosody settings.

    Args:
        text: Source text to synthesize.
        voice: Edge TTS voice short name, such as ``en-US-AriaNeural``.
        rate: Optional speaking-rate delta, for example ``+10%``.
        volume: Optional volume delta, for example ``-20%``.
        pitch: Optional pitch delta, for example ``+5Hz``.

    Returns:
        Configured communicate instance ready for ``save`` or ``stream``.
    """
    kwargs: dict[str, Any] = {"text": text, "voice": voice}
    if rate is not None:
        kwargs["rate"] = rate
    if volume is not None:
        kwargs["volume"] = volume
    if pitch is not None:
        kwargs["pitch"] = pitch
    return edge_tts.Communicate(**kwargs)
