"""Speech synthesis tools."""

import os
import re
from typing import Annotated

import edge_tts

from mcp.types import CallToolResult

from ..core.audio import build_communicate
from ..core.naming import make_output_path
from ..core.parsing import parse_multi_voice_text
from ..core.results import SynthesisResult, to_call_tool_result

RATE_PATTERN = re.compile(r"^[+-]\d+%$")
VOLUME_PATTERN = re.compile(r"^[+-]\d+%$")
PITCH_PATTERN = re.compile(r"^[+-]\d+Hz$")


def _validate_prosody(
    rate: str | None,
    volume: str | None,
    pitch: str | None,
) -> tuple[str | None, str | None]:
    """Validate optional prosody fields and return `(error_code, error_message)`."""
    if rate is not None and not RATE_PATTERN.fullmatch(rate):
        return (
            "INVALID_RATE",
            "Invalid `rate` format. Expected values like '+10%' or '-30%'.",
        )
    if volume is not None and not VOLUME_PATTERN.fullmatch(volume):
        return (
            "INVALID_VOLUME",
            "Invalid `volume` format. Expected values like '+10%' or '-30%'.",
        )
    if pitch is not None and not PITCH_PATTERN.fullmatch(pitch):
        return (
            "INVALID_PITCH",
            "Invalid `pitch` format. Expected values like '+10Hz' or '-5Hz'.",
        )
    return None, None


def _error_result(message: str, code: str, retryable: bool = False) -> CallToolResult:
    payload = SynthesisResult(
        ok=False,
        message=message,
        error_code=code,
        error_message=message,
        retryable=retryable,
    )
    return to_call_tool_result(payload, is_error=True)


def _success_result(
    message: str,
    files: list[str],
    voice: str | None = None,
    voices_used: list[str] | None = None,
    segment_count: int | None = None,
) -> CallToolResult:
    payload = SynthesisResult(
        ok=True,
        message=message,
        files=files,
        voice=voice,
        voices_used=voices_used or [],
        segment_count=segment_count,
    )
    return to_call_tool_result(payload)


async def text_to_speech(
    text: str,
    voice: str = "zh-CN-XiaoxiaoNeural",
    rate: str | None = None,
    volume: str | None = None,
    pitch: str | None = None,
    output_dir: str = ".",
) -> Annotated[CallToolResult, SynthesisResult]:
    """Convert one text input into a single MP3 file.

    Args:
        text: Text content to synthesize.
        voice: Edge TTS voice short name.
        rate: Optional speaking-rate delta, such as ``+20%``.
        volume: Optional volume delta, such as ``-10%``.
        pitch: Optional pitch delta, such as ``+5Hz``.
        output_dir: Output directory for generated files.

    Returns:
        Human-readable message including the absolute MP3 path.
    """
    if not text.strip():
        return _error_result("Input `text` must not be empty.", "EMPTY_TEXT")

    code, error = _validate_prosody(rate, volume, pitch)
    if error:
        return _error_result(error, code or "INVALID_PROSODY")

    output_path = make_output_path(text, output_dir, ".mp3")
    try:
        communicate = build_communicate(text, voice, rate, volume, pitch)
        await communicate.save(output_path)
    except Exception as exc:
        return _error_result(
            f"Speech synthesis failed: {exc}",
            "SYNTHESIS_FAILED",
            retryable=True,
        )

    abs_path = os.path.abspath(output_path)
    return _success_result(
        message=f"Audio saved to: {abs_path}",
        files=[abs_path],
        voice=voice,
        segment_count=1,
    )


async def text_to_speech_with_subtitles(
    text: str,
    voice: str = "zh-CN-XiaoxiaoNeural",
    rate: str | None = None,
    volume: str | None = None,
    pitch: str | None = None,
    output_dir: str = ".",
) -> Annotated[CallToolResult, SynthesisResult]:
    """Convert text to speech and generate both MP3 and SRT subtitle files.

    Args:
        text: Text content to synthesize.
        voice: Edge TTS voice short name.
        rate: Optional speaking-rate delta, such as ``+20%``.
        volume: Optional volume delta, such as ``-10%``.
        pitch: Optional pitch delta, such as ``+5Hz``.
        output_dir: Output directory for generated files.

    Returns:
        Human-readable message with absolute paths to MP3 and SRT outputs.
    """
    if not text.strip():
        return _error_result("Input `text` must not be empty.", "EMPTY_TEXT")

    code, error = _validate_prosody(rate, volume, pitch)
    if error:
        return _error_result(error, code or "INVALID_PROSODY")

    audio_path = make_output_path(text, output_dir, ".mp3")
    srt_path = audio_path.rsplit(".", 1)[0] + ".srt"

    try:
        communicate = build_communicate(text, voice, rate, volume, pitch)
        sub_maker = edge_tts.SubMaker()

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                data = chunk.get("data")
                if data:
                    with open(audio_path, "ab") as f:
                        f.write(data)
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                sub_maker.feed(chunk)

        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(sub_maker.get_srt())
    except Exception as exc:
        return _error_result(
            f"Speech synthesis with subtitles failed: {exc}",
            "SYNTHESIS_FAILED",
            retryable=True,
        )

    abs_audio = os.path.abspath(audio_path)
    abs_srt = os.path.abspath(srt_path)
    return _success_result(
        message=f"Audio saved to: {abs_audio}\nSubtitles saved to: {abs_srt}",
        files=[abs_audio, abs_srt],
        voice=voice,
        segment_count=1,
    )


async def batch_text_to_speech(
    texts: list[str],
    voice: str = "zh-CN-XiaoxiaoNeural",
    rate: str | None = None,
    volume: str | None = None,
    pitch: str | None = None,
    output_dir: str = ".",
) -> Annotated[CallToolResult, SynthesisResult]:
    """Convert a list of texts into multiple MP3 files.

    Args:
        texts: Input text list. Each item becomes one output file.
        voice: Edge TTS voice short name shared by all items.
        rate: Optional speaking-rate delta applied to all items.
        volume: Optional volume delta applied to all items.
        pitch: Optional pitch delta applied to all items.
        output_dir: Output directory for generated files.

    Returns:
        Summary text with one absolute output path per item.
    """
    if not texts:
        return _error_result("No texts provided.", "EMPTY_TEXTS")

    code, error = _validate_prosody(rate, volume, pitch)
    if error:
        return _error_result(error, code or "INVALID_PROSODY")

    results: list[str] = []
    output_files: list[str] = []
    for i, text in enumerate(texts, 1):
        if not text.strip():
            return _error_result(
                f"Item {i} in `texts` is empty. Every item must be non-empty.",
                "EMPTY_TEXT_ITEM",
            )
        output_path = make_output_path(text, output_dir, ".mp3")
        try:
            communicate = build_communicate(text, voice, rate, volume, pitch)
            await communicate.save(output_path)
        except Exception as exc:
            return _error_result(
                f"Batch synthesis failed at item {i}: {exc}",
                "SYNTHESIS_FAILED",
                retryable=True,
            )
        abs_path = os.path.abspath(output_path)
        output_files.append(abs_path)
        results.append(f"  [{i}/{len(texts)}] {abs_path}")

    header = f"Batch complete. Generated {len(results)} file(s):\n"
    return _success_result(
        message=header + "\n".join(results),
        files=output_files,
        voice=voice,
        segment_count=len(output_files),
    )


async def text_to_speech_multi_voice(
    text: str,
    default_voice: str = "zh-CN-XiaoxiaoNeural",
    rate: str | None = None,
    volume: str | None = None,
    pitch: str | None = None,
    output_dir: str = ".",
) -> Annotated[CallToolResult, SynthesisResult]:
    """Synthesize marked segments with multiple voices into one MP3 output.

    Marker format:
        ``[voice_name]text`` repeated across the input.

    Args:
        text: Input text with optional ``[voice_name]`` markers.
        default_voice: Voice for unmarked text.
        rate: Optional speaking-rate delta applied to all segments.
        volume: Optional volume delta applied to all segments.
        pitch: Optional pitch delta applied to all segments.
        output_dir: Output directory for generated files.

    Returns:
        Human-readable message with output file path and voices used.
    """
    if not text.strip():
        return _error_result("Input `text` must not be empty.", "EMPTY_TEXT")

    code, error = _validate_prosody(rate, volume, pitch)
    if error:
        return _error_result(error, code or "INVALID_PROSODY")

    segments = parse_multi_voice_text(text, default_voice)
    if not segments:
        return _error_result("No text provided.", "EMPTY_TEXT")

    output_path = make_output_path("multi_voice", output_dir, ".mp3")
    bytes_written = 0
    used_voices: list[str] = []

    with open(output_path, "wb") as output_file:
        for voice, segment_text in segments:
            segment_text = segment_text.strip()
            if not segment_text:
                continue

            if voice not in used_voices:
                used_voices.append(voice)

            try:
                communicate = build_communicate(
                    segment_text, voice, rate, volume, pitch
                )
                async for chunk in communicate.stream():
                    if chunk["type"] != "audio":
                        continue
                    data = chunk.get("data")
                    if not data:
                        continue
                    output_file.write(data)
                    bytes_written += len(data)
            except Exception as exc:
                return _error_result(
                    f"Multi-voice synthesis failed for voice `{voice}`: {exc}",
                    "SYNTHESIS_FAILED",
                    retryable=True,
                )

    if bytes_written == 0:
        os.unlink(output_path)
        return _error_result(
            "No non-empty text segments were provided.",
            "EMPTY_TEXT_SEGMENTS",
        )

    abs_path = os.path.abspath(output_path)
    voices_used = ", ".join(used_voices)
    return _success_result(
        message=f"Audio saved to: {abs_path}\nVoices used: {voices_used}",
        files=[abs_path],
        voice=default_voice,
        voices_used=used_voices,
        segment_count=len(used_voices),
    )
