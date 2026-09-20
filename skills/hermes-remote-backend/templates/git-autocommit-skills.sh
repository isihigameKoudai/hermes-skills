#!/bin/bash
# Skills-tree git autocommit for a `no_agent: true` cron job (zero LLM, zero credit).
# PLACE on the HOST at ~/.hermes/scripts/git-autocommit-skills.sh (NOT in the sandbox
# /root/.hermes/scripts — that tree is not the host's). Stage via /workspace + user cp,
# then create the cron with: no_agent=true, script='git-autocommit-skills.sh',
# schedule='*/5 * * * *', deliver='local'.
# Self-initialises on first run: git init, .gitignore, git user, then commits only on diff.
set -u
SKILLS_DIR="${HERMES_HOME:-$HOME/.hermes}/skills"
cd "$SKILLS_DIR" || { echo "ERROR: cannot cd $SKILLS_DIR" >&2; exit 1; }

[ -d .git ] || git init -q

[ -f .gitignore ] || printf '%s\n' \
  '.curator_backups/' '.archive/' '.hub/' '__pycache__/' '*.pyc' \
  '.usage.json' '.usage.json.lock' > .gitignore

[ -n "$(git config user.email 2>/dev/null)" ] || git config user.email "hermes@localhost"
[ -n "$(git config user.name  2>/dev/null)" ] || git config user.name  "Hermes Agent"

git add -A || exit 1
git diff --cached --quiet && exit 0          # no diff → empty stdout (silent tick)
git commit -q -m "auto $(date -u +%Y-%m-%dT%H:%M:%SZ)" || exit 1
exit 0
