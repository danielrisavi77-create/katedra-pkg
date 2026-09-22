#!/usr/bin/env bash
# rad-orchestrator — dohvat katedra-pkg paketa. SOURCE-a se (". bootstrap.sh"), ne pokreće,
# jer izvozi KATEDRA_PKG, KATEDRA_SKILL i <SLUG>_HOME u pozivajuću ljusku.
#
# Zašto datoteka, a ne blok u SKILL.md-u: blok od ~1,5 KB basha učitavao se u kontekst pri
# svakom pokretanju skilla, iako ga agent samo izvršava (v2.4, štednja tokena). Ponašanje je
# isto kao u starom bloku, OSIM tokena: GitHub token se više ne ugrađuje u URL
# (katedra-lite/references/runtime.md: "Ne ugrađuj GitHub tokene u URL, naredbu, log ili
# skill"). Privatni repo ide kroz autoriziranu vezu sesije ili priloženi zip/bundle.
#
# Redoslijed izvora (runtime.md): 1) priloženi katedra-pkg*.zip/*.bundle  2) postojeći git
# klon (pull --ff-only)  3) anonimni clone  4) synced kopija skilla kao zadnja rezerva.

export KATEDRA_PKG="${KATEDRA_PKG:-$HOME/.katedra-pkg}"
KATEDRA_PKG_URL="${KATEDRA_PKG_URL:-https://github.com/danielrisavi77-create/katedra-pkg.git}"

_P="$(find /root/.claude/uploads "$HOME/uploads" /mnt/user-data . -maxdepth 4 \
  \( -iname 'katedra*pkg*.zip' -o -iname 'katedra*pkg*.bundle' \) -printf '%T@ %p\n' 2>/dev/null \
  | sort -rn | head -1 | cut -d' ' -f2-)"
if [ -n "$_P" ]; then
  rm -rf "$KATEDRA_PKG"
  case "$_P" in
    *.bundle) git clone -q "$_P" "$KATEDRA_PKG" ;;
    *) mkdir -p "$KATEDRA_PKG" && unzip -oq "$_P" -d "$KATEDRA_PKG" && {
         [ -f "$KATEDRA_PKG/bin/env.sh" ] || {
           _D="$(ls -d "$KATEDRA_PKG"/*/ | head -1)"
           [ -f "$_D/bin/env.sh" ] && mv "$_D"/* "$_D"/.[!.]* "$KATEDRA_PKG"/ 2>/dev/null
         }
       } ;;
  esac
  echo "📦 paket iz priloga: $_P"
fi

if [ -d "$KATEDRA_PKG/.git" ]; then
  find "$KATEDRA_PKG" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null
  git -C "$KATEDRA_PKG" pull -q --ff-only 2>/dev/null || true
elif [ ! -f "$KATEDRA_PKG/bin/env.sh" ]; then
  case "$KATEDRA_PKG_URL" in
    *@github.com*) echo "⛔ KATEDRA_PKG_URL nosi vjerodajnicu u URL-u; ne koristi se (runtime.md)" ;;
    *) git clone -q --depth 1 "$KATEDRA_PKG_URL" "$KATEDRA_PKG" 2>/dev/null || true ;;
  esac
fi

if [ -f "$KATEDRA_PKG/bin/env.sh" ]; then
  . "$KATEDRA_PKG/bin/env.sh"
  echo "katedra-pkg $KATEDRA_PKG_VERZIJA"
else
  KATEDRA_SKILL="$(ls -d /root/.claude/skills/synced/*/katedra-lite ~/.claude/skills/katedra-lite 2>/dev/null | head -1)"
  export KATEDRA_SKILL
  echo "⚠️ paket nije dostupan: priloži katedra-pkg-vX.zip u chat ili priključi repo sesiji; do tada synced kopija: $KATEDRA_SKILL (skripte mogu biti starije od SKILL.md-a)"
fi
unset _P _D
