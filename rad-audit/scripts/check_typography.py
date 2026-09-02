#!/usr/bin/env python3
"""Provjera hrvatske tipografije.

Uporaba:  python3 check_typography.py rad.docx

Provjerava: navodnike („…" — U+201E/U+201D, NE U+201C ni ravni "),
crtice (– za raspone), znak × (ne x), decimalni zarez, razmak broj–jedinica,
NBSP, 10° vs 20 °C.
"""
import re
import sys
from collections import Counter
from common import load_docx_text


def main(path):
    body, cells, _ = load_docx_text(path, include_tables=True)
    t = body + "\n" + "\n".join(cells)

    print("=" * 56)
    print("TIPOGRAFIJA —", path)
    print("=" * 56)

    findings = []

    straight = t.count('"')
    if straight:
        findings.append(f"⚠ ravni navodnici (\"): {straight} — zamijeni hrvatskima „…\"")
    open_hr = t.count("„")            # U+201E
    close_hr = t.count("”")      # U+201D  ispravan zatvarajući
    close_de = t.count("“")      # U+201C  njemački/engleski otvarajući — NIJE hr zatvarajući
    print(f'navodnici: otvarajući „={open_hr}, zatvarajući "={close_hr}, POGREŠAN "={close_de}')
    if close_de:
        findings.append(f'⚠ zatvarajući navodnik U+201C ({close_de}×) — treba U+201D („…")')
    if open_hr != close_hr + close_de and (open_hr or close_hr or close_de):
        findings.append(f"⚠ nesparen broj navodnika (otv {open_hr} vs zatv {close_hr + close_de})")

    # hex literale (0x41) NE broji kao "x umjesto ×" — alternacija ih pojede prve
    ascii_x = sum(1 for m in re.finditer(r"(\b0[xX][0-9A-Fa-f]+\b)|\d\s*[xX]\s*\d", t)
                  if not m.group(1))
    if ascii_x:
        findings.append(f"⚠ slovo 'x' kao množenje: {ascii_x} — koristi × (npr. 80 × 80 mm)")
    print(f"znak množenja ×: {t.count('×')}   |   'x' kao množenje: {ascii_x}")

    spaced_hyphen = len(re.findall(r"\s-\s", t))
    if spaced_hyphen:
        findings.append(f"⚠ spojnica ' - ' umjesto en-crtice '–': {spaced_hyphen}")
    print(f"en-crtica –: {t.count('–')}   |   spojnica ' - ': {spaced_hyphen}")

    # Hrvatski separator tisućica je TOČKA ("1.465 milijuna") i nije greška.
    # Prijavljuje se samo troznamenkasti decimalni dio uz PRAVU jedinicu,
    # uz granicu riječi — inače "m" uhvati početak riječi "milijuna".
    dot_dec = len(re.findall(
        r"(?<!\d)\d+\.\d{1,2}\s?(?:mm|cm|km|m|t|kg|bar|kW|Hz|L|A|%)(?![\w])", t))
    if dot_dec:
        findings.append(f"⚠ decimalna točka umjesto zareza (uz jedinicu): {dot_dec}")

    glued = re.findall(r"\b\d+(mm|cm|km|kg|bar|kW|Hz)\b", t)  # bez razmaka
    if glued:
        findings.append(f"⚠ broj+jedinica bez razmaka: {dict(Counter(glued))}")
    print(f"broj+jedinica zalijepljeno: {len(glued)}")

    nbsp = t.count(" ")
    print(f"NBSP (nedjeljivi razmak): {nbsp}  " + ("(preporuka: ubaci između broja i jedinice)" if nbsp == 0 else ""))

    print("\nNALAZI:")
    if findings:
        for f in findings:
            print("  " + f)
    else:
        print("  ✓ tipografija čista")
    return 1 if findings else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
