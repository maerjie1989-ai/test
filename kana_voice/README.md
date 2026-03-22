# 有马加奈 AI 语音克隆

基于 [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) 实现有马加奈的语音克隆。

## 环境要求

- Python 3.9+
- NVIDIA GPU (建议 6GB+ 显存)
- CUDA 11.8+
- ffmpeg

## 快速开始

### 1. 部署环境

```bash
chmod +x setup.sh && ./setup.sh
```

### 2. 准备素材

将有马加奈的干净语音片段（WAV 格式）放入 `samples/` 目录。

**素材获取方式：**
- 从动画中提取：`python kana_tts.py --extract 动画视频.mkv`
- 用 [UVR5](https://github.com/Anjok07/ultimatevocalremovergui) 分离人声和背景音
- 用 Audacity 裁剪出加奈的台词片段
- 每段 2~10 秒，总计至少 5 秒（建议 1 分钟以上效果更佳）

### 3. Zero-shot 推理（快速体验）

```bash
# 启动 API 服务
cd GPT-SoVITS && python api.py

# 生成语音
python kana_tts.py "哼，才不是呢！" --ref samples/kana_ref.wav
```

### 4. 训练专属模型（效果更好）

```bash
# 准备标注数据
python kana_tts.py --train --data samples/
# 编辑 samples/filelist.txt 填写文本标注
# 然后通过 WebUI 训练
cd GPT-SoVITS && python webui.py
```

### 5. 批量生成

```bash
python kana_tts.py --batch demo_lines.txt --ref samples/kana_ref.wav
```

## 文件结构

```
kana_voice/
├── setup.sh          # 环境部署脚本
├── kana_tts.py       # 语音合成主脚本
├── demo_lines.txt    # 示例台词（加奈风格）
├── samples/          # 参考音频素材（需自行准备）
├── output/           # 生成的语音文件
└── GPT-SoVITS/       # GPT-SoVITS 框架（setup.sh 自动安装）
```
