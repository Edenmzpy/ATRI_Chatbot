# ATRI Chatbot

基于 **Live2D + Ollama + Genie-TTS** 的桌面 AI 对话机器人，支持实时语音合成与唇形同步。

## 功能

- **对话** — ATRI 角色模型（Ollama），流式输出
- **语音** — Genie-TTS（GPT-SoVITS ONNX 优化引擎），角色语音合成
- **口型同步** — Live2D 模型根据语音自动张嘴闭嘴
- **Live2D 交互** — 眨眼、呼吸、表情

## 前置条件

| 软件 | 下载 |
|---|---|
| Python 3.9 | https://www.python.org/downloads/ |
| Ollama | https://ollama.com/download |

## 快速开始

```bash
# 1. 克隆仓库
git clone <仓库地址>
cd ATRI_Chatbot

# 2. 创建 Ollama 模型
#    先拉取基础模型（取决于 ATRI 文件中 FROM 字段指定的模型）
ollama pull openllm/causallm
#    再用 Modelfile 创建角色模型
ollama create ATRI -f ATRI

# 3. 一键安装环境
setup.bat

# 4. 准备 TTS 模型和参考音频
#    - onnx_model/<你的角色名>/   （转换后的 ONNX 模型，见下方转换说明）
#    - GenieData/                  （TTS 推理模型，首次运行自动下载）
#    - ref/<参考音频.wav>          （TTS 参考音频，建议 3-10 秒干净人声）

# 5. 启动
gui.bat
```

### 转换现有 GPT-SoVITS 模型

如果你已有 GPT-SoVITS V2 的 `.pth` 和 `.ckpt` 权重文件：

```bash
venv\Scripts\python -c "
import genie_tts as genie
genie.convert_to_onnx(
    torch_ckpt_path='GPT_weights_v2/your_model.ckpt',
    torch_pth_path='SoVITS_weights_v2/your_model.pth',
    output_dir='onnx_model/<你的角色名>'
)
"
```

## 文件结构

```
ATRI_Chatbot/
├── gui.py                 # 主界面（PyQt5 + Live2D，内置 Genie-TTS）
├── config.yaml            # 配置文件
├── ATRI                   # Ollama 角色模型定义
├── gui.bat                # 一键启动脚本
├── setup.bat              # 环境初始化脚本
├── requirements.txt       # Python 依赖
├── Live_2d_models/        # Live2D 角色模型
├── onnx_model/            # ONNX 格式 TTS 模型（按角色名分目录）
├── GenieData/             # TTS 推理模型（HuBERT/G2P/RoBERTa）
├── ref/                   # 参考音频（需自行准备）
└── config.yaml            # 配置项
```

## 配置

编辑 `config.yaml`：

```yaml
dialog_url: 'http://localhost:11434/api/generate'   # Ollama API
chat_model: "ATRI"                                   # Ollama 模型名（与 ollama create 的名字一致）
character_name: '<你的角色名>'                        # TTS 角色名
onnx_model_dir: 'onnx_model/<你的角色名>'             # ONNX 模型目录
ref_audio_path: 'ref\your_audio.wav'                 # TTS 参考音频（自行准备）
ref_prompt_text: "参考音频的文字内容"                  # 参考音频的文字
```

## 构建你的角色

1. 编辑 Modelfile（`ATRI` 文件）中的 System Prompt
2. 先拉取基础模型：`ollama pull <FROM 字段指定的模型>`
3. 创建角色模型：`ollama create <你的模型名> -f ATRI`
4. 修改 `config.yaml` 中的 `chat_model` 为 `<你的模型名>`
