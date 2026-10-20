"""찾은 세계(data/candidates_merged.json)에서 아직 용어 조사를 안 한 곳을 조사할 차례대로 늘어놓는다.

    python scripts/queue.py            # data/queue.json 을 다시 만들고 앞 20곳을 보인다
    python scripts/queue.py next 4     # 다음 차례에 할 4곳(같은 매체가 둘을 넘지 않게)

차례: data/fame.json 이 있으면 세계가 클수록 + 마이너할수록(FAME_PREF) 앞. 없으면 세계 크기·한국어판·여러 갈래 순. SF 경계에 걸친 곳은 뒤로.
★우주와 관련된 세계만(진님 2026-10-19: "우주와 관련된 SF만 진행하자") — data/space_filter.json 에서 "예"인 곳만 차례에 든다. 사이버펑크는 우주가 아니어도 든다(진님 2026-10-20: "사이버 펑크 종류도 추가하자" — space_filter 의 "cyberpunk": true 또는 new_ideas 가 [사이버펑크] 로 시작).
"경계"는 queue.json 의 border 에 따로 모아 둔다(진님이 고르면 queue_manual.json 의 first 에).
★영화로 시작한 세계는 빼고(진님 같은 날: "영화도 좀 빼자 그냥"), 소설·애니 등에서 시작해 영화가 된 세계는 남긴다.
이미 data/terms/<id>.json 이 있으면 빠진다. 손으로 앞당기거나 미룰 곳은 data/queue_manual.json 에 적는다.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
LORE = {"큼": 3, "중간": 2, "작음": 1}
KO = {"있음": 2, "한국 원작": 2, "일부": 1}
SKIP_FIRST_MEDIUM = {"영화"}
# 알려진 정도(data/fame.json, 1 아주 마이너 ~ 5 대중 대작)에 매기는 점수 — 진님: "좀 마이너한쪽 SF면 좋겠어".
# 마이너하지만 탄탄한 2 가 가장 앞, 장르 안 유명작 3, 자료가 적을 1, 넓게 알려진 4, 대중 대작 5 는 맨 뒤.
FAME_PREF = {2: 3.0, 3: 2.5, 1: 1.5, 4: 0.5, 5: -3.0}


def build():
    worlds = json.loads((DATA / "candidates_merged.json").read_text(encoding="utf-8"))["worlds"]
    done = {p.stem for p in (DATA / "terms").glob("*.json")}
    manual = {"first": [], "skip": [], "last": []}
    mp = DATA / "queue_manual.json"
    if mp.exists():
        manual.update(json.loads(mp.read_text(encoding="utf-8")))
    space, cyber = {}, set()
    sp = DATA / "space_filter.json"
    if sp.exists():
        sp_all = json.loads(sp.read_text(encoding="utf-8"))["worlds"]
        space = {k: v["space"] for k, v in sp_all.items()}
        # 사이버펑크는 우주가 아니어도 차례에 든다 — 진님(2026-10-20): "사이버 펑크 종류도 추가하자"
        cyber = {k for k, v in sp_all.items() if v.get("cyberpunk")}
    fame = {}
    fp = DATA / "fame.json"
    if fp.exists():
        fame = {k: v["fame"] for k, v in json.loads(fp.read_text(encoding="utf-8"))["worlds"].items()}
    rows, border = [], []
    for w in worlds:
        if w["id"] in done or w["id"] in manual["skip"]:
            continue
        # 판정 파일이 있는데 판정이 없는 곳(세계 더 찾기로 새로 들어온 곳)은 판정을 더할 때까지 차례에 넣지 않는다
        if w["first_medium"] in SKIP_FIRST_MEDIUM and w["id"] not in manual["first"]:
            continue
        sv = space.get(w["id"], "판정 없음") if space else "예"
        if w["id"] in cyber or (w.get("new_ideas") or "").startswith("[사이버펑크]"):
            sv = "예"
        if sv != "예" and w["id"] not in manual["first"]:
            if sv in ("경계", "판정 없음"):
                border.append({"id": w["id"], "ko": w["ko"], "orig": w["orig"], "year": w["year"], "space": sv})
            continue
        if fame:
            # 마이너한 쪽을 앞에: 세계 크기 + 알려진 정도 점수(한국어판·여러 갈래 가산은 대작 쪽으로 기울어 쓰지 않는다)
            # 같은 단계 안에서는 한국어판이 있는 쪽을 조금 앞에(표기 근거를 찾기 쉽다) — 단계 차이(0.5)를 넘지 않게 0.2배
            score = LORE.get(w["lore_size"], 1) + FAME_PREF.get(fame.get(w["id"], 3), 2.5) + 0.2 * KO.get(w["korean"]["status"], 0)
        else:
            score = LORE.get(w["lore_size"], 1) + KO.get(w["korean"]["status"], 0) + (len(w["found_in"]) - 1)
        if w["borderline"]:
            score -= 3
        if w["id"] in manual["first"]:
            score += 100
        if w["id"] in manual["last"]:
            score -= 100
        rows.append({"id": w["id"], "ko": w["ko"], "orig": w["orig"], "year": w["year"], "media": w["media"],
                     "first_medium": w["first_medium"], "lore_size": w["lore_size"],
                     "korean": w["korean"]["status"], "borderline": w["borderline"], "fame": fame.get(w["id"]),
                     "score": score})
    rows.sort(key=lambda r: (-r["score"], r["year"] if isinstance(r["year"], int) else 9999, r["id"]))
    (DATA / "queue.json").write_text(json.dumps({"left": len(rows), "done": len(done), "queue": rows, "border": border},
                                                ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return rows


def pick(rows, n):
    out, per = [], {}
    for r in rows:
        m = r["first_medium"]
        if per.get(m, 0) >= 2:
            continue
        out.append(r)
        per[m] = per.get(m, 0) + 1
        if len(out) == n:
            break
    return out


if __name__ == "__main__":
    rows = build()
    if len(sys.argv) >= 2 and sys.argv[1] == "next":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        for r in pick(rows, n):
            print(f"{r['id']}\t{r['ko']}\t{r['year']}\t{'/'.join(r['media'])}\t세계 {r['lore_size']}\t한국어판 {r['korean']}")
    else:
        print(f"남은 곳 {len(rows)} · 조사한 작품 {len({p.stem for p in (DATA / 'terms').glob('*.json')})}")
        for r in rows[:40]:
            print(r["score"], r["id"], r["ko"], r["year"], "/".join(r["media"]), r["lore_size"], r["korean"])
