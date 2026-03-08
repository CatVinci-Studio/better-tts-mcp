"""Voice discovery tools."""

from typing import Annotated
from typing import Any

import edge_tts

from mcp.types import CallToolResult

from ..core.results import VoiceInfo, VoicesResult, to_call_tool_result


async def list_voices(
    language: str | None = None,
    gender: str | None = None,
) -> Annotated[CallToolResult, VoicesResult]:
    """List available Edge TTS voices.

    Args:
        language: Filter by language code prefix, e.g. "zh", "en", "ja", "fr".
                  Case-insensitive. If omitted, all voices are returned.
        gender: Filter by gender: "Male" or "Female". Case-insensitive.
                If omitted, both genders are returned.

    Returns:
        A formatted list of matching voices with name, gender, and locale.
    """
    voices: list[Any] = await edge_tts.list_voices()

    if language:
        lang_lower = language.lower()
        voices = [v for v in voices if v["Locale"].lower().startswith(lang_lower)]
    if gender:
        gender_lower = gender.lower()
        voices = [v for v in voices if v["Gender"].lower() == gender_lower]

    if not voices:
        payload = VoicesResult(
            ok=True,
            message="No voices found matching the specified filters.",
            voices=[],
        )
        return to_call_tool_result(payload)

    voice_items = [
        VoiceInfo(
            short_name=v["ShortName"],
            gender=v["Gender"],
            locale=v["Locale"],
            friendly_name=v.get("FriendlyName", ""),
        )
        for v in voices
    ]
    lines = [f"Found {len(voice_items)} voice(s):"]
    lines.extend(
        f"  - {v.short_name}  |  {v.gender}  |  {v.locale}  |  {v.friendly_name}"
        for v in voice_items
    )
    payload = VoicesResult(
        ok=True,
        message="\n".join(lines),
        voices=voice_items,
    )
    return to_call_tool_result(payload)
