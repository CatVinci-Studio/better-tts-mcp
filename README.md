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

---

## Requirements

- Python >= 3.10
- Internet connection (for accessing Microsoft Edge TTS service)

## License

[MIT](LICENSE)
