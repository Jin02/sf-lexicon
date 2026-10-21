#!/usr/bin/env bash
# 서버(iwinv)의 SF 개념 사전을 GitHub 최신으로 — 받아서 다시 만든다. 커밋·푸시한 뒤에 돌린다.
# 주소: https://sf.jinhyerimsync.duckdns.org — Caddy 가 /opt/sf-lexicon/dist/site 폴더만 내보낸다.
# 서버 운영 규칙은 sync-todo 레포의 docs/SERVER.md.
set -euo pipefail
KEY=~/.ssh/iwinv_jin
[ -f "$KEY" ] || KEY=~/.ssh/iwinv_laptop
ssh -n -i "$KEY" -o BatchMode=yes -o ConnectTimeout=15 root@115.68.222.81 \
  'cd /opt/sf-lexicon && git pull --ff-only -q && python3 scripts/build.py && git log -1 --format="%h %s"'
