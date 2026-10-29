"""Guinea: cache -> corpus.json. Reads only .cache (gncache). Journal officiel PDFs with their own text layer (no OCR)."""
import json
import os
import re
import fitz
import gncache as c

HERE = os.path.dirname(os.path.abspath(__file__))
JO = 'https://journal-officiel.sgg.gov.gn/JO/'
SRC = {
    'constitution': JO + '2025/guinee-jo-2025-12-sp-3.pdf',
    'charte': JO + '2021/guinee-jo-2021-11.pdf',
}
HEADER = re.compile(r'JOURNAL OFFICIEL DE LA REPUBLIQUE')
HEADING = re.compile(r'^(PREMI[ÈE]RE|DEUXI[ÈE]ME|TROISI[ÈE]ME|I+[- ]|[\d.]+\s*(TITRE|SOUS|CHAPITRE)|TITRE|SOUS-TITRE|CHAPITRE|SECTION|LIVRE)\b')
ART = re.compile(r'^Article\s*(premier|1er|\d+)\s*(bis|ter)?\s*:\s*')


def lines(pdf, pages):
    d = fitz.open(pdf)
    out = []
    for i in pages:
        p = d[i]
        w = p.rect.width
        ls = []
        for b in p.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                t = ''.join(s['text'] for s in l['spans'])
                if not t.strip():
                    continue
                x0, y0, x1, y1 = l['bbox']
                if HEADER.search(t) and (y0 < 32 or y0 > p.rect.height - 40):
                    continue
                col = 1 if x0 >= w * 0.48 else (0 if x1 <= w * 0.53 else 2)
                ls.append((y0, x0, x1, col, t))
        ls.sort()
        right = {k: max([x1 for _, _, x1, cc, _ in ls if cc == k] or [0]) for k in (0, 1, 2)}
        band = []

        def flush():
            for k in (0, 1):
                out.extend(sorted([l for l in band if l[3] == k]))
            band.clear()
        for l in ls:
            if l[3] == 2:
                flush()
                out.append(l)
            else:
                band.append(l)
        flush()
        out = [(y, x0, x1, cc, t, right[cc]) if len(o) == 5 else o for o in out
               for (y, x0, x1, cc, t) in [o[:5]]]
    return out


def paragraphs(ls):
    paras, cur = [], ''
    for (y, x0, x1, col, t, right) in ls:
        t = t.replace(' ', ' ').replace('\t', ' ')
        s = t.strip()
        if s == '•':
            if cur:
                paras.append(cur)
            cur = '• '
            continue
        if cur.endswith('­'):
            cur = cur[:-1] + s
        elif cur and not cur.endswith('• ') and (ART.match(s) or HEADING.match(s)):
            paras.append(cur)
            cur = s
        else:
            cur = (cur + ' ' + s) if cur and not cur.endswith('• ') else cur + s
        if x1 < right - 15 and not s.endswith('­'):
            paras.append(cur)
            cur = ''
    if cur:
        paras.append(cur)
    return [re.sub(r'\s+', ' ', p.replace('­', '')).strip() for p in paras if p.strip()]


def units(paras, start, stop):
    u, key, seen = {}, None, False
    pre = []
    for p in paras:
        if not seen and p.startswith(start):
            seen = True
            continue
        if not seen:
            continue
        if p.startswith(stop):
            break
        m = ART.match(p)
        if m:
            n = 1 if m.group(1) in ('premier', '1er') else int(m.group(1))
            key = f'art-{n:03d}'
            u[key] = {'label': f'Article {m.group(1)}', 'kind': 'art', 'lines': [f'# Article {m.group(1)}', p[m.end():]]}
        elif HEADING.match(p) and p.upper() == p:
            continue
        elif key:
            u[key]['lines'].append(p)
        else:
            pre.append(p)
    res = {}
    if pre:
        res['preambule'] = {'label': 'Préambule', 'kind': 'preamble', 'text': '# Préambule\n' + '\n'.join(pre) + '\n'}
    for k, v in u.items():
        res[k] = {'label': v['label'], 'kind': 'art', 'text': '\n'.join(v['lines']) + '\n'}
    return res


def main():
    cu = units(paragraphs(lines(c.cached(SRC['constitution']), range(1, 19))), 'PRÉAMBULE', 'Conakry, le 26 septembre 2025')
    # drop sommaire: units() starts after the first 'PRÉAMBULE' paragraph (the sommaire line has dots, so it differs)
    ch = units(paragraphs(lines(c.cached(SRC['charte']), range(4, 9))), 'PREAMBULE', 'Conakry, le 27 Septembre 2021')
    corpus = {
        'country': {'code': 'GN', 'name': 'Guinea', 'slug': 'guinea', 'lang': 'fr', 'tz': 'Africa/Conakry',
                    'future_branch': 'futur',
                    'publisher': {'name': 'Journal officiel de la République de Guinée (SGG)', 'email': 'jo@sgg.gov.gn.invalid'},
                    'default_in_force_rule': {'text': 'Each text here states its own commencement (Constitution 2025 art. 199: from promulgation; Charte art. 84: from signature).',
                                              'source': SRC['constitution']},
                    'licence_note': 'Journal officiel de la République de Guinée, Secrétariat général du Gouvernement.'},
        'sources': [{'name': 'Journal officiel de la République de Guinée', 'url': 'https://journal-officiel.sgg.gov.gn',
                     'retrieved': '2026-10-28', 'requests': sum(1 for _ in open(os.path.join(c.CACHE, 'requests.jsonl'))),
                     'licence': 'Official texts; robots.txt allows all.', 'notes': 'PDF issues with publisher text layer.'}],
        'laws': {
            'constitution-2025': {'label': 'Constitution du 26 septembre 2025', 'title': 'Constitution de la République de Guinée adoptée par référendum du 21 septembre 2025, promulguée par décret D/2025/176/PRG/CNRD/SGG',
                                  'kind': 'referendum', 'enacted': '2025-09-26', 'published': '2025-09-26', 'url': SRC['constitution'],
                                  'temporary_until': None, 'restores': None, 'note': None},
            'charte-2021': {'label': 'Charte de la Transition du 27 septembre 2021', 'title': 'Charte de la Transition', 'kind': 'law',
                            'enacted': '2021-09-27', 'published': '2021-12-24', 'url': SRC['charte'],
                            'temporary_until': None, 'restores': None, 'note': None},
        },
        'acts': [
            {'slug': 'constitution', 'short': 'Constitution', 'title': 'Constitution de la République de Guinée (2025)', 'url': SRC['constitution'],
             'first_law': 'constitution-2025', 'earlier_laws': [],
             'versions': [{'from': '2025-09-26', 'source_url': SRC['constitution'], 'sha256': c.sha256_of(SRC['constitution']), 'units': cu, 'credits': {}}]},
            {'slug': 'charte-de-la-transition', 'short': 'Charte', 'title': 'Charte de la Transition', 'url': SRC['charte'],
             'first_law': 'charte-2021', 'earlier_laws': [],
             'versions': [{'from': '2021-09-27', 'source_url': SRC['charte'], 'sha256': c.sha256_of(SRC['charte']), 'units': ch, 'credits': {}}]},
        ],
        'applies': [],
        'decisions': ['Constitution 2025 in force 2025-09-26 (art. 199 and promulgation decree D/2025/176 of that day).',
                      'Charte de la Transition in force 2021-09-27 (its art. 84); text from JO n°2021-11 pp. 532-536. Its end is not dated: Constitution art. 196 keeps the transition organs until the new institutions are installed.',
                      'Structural headings (Titre, Chapitre...) are not kept in article files.',
                      'The 2020 Constitution is left out: no JO issue with a text layer containing it was found (2020 ordinary issues are scans).'],
        'ai_use': ['Claude Code (claude-opus-5-5) wrote the fetch/parse scripts; no model wrote or edited legal text.'],
    }
    tmp = os.path.join(HERE, 'corpus.json.tmp')
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(corpus, f, ensure_ascii=False, indent=1)
    os.replace(tmp, os.path.join(HERE, 'corpus.json'))
    print('constitution units', len(cu), 'charte units', len(ch))


if __name__ == '__main__':
    main()
