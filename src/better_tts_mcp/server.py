"""MCP server entry point for better-tts-mcp."""

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .tools.synthesis import (
    batch_text_to_speech,
    text_to_speech,
    text_to_speech_multi_voice,
    text_to_speech_with_subtitles,
)
from .tools.voices import list_voices

mcp = FastMCP(
    "better-tts-mcp",
    instructions=(
        "A text-to-speech MCP server powered by Microsoft Edge TTS. "
        "Use `list_voices` to discover available voices, then use "
        "`text_to_speech` or `text_to_speech_with_subtitles` to synthesize speech. "
        "Use `batch_text_to_speech` for multiple texts at once, and "
        "`text_to_speech_multi_voice` for mixed-voice output."
    ),
)

mcp.tool(
    title="List Edge TTS Voices",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)(list_voices)

mcp.tool(
    title="Text to Speech",
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
)(text_to_speech)

mcp.tool(
    title="Text to Speech with Subtitles",
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
)(text_to_speech_with_subtitles)

mcp.tool(
    title="Batch Text to Speech",
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
)(batch_text_to_speech)

mcp.tool(
    title="Multi-Voice Text to Speech",
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
)(text_to_speech_multi_voice)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """Entry point for the MCP server (used by uvx / project.scripts)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
