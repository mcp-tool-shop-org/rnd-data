"""Replace the local scratchpad prefix with <scratch> in every text file under a directory.

Usage: python redact_tree.py <dir>
"""
import pathlib
import re
import sys

PAT = re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\AppData\\Local\\Temp\\claude\\[^\\\s]+\\[^\\\s]+\\scratchpad\\")
for p in pathlib.Path(sys.argv[1]).rglob("*"):
    if p.is_file() and p.suffix in {".txt", ".md", ".json"}:
        t = p.read_text(encoding="utf-8")
        n = PAT.sub(r"<scratch>\\", t)
        if n != t:
            p.write_text(n, encoding="utf-8", newline="\n")
            print("redacted", p)
