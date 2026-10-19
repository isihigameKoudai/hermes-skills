#!/usr/bin/env bash
# 移植したスキルが clone 実体のままか（コピーか手書きか）を sha256 で示す。
# 使い方: verify-port-fidelity.sh <clone側のdir> <インストール側のdir> [--expect-diff SKILL.md]...
#   意図して編集したファイルは --expect-diff で渡す（「differs (expected)」と出る）
#   DIFFERS/MISSING が 1 件でもあれば exit 1。EXTRA は移植先にしかないファイル（情報提供のみ）
set -u

if [ $# -lt 2 ]; then
  sed -n '2,6p' "$0"; exit 2
fi

ORIG=$1; INST=$2; shift 2
EXPECT=()
while [ $# -gt 0 ]; do
  case "$1" in
    --expect-diff) EXPECT+=("${2:-}"); shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

[ -d "$ORIG" ] || { echo "ERROR: not a dir: $ORIG" >&2; exit 2; }
[ -d "$INST" ] || { echo "ERROR: not a dir: $INST" >&2; exit 2; }

is_expected() {
  local rel=$1 e
  for e in ${EXPECT[@]+"${EXPECT[@]}"}; do [ "$rel" = "$e" ] && return 0; done
  return 1
}

same=0; diffn=0; missing=0; expected=0; extra=0
printf '%-52s %-17s %-17s %s\n' "file" "clone" "installed" "status"

while IFS= read -r -d '' f; do
  rel=${f#"$ORIG"/}
  a=$(sha256sum "$f" | cut -c1-16)
  if [ ! -f "$INST/$rel" ]; then
    printf '%-52s %-17s %-17s %s\n' "$rel" "$a" "-" "MISSING"
    missing=$((missing+1)); continue
  fi
  b=$(sha256sum "$INST/$rel" | cut -c1-16)
  if [ "$a" = "$b" ]; then
    printf '%-52s %-17s %-17s %s\n' "$rel" "$a" "$b" "identical"
    same=$((same+1))
  elif is_expected "$rel"; then
    printf '%-52s %-17s %-17s %s\n' "$rel" "$a" "$b" "differs (expected)"
    expected=$((expected+1))
  else
    printf '%-52s %-17s %-17s %s\n' "$rel" "$a" "$b" "DIFFERS"
    diffn=$((diffn+1))
  fi
done < <(find "$ORIG" -type f -not -path '*/.git/*' -not -path '*/__pycache__/*' -print0 | sort -z)

while IFS= read -r -d '' f; do
  rel=${f#"$INST"/}
  if [ ! -f "$ORIG/$rel" ]; then
    printf '%-52s %-17s %-17s %s\n' "$rel" "-" "$(sha256sum "$f" | cut -c1-16)" "EXTRA"
    extra=$((extra+1))
  fi
done < <(find "$INST" -type f -not -path '*/__pycache__/*' -print0 | sort -z)

echo
echo "identical=$same expected-diff=$expected DIFFERS=$diffn MISSING=$missing EXTRA=$extra"
if [ "$diffn" -ne 0 ] || [ "$missing" -ne 0 ]; then exit 1; fi
