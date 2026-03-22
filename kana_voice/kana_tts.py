#!/usr/bin/env python3
"""
有马加奈 AI 语音合成 (基于 GPT-SoVITS)

用法:
    # Zero-shot: 用参考音频直接推理（最少5秒音频）
    python kana_tts.py "哼，才不是为了你才写的！" --ref samples/kana_ref.wav

    # Few-shot: 先训练再推理（效果更好，需要1分钟+音频）
    python kana_tts.py --train --data samples/
    python kana_tts.py "叔叔你好笨啊" --model output/kana_model

    # 批量生成
    python kana_tts.py --batch lines.txt --ref samples/kana_ref.wav

前置条件:
    1. 运行 setup.sh 完成环境部署
    2. 准备有马加奈的语音素材（从动画中提取）
    3. 需要 NVIDIA GPU (建议 6GB+ 显存)
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path

# GPT-SoVITS 路径
SOVITS_DIR = Path(__file__).parent / "GPT-SoVITS"
OUTPUT_DIR = Path(__file__).parent / "output"
SAMPLES_DIR = Path(__file__).parent / "samples"


def check_env():
    """检查环境是否就绪"""
    if not SOVITS_DIR.exists():
        print("错误: GPT-SoVITS 未安装，请先运行 setup.sh")
        sys.exit(1)

    # 检查 GPU
    try:
        import torch
        if not torch.cuda.is_available():
            print("警告: 未检测到 CUDA GPU，推理速度会非常慢")
        else:
            gpu_name = torch.cuda.get_device_name(0)
            print(f"检测到 GPU: {gpu_name}")
    except ImportError:
        print("警告: PyTorch 未安装，请先运行 setup.sh")


def extract_audio_from_anime(video_path: str, output_dir: str):
    """
    从动画视频中提取音频的辅助函数
    需要 ffmpeg
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "raw_audio.wav"
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn",                    # 不要视频
        "-acodec", "pcm_s16le",   # WAV 格式
        "-ar", "44100",           # 采样率
        "-ac", "1",               # 单声道
        str(output_file)
    ]
    subprocess.run(cmd, check=True)
    print(f"音频已提取到: {output_file}")
    print("提示: 接下来需要手动裁剪出加奈的台词片段")
    print("推荐工具: Audacity (免费) 或 UVR5 (人声分离)")


def prepare_training_data(samples_dir: str):
    """
    准备训练数据
    GPT-SoVITS 需要: 音频文件 + 对应的文本标注
    """
    samples_dir = Path(samples_dir)
    if not samples_dir.exists():
        print(f"错误: 素材目录 {samples_dir} 不存在")
        sys.exit(1)

    wav_files = list(samples_dir.glob("*.wav"))
    if not wav_files:
        print("错误: 未找到 WAV 文件")
        print("请将加奈的语音片段（WAV 格式）放入 samples/ 目录")
        sys.exit(1)

    print(f"找到 {len(wav_files)} 个音频文件")

    # 检查是否有对应的文本标注
    list_file = samples_dir / "filelist.txt"
    if not list_file.exists():
        print("未找到 filelist.txt，正在生成模板...")
        with open(list_file, "w", encoding="utf-8") as f:
            for wav in sorted(wav_files):
                # 格式: 音频路径|说话人|语言|文本
                f.write(f"{wav}|kana|ja|请在这里填写对应的台词文本\n")
        print(f"已生成标注模板: {list_file}")
        print("请编辑此文件，填写每段音频对应的文本")
        return False

    print("训练数据准备就绪")
    return True


def train_model(samples_dir: str):
    """启动 GPT-SoVITS 训练"""
    check_env()

    if not prepare_training_data(samples_dir):
        return

    print("\n开始训练有马加奈语音模型...")
    print("提示: 训练过程可通过 WebUI 监控")
    print(f"  cd {SOVITS_DIR}")
    print("  python webui.py")
    print("\n或使用命令行训练:")

    # GPT-SoVITS 训练流程
    steps = [
        "1. 音频降噪 + 切片: tools/slice_audio.py",
        "2. ASR 自动标注: tools/asr/fasterwhisper_asr.py",
        "3. 语义 token 提取: prepare_datasets/get_hubert_wav32k.py",
        "4. 训练 SoVITS 模型: s2_train.py",
        "5. 训练 GPT 模型: s1_train.py",
    ]
    for step in steps:
        print(f"  {step}")


def zero_shot_tts(text: str, ref_audio: str, output_path: str, language: str = "zh"):
    """
    Zero-shot 推理：用参考音频直接生成
    只需 5 秒参考音频即可
    """
    check_env()

    ref_audio = Path(ref_audio)
    if not ref_audio.exists():
        print(f"错误: 参考音频不存在: {ref_audio}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = output_path or str(OUTPUT_DIR / "kana_output.wav")

    print(f"参考音频: {ref_audio}")
    print(f"合成文本: {text}")
    print(f"输出路径: {output_path}")

    # GPT-SoVITS API 调用
    # 实际使用时需要先启动 API 服务: python api.py
    try:
        import requests
        response = requests.post(
            "http://127.0.0.1:9880/tts",
            json={
                "text": text,
                "text_lang": language,
                "ref_audio_path": str(ref_audio.absolute()),
                "prompt_lang": "ja",  # 参考音频的语言（加奈是日语）
                "prompt_text": "",     # 参考音频对应的文本（可选）
                "top_k": 5,
                "top_p": 0.7,
                "temperature": 0.7,
                "speed": 1.05,         # 加奈说话稍快
            },
            timeout=60,
        )

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"语音已生成: {output_path}")
        else:
            print(f"API 错误: {response.status_code} - {response.text}")

    except requests.exceptions.ConnectionError:
        print("错误: GPT-SoVITS API 未启动")
        print("请先运行:")
        print(f"  cd {SOVITS_DIR}")
        print("  python api.py")


def batch_generate(lines_file: str, ref_audio: str, language: str = "zh"):
    """批量生成多段语音"""
    lines_file = Path(lines_file)
    if not lines_file.exists():
        print(f"错误: 文件不存在: {lines_file}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(lines_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"共 {len(lines)} 条台词待生成")
    for i, line in enumerate(lines, 1):
        output_path = str(OUTPUT_DIR / f"kana_{i:03d}.wav")
        print(f"\n[{i}/{len(lines)}] {line}")
        zero_shot_tts(line, ref_audio, output_path, language)

    print(f"\n全部生成完毕！文件在: {OUTPUT_DIR}")


def main():
    parser = argparse.ArgumentParser(
        description="有马加奈 AI 语音合成 (GPT-SoVITS)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 用参考音频生成语音
  python kana_tts.py "哼，才不是呢！" --ref samples/kana_ref.wav

  # 训练专属模型
  python kana_tts.py --train --data samples/

  # 批量生成
  python kana_tts.py --batch lines.txt --ref samples/kana_ref.wav

  # 从动画提取音频
  python kana_tts.py --extract video.mkv
        """,
    )

    parser.add_argument("text", nargs="?", help="要合成的文本")
    parser.add_argument("--ref", help="参考音频路径（5秒以上的加奈语音）")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--lang", default="zh", choices=["zh", "ja", "en"], help="合成语言")
    parser.add_argument("--train", action="store_true", help="训练模式")
    parser.add_argument("--data", default="samples/", help="训练数据目录")
    parser.add_argument("--batch", help="批量生成（提供台词文件）")
    parser.add_argument("--extract", help="从视频中提取音频")

    args = parser.parse_args()

    if args.extract:
        extract_audio_from_anime(args.extract, "samples/raw")
    elif args.train:
        train_model(args.data)
    elif args.batch:
        if not args.ref:
            parser.error("批量模式需要 --ref 参数")
        batch_generate(args.batch, args.ref, args.lang)
    elif args.text:
        if not args.ref:
            parser.error("需要 --ref 参数指定参考音频")
        zero_shot_tts(args.text, args.ref, args.output, args.lang)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
