"""갈래별 후보(data/candidates/*.json)를 합치고 겹침을 정리한다.

python scripts/merge_candidates.py
- 칸 점검(빠진 칸, 모르는 매체·한국어 상태, 없는 개념 id)
- 같은 세계로 보이는 것 묶기: id 가 같거나 제목(원제·영어 제목·한글 제목)을 다듬은 것이 같으면 한 건
- 비슷하지만 확실하지 않은 짝은 따로 찍어 손으로 본다
- 이미 들어 있는 18작품과 겹치는 것은 뺀다
- 결과: data/candidates_merged.json, docs/candidates.md
"""
import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

MEDIA = {"소설", "영화", "드라마", "애니메이션", "만화", "게임", "탁상 게임", "희곡"}
KOREAN = {"있음", "일부", "없음", "확인 못 함", "한국 원작"}
LORE = {"큼", "중간", "작음"}
EXISTING = {
    "dune", "star wars", "stellaris", "alpha centauri", "sid meiers alpha centauri", "beyond earth",
    "civilization beyond earth", "sid meiers civilization beyond earth", "destiny", "star trek",
    "mobile suit gundam", "gundam", "neon genesis evangelion", "evangelion", "blade runner",
    "foundation", "the three body problem", "three body problem", "three body", "legend of the galactic heroes",
    "the expanse", "expanse", "mass effect", "halo", "starcraft", "warhammer 40000", "warhammer 40k",
}
# 사람이 보고 같은 세계라고 정한 짝(합칠 때 앞의 id 로)
SAME = {
    "things_to_come": "the_shape_of_things_to_come",   # 웰스 소설과 그 영화
    "the_body_snatchers": "body_snatchers",            # 같은 소설이 두 갈래에서
    "captain_harlock": "leijiverse",                   # 마츠모토 레이지 세계 — 인물·배가 서로 오감
    "galaxy_express_999": "leijiverse",
    "snow_queen_vinge": "the_snow_queen_vinge",
    "we_can_remember_it_for_you_wholesale": "total_recall",  # 원작 단편과 영화
    "make_room_make_room": "soylent_green",            # 원작 소설과 영화
    "story_of_your_life": "arrival",                   # 원작 단편과 영화(컨택트)
    "bimyeongeul_chajaseo": "lost_memories",           # 비명을 찾아서와 그 영화
    "oms_en_serie": "la_planete_sauvage",              # 원작 소설과 애니메이션 영화
    "mystery_of_the_third_planet": "alisa_selezneva",  # 앨리스 연작과 그 애니메이션
    "who_goes_there": "the_thing",                     # 캠벨 원작 소설과 영화 「괴물」(1982)
}
STOP = {"games", "game", "studios", "studio", "entertainment", "interactive", "software", "productions", "pictures",
        "animation", "films", "film", "the", "and", "inc", "ltd", "co", "netflix", "hbo", "bbc", "nbc", "cbs", "abc",
        "fox", "sony", "nintendo", "sega", "konami", "square", "enix", "capcom", "bandai", "namco", "ubisoft", "microsoft",
        "선라이즈", "토에이", "동화", "애니메이션", "원작", "감독", "제작", "소설", "만화", "영화", "게임즈", "스튜디오"}
# 사람이 보고 다른 세계라고 정한 짝(일부러 나눈 것) — 다시 찍지 않는다
DIFFERENT = {
    frozenset(p) for p in [
        ("phantasy_star", "phantasy_star_online"), ("phantasy_star", "phantasy_star_online_2"),
        ("phantasy_star_online", "phantasy_star_online_2"), ("xenoblade_chronicles", "xenoblade_chronicles_x"),
        ("gundam_wing", "gundam_seed"), ("gundam_wing", "gundam_00"), ("gundam_wing", "gundam_age"),
        ("gundam_seed", "gundam_00"), ("gundam_seed", "gundam_age"), ("gundam_00", "gundam_age"),
        ("planetfall", "age_of_wonders_planetfall"), ("stalker", "stalker_gsc"),
    ]
}
_rev = DATA / "candidates_reviewed.json"
if _rev.exists():
    DIFFERENT |= {frozenset(p) for p in json.loads(_rev.read_text(encoding="utf-8"))["different"]}

problems = []


def norm(s):
    s = (s or "").lower()
    s = re.sub(r"[’'`\"·:;,.!?()\[\]{}«»「」『』〈〉《》\-–—/&+]", " ", s)
    s = re.sub(r"\b(the|a|an)\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def keys(c):
    out = {c["id"]}
    for k in ("orig", "orig_en", "ko"):
        v = norm(c.get(k))
        if v:
            out.add(v)
    return out


def main():
    concepts = {c["id"] for c in json.load(open(DATA / "concepts.json", encoding="utf-8"))["concepts"]}
    rows = []
    for p in sorted((DATA / "candidates").glob("*.json")):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            problems.append(f"{p.name}: JSON 을 못 읽음 — {e}")
            continue
        for c in d.get("candidates", []):
            c = dict(c)
            c["_group"] = p.stem
            w = f"{p.stem}/{c.get('id')}"
            for k in ("id", "orig", "media", "first_medium", "by", "year", "setting", "lore_size", "notability", "korean"):
                if c.get(k) in (None, "", []):
                    problems.append(f"{w}: {k} 가 비었다")
            for m in c.get("media", []) or []:
                if m not in MEDIA:
                    problems.append(f"{w}: 모르는 매체 {m}")
            if c.get("first_medium") and c["first_medium"] not in MEDIA:
                problems.append(f"{w}: 모르는 first_medium {c['first_medium']}")
            k = (c.get("korean") or {}).get("status")
            if k not in KOREAN:
                problems.append(f"{w}: korean.status 가 '{k}'")
            if c.get("lore_size") and c["lore_size"] not in LORE:
                problems.append(f"{w}: lore_size 가 '{c['lore_size']}'")
            bad = [x for x in c.get("concepts", []) or [] if x not in concepts]
            if bad:
                problems.append(f"{w}: 없는 개념 {bad}")
                c["concepts"] = [x for x in c.get("concepts", []) if x in concepts]
            if c.get("ko") and not c.get("ko_src"):
                problems.append(f"{w}: 한글 제목이 있는데 ko_src 가 없다")
            rows.append(c)

    # 이미 들어 있는 것 빼기
    kept, dropped = [], []
    for c in rows:
        if keys(c) & EXISTING:
            dropped.append(c)
        else:
            kept.append(c)

    # 같은 세계 묶기 (union-find)
    parent = list(range(len(kept)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a, b):
        parent[find(a)] = find(b)

    # 제목·id 가 같아도 같은 해이거나 만든 이가 겹칠 때만 같은 세계로 본다(동명이작 — 괴물·무적호·더 문 같은 것을 막는다).
    def creators0(c):
        return {t for t in re.split(r"[\s,·()/\[\];]+", (c.get("by") or "").lower()) if len(t) >= 3 and t not in STOP}

    def compatible(a, b):
        if SAME.get(a["id"]) == b["id"] or SAME.get(b["id"]) == a["id"] or (SAME.get(a["id"]) and SAME.get(a["id"]) == SAME.get(b["id"])):
            return True
        if a.get("year") and a.get("year") == b.get("year"):
            return True
        return bool(creators0(a) & creators0(b))

    by_key = {}
    for i, c in enumerate(kept):
        cid = SAME.get(c["id"], c["id"])
        for k in keys(c) | {cid}:
            by_key.setdefault(k, []).append(i)
    blocked = set()
    for k, idx in by_key.items():
        for x in range(len(idx)):
            for y in range(x + 1, len(idx)):
                a, b = kept[idx[x]], kept[idx[y]]
                if compatible(a, b):
                    union(idx[x], idx[y])
                else:
                    blocked.add(tuple(sorted((f"{a['_group']}/{a['id']}", f"{b['_group']}/{b['id']}"))))
    groups = {}
    for i in range(len(kept)):
        groups.setdefault(find(i), []).append(kept[i])

    merged = []
    for members in groups.values():
        # 가장 칸이 많이 찬 것을 바탕으로
        base = dict(max(members, key=lambda m: sum(1 for v in m.values() if v not in (None, "", []))))
        base["found_in"] = sorted({m["_group"] for m in members})
        base["media"] = sorted({x for m in members for x in (m.get("media") or [])})
        base["concepts"] = sorted({x for m in members for x in (m.get("concepts") or [])})
        base["year"] = min((m.get("year") or 9999) for m in members)
        if not base.get("ko"):
            for m in members:
                if m.get("ko"):
                    base["ko"], base["ko_src"] = m["ko"], m.get("ko_src")
                    break
        statuses = [(m.get("korean") or {}).get("status") for m in members]
        if len(set(statuses)) > 1:
            # 매체마다 판정이 갈리면: 정식 한국어판이 하나라도 있으면 그 세계는 '있음'(한국 원작이 가장 앞)
            for st in ("한국 원작", "있음", "일부", "없음", "확인 못 함"):
                if st in statuses:
                    combined = st
                    break
            if combined == "없음" and "확인 못 함" in statuses:
                combined = "확인 못 함"   # 한쪽만 '없음'이면 아직 단정하지 않는다
            base["korean"] = {"status": combined, "detail": "매체마다 판정이 갈려 합침 — korean_by_group 참고"}
            base["korean_by_group"] = [{"group": m["_group"], **(m.get("korean") or {})} for m in members]
        base["members"] = [{"group": m["_group"], "id": m["id"], "orig": m.get("orig"), "ko": m.get("ko"),
                            "year": m.get("year"), "by": m.get("by"), "first_medium": m.get("first_medium")} for m in members]
        base.pop("_group", None)
        merged.append(base)
    # 용어까지 조사한 작품도 목록에 넣는다 — 진님(2026-10-20): "지구상 이제까지 만들어진 sf 모든 작품을 찾아서 정리한다".
    # 첫 묶음 18작품은 후보 찾기에서 일부러 뺐기 때문에 목록에 없었다(헤일로·스텔라리스가 안 보인다는 지적).
    wpath = DATA / "works.json"
    if wpath.exists():
        have = {c["id"]: c for c in merged}
        for w in json.load(open(wpath, encoding="utf-8"))["works"]:
            tp = DATA / "terms" / f"{w['id']}.json"
            if not tp.exists():
                continue
            if w["id"] in have:
                have[w["id"]]["researched"] = True
                continue
            terms = json.load(open(tp, encoding="utf-8"))["terms"]
            official = w.get("ko_status") == "공식" or any(t.get("ko_status") == "공식" for t in terms)
            n = len(terms)
            merged.append({
                "id": w["id"], "orig": w.get("orig"), "orig_en": w.get("orig_en", ""), "ko": w.get("ko"), "ko_src": w.get("ko_src") or "works.json",
                "media": w.get("media") or [], "first_medium": (w.get("media") or [""])[0], "series": (w.get("scope") or "")[:160],
                "by": w.get("by"), "year": w.get("year"), "country": w.get("country", ""), "setting": w.get("one"),
                "concepts": sorted({c for t in terms for c in t.get("concepts", [])}), "new_ideas": "",
                "lore_size": "큼" if n >= 60 else ("중간" if n >= 30 else "작음"),
                "notability": "용어 조사를 마친 작품", "korean": {"status": "있음" if official else "확인 못 함", "detail": "용어 조사 때 확인(작품 쪽 참고)"},
                "borderline": False, "found_in": ["조사한 작품"], "members": [], "researched": True,
            })
    merged.sort(key=lambda c: (c.get("year") or 9999, c.get("orig", "")))
    # 다른 세계가 같은 id 를 쓰면(괴물 2006 과 The Host 2008 이 둘 다 the_host 였다) 둘 다 뒤에 해를 붙여 가른다
    n_id = {}
    for c in merged:
        n_id[c["id"]] = n_id.get(c["id"], 0) + 1
    for c in merged:
        if n_id[c["id"]] > 1:
            c["id"] = f"{c['id']}_{c.get('year')}"
    assert len({c["id"] for c in merged}) == len(merged), "세계 id 가 겹친다"

    # 확실하지 않은 짝
    near = []

    def creators(c):
        return {t for t in re.split(r"[\s,·()/\[\]]+", (c.get("by") or "").lower()) if len(t) >= 3 and t not in STOP}

    # 모든 짝을 다 견주면 세계가 늘수록 느려진다(1,500곳에 46초) — 제목 머리·긴 낱말·같은 해로 묶어 견줄 짝만 고른다
    titles = [norm(c.get("orig_en") or c.get("orig")) for c in merged]
    makers = [creators(c) for c in merged]
    block = {}
    for i, t in enumerate(titles):
        if not t or len(t) < 6:
            continue
        for k in {"p:" + t[:4]} | {"w:" + w for w in t.split() if len(w) >= 5}:
            block.setdefault(k, []).append(i)
    for i, c in enumerate(merged):
        if c.get("year") and makers[i]:
            block.setdefault(f"y:{c['year']}", []).append(i)
    pairs = set()
    for k, idx in block.items():
        if len(idx) > 400 and not k.startswith("y:"):
            continue   # 너무 흔한 낱말(star, space …)로 묶인 덩어리는 머리글자 쪽에서 잡힌다
        for x in range(len(idx)):
            for y in range(x + 1, len(idx)):
                pairs.add((idx[x], idx[y]))
    for i, j in sorted(pairs):
        ci, cj = merged[i], merged[j]
        if frozenset((ci["id"], cj["id"])) in DIFFERENT:
            continue
        a, b = titles[i], titles[j]
        similar_title = False
        if a and b and min(len(a), len(b)) >= 6:
            if difflib.SequenceMatcher(None, a, b).ratio() > 0.85:
                similar_title = True
            elif re.search(r"\b" + re.escape(a) + r"\b", b) or re.search(r"\b" + re.escape(b) + r"\b", a):
                similar_title = True
        same_maker = ci.get("year") and ci.get("year") == cj.get("year") and makers[i] & makers[j]
        if similar_title or same_maker:
            near.append((ci["id"], cj["id"]))

    out = {"count": len(merged), "dropped_existing": [c["id"] for c in dropped], "near_pairs": near,
           "homonyms": sorted(blocked), "worlds": merged}
    (DATA / "candidates_merged.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"갈래 {len(list((DATA / 'candidates').glob('*.json')))} · 후보 {len(rows)}건 → 이미 있는 것 {len(dropped)} 빼고 → 세계 {len(merged)}개")
    print(f"확실하지 않은 짝 {len(near)} · 제목은 같지만 해·만든 이가 달라 따로 둔 짝 {len(blocked)}")
    for a, b in sorted(blocked):
        print("  ≠", a, "/", b)
    for a, b in near:
        print("  ?", a, "~", b)
    if problems:
        print(f"\n칸 문제 {len(problems)}개")
        for p in problems:
            print(" -", p)


if __name__ == "__main__":
    main()
    sys.exit(0)
