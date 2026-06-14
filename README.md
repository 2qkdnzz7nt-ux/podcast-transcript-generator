# 播客逐字稿生成器 (Podcast Transcript Generator)

将苹果播客（或其他音频）下载并转换为逐字稿的工具。基于 OpenAI Whisper 和 yt-dlp。

## 功能

- 支持从 **URL** 或 **本地音频文件** 生成逐字稿
- 支持三种输出格式：
  - **纯文本** (`.txt`) — 不带时间戳的连续文本
  - **带时间戳的文本** (`.txt`) — 每段前带有 `[HH:MM:SS]` 时间标记
  - **SRT 字幕** (`.srt`) — 标准字幕格式，可在视频播放器中加载

## 功能

- 支持从 **URL** 或 **本地音频文件** 生成逐字稿
- 支持多种平台：**Apple Podcasts**、**B站 (Bilibili)**、**YouTube** 等
- 自动识别国内网站并绕过代理直连，解决 412/403 错误
- 支持三种输出格式：
  - **纯文本** (`.txt`) — 不带时间戳的连续文本
  - **带时间戳的文本** (`.txt`) — 每段前带有 `[HH:MM:SS]` 时间标记
  - **SRT 字幕** (`.srt`) — 标准字幕格式，可在视频播放器中加载

## 环境要求

- Python 3.8+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)（用于下载在线音频）
- [OpenAI Whisper](https://github.com/openai/whisper)（用于语音识别）

## 安装

```bash
# 克隆仓库
git clone https://github.com/2qkdnzz7nt-ux/podcast-transcript-generator.git
cd podcast-transcript-generator

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
# 从播客链接生成所有格式的逐字稿
python transcript_generator.py "https://example.com/podcast-episode"

# 从本地音频文件生成
python transcript_generator.py "audio_file.m4a"
```

### 指定输出格式

```bash
# 只生成纯文本
python transcript_generator.py "您的播客链接" --output_format txt

# 只生成带时间戳的文本
python transcript_generator.py "您的播客链接" --output_format verbose_txt

# 只生成 SRT 字幕
python transcript_generator.py "您的播客链接" --output_format srt

# 生成所有格式（默认）
python transcript_generator.py "您的播客链接" --output_format all
```

### 其他参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--model` | Whisper 模型大小 (`tiny`, `base`, `small`, `medium`, `large`) | `base` |
| `--language` | 音频语言（如 `zh`, `en`），不指定则自动检测 | 自动检测 |
| `--output_dir` | 输出目录 | 音频文件所在目录 |

```bash
# 使用更大的模型提高准确率
python transcript_generator.py "播客链接" --model medium --language zh
```

## 输出示例

### 纯文本格式 (txt)
```
欢迎收听本期播客 今天我们来聊聊人工智能的发展趋势 首先...
```

### 带时间戳格式 (verbose_txt)
```
[00:00:00] 欢迎收听本期播客
[00:00:05] 今天我们来聊聊人工智能的发展趋势
[00:00:12] 首先让我们回顾一下最近的新闻
```

### SRT 字幕格式 (srt)
```
1
00:00:00,000 --> 00:00:05,000
欢迎收听本期播客

2
00:00:05,000 --> 00:00:12,000
今天我们来聊聊人工智能的发展趋势
```

## 依赖

- `openai-whisper` — 语音识别引擎
- `yt-dlp` — 音频下载工具
- `ffmpeg` — 音频处理（Whisper 和 yt-dlp 均需要）

安装 ffmpeg：
- **Windows**: `winget install ffmpeg` 或从 [ffmpeg.org](https://ffmpeg.org) 下载
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

## License

MIT
