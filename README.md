# ATRI Chatbot

基于 **Live2D + Ollama + GPT-SoVITS** 的桌面 AI 对话机器人，支持实时语音合成与唇形同步。

## 功能

- **对话** — ATRI 角色模型（Ollama），流式流式输出
- **语音** — GPT-SoVITS TTS，角色语音合成
- **口型同步** — Live2D 模型根据语音自动张嘴闭嘴
- **Live2D 交互** — 眨眼、呼吸、表情

## 前置条件

| 软件 | 下载 |
|---|---|
| Python 3.9 | https://www.python.org/downloads/ |
| Ollama | https://ollama.com/download |
| ffmpeg | https://ffmpeg.org/download.html |

## 快速开始

```bash
# 1. 克隆仓库
git clone <仓库地址>
cd ATRI_Chatbot

# 2. 创建 Ollama 模型
ollama create ATRI -f ATRI

# 3. 一键安装环境
setup.bat

# 4. 将以下文件放入项目根目录
#    - GPT_weights_v2/     （GPT 模型权重）
#    - SoVITS_weights_v2/  （SoVITS 模型权重）
#    - ffmpeg.exe          （音频处理）
#    - ffprobe.exe         （音频处理）

# 5. 启动
gui.bat
```

## 文件结构

```
ATRI_Chatbot/
├── gui.py                 # 主界面（PyQt5 + Live2D）
├── api_v2.py              # TTS 服务（GPT-SoVITS）
├── config.yaml            # 配置文件
├── ATRI                   # Ollama 角色模型定义
├── gui.bat                # 一键启动脚本
├── start_api.bat          # 单独启动 TTS 服务
├── start_gui.bat          # 单独启动 GUI
├── setup.bat              # 环境初始化脚本
├── download_models.py     # 预训练模型下载
├── requirements.txt       # Python 依赖
├── Live_2d_models/        # Live2D 角色模型
├── GPT_SoVITS/            # TTS 推理引擎（源码）
├── tools/                 # 工具模块
├── ref/                   # 参考音频
└── config.yaml            # 配置项
```

## 配置

编辑 `config.yaml`：

```yaml
dialog_url: 'http://localhost:11434/api/generate'   # Ollama API
tts_url: 'http://localhost:9880/tts'                 # TTS API
chat_model: "ATRI:latest"                            # Ollama 模型名
chat_robot_name: 'ATRI'                              # 机器人名称
user_name: 'Eden'                                    # 用户名称
ref_audio_path: 'ref\xxx.wav'                        # TTS 参考音频
```

## 构建你的角色

1. 编辑 `ATRI` 文件中的 System Prompt
2. `ollama create <你的模型名> -f ATRI`
3. 修改 `config.yaml` 中的 `chat_model`
