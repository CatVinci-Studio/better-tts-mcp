# better-tts-mcp

[![PyPI version](https://img.shields.io/pypi/v/better-tts-mcp.svg)](https://pypi.org/project/better-tts-mcp/)
[![Python Version](https://img.shields.io/pypi/pyversions/better-tts-mcp.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io)
[![Edge TTS](https://img.shields.io/badge/TTS-Microsoft%20Edge-0078D4.svg)](https://github.com/rany2/edge-tts)

[English](README.md) | [中文](README_zh.md)

> A feature-rich MCP (Model Context Protocol) server for Microsoft Edge Text-to-Speech.
> No API key required. 300+ voices in 50+ languages. Zero configuration.

---

## Features

- **List Voices** — Browse 300+ voices in 50+ languages, filter by language and gender
- **Text-to-Speech** — Convert text to MP3 with customizable rate, volume, and pitch
- **Subtitles** — Generate SRT subtitle files alongside audio
- **Batch Processing** — Synthesize multiple texts in one call
- **Multi-Voice Synthesis** — Mix multiple voices in one output MP3 using `[voice]text` markers

## Quick Start

### Installation

```bash
# Using uvx (recommended)
uvx better-tts-mcp

# Or install via pip
pip install better-tts-mcp
```

### Claude Code

```bash
claude mcp add edge-tts -- uvx better-tts-mcp
```

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "edge-tts": {
      "command": "uvx",
      "args": ["better-tts-mcp"]
    }
  }
}
```

---

## Available Tools

### `list_voices`

List available Edge TTS voices with optional filtering.

| Parameter  | Type   | Required | Description                              |
|------------|--------|----------|------------------------------------------|
| `language` | string | No       | Filter by language code, e.g. `"zh"`, `"en"` |
| `gender`   | string | No       | Filter by gender: `"Male"` or `"Female"` |

### `text_to_speech`

Convert text to speech and save as MP3.

| Parameter    | Type   | Required | Default                | Description                        |
|--------------|--------|----------|------------------------|------------------------------------|
| `text`       | string | Yes      | —                      | Text to convert                    |
| `voice`      | string | No       | `zh-CN-XiaoxiaoNeural` | Voice name                         |
| `rate`       | string | No       | —                      | Speed, e.g. `"+50%"`, `"-30%"`     |
| `volume`     | string | No       | —                      | Volume, e.g. `"+20%"`, `"-50%"`    |
| `pitch`      | string | No       | —                      | Pitch, e.g. `"+10Hz"`, `"-5Hz"`    |
| `output_dir` | string | No       | `.` (current directory)| Output directory                   |

### `text_to_speech_with_subtitles`

Same parameters as `text_to_speech`. Generates both MP3 and SRT files.

### `batch_text_to_speech`

Convert multiple texts to speech, each saved as a separate MP3 file.

| Parameter    | Type     | Required | Default                | Description                        |
|--------------|----------|----------|------------------------|------------------------------------|
| `texts`      | string[] | Yes      | —                      | List of texts to convert           |
| `voice`      | string   | No       | `zh-CN-XiaoxiaoNeural` | Voice name (shared for all texts)  |
| `rate`       | string   | No       | —                      | Speed (shared)                     |
| `volume`     | string   | No       | —                      | Volume (shared)                    |
| `pitch`      | string   | No       | —                      | Pitch (shared)                     |
| `output_dir` | string   | No       | `.` (current directory)| Output directory                   |

### `text_to_speech_multi_voice`

Convert text with voice markers into one merged MP3 file.

Format example:

```text
[zh-CN-XiaoxiaoNeural]你好。[en-US-AriaNeural]Hello.
```

| Parameter       | Type   | Required | Default                | Description                        |
|----------------|--------|----------|------------------------|------------------------------------|
| `text`         | string | Yes      | —                      | Input text with optional `[voice]` markers |
| `default_voice`| string | No       | `zh-CN-XiaoxiaoNeural` | Voice used when no marker is present |
| `rate`         | string | No       | —                      | Speed adjustment                    |
| `volume`       | string | No       | —                      | Volume adjustment                   |
| `pitch`        | string | No       | —                      | Pitch adjustment                    |
| `output_dir`   | string | No       | `.` (current directory)| Output directory                    |

---

## MCP Integration Contract (for external callers)

This server follows the MCP tool-call flow used by standard MCP clients:

- `initialize` -> capability negotiation
- `tools/list` -> discover tool names and JSON schemas
- `tools/call` -> invoke a tool by name with arguments

Transport:

- Default transport is `stdio` (entrypoint: `better-tts-mcp`)

### Tool call example (`tools/call`)

```json
{
  "method": "tools/call",
  "params": {
    "name": "text_to_speech",
    "arguments": {
      "text": "Hello from MCP",
      "voice": "en-US-AriaNeural",
      "rate": "+0%",
      "volume": "+0%",
      "pitch": "+0Hz",
      "output_dir": "./outputs"
    }
  }
}
```

Typical successful result text:

```text
Audio saved to: /absolute/path/to/outputs/20260307_123456_Hello_from_MCP.mp3
```

### Return-value conventions

- All tools return human-readable text in `content`.
- All tools also return machine-readable `structuredContent` with stable fields (`ok`, `message`, etc.) for robust LLM/tooling integration.
- Paths returned by synthesis tools are absolute paths.
- `text_to_speech_with_subtitles` returns two lines (audio path + subtitle path).
- `batch_text_to_speech` returns a summary header plus one output path per item.

### Error behavior

- Malformed requests (JSON-RPC or schema-level) are protocol errors.
- Input validation and business/runtime failures are returned as tool execution errors with `isError: true`, so LLM clients can self-correct and retry.
- Error payloads include `error_code`, `error_message`, and `retryable` in `structuredContent`.

Common error codes:

- `EMPTY_TEXT`
- `EMPTY_TEXTS`
- `EMPTY_TEXT_ITEM`
- `EMPTY_TEXT_SEGMENTS`
- `INVALID_RATE`
- `INVALID_VOLUME`
- `INVALID_PITCH`
- `SYNTHESIS_FAILED`

### Stability notes for API consumers

- Tool names are treated as stable API surface:
  - `list_voices`
  - `text_to_speech`
  - `text_to_speech_with_subtitles`
  - `batch_text_to_speech`
  - `text_to_speech_multi_voice`
- New optional parameters may be added in future versions without breaking existing callers.

---

## Requirements

- Python >= 3.10
- Internet connection (for accessing Microsoft Edge TTS service)

## License

[MIT](LICENSE)
