"""2차 개념(scripts/concepts_r2.json)을 concepts.json 에 넣고, 적어 둔 용어들을 새 개념에 잇는다.
여러 번 돌려도 된다(이미 있는 개념·이미 이은 자리는 건너뜀). 워해머처럼 나중에 온 작품은 links 에 더하고 다시 돌린다.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def main():
    r2 = json.loads((ROOT / "scripts" / "concepts_r2.json").read_text(encoding="utf-8"))
    p = DATA / "concepts.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    by = {c["id"]: c for c in d["concepts"]}
    added = 0
    for c in r2["new"]:
        if c["id"] not in by:
            d["concepts"].append(c)
            by[c["id"]] = c
            added += 1
    for cid, fields in r2.get("edit", {}).items():
        by[cid].update(fields)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def ancestors(cid):
        out, cur = set(), by[cid].get("parent")
        while cur:
            out.add(cur)
            cur = by[cur].get("parent")
        return out

    linked = 0
    for work, m in r2["links"].items():
        tp = DATA / "terms" / f"{work}.json"
        td = json.loads(tp.read_text(encoding="utf-8"))
        ids = {t["id"] for t in td["terms"]}
        missing = set(m) - ids
        assert not missing, f"{work}: 없는 용어 {missing}"
        for t in td["terms"]:
            for cid in m.get(t["id"], []):
                assert cid in by, cid
                if cid not in t["concepts"]:
                    t["concepts"].append(cid)
                    linked += 1
                # 새로 단 개념의 상위가 이미 달려 있으면 빼서 가장 좁은 것만 남긴다
                for a in ancestors(cid):
                    if a in t["concepts"]:
                        t["concepts"].remove(a)
        tp.write_text(json.dumps(td, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"새 개념 {added}개, 새로 이은 자리 {linked}개")


if __name__ == "__main__":
    main()
