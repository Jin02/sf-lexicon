"""data/works_parts/*.json 을 data/works.json 하나로 합친다(칸 모양을 하나로 맞춘다).

python scripts/merge_works.py
- ko_sources 는 [{what, url}] 로 맞춘다(글만 있으면 {what}).
- 조사 쪽이 다른 칸 이름을 썼으면(ko_title_src 등) 맞는 칸으로 옮긴다.
- OVERRIDE 는 사람이 보고 정한 값(작품 제목의 공식 여부, 표에 쓸 짧은 이름 등).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

OVERRIDE = {
    "destiny": {"ko_status": "우리 표기", "short": "데스티니",
                "ko_src": "데스티니 1은 한국어판이 없고, 데스티니 2 의 정식 한국어 제목은 「데스티니 가디언즈」다. 1·2를 함께 다루므로 줄여 적었다."},
    "stellaris": {"ko_status": "우리 표기", "short": "스텔라리스",
                  "ko_src": "정식 한국어판(게임 화면·Steam 한국어 상점)은 제목을 라틴 문자 Stellaris 그대로 쓴다."},
    "evangelion": {"ko_status": "공식", "short": "에반게리온"},
    "dune": {"short": "듄"},
}


def norm_sources(src):
    out = []
    for s in src or []:
        if isinstance(s, str):
            out.append({"what": s})
        elif isinstance(s, dict):
            if "what" in s:
                out.append({k: s[k] for k in ("what", "url") if s.get(k)})
            else:
                parts = [s.get("name", "")]
                if s.get("date"):
                    parts.append(f"({s['date']})")
                if s.get("note"):
                    parts.append("— " + s["note"])
                item = {"what": " ".join(p for p in parts if p)}
                if s.get("url"):
                    item["url"] = s["url"]
                out.append(item)
    return out


def main():
    works = []
    for p in sorted((DATA / "works_parts").glob("*.json")):
        w = json.loads(p.read_text(encoding="utf-8"))
        w = w.get("work", w)
        if "ko_title_src" in w and not w.get("ko_src"):
            w["ko_src"] = w.pop("ko_title_src")
        w.pop("ko_title_src", None)
        w["ko_sources"] = norm_sources(w.get("ko_sources"))
        w.update(OVERRIDE.get(w["id"], {}))
        w.setdefault("orig_en", "")
        w.setdefault("short", w["ko"])
        order = ["id", "ko", "ko_status", "ko_src", "short", "orig", "orig_en", "media", "year", "by", "scope", "one", "ko_sources"]
        works.append({k: w[k] for k in order if k in w} | {k: v for k, v in w.items() if k not in order})
    works.sort(key=lambda w: (w.get("year") or 9999, w["id"]))
    (DATA / "works.json").write_text(json.dumps({"works": works}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"works.json — 작품 {len(works)}")


if __name__ == "__main__":
    main()
