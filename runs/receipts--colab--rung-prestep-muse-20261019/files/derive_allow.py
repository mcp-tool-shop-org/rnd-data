"""PRESTEP_ALLOW_MISMATCH's indices (R&D, 2026-10-19): the TOKENIZER_STRINGS whose letters are all outside the Latin
script. A string with any Latin letter, or with no letters at all (digits, symbols, emoji), is not allowed: English
critic items can contain those."""
import json, sys, unicodedata
sys.path.insert(0, sys.argv[1])
import pin_window as pw
rows = []
for i, s in enumerate(pw.TOKENIZER_STRINGS):
    letters = [c for c in s if c.isalpha()]
    scripts = sorted({unicodedata.name(c, "?").split()[0] for c in letters})
    allowed = bool(letters) and not any("LATIN" in unicodedata.name(c, "") for c in letters)
    rows.append({"i": i, "text": s, "letter_scripts": scripts, "allowed": allowed})
allow = [r["i"] for r in rows if r["allowed"]]
print(json.dumps({"allow": allow, "rows": rows}, ensure_ascii=False, indent=1))
