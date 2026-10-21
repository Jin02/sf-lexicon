# 새 세계 판정 — 우주(space_filter.json)·알려진 정도(fame.json)·사이버펑크 표시를 한꺼번에 매긴다.
# 판정은 에이전트가 docs/judge_brief.md 대로 덩이마다 out_NN.txt 로 쓴다.
#
#   python scripts/judge.py make <작업 폴더> [덩이 크기=400] [사이버펑크 후보 id 파일]
#       → 판정이 빈 세계를 in_NN.tsv 로 나눈다(이미 out_ 에 있는 id 와 앞선 in_ 번호는 건너뜀)
#   python scripts/judge.py apply <작업 폴더>
#       → out_NN.txt 를 검사해 비어 있는 판정만 더한다(이미 있는 우주 판정·알려진 정도는 바꾸지 않음)
import collections
import glob
import json
import os
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
V = {"Y": "예", "N": "아니오", "B": "경계"}
HEAD = "id\t제목\t원제\t해\t매체\t첫 매체\t나라\t만든 이\t세계 한 줄\t붙은 개념\t알려진 근거\t이미 한 우주 판정"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def save(name, d):
    (DATA / name).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def clean(x):
    return str(x or "").replace("\t", " ").replace("\n", " ")


def make(work, size, cp):
    worlds = load("candidates_merged.json")["worlds"]
    sf, fm = load("space_filter.json")["worlds"], load("fame.json")["worlds"]
    done, last = set(), 0
    for f in glob.glob(os.path.join(work, "out_*.txt")):
        for line in open(f, encoding="utf-8"):
            if line.strip():
                done.add(line.split("\t")[0])
    for f in glob.glob(os.path.join(work, "in_*.tsv")):
        last = max(last, int(os.path.basename(f)[3:5]))
        for line in open(f, encoding="utf-8").read().splitlines()[1:]:
            if line:
                done.add(line.split("\t")[0])
    rows = []
    for w in worlds:
        i = w["id"]
        if w.get("researched") or i in done:
            continue
        need_s = i not in sf
        need_f = i not in fm and (need_s or sf[i]["space"] == "예" or i in cp)
        need_c = need_s or (i in cp and not sf[i].get("cyberpunk"))
        if not (need_s or need_f or need_c):
            continue
        rows.append("\t".join([i, clean(w["ko"]), clean(w["orig"]), clean(w["year"]), "/".join(w["media"]),
                               clean(w.get("first_medium")), clean(w.get("country")), clean(w.get("by"))[:40],
                               clean(w.get("setting")), ",".join(w.get("concepts") or []),
                               clean(w.get("notability"))[:120], sf.get(i, {}).get("space", "")]))
    n = last
    for k in range(0, len(rows), size):
        n += 1
        Path(work, f"in_{n:02d}.tsv").write_text(HEAD + "\n" + "\n".join(rows[k:k + size]) + "\n", encoding="utf-8")
    print(f"판정할 세계 {len(rows)} · 덩이 in_{last + 1:02d}~in_{n:02d}" if rows else "판정할 세계 없음")


def apply(work):
    sp, fm = load("space_filter.json"), load("fame.json")
    ids = {w["id"] for w in load("candidates_merged.json")["worlds"]}
    cnt, bad, seen = collections.Counter(), [], set()
    for f in sorted(glob.glob(os.path.join(work, "out_*.txt"))):
        name = os.path.basename(f)
        src = f.replace("out_", "in_").replace(".txt", ".tsv")
        want = [l.split("\t")[0] for l in open(src, encoding="utf-8").read().splitlines()[1:] if l]
        got = [l.split("\t") for l in open(f, encoding="utf-8").read().splitlines() if l.strip()]
        if [g[0] for g in got] != want:
            bad.append((name, "id 차례가 입력과 다름", len(got), len(want)))
            continue
        for g in got:
            if len(g) != 5 or g[1] not in V or len(g[2]) != 1 or g[2] not in "12345" or g[3] not in ("C", "-") \
                    or not g[4] or len(g[4]) > 30:
                bad.append((name, g))
                continue
            i, s, fa, c, why = g
            if i not in ids:   # 판정한 뒤 다른 세계와 합쳐져 사라진 id — 건너뛴다(합친 세계는 다음 make 에 다시 나온다)
                cnt["사라진 id"] += 1
                print("사라진 id 건너뜀:", name, i)
                continue
            if i in seen:
                bad.append((name, "덩이 사이에 겹침", i))
                continue
            seen.add(i)
            if i not in sp["worlds"]:
                sp["worlds"][i] = {"space": V[s], "why": why}
                cnt["우주 " + V[s]] += 1
            if c == "C" and not sp["worlds"][i].get("cyberpunk"):
                sp["worlds"][i]["cyberpunk"] = True
                cnt["사이버펑크"] += 1
            if i not in fm["worlds"]:
                fm["worlds"][i] = {"fame": int(fa), "why": "한꺼번에 매김"}
                cnt["알려진 정도 " + fa] += 1
    if bad:
        for x in bad[:30]:
            print("문제", x)
        raise SystemExit(f"문제 {len(bad)}건 — 아무것도 쓰지 않음")
    save("space_filter.json", sp)
    save("fame.json", fm)
    print("더함:", dict(sorted(cnt.items())))
    print("우주 판정", len(sp["worlds"]), "· 알려진 정도", len(fm["worlds"]))


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "make":
        cp = set(Path(sys.argv[4]).read_text(encoding="utf-8").split()) if len(sys.argv) > 4 else set()
        make(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 400, cp)
    elif len(sys.argv) == 3 and sys.argv[1] == "apply":
        apply(sys.argv[2])
    else:
        raise SystemExit(__doc__ or "쓰기: judge.py make <폴더> [크기] [후보 id 파일] | judge.py apply <폴더>")
