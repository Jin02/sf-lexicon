"""작품 하나의 용어를 사람이 전수로 읽기 좋게 펼친다.

python scripts/review_dump.py <작품 id> [출력 파일]
- 한 건마다: 갈래, 한글(원어), 개념, 줄거리 누설, 표기 확인 상태, 다른 표기, 한 줄, 설명, 근거 앞부분
- 맨 위에 수 요약(공식 원자료 / 2차 자료 / 우리 표기, 개념에 이은 수)
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    wid = sys.argv[1]
    terms = json.loads((ROOT / "data" / "terms" / f"{wid}.json").read_text(encoding="utf-8"))["terms"]
    st = Counter((t["ko_status"] + ("/" + t.get("ko_check", "") if t["ko_status"] == "공식" else "")) for t in terms)
    lines = [f"# {wid} — 용어 {len(terms)} · " + " · ".join(f"{k} {v}" for k, v in st.most_common())
             + f" · 개념에 이음 {sum(1 for t in terms if t.get('concepts'))} · 누설 {sum(1 for t in terms if t.get('spoiler'))}", ""]
    for t in terms:
        s = t["ko_status"] + ("/" + t.get("ko_check", "") if t["ko_status"] == "공식" else "")
        alt = " alt=" + ", ".join(a["ko"] for a in t.get("alt_ko", [])) if t.get("alt_ko") else ""
        lines.append(f"[{t['kind']}] {t['ko']} ({t['orig']}) {t.get('concepts')} 누설={t.get('spoiler')} {s}{alt}")
        lines.append(f"   한 줄: {t['one']}")
        lines.append(f"   설명: {t.get('note', '')}")
        lines.append(f"   근거: {(t.get('ko_src') or '')[:120]}")
    text = "\n".join(lines) + "\n"
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(text, encoding="utf-8")
        print(lines[0])
    else:
        print(text)


if __name__ == "__main__":
    main()
