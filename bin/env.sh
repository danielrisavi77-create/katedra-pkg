#!/usr/bin/env bash
# katedra-pkg — okolina za jedan bash poziv.
# Svaki bash poziv u Cowork sesiji kreće iz čiste ljuske, pa se ovo source-a
# na početku SVAKOG poziva:   . "${KATEDRA_PKG:-$HOME/.katedra-pkg}/bin/env.sh"
#
# Izvozi: KATEDRA_PKG, KATEDRA_SKILL, RAD_AUDIT_HOME, RAD_DOCX_HOME,
#         FPZG_DIPLOMSKI_HOME, REPLIKACIJA_PSPP_HOME, RAD_ORCHESTRATOR_HOME,
#         KATEDRA_PKG_VERZIJA
# Ne mijenja cwd. Ne ispisuje ništa osim uz KATEDRA_ENV_GLASNO=1.

_kp="${KATEDRA_PKG:-}"
if [ -z "$_kp" ]; then
  # tražimo korijen paketa: env → $HOME/.katedra-pkg → mapa ove skripte
  if [ -f "$HOME/.katedra-pkg/katedra-lite/scripts/gate.py" ]; then
    _kp="$HOME/.katedra-pkg"
  else
    _kp="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  fi
fi
export KATEDRA_PKG="$_kp"
export KATEDRA_SKILL="$KATEDRA_PKG/katedra-lite"
export RAD_AUDIT_HOME="$KATEDRA_PKG/rad-audit"
export RAD_DOCX_HOME="$KATEDRA_PKG/rad-docx"
export FPZG_DIPLOMSKI_HOME="$KATEDRA_PKG/fpzg-diplomski"
export REPLIKACIJA_PSPP_HOME="$KATEDRA_PKG/replikacija-pspp"
export RAD_ORCHESTRATOR_HOME="$KATEDRA_PKG/rad-orchestrator"
export KATEDRA_PKG_VERZIJA="$(cat "$KATEDRA_PKG/VERSION" 2>/dev/null || echo nepoznato)"
unset _kp

if [ "${KATEDRA_ENV_GLASNO:-0}" = "1" ]; then
  echo "katedra-pkg $KATEDRA_PKG_VERZIJA @ $KATEDRA_PKG"
  for v in KATEDRA_SKILL RAD_AUDIT_HOME RAD_DOCX_HOME FPZG_DIPLOMSKI_HOME REPLIKACIJA_PSPP_HOME; do
    if [ -d "${!v}" ]; then echo "  ✅ $v"; else echo "  ❌ $v (nema mape)"; fi
  done
fi
