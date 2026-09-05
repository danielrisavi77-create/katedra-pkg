#!/usr/bin/env bash
# Pokreni sve testove paketa. Jedan ulaz, jedan izlazni kod.
#
# Zašto postoji: testovi su bili razasuti po skillovima i nitko ih nije pokretao
# u cjelini, pa je "82/82 prolazi" u jednom SKILL.md-u stajalo uz 87 stvarnih
# testova i uz manifest koji se razišao s kodom.
set -uo pipefail
KORIJEN="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UKUPNO=0
PALO=0

pokreni() {
  local naziv="$1"; shift
  echo ""
  echo "── $naziv ────────────────────────────────────────────"
  if "$@"; then
    echo "   ✅ $naziv"
  else
    echo "   ❌ $naziv (izlazni kod $?)"
    PALO=$((PALO + 1))
  fi
  UKUPNO=$((UKUPNO + 1))
}

pokreni "rad-audit: regresije" \
  python3 "$KORIJEN/rad-audit/scripts/tests/test_all.py"
pokreni "rad-audit: bolesni rad mora pasti" \
  python3 "$KORIJEN/rad-audit/scripts/tests/test_bolesni.py"
pokreni "katedra-lite: gate" \
  python3 "$KORIJEN/katedra-lite/scripts/tests/test_gate.py"

for skill in katedra katedra-lite rad-audit rad-docx fpzg-diplomski replikacija-pspp; do
  pokreni "tvrdnje: $skill" \
    python3 "$KORIJEN/katedra/scripts/zakrpa.py" --provjeri-tvrdnje "$KORIJEN/$skill"
done

echo ""
echo "══════════════════════════════════════════════════════"
if [ "$PALO" -eq 0 ]; then
  echo "✅ svih $UKUPNO skupina prošlo"
else
  echo "❌ $PALO od $UKUPNO skupina palo"
fi
exit "$PALO"
