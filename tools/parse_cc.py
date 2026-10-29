"""Guinea: the Code civil (Loi L/2019/035/AN du 04 juillet 2019) -> corpus.d/50-code-civil.json. Cache only (no OCR).

    python -X utf8 scripts/guinea-law/parse_cc.py [--check]

Source: the Journal officiel spécial of August 2019 that printed the Code civil (born-digital, text layer; published on
the SGG "Codes en vigueur" page), read with
the column and paragraph rules of parse.py. Articles are one unit each; the structural headings (Livre, Titre,
Chapitre, Section, Paragraphe and lettered sub-headings) go into one "plan" unit, each followed by the first article
under it. --check prints the verification: every character of
the text layer from the enacting formula to the Assembly's signature is in exactly one unit in order, and article
numbers run 1 to 1636 without a gap.
"""
import json
import os
import re
import sys

import fitz
import gncache as c
import parse

HERE = os.path.dirname(os.path.abspath(__file__))
# The SGG publishes this Journal officiel spécial (August 2019, pages 02-85) only on its "Codes en vigueur" page; the
# listing's guinee-jo-2019-08-02-sp.pdf is a different special issue (mining texts of 2014).
SRC = 'https://journal-officiel.sgg.gov.gn/codes/guinee-code-2019-civil.pdf'
START = 'Après en avoir délibéré, a adopté la loi dont la teneur suit :'
STOP = 'Conakry, le 04 Juillet 2019'
PART = os.path.join(HERE, 'corpus.d', '50-code-civil.json')
RETRIEVED = '2026-10-29'

# "Article 12 :", and two misprints the Journal officiel carries: "Articule 153 :" and "Article 80 6:".
ART = re.compile(r'^Artic(?:le|ule)\s*(premier|1er|\d+(?: \d)?)\s*(bis|ter)?\s*[:.]\s*')
HEAD = re.compile(r'^(LIVRE|TITRE|TITTRE|CHAPITRE|SECTION|SOUS-SECTION|Sous-section|Paragraphe|PARAGRAPHE|'
                  r'DISPOSITIONS?)\b')
# lettered and numbered sub-headings: "A- Du …", "E - Du …", "A: Du …", "I- La capacité"
LETTER_HEAD = re.compile(r'^(?:[A-Z]\s?[-:]\s*(?=[A-ZÀ-Ý])|[IVX]+\s?[-.]\s*(?=[A-Za-zÀ-ÿ]))')
# a heading run onto the end of the previous paragraph at a column or page break ("… constituée. DISPOSITIONS
# FINALES", "… est guinéen. Paragraphe 2 : De l'acquisition …", "… est nulle. B- Du cheptel …")
TAIL = re.compile(r'(?<=[.;!?»)])\s+((?:LIVRE|TITRE|TITTRE|CHAPITRE|SECTION|DISPOSITIONS?)\b[^a-zà-ÿ]*'
                  r'|Paragraphe\s+\d+\s*:[^.;:]*|(?:[A-Z]|[IVX]+)\s?[-:]\s*(?:Du|De|Des|La|Le|Les|L\'|D\')\b[^.;:]*)$')
SMALL = 6.0  # points: superscripts ("10ème", "7/12ème") and stray hyphen marks are set at 4.5 pt, body text at 9 pt


def caps(p):
    return not re.search(r'[a-zà-ÿ]', p) and re.search(r'[A-Z]', p) is not None


STATS = {'superscripts': 0, 'marks_dropped': 0}


def cc_lines(pdf):
    """parse.lines(), after one correction made on the page: each 4.5-pt superscript ("ème", "er") is put back into
    the line it belongs to, at its x position (the text layer stores it as a separate line above), and the stray
    4.5-pt hyphen marks are dropped."""
    d = fitz.open(pdf)
    out = []
    STATS.update(superscripts=0, marks_dropped=0)
    for i in range(len(d)):
        p = d[i]
        w = p.rect.width
        rows = []
        for b in p.get_text('rawdict')['blocks']:
            for l in b.get('lines', []):
                chars = [ch for sp in l['spans'] for ch in sp['chars']]
                t = ''.join(ch['c'] for ch in chars)
                if not t.strip():
                    continue
                small = all(sp['size'] < SMALL for sp in l['spans'] if ''.join(ch['c'] for ch in sp['chars']).strip())
                rows.append({'bbox': list(l['bbox']), 'chars': chars, 't': t, 'small': small})
        hosts = [r for r in rows if not r['small']]
        for r in rows:
            if not r['small']:
                continue
            s = r['t'].strip()
            if not re.search(r'[A-Za-zÀ-ÿ]', s):
                STATS['marks_dropped'] += 1
                continue
            x0, y0, x1, y1 = r['bbox']
            cand = [h for h in hosts if h['bbox'][0] - 2 <= x0 <= h['bbox'][2] + 3 and
                    min(y1, h['bbox'][3]) - max(y0, h['bbox'][1]) > 0]
            if len(cand) != 1:
                raise ValueError(f'page {i + 1}: superscript {s!r} at {r["bbox"]} has {len(cand)} host lines')
            h = cand[0]
            pos = sum(1 for ch in h['chars'] if (ch['bbox'][0] + ch['bbox'][2]) / 2 < x0)
            h['t'] = h['t'][:pos] + s + h['t'][pos:]
            h['chars'] = h['chars'][:pos] + [{'c': ch, 'bbox': (x0, y0, x1, y1)} for ch in s] + h['chars'][pos:]
            STATS['superscripts'] += 1
        ls = []
        for h in hosts:
            x0, y0, x1, y1 = h['bbox']
            t = h['t']
            if parse.HEADER.search(t) and (y0 < 32 or y0 > p.rect.height - 40):
                continue
            col = 1 if x0 >= w * 0.48 else (0 if x1 <= w * 0.53 else 2)
            ls.append((y0, x0, x1, col, t))
        ls.sort()
        right = {k: max([x1 for _, _, x1, cc, _ in ls if cc == k] or [0]) for k in (0, 1, 2)}
        band = []

        def flush():
            for k in (0, 1):
                out.extend((y, a, b2, cc, t, right[cc]) for (y, a, b2, cc, t) in sorted(l for l in band if l[3] == k))
            band.clear()
        for l in ls:
            if l[3] == 2:
                flush()
                out.append(l + (right[2],))
            else:
                band.append(l)
        flush()
    return out


def cc_paragraphs(ls):
    """parse.paragraphs(), except that a line ending in . ; : ! ? or » closes its paragraph when it stops more than
    5 pt short of the justified column edge (parse.py uses 15 pt; this issue sets the last line of many paragraphs
    6-15 pt short)."""
    keep = parse.hyphen_words(ls)
    paras, cur, pending = [], '', False
    prev = None
    for line in ls:
        (y, x0, x1, col, t, right) = line
        s = parse._clean(t)
        gap = prev is not None and prev[3] == col and y - prev[0] >= parse.PARA_GAP
        prev = line
        if s == '•':
            if cur:
                paras.append(cur)
            cur, pending = '• ', False
            continue
        if cur and not cur.endswith('• '):
            mid_sentence = not parse.END.search(cur.rstrip(parse.SOFT + '-')) and parse.CONTINUES.match(s) and not parse.ART.match(s)
            if (pending or (gap and parse.END.search(cur))) and not mid_sentence:
                paras.append(cur)
                cur = ''
        pending = False
        if cur.endswith(parse.SOFT):
            cur = cur[:-1] + s
        elif cur and not cur.endswith('• ') and (parse.ART.match(s) or parse.HEADING.match(s)):
            paras.append(cur)
            cur = s
        elif re.search(r'\w-$', cur) and parse.CONTINUES.match(s):
            left = re.search(r'([\w’]+)-$', cur).group(1)
            right_part = re.match(r'[\w’]+', s).group(0) if re.match(r'[\w’]+', s) else ''
            if (left.lower(), right_part.lower()) in keep or left.lower() in parse.COMPOUND:
                cur = cur + s
            else:
                cur = cur[:-1] + s
        else:
            cur = (cur + ' ' + s) if cur and not cur.endswith('• ') else cur + s
        if (x1 < right - 15 or (x1 < right - 5 and parse.END.search(s.rstrip()))) and not s.endswith(parse.SOFT):
            pending = True
    if cur:
        paras.append(cur)
    return [re.sub(r'\s+', ' ', p.replace(parse.SOFT, '')).strip() for p in paras if p.strip()]



def body(url, lines=None):
    pdf = c.cached(url)
    paras = cc_paragraphs(lines if lines is not None else cc_lines(pdf))
    i = paras.index(START)
    j = next(k for k in range(i + 1, len(paras)) if paras[k].startswith(STOP))
    out = []
    for p in paras[i + 1:j]:
        if p.startswith(',') and out:
            out[-1] = out[-1] + p  # "lésion de plus de 7/12ème" / ", l'immeuble …": a short line before a comma
            continue
        for part in re.split(r'(?<=[.;:] )(?=Article\s*\d+\s*[.:]\s)', p):
            part = part.strip()
            m = TAIL.search(part)
            if m and not HEAD.match(part) and not LETTER_HEAD.match(part):
                out += [part[:m.start()].strip(), m.group(1).strip()]
            elif part:
                out.append(part)
    # "Paragraphe 2 : De la capacité et de la représentation I-" + "La capacité": the marker belongs to the next
    # heading
    for k in range(len(out) - 1):
        m = re.search(r'\s([IVX]+-)$', out[k])
        if m and HEAD.match(out[k]):
            out[k], out[k + 1] = out[k][:m.start()], m.group(1) + ' ' + out[k + 1]
    return out


def units(paras, trace=None):
    arts, plan, pending, problems = [], [], [], []
    cur, num, last_head = None, 0, False
    for i, p in enumerate(paras):
        nxt = paras[i + 1] if i + 1 < len(paras) else ''
        m = ART.match(p)
        if m:
            n = 1 if m.group(1) in ('premier', '1er') else int(m.group(1).replace(' ', ''))
            if n != num + 1:
                problems.append(f'article {n} after {num}: {p[:60]}')
            num = n
            label = f'Article {m.group(1).replace(" ", "")}'
            cur = {'key': f'art-{n:04d}', 'label': label, 'lines': [p[m.end():]] if p[m.end():] else []}
            arts.append(cur)
            plan.extend((h, label) for h in pending)
            pending, last_head = [], False
            if trace is not None:
                trace.append((p, cur['key']))
            continue
        is_head = bool(HEAD.match(p)) and (caps(p) or p.startswith(('Paragraphe', 'Sous-section'))) or (
            last_head and caps(p)) or (bool(LETTER_HEAD.match(p)) and not re.search(r'[.;:]$', p) and len(p) < 160
                                       and (ART.match(nxt) or HEAD.match(nxt) or LETTER_HEAD.match(nxt)))
        if is_head:
            if last_head and caps(p) and not HEAD.match(p) and pending:
                pending[-1] += ' ' + p  # a heading wrapped onto a second line
            else:
                pending.append(p)
            last_head = True
            if trace is not None:
                trace.append((p, 'plan'))
            continue
        last_head = False
        if cur is None:
            problems.append(f'text before the first article: {p[:60]}')
            continue
        cur['lines'].append(p)
        if trace is not None:
            trace.append((p, cur['key']))
    plan.extend((h, None) for h in pending)
    out = {'plan': {'label': 'Plan', 'kind': 'other',
                    'text': '# Plan\n' + '\n'.join(h if a is None else f'{h} ({a})' for h, a in plan) + '\n'}}
    for a in arts:
        if a['key'] in out:
            problems.append(f'duplicate {a["key"]}')
        out[a['key']] = {'label': a['label'], 'kind': 'art', 'text': '\n'.join([f'# {a["label"]}'] + a['lines']) + '\n'}
    if num != 1636:
        problems.append(f'last article {num}, expected 1636')
    return out, problems


DECISIONS = [
    'Code civil: Loi L/2019/035/AN du 04 juillet 2019, adopted by the Assemblée nationale on 4 July 2019 and promulgated '
    'by Décret D/2019/222/PRG/SGG of 26 July 2019, both printed in the Journal officiel spécial of August 2019. Art. '
    '1636 makes the law take effect "à compter de la date de sa promulgation", so the version is dated 26 July 2019; '
    'this overrides the general rule of art. 1er (the day after publication).',
    'Code civil: the text is the Journal officiel spécial of August 2019 (pages 02 to 85: the law, the promulgation '
    'decree and an annexed table), which the SGG publishes on its "Codes en vigueur" page (retrieved 2026-10-29) as '
    'codes/guinee-code-2019-civil.pdf; the Journal officiel listing has no separate copy of that issue.',
    'Code civil: every Journal officiel issue listed on journal-officiel.sgg.gov.gn from July 2019 to October 2026 was '
    'searched (text layer) for a law amending Loi L/2019/035/AN; none was found. Issues without a text layer (scans) '
    'could not be searched; they are named in the README.',
    'Code civil: structural headings (Livre, Titre, Chapitre, Section, Paragraphe and lettered sub-headings such as '
    '"A- …") are kept in one "plan" file, each followed by the first article under it; a heading that the Journal '
    'officiel runs onto the end of an article at a column break is moved to the plan. The promulgation decree and the '
    'annexed table of articles are left out. The printed misspelling "TITTRE" in some headings is kept.',
]


def build():
    paras = body(SRC)
    u, problems = units(paras)
    d = c.read(SRC)
    import hashlib
    laws = {'loi-l-2019-035-an': {
        'label': 'Loi L/2019/035/AN', 'title': 'Loi ordinaire L/2019/035/AN du 04 juillet 2019 portant Code civil de la '
                                              'République de Guinée',
        'kind': 'law', 'enacted': '2019-07-04', 'published': '2019-08-02', 'url': SRC,
        'temporary_until': None, 'restores': None, 'note': None}}
    act = {'slug': 'code-civil', 'short': 'Code civil', 'title': 'Code civil de la République de Guinée (Loi L/2019/035/AN)',
           'url': SRC, 'first_law': 'loi-l-2019-035-an', 'earlier_laws': [],
           'versions': [{'from': '2019-07-26', 'source_url': SRC, 'sha256': hashlib.sha256(d).hexdigest(), 'units': u,
                         'credits': {}, 'note': 'Journal officiel, numéro spécial d\'août 2019; promulgated by Décret '
                                                'D/2019/222/PRG/SGG of 26 July 2019 (art. 1636: in force on '
                                                'promulgation).'}]}
    part = {'sources': [{'name': 'Journal officiel de la République de Guinée: Code civil (numéro spécial, août 2019)',
                         'url': 'https://journal-officiel.sgg.gov.gn/fr/textes-officiels/les-codes-consolides.html',
                         'retrieved': RETRIEVED,
                         'licence': 'Official legal texts published by the Secrétariat général du Gouvernement; the '
                                    'site states no licence.',
                         'notes': 'Journal officiel spécial of August 2019, published on the Codes en vigueur page as '
                                  'codes/guinee-code-2019-civil.pdf; later issues read only to search for amendments.'}],
            'laws': laws, 'acts': [act], 'decisions': DECISIONS,
            'ai_use': ["Claude Code (Claude Opus 5.5) wrote Lexifina's code. No model wrote, translated or summarised legal "
                       'text; all text is extracted by code from the official PDF.']}
    return part, problems


def squash(s):
    return re.sub(r'[\s\-‐­]', '', s)


def check():
    a = body(SRC)
    trace = []
    u, problems = units(a, trace)
    print('placement:', 'ok' if [p for p, _ in trace] == a else 'FAILED', '; problems:', problems)
    # every unit is the concatenation of its paragraphs
    got = {}
    for p, k in trace:
        got.setdefault(k, []).append(p)
    bad = [k for k in u if k != 'plan' and squash(u[k]['text'].split('\n', 1)[1]) !=
           squash(''.join([ART.sub('', got[k][0])] + got[k][1:]))]
    print('units equal their paragraphs:', 'ok' if not bad else bad[:10])
    # raw text layer between the markers vs the paragraphs
    pdf = c.cached(SRC)
    raw = squash(''.join(l[4] for l in cc_lines(pdf)))
    print('superscripts put back:', STATS['superscripts'], '; 4.5-pt hyphen marks dropped:', STATS['marks_dropped'])
    s = raw.find(squash(START))
    i = raw.find(squash(a[0]), s)
    j = raw.find(squash(STOP), i)
    print('text layer between enacting formula and signature:',
          'identical' if raw[i:j] == squash(''.join(a)) else 'DIFFERENT')
    if raw[i:j] != squash(''.join(a)):
        x, y = raw[i:j], squash(''.join(a))
        k = next((k for k in range(min(len(x), len(y))) if x[k] != y[k]), min(len(x), len(y)))
        print('  first difference:', x[max(0, k - 80):k + 80], '|', y[max(0, k - 80):k + 80])
    # suspicious paragraphs: text in an article ending without punctuation, or a heading word inside a paragraph
    for k, v in u.items():
        if k == 'plan':
            continue
        for line in v['text'].split('\n')[1:-1]:
            if not re.search(r'[.;:!?»)]$', line):
                print('  no final punctuation:', k, line[-90:])
            if re.search(r'\b(CHAPITRE|SECTION|TITRE|LIVRE)\b', line):
                print('  heading word inside:', k, line[:120])


def main():
    if '--check' in sys.argv:
        check()
        return
    part, problems = build()
    for p in problems:
        print('PROBLEM', p)
    print('units', len(part['acts'][0]['versions'][0]['units']))
    os.makedirs(os.path.dirname(PART), exist_ok=True)
    tmp = PART + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(part, ensure_ascii=False, indent=1) + '\n')
    if '--dry' not in sys.argv:
        os.replace(tmp, PART)


if __name__ == '__main__':
    main()
