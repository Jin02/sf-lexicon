"""검토를 마친 변경을 '커밋할 것'으로 적어 두고, 커밋해도 되는 때에 한꺼번에 커밋·푸시한다.

진님(2026-10-20): "커밋은 12시 넘어서 해라", "아님 휴일에". 낮에 끝낸 조사는 바로 커밋하지 않고 여기에 적어 둔다.
적어 둔 목록은 data/ready.json(레포에 올리지 않음).

    python scripts/ready.py add "커밋 메시지 첫 줄" [--body "둘째 줄부터"] 파일 [파일 …]
    python scripts/ready.py list
    python scripts/ready.py commit     # 커밋해도 되는 때이고 점검이 통과하면, 적힌 차례대로 커밋하고 푸시
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "data" / "ready.json"
TRAILER = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
sys.path.insert(0, str(ROOT / "scripts"))
import commit_window  # noqa: E402


def load():
    if READY.exists():
        return json.loads(READY.read_text(encoding="utf-8"))
    return []


def save(items):
    READY.write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=ROOT, check=check, capture_output=True, text=True, encoding="utf-8")


def add(argv):
    msg, body, files = argv[0], "", []
    i = 1
    while i < len(argv):
        if argv[i] == "--body":
            body = argv[i + 1]
            i += 2
        else:
            files.append(argv[i])
            i += 1
    missing = [f for f in files if not (ROOT / f).exists() and git("ls-files", "--error-unmatch", f, check=False).returncode != 0]
    if missing:
        sys.exit(f"없는 파일: {missing}")
    items = load()
    items.append({"message": msg, "body": body, "files": files})
    save(items)
    print(f"적어 둠({len(items)}번째): {msg} — 파일 {len(files)}개")


def commit():
    ok, why = commit_window.check()
    if not ok:
        sys.exit("커밋 안 됨: " + why)
    items = load()
    if not items:
        print("커밋할 것 없음")
        return
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "check.py")], cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                       env={**__import__("os").environ, "PYTHONUTF8": "1"})
    if "틀린 곳 없음" not in r.stdout:
        sys.exit("점검이 통과하지 않아 커밋하지 않음:\n" + r.stdout[-2000:])
    git("reset", "-q")   # 다른 것이 올라가 있지 않게
    done = 0
    for it in items:
        git("add", "-A", "--", *it["files"])
        if not git("diff", "--cached", "--name-only").stdout.strip():
            continue
        text = it["message"] + ("\n\n" + it["body"] if it.get("body") else "") + "\n\n" + TRAILER
        git("commit", "-q", "-m", text)
        done += 1
    if done:
        git("push", "-q", "origin", "HEAD")
    save([])
    print(f"커밋 {done}개, 푸시 {'함' if done else '할 것 없음'} ({why})")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "add":
        add(sys.argv[2:])
    elif cmd == "commit":
        commit()
    else:
        for i, it in enumerate(load(), 1):
            print(i, it["message"], "|", " ".join(it["files"]))
