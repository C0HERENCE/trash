# concat_clips.py
# 用法：python concat_clips.py
# 需求：输入一个字符串 subdir，把 .\clips\subdir\ 下 clip_<timestamp>_<idx>.mp4 按 timestamp 排序后无重编码拼接为 clilps_all.mp4
# ffmpeg 路径：.\bin\ffmpeg.exe
# 关键点：使用 -fflags +genpts 生成连续 PTS，降低音画不同步风险（仍然 -c copy 不重编码）

import re
import sys
import subprocess
from pathlib import Path

NAME_RE = re.compile(r"^clip_(\d+)_(\d+)\.mp4$", re.IGNORECASE)

def sort_key(p: Path):
    m = NAME_RE.match(p.name)
    if not m:
        return None
    ts = int(m.group(1))   # 第二段：时间戳
    idx = int(m.group(2))  # 第三段：序号（同时间戳时的次序）
    return (ts, idx, p.name)

def main():
    root = Path.cwd()
    ffmpeg = root / "bin" / "ffmpeg.exe"
    clips_root = root / "clips"

    if not ffmpeg.exists():
        print(f"[Error] 找不到 ffmpeg：{ffmpeg}")
        sys.exit(1)
    if not clips_root.exists():
        print(f"[Error] 找不到 clips 目录：{clips_root}")
        sys.exit(1)

    sub = input("请输入 clips 下的子目录名（字符串）：").strip()
    if not sub:
        print("[Error] 输入为空。")
        sys.exit(1)

    target_dir = clips_root / sub
    if not target_dir.exists():
        print(f"[Error] 目录不存在：{target_dir}")
        sys.exit(1)

    # 收集并按时间戳排序
    items = []
    for p in target_dir.iterdir():
        if p.is_file() and p.suffix.lower() == ".mp4":
            k = sort_key(p)
            if k is not None:
                items.append((k, p))

    if not items:
        print(f"[Error] 在 {target_dir} 下未找到符合 clip_<timestamp>_<idx>.mp4 的 mp4 文件。")
        sys.exit(1)

    items.sort(key=lambda x: x[0])
    files = [p for _, p in items]

    # 输出文件（按你的拼写要求：clilps_all.mp4）
    output_path = target_dir / "clilps_all.mp4"

    # 生成 concat demuxer 列表文件
    list_file = target_dir / "_ffmpeg_concat_list.txt"
    with list_file.open("w", encoding="utf-8", newline="\n") as f:
        for p in files:
            # 用绝对路径 + posix 风格，避免 Windows 反斜杠/转义坑
            f.write(f"file '{p.resolve().as_posix()}'\n")

    # ffmpeg 拼接：不重编码 + 生成 PTS
    cmd = [
        str(ffmpeg.resolve()),
        "-y",
        "-hide_banner",
        "-loglevel", "error",

        "-fflags", "+genpts",                 # 关键：生成/修复 PTS
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file.resolve()),

        "-avoid_negative_ts", "make_zero",    # 可选：把负时间戳归零，兼容部分播放器
        "-c", "copy",                         # 不重编码
        str(output_path.resolve()),
    ]

    print(f"[Info] 片段数：{len(files)}")
    print(f"[Info] 输出：{output_path}")
    try:
        subprocess.run(cmd, check=True)
        print("[OK] 拼接完成。")
    except subprocess.CalledProcessError as e:
        print("[Error] ffmpeg 执行失败。常见原因：片段参数不一致（分辨率/帧率/音频采样率/音轨等）导致无法 -c copy。")
        print("命令为：")
        print(" ".join(cmd))
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
