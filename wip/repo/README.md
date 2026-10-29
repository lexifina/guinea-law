# Guinea: law history in git

The law of the Republic of Guinea as a git history. Each provision is one file, each law gets one commit on the day it took effect, and the law that made each change is the commit's author. `git blame` names the law behind every paragraph, `git log` lists every change to an article, and `tools/en_vigueur_au.py` gives the text in force on any day.

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law), which places it at `gn/`.

**What is in it now**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `constitution/` | Constitution de la République de Guinée, adopted by the referendum of 21 September 2025 | 1 | As promulgated, in force 26 September 2025; not revised since |
| `charte-de-la-transition/` | Charte de la Transition du 27 septembre 2021 | 1 | As signed, in force 27 September 2021; never amended |

The per-act `README.md` in each folder lists every provision, how often it changed and when.

**Why so little history.** The Journal officiel (journal-officiel.sgg.gov.gn) is the only official source. It publishes every issue as a PDF but no consolidated or dated versions of any act, so a history has to be rebuilt by applying each amending law in turn. Both texts here are young and have never been amended, so each has one version. The 2020 Constitution is not included: the 2020 issues that would hold it are image scans, and this record does not transcribe images. Earlier constitutions have not been sought yet.

**The Charte and the Constitution overlap.** The Charte de la Transition was the fundamental law from the coup of 5 September 2021 until the Constitution of 2025. Article 196 of the Constitution keeps the organs of the transition, and the powers the Charte gives them, until the new institutions are installed. No text in the Journal officiel dates that moment, so the Charte has no closing commit here and still reads as current. Read it as the law of the transition, not as law in force after the new institutions took office.

## A lawyer's questions as git commands

| Question | Command |
| --- | --- |
| What does art. 46 of the Constitution say on 1 January 2026? | `python tools/en_vigueur_au.py 2026-01-01 constitution 46` |
| The same, with raw git (bash) | `git show $(git rev-list -1 --before="2026-01-01T23:59:59Z" main -- constitution/art-046.md):constitution/art-046.md` |
| The same, in PowerShell | `$r = git rev-list -1 --before="2026-01-01T23:59:59Z" main -- constitution/art-046.md; git show "$($r):constitution/art-046.md"` |
| Which law wrote each paragraph of an article? | `git blame constitution/art-046.md` |
| Every change to an article, word by word | `git log -p --word-diff charte-de-la-transition/art-060.md` |
| Every law in the record, in order | `git log --reverse --format="%ad %an" --date=short main` |
| Everything one law made | `git show law/constitution-2025` (tags `law/<key>` mark each law's commit) |
| The whole Charte on a date | `python tools/en_vigueur_au.py 2022-01-01 charte-de-la-transition` |

After a rebuild, refresh tags with `git fetch --force --tags`: a plain fetch keeps stale tags.

## Dates

- Each commit is dated at **noon, Africa/Conakry (UTC), on the day the text took effect**. The day is also in the `In-force:` trailer, which the tools read.
- **The Constitution fixes its own entry into force** (art. 199): it "entre en vigueur à compter de sa date de promulgation par le Président de la République". It was promulgated by decree D/2025/176/PRG/CNRD/SGG of 26 September 2025 and published in the Journal officiel, n° 2025-12, numéro spécial 3.
- **The Charte fixes its own too** (art. 84): it "prend effet à partir de sa date de signature", 27 September 2021 ("Conakry, le 27 Septembre 2021"). It was published in the Journal officiel n° 2021-11, pages 532 to 536.
- `--before="YYYY-MM-DD"` alone uses your clock's time of day, so a law that took effect that day may be missed before noon. Use `T23:59:59Z` as above, or the tool.

## How it is checked

- Every version is read back from git on the day it took effect and on the day before (`tools/check_repo.py`); both must match `corpus.json`. Results are in `REPRODUCE.md`.
- **Nothing dropped, nothing added, nothing out of order:** the words of every article, read from the Journal officiel's two-column pages, were compared with an independent extraction of the same pages (poppler's `pdftotext`). Every word of the body is in a provision file, except titles, chapter headings, running headers and page numbers; no word is in a file that is not on the page; and articles run 1 to 199 and 1 to 84 without a gap.
- **The Charte against the Journal officiel's own website:** the site publishes an edited HTML copy of the Charte. It matches this record word for word, apart from headings, three numbers in brackets the site leaves out ("(15) jours") and two slips in the printed Journal officiel that the site corrects ("I ‘Etat" for "l’Etat", "gouvemance" for "gouvernance"). This record keeps the printed words (`tools/verify.py`).
- **Still current:** every Journal officiel issue published after the Constitution, up to n° 2026-07 of 15 April 2026 (the latest on the site when this was built), was searched. None revises the Constitution or amends or repeals the Charte.
- The PDFs are born-digital (Adobe InDesign, no images), so their text layer is the printed text; nothing here was read by OCR.
- The repository is rebuilt from the same data a second time and must give identical hashes.

## What "author" means

The author of a commit is the law that made the change, with an e-mail address that cannot exist, so `git blame` and `git log --author` name laws. The committer is always Lexifina.

- **The Constitution's commit** is credited to the Constitution of 26 September 2025, adopted by referendum.
- **The Charte's commit** is credited to the Charte de la Transition of 27 September 2021.

## What it does not show

- **Earlier constitutions** (among them those of 2010 and 2020) and the codes are not in this record yet.
- **Headings** (Partie, Titre, Sous-titre, Chapitre, Section) are left out; each file starts with "# Article N". The preamble is one file.
- **Article 61 of the Constitution** is printed by the Journal officiel inside the paragraph of article 60 ("… de ses biens. Article 61. Les écarts …"); here it is its own file, with no word changed.
- **The end of the Charte**, as explained above.
- **No OCR.** Texts published only as scanned images are not included.

## How it is built

`tools/fetch.py` downloads each source in `tools/sources.json` once with curl (`tools/gncache.py`), at no more than three requests a second, cached by the sha256 of its URL. `tools/parse.py` reads only the cache: it reads each page's text lines with their positions, puts the two columns in reading order, joins lines into paragraphs and splits them into articles, and writes `corpus.json`; the shared builder `tools/build.py` turns that into the commits. `tools/verify.py` repeats the checks against the website and the later issues. `REPRODUCE.md` lists every source, command, tool version and decision, and the result of the hash-for-hash rebuild.

## Sources

| Source | What it gives | Used for |
| --- | --- | --- |
| [Journal officiel n° 2025-12, numéro spécial 3](https://journal-officiel.sgg.gov.gn/JO/2025/guinee-jo-2025-12-sp-3.pdf) | The Constitution of 2025 and its promulgation decree (PDF with a text layer) | The Constitution |
| [Journal officiel n° 2021-11](https://journal-officiel.sgg.gov.gn/JO/2021/guinee-jo-2021-11.pdf) | The Charte de la Transition, pages 532 to 536 | The Charte |
| [Journal officiel, Charte de la transition](https://journal-officiel.sgg.gov.gn/fr/textes-officiels/constitution.html) | The site's HTML copy of the Charte | Checking the Charte |
| [Journal officiel, issues 2025-12-12 to 2026-07](https://journal-officiel.sgg.gov.gn/fr/m-journal-officiel/le-journal-officiel.html) | Every issue after the Constitution | Checking that neither text has changed |

Research guides that cover every country: [GlobaLex](https://www.nyulawglobal.org/globalex/) and the [Law Library of Congress Guide to Law Online](https://www.loc.gov/research-centers/law-library-of-congress/researcher-resources/guide-to-law-online/).

## Licence

See [LICENSE](LICENSE). Texts: Journal officiel de la République de Guinée, Secrétariat général du Gouvernement (https://journal-officiel.sgg.gov.gn), official texts reproduced with that attribution. Lexifina's arrangement, messages, tables and tools are CC0.

This repository is not legal advice.

## En français

Ce dépôt retrace dans git le droit de la République de Guinée : un fichier par article, un commit par texte à la date de son entrée en vigueur, et le texte à l’origine de la rédaction comme auteur du commit. Il contient la Constitution adoptée par le référendum du 21 septembre 2025, en vigueur depuis sa promulgation le 26 septembre 2025 (Journal officiel n° 2025-12, numéro spécial 3), et la Charte de la Transition du 27 septembre 2021, en vigueur depuis sa signature (Journal officiel n° 2021-11). Aucun des deux textes n’a été modifié depuis : tous les numéros du Journal officiel parus jusqu’au n° 2026-07 du 15 avril 2026 ont été vérifiés. L’article 196 de la Constitution maintient les organes de la Transition jusqu’à l’installation des nouvelles institutions ; aucune date de fin de la Charte n’est donc enregistrée ici. `python tools/en_vigueur_au.py 2026-01-01 constitution 46` affiche l’article 46 tel qu’il était en vigueur à cette date. Ce dépôt ne constitue pas un avis juridique.
