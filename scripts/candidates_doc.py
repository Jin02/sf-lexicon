"""data/candidates_merged.json → docs/candidates.md (찾은 SF 세계 목록 문서).

python scripts/candidates_doc.py
"""
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

ORDER = ["소설", "희곡", "영화", "드라마", "애니메이션", "만화", "게임", "탁상 게임"]


def cell(s):
    return str(s or "").replace("|", "／").replace("\n", " ")


def main():
    d = json.loads((DATA / "candidates_merged.json").read_text(encoding="utf-8"))
    ws = d["worlds"]
    kc = collections.Counter(w["korean"]["status"] for w in ws)
    mc = collections.Counter(w.get("first_medium") for w in ws)
    out = ["# 찾은 SF 세계", "",
           f"매체를 가리지 않고 SF 세계 후보를 13갈래로 나눠 찾은 결과다. 같은 세계(소설과 그 영화, 같은 시리즈)는 한 건으로 합쳤다. "
           f"모두 **{len(ws)}개** — 첫 묶음 18작품(용어 조사 중)은 빠져 있다.", "",
           "- 이 목록은 **용어 조사 전**이다. 세계관 한 줄과 개념 표시는 후보를 찾은 조사가 붙인 것이라 검증 전이다.",
           "- 한국어: 정식 한국어판(번역 출간·국내 개봉·정식 방영·게임 한국어 지원)이 있는지. 매체마다 갈리면 하나라도 있으면 '있음'.",
           "- (경계)는 판타지·공포·슈퍼히어로가 바탕이거나 SF 비중이 작은 것.", "",
           "| 처음 나온 매체 | 수 |", "|---|---|"]
    for m in ORDER:
        if mc.get(m):
            out.append(f"| {m} | {mc[m]} |")
    out += ["", "| 한국어 정식판 | 수 |", "|---|---|"]
    for k in ("있음", "한국 원작", "일부", "없음", "확인 못 함"):
        out.append(f"| {k} | {kc.get(k, 0)} |")
    for m in ORDER:
        rows = sorted([w for w in ws if w.get("first_medium") == m], key=lambda w: (w.get("year") or 9999, w.get("orig") or ""))
        if not rows:
            continue
        out += ["", f"## {m}에서 시작한 세계 ({len(rows)})", "",
                "| 해 | 제목 | 원제 | 만든 이 | 매체 | 한국어 | 세계관 |", "|---|---|---|---|---|---|---|"]
        for w in rows:
            title = w.get("ko") or w.get("orig")
            if w.get("borderline"):
                title += " (경계)"
            out.append("| {} | {} | {} | {} | {} | {} | {} |".format(
                w.get("year") or "?", cell(title), cell(w.get("orig")), cell((w.get("by") or "")[:40]),
                cell("·".join(w.get("media") or [])), cell(w["korean"]["status"]), cell(w.get("setting"))))
    (ROOT / "docs" / "candidates.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"docs/candidates.md — 세계 {len(ws)}")


if __name__ == "__main__":
    main()
