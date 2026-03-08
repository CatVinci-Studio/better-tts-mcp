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

---

## 环境要求

- Python >= 3.10
- 互联网连接（用于访问 Microsoft Edge TTS 服务）

## 许可证

[MIT](LICENSE)
