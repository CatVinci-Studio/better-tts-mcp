"""Structured MCP tool result helpers."""

from pydantic import BaseModel, Field

from mcp.types import CallToolResult, TextContent


class VoiceInfo(BaseModel):
    """A normalized voice entry returned by the voice listing tool."""

    short_name: str
    gender: str
    locale: str
    friendly_name: str = ""


class VoicesResult(BaseModel):
    """Structured result for voice discovery."""

    ok: bool
    message: str
    voices: list[VoiceInfo] = Field(default_factory=list)
    error_code: str | None = None
    error_message: str | None = None
    retryable: bool = False


class SynthesisResult(BaseModel):
    """Structured result for speech synthesis tools."""

    ok: bool
    message: str
    files: list[str] = Field(default_factory=list)
    voice: str | None = None
    voices_used: list[str] = Field(default_factory=list)
    segment_count: int | None = None
    error_code: str | None = None
    error_message: str | None = None
    retryable: bool = False


def to_call_tool_result(
    payload: BaseModel, *, is_error: bool = False
) -> CallToolResult:
    """Convert a pydantic payload model into a structured MCP tool result."""
    text = getattr(payload, "message", payload.model_dump_json())
    return CallToolResult(
        content=[TextContent(type="text", text=text)],
        structuredContent=payload.model_dump(),
        isError=is_error,
    )
