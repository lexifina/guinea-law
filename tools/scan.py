"""Searches the cached Journal officiel issues for a pattern (to find the laws amending an act). Cache only.

    python -X utf8 scripts/guinea-law/scan.py REGEX [FROM] [TO]

Issues without a text layer are reported as scans, and unreadable files as such.
"""
import re
import sys

import fitz
import gncache as c
from jo_index import jo_index


def main(pat, lo='0000', hi='9999'):
    rx = re.compile(pat, re.I)
    for r in sorted(jo_index(), key=lambda r: (r['date'], r['url'])):
        if not lo <= r['date'] <= hi:
            continue
        if not c.cached(r['url']):
            print(r['date'], r['url'], 'NOT CACHED')
            continue
        try:
            d = fitz.open(c.cached(r['url']))
            t = '\n'.join(p.get_text() for p in d)
        except Exception as e:  # noqa: BLE001
            print(r['date'], r['url'], 'UNREADABLE', type(e).__name__)
            continue
        if len(t.strip()) < 200 * max(1, len(d) // 4):
            print(r['date'], r['url'], f'SCAN (text layer {len(t.strip())} chars, {len(d)} pages)')
            continue
        flat = ' '.join(t.split())
        for m in rx.finditer(flat):
            print(r['date'], r['url'].rsplit('/', 1)[-1], '|', flat[max(0, m.start() - 100):m.end() + 160])


if __name__ == '__main__':
    main(*sys.argv[1:])
