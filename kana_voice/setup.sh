#!/bin/bash
# ===========================================
# 有马加奈 AI 语音克隆 - 环境部署脚本
# 基于 GPT-SoVITS (https://github.com/RVC-Boss/GPT-SoVITS)
# ===========================================

set -e

echo "========================================="
echo "  有马加奈 AI 语音 - 环境部署"
echo "  基于 GPT-SoVITS"
echo "========================================="

# 1. 克隆 GPT-SoVITS
if [ ! -d "GPT-SoVITS" ]; then
    echo "[1/4] 克隆 GPT-SoVITS 仓库..."
    git clone https://github.com/RVC-Boss/GPT-SoVITS.git
else
    echo "[1/4] GPT-SoVITS 已存在，跳过克隆"
fi

cd GPT-SoVITS

# 2. 创建虚拟环境
echo "[2/4] 创建 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
echo "[3/4] 安装依赖（需要 CUDA 环境）..."
pip install -r requirements.txt

# 4. 下载预训练模型
echo "[4/4] 下载预训练模型..."
python3 -c "
from tools.download_models import download_all_models
download_all_models()
" 2>/dev/null || echo "请手动下载模型，参考: https://github.com/RVC-Boss/GPT-SoVITS#pretrained-models"

echo ""
echo "========================================="
echo "  部署完成！"
echo "  接下来："
echo "  1. 准备加奈的语音素材放入 kana_voice/samples/"
echo "  2. 运行 python3 kana_tts.py --help 查看用法"
echo "========================================="
