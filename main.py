import time
from pathlib import Path

from auto_cut import get_wonderful_times, preprocess_wonderful
from bili_replay_min import init, get_replay_list, get_streams, cut_hls_segment
from g4p_battles import g4p_login
from tqdm import tqdm

COOKIE_FILE = Path("cookie.txt")
if not COOKIE_FILE.exists():
    COOKIE_FILE.write_text("PUT_YOUR_BILIBILI_COOKIE_HERE", encoding="utf-8")
    raise SystemExit("已自动创建 cookie.txt，请按照 README 步骤粘贴你的 B 站 Cookie 后重新运行。")

cookie_str = COOKIE_FILE.read_text(encoding="utf-8").lstrip("\ufeff").strip()
if not cookie_str or "PUT_YOUR_BILIBILI_COOKIE_HERE" in cookie_str:
    raise SystemExit("cookie.txt 未配置，请粘贴完整的 B 站 Cookie。")

recording_tab_modes = [('计分', ['全部']), ('不计分', ['全部'])]
query_time = time.time()
query_range = 86400

# game for peace
g4p_client = g4p_login()
tabs = g4p_client.get_battle_mode_tabs()
all_battles = []
for t in recording_tab_modes:
    tab = next((x for x in tabs if x["tabName"] == t[0]), None)
    if not tab:
        continue
    modes = [x['mode'] for x in tab['modeList'] if x['name'] in t[1]]
    if not modes:
        continue
    battles = g4p_client.get_pubg_battle_list(page=1, count=30, tabIndex=tab['tabIndex'], modes=modes)
    all_battles.extend(battles['list'])
recent_battles = [x for x in all_battles if 0 <= query_time - int(x['startime']) <= query_range]
wonderful_times = []

for b in tqdm(recent_battles, desc="获取精彩时间", unit="局"):
    attempt = 15
    while attempt > 0:
        replay_data = g4p_client.parse_replay_data(battleId=b['battleId'])
        if replay_data["reviewStatus"] == 3:
            rep_data = g4p_client.get_pubg_replay_data(b['battleId'])
            wonderful_times.extend(get_wonderful_times(g4p_client.account_manager.game_open_id, rep_data['dataUrl']))
            break
        attempt -= 1
        time.sleep(1)


# bilibili
init(cookie_str)
try:
    replays = get_replay_list()
except Exception as exc:
    raise SystemExit(f"获取 B 站录像列表失败: {exc}")

if not replays:
    raise SystemExit("未找到可用的直播录像。")

current_replay = replays[0]
streams = get_streams(current_replay)
if not streams:
    raise SystemExit("未获取到任何录像码流。")

m3u8 = streams[0]
output_dir = Path("clips") / str(current_replay["live_key"])
output_dir.mkdir(parents=True, exist_ok=True)

start_time = m3u8["start_time"]
end_time = m3u8["end_time"]
merged_clips = preprocess_wonderful(wonderful_times, start_time, end_time, pad_before=15, pad_after=6)
if not merged_clips:
    raise SystemExit("近 24 小时内未检测到精彩时刻，或录像尚未生成。")

success_count = 0
failed = []
for s, d in tqdm(merged_clips, desc="导出精彩片段", unit="段"):
    output_path = output_dir / f"clip_{int(start_time+s)}_{int(d)}.mp4"
    try:
        cut_hls_segment(m3u8['stream'], start=s, duration=d, output_path=str(output_path))
        success_count += 1
    except Exception as exc:
        msg = f"[WARN] 导出 {output_path.name} 失败：{exc}"
        print(msg)
        failed.append(msg)

print(f"[INFO] 本次共导出 {success_count} 段精彩片段，已保存到 {output_dir.resolve()}")
if failed:
    print("[INFO] 失败详情：")
    for msg in failed:
        print("   " + msg)
