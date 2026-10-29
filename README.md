# Guinea: law history in git

The law of the Republic of Guinea as a git history. Each provision is one file, each law gets one commit on the day it took effect, and the law that made each change is the commit's author. `git blame` names the law behind every paragraph, `git log` lists every change to an article, and `tools/en_vigueur_au.py` gives the text in force on any day.

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law), which places it at `gn/`.

**What is in it now**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `constitution/` | Constitution de la République de Guinée, adopted by the referendum of 21 September 2025 | 1 | As promulgated, in force 26 September 2025; not revised since |
| `charte-de-la-transition/` | Charte de la Transition du 27 septembre 2021 | 1 | As signed, in force 27 September 2021; never amended |
| `code-civil/` | Code civil de la République de Guinée (Loi L/2019/035/AN du 04 juillet 2019), 1,636 articles | 1 | As promulgated, in force 26 July 2019; no amendment found |

The per-act `README.md` in each folder lists every provision, how often it changed and when.

**Why so little history.** The Journal officiel (journal-officiel.sgg.gov.gn) is the only official source. It publishes every issue as a PDF but no consolidated or dated versions of any act, so a history has to be rebuilt by applying each amending law in turn. The texts here are young and no amendment to any of them has been found, so each has one version. The 2020 Constitution is not included: the 2020 issues that would hold it are image scans, and this record does not transcribe images. Earlier constitutions have not been sought yet.

**The Code civil.** Loi L/2019/035/AN, adopted by the Assemblée nationale on 4 July 2019 and promulgated by Décret D/2019/222/PRG/SGG of 26 July 2019, as printed in the Journal officiel numéro spécial of August 2019 (pages 02 to 85), which the Secrétariat général du Gouvernement publishes on its "Codes en vigueur" page. Each article is one file; `code-civil/plan.md` lists its Livres, Titres, Chapitres, Sections, Paragraphes and lettered sub-headings, each followed by the first article under it.

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
- **The Code civil fixes its own too** (art. 1636): it "prend effet à compter de la date de sa promulgation", 26 July 2019 (Décret D/2019/222/PRG/SGG). This overrides its own art. 1er, the general rule that laws are binding from the day after their publication.
- `--before="YYYY-MM-DD"` alone uses your clock's time of day, so a law that took effect that day may be missed before noon. Use `T23:59:59Z` as above, or the tool.

## How it is checked

- Every version is read back from git on the day it took effect and on the day before (`tools/check_repo.py`); both must match `corpus.json`. Results are in `REPRODUCE.md`.
- **Nothing dropped, nothing added, nothing out of order:** the words of every article, read from the Journal officiel's two-column pages, were compared with an independent extraction of the same pages (poppler's `pdftotext`). Every word of the body is in a provision file, except titles, chapter headings, running headers and page numbers; no word is in a file that is not on the page; and articles run 1 to 199 and 1 to 84 without a gap.
- **The Code civil, character by character:** every character of the Journal officiel's text layer from the enacting formula to the Assembly's signature is in exactly one file, in the order printed, and its articles run 1 to 1,636 without a gap. Two article numbers are misprinted in the Journal officiel ("Articule 153", "Article 80 6") and are read as articles 153 and 806. Eleven superscripts that the text layer stores apart from their line ("10ème", "7/12ème") are put back in place, and ten stray 4.5-point hyphen marks above article 1494 and its neighbours are left out.
- **The Charte against the Journal officiel's own website:** the site publishes an edited HTML copy of the Charte. It matches this record word for word, apart from headings, three numbers in brackets the site leaves out ("(15) jours") and two slips in the printed Journal officiel that the site corrects ("I ‘Etat" for "l’Etat", "gouvemance" for "gouvernance"). This record keeps the printed words (`tools/verify.py`).
- **Still current:** every Journal officiel issue published after the Constitution, up to n° 2026-12 spécial of 27 October 2026 (the latest on the site when this was built), was searched. None revises the Constitution or amends or repeals the Charte.
- **The Code civil is still the enacted text** as far as the record shows: every issue listed from July 2019 to October 2026 that has a text layer was searched for a law amending Loi L/2019/035/AN, and none was found; the SGG still lists the 2019 text among the codes in force. Thirty issues of that period are image scans and could not be searched (see below).
- The PDFs are born-digital (Adobe InDesign, no images), so their text layer is the printed text; nothing here was read by OCR.
- The repository is rebuilt from the same data a second time and must give identical hashes.

## What "author" means

The author of a commit is the law that made the change, with an e-mail address that cannot exist, so `git blame` and `git log --author` name laws. The committer is always Lexifina.

- **The Constitution's commit** is credited to the Constitution of 26 September 2025, adopted by referendum.
- **The Charte's commit** is credited to the Charte de la Transition of 27 September 2021.

## What it does not show

- **Earlier constitutions** (among them those of 2010 and 2020) and the other codes are not in this record yet.
- **Headings** of the Constitution and the Charte (Partie, Titre, Sous-titre, Chapitre, Section) are left out; each file starts with "# Article N". The preamble is one file. The Code civil keeps its headings in `code-civil/plan.md`; its promulgation decree and the annexed table of articles are left out.
- **Issues that could not be searched for amendments to the Code civil:** the monthly issues of July to December 2019, nos. 2020-01 to 2020-12, the special issue of 5 February 2021, nos. 2021-01 to 2021-07, the special issue of 13 October 2021 and no. 2022-09 are image scans; two compilations of 2018 issues listed in March 2020 are scans too; and the special issue 2025-11 no. 2 (14 November 2025) is listed but returns an error. An amendment printed only there would be missed.
- **Article 61 of the Constitution** is printed by the Journal officiel inside the paragraph of article 60 ("… de ses biens. Article 61. Les écarts …"); here it is its own file, with no word changed.
- **The end of the Charte**, as explained above.
- **No OCR.** Texts published only as scanned images are not included.

## How it is built

Lexifina reads the sources listed here and records each act's dated versions, and the laws that made each change, in one corpus file. `tools/build.py` writes this repository from that file, and the same corpus always gives the same commit hashes; `REPRODUCE.md` gives the details and the checks. A model (Claude) wrote Lexifina's code; it wrote no legal text, and no model runs when the history is built.

`tools/verify.py` repeats the checks against the website and the later issues.

## Sources

| Source | What it gives | Used for |
| --- | --- | --- |
| [Journal officiel n° 2025-12, numéro spécial 3](https://journal-officiel.sgg.gov.gn/JO/2025/guinee-jo-2025-12-sp-3.pdf) | The Constitution of 2025 and its promulgation decree (PDF with a text layer) | The Constitution |
| [Journal officiel n° 2021-11](https://journal-officiel.sgg.gov.gn/JO/2021/guinee-jo-2021-11.pdf) | The Charte de la Transition, pages 532 to 536 | The Charte |
| [Journal officiel, Charte de la transition](https://journal-officiel.sgg.gov.gn/fr/textes-officiels/constitution.html) | The site's HTML copy of the Charte | Checking the Charte |
| [Journal officiel numéro spécial, August 2019 (Codes en vigueur)](https://journal-officiel.sgg.gov.gn/codes/guinee-code-2019-civil.pdf) | The Code civil, Loi L/2019/035/AN, and its promulgation decree (PDF with a text layer) | The Code civil |
| [Journal officiel, issues 2025-12-12 to 2026-12 spécial](https://journal-officiel.sgg.gov.gn/fr/m-journal-officiel/le-journal-officiel.html) | Every issue after the Constitution, and every issue from July 2019 for the Code civil | Checking that no text has changed |

Research guides that cover every country: [GlobaLex](https://www.nyulawglobal.org/globalex/) and the [Law Library of Congress Guide to Law Online](https://www.loc.gov/research-centers/law-library-of-congress/researcher-resources/guide-to-law-online/).

## Licence

See [LICENSE](LICENSE). Texts: Journal officiel de la République de Guinée, Secrétariat général du Gouvernement (https://journal-officiel.sgg.gov.gn), official texts reproduced with that attribution. Lexifina's arrangement, messages, tables and tools are CC0.

This repository is not legal advice.

## En français

Ce dépôt retrace dans git le droit de la République de Guinée : un fichier par article, un commit par texte à la date de son entrée en vigueur, et le texte à l’origine de la rédaction comme auteur du commit. Il contient la Constitution adoptée par le référendum du 21 septembre 2025, en vigueur depuis sa promulgation le 26 septembre 2025 (Journal officiel n° 2025-12, numéro spécial 3), et la Charte de la Transition du 27 septembre 2021, en vigueur depuis sa signature (Journal officiel n° 2021-11). Aucun des deux textes n’a été modifié depuis : tous les numéros du Journal officiel parus jusqu’au n° 2026-12 spécial du 27 octobre 2026 ont été vérifiés. Il contient aussi le Code civil (Loi L/2019/035/AN du 04 juillet 2019, Journal officiel numéro spécial d’août 2019), en vigueur depuis sa promulgation le 26 juillet 2019 (art. 1636) ; aucune loi modificative n’a été trouvée dans les numéros parus depuis, hormis trente numéros numérisés en image qui n’ont pas pu être examinés. L’article 196 de la Constitution maintient les organes de la Transition jusqu’à l’installation des nouvelles institutions ; aucune date de fin de la Charte n’est donc enregistrée ici. `python tools/en_vigueur_au.py 2026-01-01 constitution 46` affiche l’article 46 tel qu’il était en vigueur à cette date. Ce dépôt ne constitue pas un avis juridique.
