"""지금 이 레포에 커밋해도 되는 때인가.

진님(2026-10-20): "커밋은 12시 넘어서 해라", "아님 휴일에" — 이 레포를 공개로 돌리면서 정한 것.
되는 때: 밤 0시~아침 9시 전, 또는 토·일요일, 또는 공휴일(Sync 의 공휴일 표 — sync-todo/public/index.html 의 HOLIDAYS).

    python scripts/commit_window.py      # 되면 0, 안 되면 1 로 끝나고 까닭을 한 줄 찍는다
"""
import datetime
import json
import re
import sys
from pathlib import Path

SYNC_INDEX = Path(r"C:\Users\jin0x\dev\sync-todo\public\index.html")
NIGHT_END_HOUR = 9   # 0시부터 이 시각 전까지


def holidays():
    try:
        s = SYNC_INDEX.read_text(encoding="utf-8")
    except OSError:
        return {}, "Sync 공휴일 표를 못 읽음(주말만 봄)"
    m = re.search(r"HOLIDAYS = (\{.*?\n\});", s, re.S)
    if not m:
        return {}, "Sync 공휴일 표를 못 찾음(주말만 봄)"
    body = re.sub(r",\s*}", "}", m.group(1))
    try:
        return json.loads(body), ""
    except ValueError:
        return {}, "Sync 공휴일 표를 못 읽음(주말만 봄)"


def check(now=None):
    now = now or datetime.datetime.now()
    if now.hour < NIGHT_END_HOUR:
        return True, f"{now:%m-%d %H:%M} 밤 시간"
    if now.weekday() >= 5:
        return True, f"{now:%m-%d} 주말"
    table, note = holidays()
    name = table.get(f"{now:%Y}", {}).get(f"{now:%m-%d}")
    if name:
        return True, f"{now:%m-%d} 공휴일({name})"
    return False, f"{now:%m-%d %H:%M} 평일 9시~24시 — 커밋은 0시~9시 또는 주말·공휴일에" + (f" · {note}" if note else "")


if __name__ == "__main__":
    ok, why = check()
    print(("커밋해도 됨: " if ok else "커밋 안 됨: ") + why)
    sys.exit(0 if ok else 1)
