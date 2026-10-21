"""자료를 모아 화면 한 장(dist/index.html)으로 묶는다.

python scripts/build.py
- data/concepts.json, data/works.json(없으면 data/works_parts/*), data/terms/*.json 을 읽어
  app/index.html 의 /*DATA*/ 자리에 넣는다. 파일 하나라서 그냥 열어도 보인다.
"""
import datetime
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    concepts = load(DATA / "concepts.json")
    works = []
    seen = set()
    if (DATA / "works.json").exists():
        for w in load(DATA / "works.json")["works"]:
            works.append(w)
            seen.add(w["id"])
    for p in sorted((DATA / "works_parts").glob("*.json")):
        w = load(p)
        w = w.get("work", w)
        if w["id"] not in seen:
            works.append(w)
            seen.add(w["id"])
    terms = []
    for p in sorted((DATA / "terms").glob("*.json")):
        d = load(p)
        for t in d["terms"] if isinstance(d, dict) else d:
            t = dict(t)
            t["work"] = p.stem
            t.pop("refs", None)  # 화면에는 안 쓰고 무게만 늘린다
            terms.append(t)
    for w in works:
        w.setdefault("year", 0)
    # 로어 조각(작품이 이야기로 들려주는 것) — data/lore/<작품>.json
    lore = []
    for p in sorted((DATA / "lore").glob("*.json")) if (DATA / "lore").exists() else []:
        for x in load(p).get("lore", []):
            x = dict(x)
            x["work"] = p.stem
            x.pop("refs", None)
            lore.append(x)
    # 찾은 세계(용어 조사 전) — 화면에 필요한 칸만 줄여 싣는다
    cands = []
    cpath = DATA / "candidates_merged.json"
    if cpath.exists():
        for c in load(cpath)["worlds"]:
            cands.append({
                "id": c["id"], "t": c.get("ko") or c.get("orig"), "o": c.get("orig"), "y": c.get("year"),
                "m": c.get("media") or [], "fm": c.get("first_medium"), "by": (c.get("by") or "")[:60],
                "s": c.get("setting"), "k": c["korean"]["status"], "b": bool(c.get("borderline")),
                "l": c.get("lore_size"), "cs": c.get("concepts") or [], "r": bool(c.get("researched")),
            })
    bundle = {
        "categories": concepts["categories"],
        "concepts": concepts["concepts"],
        "works": works,
        "terms": terms,
        "lore": lore,
        "cands": cands,
        "built": datetime.date.today().isoformat(),
    }
    text = json.dumps(bundle, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    tpl = (ROOT / "app" / "index.html").read_text(encoding="utf-8")
    out = tpl.replace("/*DATA*/", text)
    (ROOT / "dist").mkdir(exist_ok=True)
    (ROOT / "dist" / "index.html").write_text(out, encoding="utf-8")
    # 공개용 index.html 은 뼈대(doctype·head)를 공개할 때 덧씌우므로 비워 둔다. 이 컴퓨터에서 열어 볼 판만 따로 감싼다.
    local = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
             '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
             '<style>body{margin:0}[hidden]{display:none!important}</style></head><body>' + out + "</body></html>")
    (ROOT / "dist" / "local.html").write_text(local, encoding="utf-8")
    # 서버(iwinv, https://sf.jinhyerimsync.duckdns.org)가 내보내는 판 — 이 폴더 하나만 공개한다(2026-10-21 진님: "서버에 올려줘 iwinv").
    site = local.replace('<meta charset="utf-8">', '<meta charset="utf-8"><title>SF 개념 사전</title>'
                         '<meta name="description" content="SF 세계관을 작품을 가로지르는 개념으로 묶어 보는 사전">', 1)
    (ROOT / "dist" / "site").mkdir(exist_ok=True)
    (ROOT / "dist" / "site" / "index.html").write_text(site, encoding="utf-8")
    print(f"dist/index.html — 개념 {len(bundle['concepts'])} · 작품 {len(works)} · 용어 {len(terms)} · 로어 {len(lore)} · 찾은 세계 {len(cands)} · {len(out.encode('utf-8')) // 1024}KB")


if __name__ == "__main__":
    main()
