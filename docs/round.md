# 정기 조사 한 차례

진님 말(2026-10-19): "조사 비용이 커도 돼. 천천히 계속 주기적으로 하면 되지." — 찾은 세계를 차례대로 조금씩 조사하고, 세계 목록도 계속 넓힌다.
예약 작업 `sf-lexicon-round`(매일)가 이 문서를 따라 한 차례를 돈다. 손으로 돌릴 때도 같다.

## 한 차례 = 조사 에이전트 다섯 (동시에) — 새 작품 둘 · 로어 둘 · 손질 하나

- ★2026-10-20 부터 **새 작품 둘 + 로어 깊게 보기 둘**(진님: "너무 요약하면 이런걸 모르지" — `docs/lore_brief.md`). 로어는 `docs/lore_brief.md` 의 '차례'에서 아직 안 한 위의 둘.
- **새 작품 둘**: `PYTHONUTF8=1 python scripts/queue.py next 2` 가 고른 곳(같은 매체 둘까지). ★우주와 관련된 세계만(`data/space_filter.json` 이 '예'인 곳) 차례에 든다 — 사이버펑크는 우주가 아니어도 든다(진님 "사이버 펑크 종류도 추가하자", space_filter 의 `"cyberpunk": true`). 세계 더 찾기로 새로 들어온 세계는 판정이 없으니, 그 차례 끝에 같은 기준으로 판정을 더한다.
  ★영화로 시작한 세계는 차례에 들지 않고(진님 "영화도 좀 빼자 그냥"), 마이너한 쪽이 먼저 온다(진님 "좀 마이너한쪽 SF면 좋겠어" — `data/fame.json`). 새로 들어온 세계에는 알려진 정도(1~5)도 그 차례 끝에 더한다.
  ★슈퍼히어로 계열(DC·마블·인빈시블·벤10, 테카맨 같은 변신·강화 히어로물, 실버호크·스티븐 유니버스 같은 히어로 만화영화)은 조사하지 않는다(군대·나라가 만든 강화 병사가 나오는 전쟁 SF — 헤일로의 스파르탄, 워해머의 스페이스 마린 같은 것 — 는 슈퍼히어로가 아니다) — 새로 들어온 세계를 판정할 때 이런 곳은 `data/queue_manual.json` 의 skip 에 까닭과 함께 넣는다.
- **손질 하나** — ★진님(2026-10-20): "지구상 이제까지 만들어진 sf 모든 작품을 찾아서 정리한다" — **세계 더 찾기가 기본**이다: `docs/sweep_sources.md` 에서 아직 안 한(`[ ]`) 맨 위 한 줄을 `[~]` 로 표시하고 맡긴다. 지침은 `docs/survey_brief.md`(★'많이 훑을 때') + 그 문서의 '더 찾기' 절. 에이전트에게 `merge_candidates.py` 는 돌리지 말라고 하고, 끝나면 내가 합친다.
  - 차례 번호(`data/rounds.json` 의 마지막 `n` + 1)가 4의 배수일 때만 세계 더 찾기 대신 **우리 표기 다시 찾기**(`docs/recheck_brief.md` 1절)나 **한국어판 '확인 못 함' 다시 보기**(2절, 40곳씩)를 번갈아.
  - 세계 더 찾기로 들어온 새 세계에는 차례 끝에 우주 판정(`data/space_filter.json`, 사이버펑크면 `"cyberpunk": true`)과 알려진 정도(`data/fame.json`)를 더한다.
- 웹 검색 한도(한 차례 200회 남짓)를 다섯이 나눠 쓴다. 다 쓰면 그 차례는 거기까지.

## ★커밋하는 때 (진님 2026-10-20: "커밋은 12시 넘어서 해라", "아님 휴일에")

- 이 레포는 공개 레포다. **커밋은 밤 0시~9시 전, 또는 주말·공휴일에만** 한다 — `python scripts/commit_window.py` 가 판정한다.
- 차례 중에 검토를 마친 것은 바로 커밋하지 말고 `python scripts/ready.py add "메시지" 파일…` 로 적어 둔다.
  예약 작업 `sf-lexicon-night-commit`(매일 0시 20분)이 `python scripts/ready.py commit` 으로 적힌 차례대로 커밋·푸시한다.
- 지금이 커밋해도 되는 때라면 차례 끝에 직접 `python scripts/ready.py commit` 을 돌려도 된다.
- 커밋 날짜를 바꾸는 꾀(GIT_COMMITTER_DATE 등)는 쓰지 않는다.

## 순서

1. `git pull` 뒤 `CLAUDE.md` · `docs/research_brief.md` · 이 문서를 읽는다.
2. 다섯을 배경으로 띄운다(Agent, general-purpose). 맡길 글에 꼭 넣을 것:
   - 지침 파일 경로, 작품 id, 후보 칸(`data/candidates_merged.json` 의 그 세계: series·media·lore_size·korean), 세계 크기에 맞춘 용어 수.
   - 스크래치 폴더 안 `<작품 id>` 하위 폴더만 쓸 것.
   - **개인 정보(이름·전자우편)를 어떤 요청에도 넣지 말 것.** 처음 여는 사이트는 robots.txt 부터, 봇 확인 화면은 풀지 말 것. 파일을 내려받아 실행하지 말 것.
   - 커밋하지 말 것. 다른 작품 파일·`concepts.json` 을 고치지 말 것.
3. 하나씩 끝나는 대로:
   - `PYTHONUTF8=1 python scripts/review_dump.py <id> <스크래치>/rev_<id>.txt` 로 뽑아 **전부 읽는다**. 누설(반전이 한 줄·설명·근거에 드러남), 남의 글 옮김, 인물, 개념 잘못 잇기를 고친다.
   - 이어 줄 개념이 있으면 `scripts/concepts_r2.json` 의 `links` 에 더하고 `python scripts/apply_concepts_r2.py`.
   - `python scripts/merge_works.py` → `python scripts/check.py`(틀린 곳 0) → 그 작품 파일만 골라 `python scripts/ready.py add "한국어 메시지" 파일…` 로 적어 둔다(커밋은 위 '커밋하는 때'에).
   - 손질 결과도 같은 식으로 검토 후 적어 둔다. 세계 더 찾기는 `python scripts/merge_candidates.py` → `python scripts/candidates_doc.py` 뒤 적어 둔다.
4. 다섯이 다 끝나면 `python scripts/queue.py` · `python scripts/build.py` → 미리보기(`.claude/launch.json` 의 `sf-lexicon`, 포트 8340 `local.html`)로 새 작품 쪽과 개념 쪽을 확인.
5. 화면을 다시 올린다: Artifact `read` 로 https://claude.ai/artifact/VJKi9nQhEiwiTV3wDPMNKj 를 읽은 뒤, 같은 `url` 로 `dist/index.html` 을 publish.
6. 에이전트 기록(`~/.claude/projects/<프로젝트>/<세션>/subagents/*.jsonl`)에서 진님 전자우편이 도구 호출에 들어갔는지 훑는다(시스템 안내 문장 말고).
7. `data/rounds.json` 에 한 줄 더하고(`n, date, works, upkeep, terms_added, notes`) 적어 둔다.
8. 개념 제안(`data/concept_proposals/*.json`)을 `docs/concept_ideas.md` 에 모은다. **세 차례마다** 되풀이된 생각을 묶어 새 개념 차례(`scripts/concepts_r<N>.json`, r2 와 같은 꼴)를 만든다.
9. 보고는 짧게: 새 작품과 용어 수(공식 원자료·2차·우리 표기), 손질 결과, 남은 곳 수, 걸린 것.

## 멈출 때

- 같은 사이트에서 봇 확인이 거듭 뜨거나, 검색 한도가 바닥나면 그 차례는 거기서 마무리한다(다 된 것만 올린다).
- 진님이 순서를 바꾸고 싶으면 `data/queue_manual.json` (`first` · `skip` · `last` 에 세계 id).
