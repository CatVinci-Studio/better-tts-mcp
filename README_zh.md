# better-tts-mcp

[![PyPI version](https://img.shields.io/pypi/v/better-tts-mcp.svg)](https://pypi.org/project/better-tts-mcp/)
[![Python Version](https://img.shields.io/pypi/pyversions/better-tts-mcp.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io)
[![Edge TTS](https://img.shields.io/badge/TTS-Microsoft%20Edge-0078D4.svg)](https://github.com/rany2/edge-tts)

[English](README.md) | [中文](README_zh.md)

> 一个功能丰富的 MCP（模型上下文协议）服务器，基于 Microsoft Edge 文本转语音引擎。
> 无需 API Key，支持 50+ 语言 300+ 种语音，开箱即用。

---

## 功能特性

- **语音列表** — 浏览 300+ 种语音，支持按语言和性别筛选
- **文本转语音** — 将文本转换为 MP3 文件，支持调节语速、音量和音调
- **字幕生成** — 在生成音频的同时生成 SRT 字幕文件
- **批量合成** — 一次调用合成多段文本
- **多音色合成** — 使用 `[voice]文本` 标记在一个 MP3 中混合多种语音

## 快速开始

### 安装

```bash
# 使用 uvx（推荐）
uvx better-tts-mcp

# 或通过 pip 安装
pip install better-tts-mcp
```

### Claude Code 集成

```bash
claude mcp add edge-tts -- uvx better-tts-mcp
```

### Claude Desktop 集成

在 `claude_desktop_config.json` 中添加：

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

## 可用工具

### `list_voices`

列出可用的 Edge TTS 语音，支持可选过滤。

| 参数       | 类型   | 必填 | 说明                                     |
|------------|--------|------|------------------------------------------|
| `language` | string | 否   | 按语言代码筛选，如 `"zh"`、`"en"`、`"ja"` |
| `gender`   | string | 否   | 按性别筛选：`"Male"` 或 `"Female"`        |

### `text_to_speech`

将文本转换为语音并保存为 MP3 文件。

| 参数         | 类型   | 必填 | 默认值                   | 说明                           |
|--------------|--------|------|--------------------------|--------------------------------|
| `text`       | string | 是   | —                        | 要转换的文本                   |
| `voice`      | string | 否   | `zh-CN-XiaoxiaoNeural`   | 语音名称                       |
| `rate`       | string | 否   | —                        | 语速，如 `"+50%"`、`"-30%"`    |
| `volume`     | string | 否   | —                        | 音量，如 `"+20%"`、`"-50%"`    |
| `pitch`      | string | 否   | —                        | 音调，如 `"+10Hz"`、`"-5Hz"`   |
| `output_dir` | string | 否   | `.`（当前目录）           | 输出目录                       |

### `text_to_speech_with_subtitles`

参数与 `text_to_speech` 相同，同时生成 MP3 音频文件和 SRT 字幕文件。

### `batch_text_to_speech`

批量将多段文本转换为语音，每段文本保存为独立的 MP3 文件。

| 参数         | 类型     | 必填 | 默认值                   | 说明                           |
|--------------|----------|------|--------------------------|--------------------------------|
| `texts`      | string[] | 是   | —                        | 要转换的文本列表               |
| `voice`      | string   | 否   | `zh-CN-XiaoxiaoNeural`   | 语音名称（所有文本共用）       |
| `rate`       | string   | 否   | —                        | 语速（共用）                   |
| `volume`     | string   | 否   | —                        | 音量（共用）                   |
| `pitch`      | string   | 否   | —                        | 音调（共用）                   |
| `output_dir` | string   | 否   | `.`（当前目录）           | 输出目录                       |

### `text_to_speech_multi_voice`

将带有语音标记的文本合成为一个 MP3 文件。

格式示例：

```text
[zh-CN-XiaoxiaoNeural]你好。[en-US-AriaNeural]Hello.
```

| 参数            | 类型   | 必填 | 默认值                   | 说明                                  |
|-----------------|--------|------|--------------------------|---------------------------------------|
| `text`          | string | 是   | —                        | 含可选 `[voice]` 标记的输入文本       |
| `default_voice` | string | 否   | `zh-CN-XiaoxiaoNeural`   | 未标记文本使用的默认语音              |
| `rate`          | string | 否   | —                        | 语速调节                               |
| `volume`        | string | 否   | —                        | 音量调节                               |
| `pitch`         | string | 否   | —                        | 音调调节                               |
| `output_dir`    | string | 否   | `.`（当前目录）           | 输出目录                               |

---

## MCP 对接契约（给外部调用方）

本服务遵循标准 MCP 工具调用流程：

- `initialize` -> 协商能力
- `tools/list` -> 获取工具列表和 JSON Schema
- `tools/call` -> 按工具名 + 参数执行调用

传输方式：

- 默认使用 `stdio`（入口命令：`better-tts-mcp`）

### `tools/call` 调用示例

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

典型成功返回文本：

```text
Audio saved to: /absolute/path/to/outputs/20260307_123456_Hello_from_MCP.mp3
```

### 返回约定

- 所有工具都返回可读文本（`content`）。
- 所有工具同时返回机器可读的 `structuredContent`（如 `ok`、`message` 等稳定字段），方便 LLM/自动化调用稳定解析。
- 语音合成相关工具返回的文件路径为绝对路径。
- `text_to_speech_with_subtitles` 返回两行（音频路径 + 字幕路径）。
- `batch_text_to_speech` 返回汇总头 + 每条文本对应的输出路径。

### 错误行为

- 请求结构错误（JSON-RPC 或 Schema 层）会作为协议错误返回。
- 输入校验、业务错误和运行期错误会作为工具执行错误返回（`isError: true`），便于 LLM 自动修正后重试。
- 错误时 `structuredContent` 会包含 `error_code`、`error_message`、`retryable` 字段。

常见错误码：

- `EMPTY_TEXT`
- `EMPTY_TEXTS`
- `EMPTY_TEXT_ITEM`
- `EMPTY_TEXT_SEGMENTS`
- `INVALID_RATE`
- `INVALID_VOLUME`
- `INVALID_PITCH`
- `SYNTHESIS_FAILED`

### 给 API 使用方的稳定性说明

- 以下工具名可视为稳定 API：
  - `list_voices`
  - `text_to_speech`
  - `text_to_speech_with_subtitles`
  - `batch_text_to_speech`
  - `text_to_speech_multi_voice`
- 后续版本可能新增可选参数，但会尽量保持现有调用兼容。

---

## 环境要求

- Python >= 3.10
- 互联网连接（用于访问 Microsoft Edge TTS 服务）

## 许可证

[MIT](LICENSE)
