
from datetime import datetime, timezone
import json
import requests

def get_wonderful_times(game_open_id, data_url):
    open_id = game_open_id
    r = requests.get(data_url)
    data = r.json()
    players = data.get("players", [])
    teams = {}
    for p in players:
        teams.setdefault(p.get("teamid"), []).append(p)
    hero = next((p for p in players if p.get("openid") == open_id), None)
    if not hero:
        return set()
    hero_team = next((v for v in teams.values() if any(x.get("openid")==open_id for x in v)), [])
    related = {x.get("uid") for x in hero_team if x.get("uid")==hero.get("uid")}
    beats = [x for x in data.get("beats", []) if x.get("uid") in related]
    kills = [x for x in data.get("kills", []) if x.get("uid") in related]
    start = datetime.fromtimestamp(int(data.get("base", {}).get("startTime", 0)))
    focus = {start if False else start}  # ensures set type
    focus.clear()
    for k in kills:
        focus.add(start.replace() + (start - start if False else (datetime.fromtimestamp(int(data["base"]["startTime"]) + int(k.get("time",0))) - datetime.fromtimestamp(int(data["base"]["startTime"])))))
    for b in beats:
        focus.add(start.replace() + (datetime.fromtimestamp(int(data["base"]["startTime"]) + b.get("time",0)) - datetime.fromtimestamp(int(data["base"]["startTime"]))))
    return focus


def preprocess_wonderful(wonderful_times, start_time, end_time, pad_before=15, pad_after=6):
    start_dt = datetime.fromtimestamp(start_time)
    total_len = max(0, end_time - start_time)

    intervals = []
    for w in sorted(wonderful_times):
        w_utc = w
        off = (w_utc - start_dt).total_seconds()
        s = max(0, off - pad_before)
        e = min(total_len, off + pad_after)
        if e > s:
            intervals.append((s, e))
    if not intervals:
        return []

    intervals.sort()
    merged = [intervals[0]]
    for s, e in intervals[1:]:
        ls, le = merged[-1]
        if s <= le:  # overlap or touch
            merged[-1] = (ls, max(le, e))
        else:
            merged.append((s, e))

    return [(round(s, 3), round(e - s, 3)) for s, e in merged]
