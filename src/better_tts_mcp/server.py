"""
better-tts-mcp: A feature-rich MCP server for Microsoft Edge Text-to-Speech.

Provides tools for:
- Listing available voices (with language/gender filtering)
- Text-to-speech synthesis (MP3 output)
- Text-to-speech with subtitle generation (MP3 + SRT)
- Batch text-to-speech synthesis
"""

import os
import re
from datetime import datetime

import edge_tts
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "better-tts-mcp",
    instructions=(
        "A text-to-speech MCP server powered by Microsoft Edge TTS. "
        "Use `list_voices` to discover available voices, then use "
        "`text_to_speech` or `text_to_speech_with_subtitles` to synthesize speech. "
        "Use `batch_text_to_speech` for multiple texts at once."
    ),
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sanitize_filename(text: str, max_len: int = 20) -> str:
    """Create a safe filename fragment from text."""
    # Keep only alphanumeric, CJK characters, and spaces
    safe = re.sub(r"[^\w\s\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]", "", text)
    safe = safe.strip().replace(" ", "_")
    if len(safe) > max_len:
        safe = safe[:max_len]
    return safe or "audio"


def _make_output_path(text: str, output_dir: str, suffix: str) -> str:
    """Generate a unique output file path."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fragment = _sanitize_filename(text)
    filename = f"{timestamp}_{fragment}{suffix}"
    return os.path.join(output_dir, filename)


def _build_communicate(
    text: str,
    voice: str,
    rate: str | None = None,
    volume: str | None = None,
    pitch: str | None = None,
) -> edge_tts.Communicate:
    """Build an edge_tts.Communicate instance with optional parameters."""
    kwargs: dict = {"text": text, "voice": voice}
    if rate is not None:
        kwargs["rate"] = rate
    if volume is not None:
        kwargs["volume"] = volume
    if pitch is not None:
        kwargs["pitch"] = pitch
    return edge_tts.Communicate(**kwargs)


# ---------------------------------------------------------------------------
# Tool: list_voices
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_voices(
    language: str | None = None,
    gender: str | None = None,
) -> str:
    """List available Edge TTS voices.

    Args:
        language: Filter by language code prefix, e.g. "zh", "en", "ja", "fr".
                  Case-insensitive. If omitted, all voices are returned.
        gender: Filter by gender: "Male" or "Female". Case-insensitive.
                If omitted, both genders are returned.

    Returns:
        A formatted list of matching voices with name, gender, and locale.
    """
    voices = await edge_tts.list_voices()

    # Apply filters
    if language:
        lang_lower = language.lower()
        voices = [v for v in voices if v["Locale"].lower().startswith(lang_lower)]
    if gender:
        gender_lower = gender.lower()
        voices = [v for v in voices if v["Gender"].lower() == gender_lower]

    if not voices:
        return "No voices found matching the specified filters."

    # Format output
    lines = [f"Found {len(voices)} voice(s):\n"]
    for v in voices:
        lines.append(
            f"  - {v['ShortName']}"
            f"  |  {v['Gender']}"
            f"  |  {v['Locale']}"
            f"  |  {v.get('FriendlyName', '')}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool: text_to_speech
# ---------------------------------------------------------------------------


@mcp.tool()
async def text_to_speech(
    text: str,
    voice: str = "zh-CN-XiaoxiaoNeural",
    rate: str | None = None,
    volume: str | None = None,
    pitch: str | None = None,
    output_dir: str = ".",
) -> str:
    """Convert text to speech and save as an MP3 file.

    Args:
        text: The text to convert to speech.
        voice: The voice to use. Run `list_voices` to see available options.
               Defaults to "zh-CN-XiaoxiaoNeural".
        rate: Speech rate adjustment, e.g. "+50%", "-30%", "+0%".
        volume: Volume adjustment, e.g. "+20%", "-50%", "+0%".
        pitch: Pitch adjustment, e.g. "+10Hz", "-5Hz", "+0Hz".
        output_dir: Directory to save the output file. Defaults to current directory.

    Returns:
        The absolute path of the generated MP3 file.
    """
    output_path = _make_output_path(text, output_dir, ".mp3")
    communicate = _build_communicate(text, voice, rate, volume, pitch)
    await communicate.save(output_path)
    abs_path = os.path.abspath(output_path)
    return f"Audio saved to: {abs_path}"


# ---------------------------------------------------------------------------
# Tool: text_to_speech_with_subtitles
# ---------------------------------------------------------------------------


@mcp.tool()
async def text_to_speech_with_subtitles(
    text: str,
    voice: str = "zh-CN-XiaoxiaoNeural",
    rate: str | None = None,
    volume: str | None = None,
    pitch: str | None = None,
    output_dir: str = ".",
) -> str:
    """Convert text to speech and save both an MP3 audio file and an SRT subtitle file.

    Args:
        text: The text to convert to speech.
        voice: The voice to use. Run `list_voices` to see available options.
               Defaults to "zh-CN-XiaoxiaoNeural".
        rate: Speech rate adjustment, e.g. "+50%", "-30%", "+0%".
        volume: Volume adjustment, e.g. "+20%", "-50%", "+0%".
        pitch: Pitch adjustment, e.g. "+10Hz", "-5Hz", "+0Hz".
        output_dir: Directory to save the output files. Defaults to current directory.

    Returns:
        The absolute paths of the generated MP3 and SRT files.
    """
    audio_path = _make_output_path(text, output_dir, ".mp3")
    srt_path = audio_path.rsplit(".", 1)[0] + ".srt"

    communicate = _build_communicate(text, voice, rate, volume, pitch)
    sub_maker = edge_tts.SubMaker()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            data = chunk.get("data")
            if data:
                with open(audio_path, "ab") as f:
                    f.write(data)
        elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
            sub_maker.feed(chunk)

    srt_content = sub_maker.get_srt()
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    abs_audio = os.path.abspath(audio_path)
    abs_srt = os.path.abspath(srt_path)
    return f"Audio saved to: {abs_audio}\nSubtitles saved to: {abs_srt}"


# ---------------------------------------------------------------------------
# Tool: batch_text_to_speech
# ---------------------------------------------------------------------------


@mcp.tool()
async def batch_text_to_speech(
    texts: list[str],
    voice: str = "zh-CN-XiaoxiaoNeural",
    rate: str | None = None,
    volume: str | None = None,
    pitch: str | None = None,
    output_dir: str = ".",
) -> str:
    """Convert multiple texts to speech, each saved as a separate MP3 file.

    All files share the same voice and parameter settings.

    Args:
        texts: A list of text strings to convert.
        voice: The voice to use for all texts. Defaults to "zh-CN-XiaoxiaoNeural".
        rate: Speech rate adjustment, e.g. "+50%", "-30%", "+0%".
        volume: Volume adjustment, e.g. "+20%", "-50%", "+0%".
        pitch: Pitch adjustment, e.g. "+10Hz", "-5Hz", "+0Hz".
        output_dir: Directory to save the output files. Defaults to current directory.

    Returns:
        A summary listing the absolute path of each generated MP3 file.
    """
    if not texts:
        return "Error: No texts provided."

    results = []
    for i, text in enumerate(texts, 1):
        output_path = _make_output_path(text, output_dir, ".mp3")
        communicate = _build_communicate(text, voice, rate, volume, pitch)
        await communicate.save(output_path)
        abs_path = os.path.abspath(output_path)
        results.append(f"  [{i}/{len(texts)}] {abs_path}")

    header = f"Batch complete. Generated {len(results)} file(s):\n"
    return header + "\n".join(results)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """Entry point for the MCP server (used by uvx / project.scripts)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
