# 공개로 돌리기 (한 번만)

진님(2026-10-20 밤): "이거 repo는 github에 올려도 되겠네", "public", "근데 커밋은 12시 넘어서 해라", "아님 휴일에".
지금까지의 커밋은 평일 낮 시각이 많아서, **공개 전에 지난 기록을 커밋 하나로 합친다**(진님 규약: 공유 레포는 단일 커밋으로 합친다). 합친 커밋도 밤 0시 넘어서 만든다.
예약 작업 `sf-lexicon-go-public`(2026-10-21 0시 10분, 한 번)이 이 순서를 따른다.

## 순서

1. `cd C:\Users\jin0x\dev\sandbox\sf-lexicon`. `python scripts/commit_window.py` 가 '커밋해도 됨'이 아니면 멈추고 보고한다.
2. `git fetch` 뒤 `git status`. 로컬 `main` 이 `origin/main` 과 같아야 한다(앞서거나 갈렸으면 멈추고 보고).
3. `PYTHONUTF8=1 python scripts/check.py` 가 '틀린 곳 없음'이 아니면 멈추고 보고한다.
4. `PYTHONUTF8=1 python scripts/ready.py commit` — 검토를 마치고 적어 둔 변경을 커밋·푸시한다.
   적히지 않은 변경(검토 전 파일)은 그대로 두고 건드리지 않는다.
5. 공개해도 되는지 훑는다: 올라간 파일(`git ls-files`)에서 전자우편 주소·비밀번호·열쇠 같은 것이 없는지 `git grep -n -i -E "@gmail|password|api[_-]?key|secret|token"` 으로 본다. 나오면 멈추고 보고한다(근거 글 안의 평범한 낱말이면 괜찮다 — 무엇이 걸렸는지 적는다).
6. 지난 기록을 로컬 가지에 남긴다: `git branch backup/private-history-2026-10-20 main` (푸시하지 않는다).
7. 지금 내용 그대로 커밋 하나를 만든다:
   - `NEW=$(git commit-tree HEAD^{tree} -F <메시지 파일>)` — 메시지: 첫 줄 `SF 개념 사전 — 공개`, 빈 줄, 개념·작품·용어·세계 수와 '2026-10-19~20 private 레포의 기록을 하나로 합침' 한 줄, 빈 줄, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
   - `git reset --soft $NEW` (작업 폴더의 검토 전 변경은 그대로 남는다).
   - `git log --oneline` 이 한 줄인지 본다.
8. `git push --force-with-lease origin main`.
9. 공개로 돌린다: `"C:\Program Files\GitHub CLI\gh.exe" repo edit Jin02/sf-lexicon --visibility public --accept-visibility-change-consequences`.
   막히면(권한·분류기) 억지로 하지 말고, 진님이 직접 칠 이 명령 한 줄과 함께 보고한다.
10. `gh repo view Jin02/sf-lexicon --json visibility` 가 PUBLIC 인지, 원격 기록이 커밋 하나인지 확인한다.

## 보고 (짧게, 한국어)

- 공개됐는지, 합친 커밋 이름, 남겨 둔 로컬 가지 이름, 커밋한 적어 둔 변경 수, 걸린 것.
