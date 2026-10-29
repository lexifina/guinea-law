# How this repository was made (Guinea)

This file is written by the build on 2026-10-29, the day the source data was retrieved.

## Sources

| Source | Address | Retrieved | Licence |
| --- | --- | --- | --- |
| Journal officiel de la République de Guinée | <https://journal-officiel.sgg.gov.gn> | 2026-10-28 | Official texts. |
| Journal officiel de la République de Guinée: Code civil (numéro spécial, août 2019) | <https://journal-officiel.sgg.gov.gn/fr/textes-officiels/les-codes-consolides.html> | 2026-10-29 | Official legal texts published by the Secrétariat général du Gouvernement; the site states no licence. |

Every word of law in this repository comes from these sources. Lexifina reads them and records each act's dated versions, and the laws that made each change, in one corpus file. This repository is built from that file.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `constitution` | Constitution de la République de Guinée (2025) | 1 | 2025-09-26 to 2025-09-26 |
| `charte-de-la-transition` | Charte de la Transition | 1 | 2021-09-27 to 2021-09-27 |
| `code-civil` | Code civil de la République de Guinée (Loi L/2019/035/AN) | 1 | 2019-07-26 to 2019-07-26 |

The build made 3 commits:

| Commits | Kind |
| ---: | --- |
| 3 | first version of an act |
| 0 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `futur`: laws not yet in force on 2026-10-29.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 3 laws in the record.
- 6 tags.

## Dates

Each commit is dated at noon (Africa/Conakry) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: Each text here states its own commencement (Constitution 2025 art. 199: from promulgation; Charte art. 84: from signature). https://journal-officiel.sgg.gov.gn/JO/2025/guinee-jo-2025-12-sp-3.pdf

## How the history is built

`tools/build.py` turns the corpus into this history in one pass: one commit per law, on the day it took effect. The same corpus always gives the same commit hashes. `tools/check_repo.py` reads every version back from git and compares it with the corpus. `tools/on.py` shows the law as it stood on any date. The corpus format is described in `tools/SCHEMA.md`.

- Corpus: sha256 `ea4373262eb8c60aecf026568c171a578a746dfe4b398766b9d3a789a400affb` (957344 bytes).
- Builder blob hashes (`git hash-object`): `build.py` `a4faa25af85facb64b956b372f6b528aafdd7ec1`, `check.py` `3d00541d258745461ab52b1b0cb4e1716a27a95d`, `on.py` `644a6c0857fbcc72562032b58d57aa113fee0641`.
- Python 3.12.10; git version 2.46.0.windows.1.

## Checks

3 versions of 3 acts read back from git on the day each took effect and on the day before: 0 mismatches. Trailers: 0 commits whose trailers git cannot parse. Health: 0 merge commits on main, 0 commit dates that go backwards, 0 commits dated after the build.

No second build of this corpus has been compared yet.

## Decisions made by hand

- Constitution 2025 in force 2025-09-26 (art. 199 and promulgation decree D/2025/176 of that day).
- Charte de la Transition in force 2021-09-27 (its art. 84); text from JO n°2021-11 pp. 532-536. Its end is not dated: Constitution art. 196 keeps the transition organs until the new institutions are installed.
- Structural headings (Titre, Chapitre...) are not kept in article files.
- The 2020 Constitution is left out: no JO issue with a text layer containing it was found (2020 ordinary issues are scans).
- Paragraphs are rebuilt from the two-column layout by line geometry; a line that stops short or is followed by a wider gap ends a paragraph unless it breaks off mid-sentence.
- Line-end hyphens that split a word are removed (the Charte prints ordinary hyphens there); hyphens of compounds written so elsewhere in the text, or in a short list (bien-être, soixante-douze ...), are kept.
- Constitution art. 61 is printed by the JO inside the paragraph of art. 60 ("... de ses biens. Article 61. Les écarts ..."); it is split out as its own article without changing a word.
- Each text ends at its signature line ("Conakry, le ..."); the decrees that follow in the same JO issue are not part of it.
- The JO text is kept as printed, including two slips in the Charte ("I ‘Etat" for "l’Etat", "gouvemance"); the PDFs are born-digital, so these are the printed words, not a reading error.
- Checked: the Charte equals the site's own HTML copy word for word apart from headings, those two slips and three numbers in brackets the site omits; no JO issue published after the Constitution, up to n° 2026-07 of 15 April 2026, revises the Constitution or amends or repeals the Charte.
- The Charte has no end commit: Constitution art. 196 keeps the transition organs and their Charte powers until the new institutions are installed, and no JO text found dates that.
- Code civil: Loi L/2019/035/AN du 04 juillet 2019, adopted by the Assemblée nationale on 4 July 2019 and promulgated by Décret D/2019/222/PRG/SGG of 26 July 2019, both printed in the Journal officiel spécial of August 2019. Art. 1636 makes the law take effect "à compter de la date de sa promulgation", so the version is dated 26 July 2019; this overrides the general rule of art. 1er (the day after publication).
- Code civil: the text is the Journal officiel spécial of August 2019 (pages 02 to 85: the law, the promulgation decree and an annexed table), which the SGG publishes on its "Codes en vigueur" page (retrieved 2026-10-29) as codes/guinee-code-2019-civil.pdf; the Journal officiel listing has no separate copy of that issue.
- Code civil: every Journal officiel issue listed on journal-officiel.sgg.gov.gn from July 2019 to October 2026 was searched (text layer) for a law amending Loi L/2019/035/AN; none was found. Issues without a text layer (scans) could not be searched; they are named in the README.
- Code civil: structural headings (Livre, Titre, Chapitre, Section, Paragraphe and lettered sub-headings such as "A- …") are kept in one "plan" file, each followed by the first article under it; a heading that the Journal officiel runs onto the end of an article at a column break is moved to the plan. The promulgation decree and the annexed table of articles are left out. The printed misspelling "TITTRE" in some headings is kept.

## What AI did and did not do

The scripts that read the sources and build this repository were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- Claude Code (claude-opus-5-5) wrote Lexifina's code; no model wrote or edited legal text.
- Claude Code (Claude Opus 5.5) wrote Lexifina's code. No model wrote, translated or summarised legal text; all text is extracted by code from the official PDF.
