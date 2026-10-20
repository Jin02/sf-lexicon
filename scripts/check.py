"""전수 점검: 개념 사전·작품·작품 용어를 모두 읽어 틀을 어긴 곳을 전부 찍는다.

python scripts/check.py        # 틀린 곳이 하나라도 있으면 끝 코드 1
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

KINDS = {"세력", "종족·생물", "존재", "기술·물건", "장소", "사건·시대", "제도·직위", "현상·힘"}
KO_STATUS = {"공식", "우리 표기"}
MEDIA = {"소설", "영화", "드라마", "애니메이션", "게임", "탁상 게임", "만화"}

problems = []


def bad(where, msg):
    problems.append(f"{where}: {msg}")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_concepts():
    d = load(DATA / "concepts.json")
    cats = {c["id"] for c in d["categories"]}
    ids = {}
    for c in d["concepts"]:
        cid = c.get("id")
        if cid in ids:
            bad(f"개념 {cid}", "id 가 겹친다")
        ids[cid] = c
        for k in ("ko", "en", "cat", "one", "note"):
            if not c.get(k):
                bad(f"개념 {cid}", f"{k} 가 비었다")
        if c.get("cat") not in cats:
            bad(f"개념 {cid}", f"없는 갈래 {c.get('cat')}")
    for cid, c in ids.items():
        p = c.get("parent")
        if p is not None:
            if p not in ids:
                bad(f"개념 {cid}", f"없는 상위 개념 {p}")
            elif ids[p]["cat"] != c["cat"]:
                bad(f"개념 {cid}", f"상위 개념 {p} 와 갈래가 다르다")
        seen = set()
        for s in c.get("similar", []):
            if s.get("id") not in ids:
                bad(f"개념 {cid}", f"없는 비슷한 개념 {s.get('id')}")
            if s.get("id") == cid:
                bad(f"개념 {cid}", "자기 자신을 비슷한 개념으로 걸었다")
            if s.get("id") in seen:
                bad(f"개념 {cid}", f"비슷한 개념 {s.get('id')} 가 두 번")
            seen.add(s.get("id"))
            if not s.get("how"):
                bad(f"개념 {cid}", f"비슷한 개념 {s.get('id')} 에 어떻게 다른지가 없다")
    # 같은 짝이 양쪽에 따로 적히면 화면에 두 줄이 된다
    pairs = {}
    for cid, c in ids.items():
        for s in c.get("similar", []):
            key = tuple(sorted((cid, s["id"])))
            if key in pairs:
                bad(f"개념 {cid}", f"{s['id']} 와의 짝이 양쪽에 다 적혔다(한쪽만)")
            pairs[key] = True
    # 상위 고리
    for cid in ids:
        seen, cur = set(), cid
        while cur is not None and cur in ids:
            if cur in seen:
                bad(f"개념 {cid}", "상위 개념이 고리를 이룬다")
                break
            seen.add(cur)
            cur = ids[cur].get("parent")
    return ids


def check_works():
    path = DATA / "works.json"
    if not path.exists():
        return {}
    d = load(path)
    ids = {}
    for w in d["works"]:
        wid = w.get("id")
        if wid in ids:
            bad(f"작품 {wid}", "id 가 겹친다")
        ids[wid] = w
        for k in ("ko", "ko_status", "orig", "media", "year", "by", "scope", "one"):
            if not w.get(k):
                bad(f"작품 {wid}", f"{k} 가 비었다")
        if w.get("ko_status") not in KO_STATUS:
            bad(f"작품 {wid}", f"ko_status 가 '{w.get('ko_status')}'")
        if w.get("ko_status") == "공식" and not w.get("ko_src"):
            bad(f"작품 {wid}", "공식 제목인데 ko_src 가 없다")
        for m in w.get("media", []):
            if m not in MEDIA:
                bad(f"작품 {wid}", f"모르는 매체 {m}")
    return ids


def check_terms(concepts, works):
    used = {}
    tdir = DATA / "terms"
    for path in sorted(tdir.glob("*.json")):
        wid = path.stem
        if works and wid not in works:
            bad(f"용어 파일 {path.name}", "works.json 에 없는 작품")
        d = load(path)
        terms = d["terms"] if isinstance(d, dict) else d
        ids = set()
        kos = {}
        for t in terms:
            tid = t.get("id")
            where = f"{wid}/{tid}"
            if tid in ids:
                bad(where, "id 가 겹친다")
            ids.add(tid)
            for k in ("ko", "orig", "ko_status", "kind", "one"):
                if not t.get(k):
                    bad(where, f"{k} 가 비었다")
            if t.get("ko_status") not in KO_STATUS:
                bad(where, f"ko_status 가 '{t.get('ko_status')}'")
            if t.get("ko_status") == "공식":
                if not t.get("ko_src"):
                    bad(where, "공식 표기인데 ko_src(어디서 확인했나)가 없다")
                if t.get("ko_check") not in ("원자료", "2차 자료"):
                    bad(where, f"공식 표기인데 ko_check 가 '{t.get('ko_check')}'")
            if len(t.get("one", "")) > 50:
                bad(where, f"one 이 {len(t['one'])}자(50자 안쪽)")
            if len(t.get("note", "")) > 260:
                bad(where, f"note 가 {len(t['note'])}자(260자 안쪽)")
            if t.get("kind") not in KINDS:
                bad(where, f"모르는 kind '{t.get('kind')}'")
            if not isinstance(t.get("spoiler"), bool):
                bad(where, "spoiler 가 참/거짓이 아니다")
            for a in t.get("alt_ko", []):
                if not a.get("ko") or not a.get("src"):
                    bad(where, "alt_ko 에 ko 나 src 가 비었다")
            cs = t.get("concepts", [])
            for c in cs:
                if c not in concepts:
                    bad(where, f"없는 개념 {c}")
                used.setdefault(c, []).append(where)
            # 상위와 하위를 같이 달면 화면에 두 번 나온다 — 가장 좁은 것만
            for c in cs:
                p = concepts.get(c, {}).get("parent")
                while p:
                    if p in cs:
                        bad(where, f"{c} 와 그 상위 {p} 를 같이 달았다(좁은 것만)")
                    p = concepts.get(p, {}).get("parent")
            if not t.get("refs"):
                bad(where, "refs(참고한 곳)가 없다")
            k = t.get("ko")
            if k in kos:
                bad(where, f"한글 이름 '{k}' 이 {kos[k]} 와 겹친다")
            kos[k] = tid
    return used


LORE_KINDS = {"불가사의", "유물", "유적", "사건", "기록", "인용", "결말", "전설", "소개"}


def check_lore(concepts, works):
    """data/lore/<작품>.json — 작품이 이야기로 들려주는 조각(docs/lore_brief.md)."""
    n = 0
    ldir = DATA / "lore"
    if not ldir.exists():
        return 0
    for path in sorted(ldir.glob("*.json")):
        wid = path.stem
        if works and wid not in works:
            bad(f"로어 파일 {path.name}", "works.json 에 없는 작품")
        tpath = DATA / "terms" / f"{wid}.json"
        tids = set()
        if tpath.exists():
            td = load(tpath)
            tids = {t["id"] for t in (td["terms"] if isinstance(td, dict) else td)}
        ids = set()
        for x in load(path).get("lore", []):
            n += 1
            lid = x.get("id")
            where = f"로어 {wid}/{lid}"
            if lid in ids:
                bad(where, "id 가 겹친다")
            ids.add(lid)
            for k in ("ko", "orig", "ko_status", "kind", "where", "summary"):
                if not x.get(k):
                    bad(where, f"{k} 가 비었다")
            if x.get("ko_status") not in KO_STATUS:
                bad(where, f"ko_status 가 '{x.get('ko_status')}'")
            if x.get("ko_status") == "공식" and (not x.get("ko_src") or x.get("ko_check") not in ("원자료", "2차 자료")):
                bad(where, "공식 표기인데 ko_src·ko_check 가 모자라다")
            if x.get("kind") not in LORE_KINDS:
                bad(where, f"모르는 kind '{x.get('kind')}'")
            if len(x.get("summary", "")) > 700:
                bad(where, f"summary 가 {len(x['summary'])}자(700자 안쪽)")
            if len(x.get("reveals", "")) > 60:
                bad(where, f"reveals 가 {len(x['reveals'])}자(60자 안쪽)")
            if not isinstance(x.get("spoiler"), bool):
                bad(where, "spoiler 가 참/거짓이 아니다")
            for t in x.get("terms", []):
                if t not in tids:
                    bad(where, f"이 작품 용어에 없는 id {t}")
            cs = x.get("concepts", [])
            for c in cs:
                if c not in concepts:
                    bad(where, f"없는 개념 {c}")
            for c in cs:
                q = concepts.get(c, {}).get("parent")
                while q:
                    if q in cs:
                        bad(where, f"{c} 와 그 상위 {q} 를 같이 달았다(좁은 것만)")
                    q = concepts.get(q, {}).get("parent")
            # 원문 인용이 섞였는지 — 따옴표로 묶은 긴 문장은 옮긴 글일 수 있다
            for qm in re.findall(r"[\"“'‘「『]([^\"”'’」』]{25,})[\"”'’」』]", x.get("summary", "")):
                bad(where, f"요약에 따옴표로 묶은 긴 글이 있다(원문을 옮겼나?): {qm[:30]}…")
            if not x.get("refs"):
                bad(where, "refs(참고한 곳)가 없다")
    return n


def main():
    concepts = check_concepts()
    works = check_works()
    used = check_terms(concepts, works)
    n_lore = check_lore(concepts, works)
    if n_lore:
        print(f"로어 조각 {n_lore}")
    n_terms = sum(len(v) for v in used.values())
    print(f"개념 {len(concepts)} · 작품 {len(works)} · 개념에 걸린 용어 자리 {n_terms}")
    empty = [c for c in concepts if c not in used]
    if used:
        print(f"아직 용어가 하나도 안 걸린 개념 {len(empty)}개")
    if problems:
        print(f"\n틀린 곳 {len(problems)}개")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    print("틀린 곳 없음")


if __name__ == "__main__":
    main()
