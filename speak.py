#!/usr/bin/env python3
"""
有马加奈语音生成器
使用 Edge TTS 将文本转为语音文件（mp3）

用法:
    python speak.py "哼，才不是为了你才写的代码！"
    python speak.py "你好叔叔" -v zh-CN-XiaoyiNeural
    python speak.py "こんにちは" -v ja-JP-NanamiNeural -o output.mp3

依赖: pip install edge-tts
"""

import argparse
import asyncio
import sys
from pathlib import Path

import edge_tts

# 推荐音色（年轻女性，适合加奈的角色感）
VOICE_PRESETS = {
    "cn": "zh-CN-XiaoyiNeural",       # 中文 - 小艺（年轻活泼）
    "cn2": "zh-CN-XiaohanNeural",      # 中文 - 小涵
    "jp": "ja-JP-NanamiNeural",        # 日语 - 七海
    "tw": "zh-TW-HsiaoChenNeural",     # 中文台湾 - 小臻
}

DEFAULT_VOICE = VOICE_PRESETS["cn"]
DEFAULT_OUTPUT = "kana_voice.mp3"


async def generate_voice(text: str, voice: str, output: str, rate: str = "+0%"):
    """生成语音文件"""
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output)
    print(f"语音已保存到: {output}")


async def list_voices():
    """列出所有可用的中日文音色"""
    voices = await edge_tts.list_voices()
    print("\n可用的中日文音色：")
    print("-" * 60)
    for v in voices:
        locale = v["Locale"]
        if locale.startswith(("zh", "ja")):
            gender = v["Gender"]
            name = v["ShortName"]
            print(f"  {name:<30} {gender:<8} {locale}")


def main():
    parser = argparse.ArgumentParser(description="有马加奈语音生成器")
    parser.add_argument("text", nargs="?", help="要转换的文本")
    parser.add_argument("-v", "--voice", default=DEFAULT_VOICE, help=f"音色 (默认: {DEFAULT_VOICE})")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT, help=f"输出文件 (默认: {DEFAULT_OUTPUT})")
    parser.add_argument("-r", "--rate", default="+5%", help="语速调整 (默认: +5%%，加奈说话比较快)")
    parser.add_argument("-l", "--list", action="store_true", help="列出可用音色")
    parser.add_argument("-p", "--preset", choices=VOICE_PRESETS.keys(), help="使用预设音色 (cn/cn2/jp/tw)")

    args = parser.parse_args()

    if args.list:
        asyncio.run(list_voices())
        return

    if not args.text:
        parser.error("请提供要转换的文本，或使用 -l 列出音色")

    voice = VOICE_PRESETS.get(args.preset, args.voice) if args.preset else args.voice

    asyncio.run(generate_voice(args.text, voice, args.output, args.rate))


if __name__ == "__main__":
    main()
