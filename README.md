# Guinea: law history in git


The law of the Republic of Guinea as a git history: one file per provision, each version committed on the day it took effect, and the law that made each change as the commit's author. `git blame` names the law behind every paragraph; `git log` lists every change to an article; picking a date gives the text in force that day.

Part of [lexifina/global-law](https://github.com/lexifina/global-law), one git history for every country's law: this is Guinea's national law, which global-law reads at `guinea/national/acts/`.

**What is in it now:** three acts, each in one version: the Constitution adopted by the referendum of 21 September 2025 (the preamble and 199 articles), the Charte de la Transition of 27 September 2021 (the preamble and 84 articles) and the Code civil, Loi L/2019/035/AN of 4 July 2019 (1,636 articles). The `README.md` in each act's folder lists every provision.

**Why one version each.** The Journal officiel publishes each issue as a PDF and no consolidated or dated versions, so a history is rebuilt by applying each amending law in turn. No law amending any of the three has been found, so each is its text as enacted.

Each act has its own folder of article files: `constitution/`, `charte-de-la-transition/` and `code-civil/` (`constitution/art-044.md` is Article 44 of the Constitution, the President's term of office; `code-civil/art-0001.md` is Article 1 of the Code civil). The Constitution and the Charte have their preambles in `preambule.md`, and [`code-civil/plan.md`](code-civil/plan.md) lists the Code civil's headings, each with the first article under it.

The text is in French, as the Journal officiel prints it. An English translation is not part of this record.

## Questions as git commands

| Question | Command |
| --- | --- |
| Every change to Article 44 of the Constitution (the President's term) | `git log -p --word-diff -- constitution/art-044.md` |
| Which law wrote each line of Article 44? | `git blame constitution/art-044.md` |
| Every version of Article 44, with the day each took effect | `git log --format="%h %(trailers:key=In-force,valueonly,separator=) %an" -- constitution/art-044.md` |
| Article 44 as in force on 1 January 2026 | `python tools/en_vigueur_au.py 2026-01-01 constitution 44` |

**Outside git**, we also host this record publicly, for free:

- **[Ask Claude about the law of Guinea](https://global-law.lexifina.com/v1/try_claude?country=guinea)**: opens Claude with a first question ready.
- **[Ask ChatGPT](https://global-law.lexifina.com/v1/try_chatgpt?country=guinea)**: the same question in ChatGPT.
- **[Search the law of Guinea on our site](https://lexifina.com/law?country=guinea&q=droit+de+gr%C3%A8ve)**: a search for "droit de grève" (the right to strike), with each provision's text and its versions, no account needed.
- **[Developer REST API](https://global-law.lexifina.com/v1/search_law?query=droit+de+gr%C3%A8ve&jurisdiction=guinea)**: the same search as JSON, with no key. See the [documentation here](https://lexifina.com/api/global-law).

Both assistants read the record through the free Global law connector (MCP, `https://global-law.lexifina.com/mcp`); the first time, the chat gives you the link that adds it. Ask in French or in English.

**Host it yourself easily.** All it takes is git and Python, and the tools run on your machine:

```sh
git clone --depth 1 https://github.com/lexifina/global-law && cd global-law
python3 tools/countries.py add guinea/national/acts
python3 tools/law.py show 2026-01-01 guinea/national/acts/constitution/art-044.md
```

Opened in Claude Code, Cursor, VS Code or Codex, the clone also starts a local MCP server with the same tools ([MCP.md](https://github.com/lexifina/global-law/blob/main/MCP.md)).

## Dates

Each commit is dated at noon, Africa/Conakry (UTC), on the day the version took effect, and carries it in its `In-force:` trailer. Each act fixes that day itself:

- the Constitution "entre en vigueur à compter de sa date de promulgation" (art. 199): 26 September 2025, by Décret D/2025/176/PRG/CNRD/SGG (Journal officiel n° 2025-12, numéro spécial 3);
- the Charte "prend effet à partir de sa date de signature" (art. 84): 27 September 2021 (Journal officiel n° 2021-11, pages 532 to 536);
- the Code civil "prend effet à compter de la date de sa promulgation" (art. 1636): 26 July 2019, by Décret D/2019/222/PRG/SGG, overriding its own art. 1er (laws bind from the day after publication).

Each commit is credited to the act itself, as enacted (`git log --author` names laws); the committer is always Lexifina.

## How it is checked

- `tools/check_repo.py` reads every version back from git on the day it took effect and on the day before, and both must match the corpus the history was built from; it also checks that every commit's trailers parse, that there are no merge commits and that no commit is dated in the future. The results are in [`REPRODUCE.md`](REPRODUCE.md).
- The words of the Constitution and the Charte were compared with an independent extraction of the same pages (poppler's `pdftotext`): every word of the body is in a provision file and none is added. Every character of the Code civil's text layer is in exactly one file, in the order printed. The PDFs are born-digital, so nothing was read by OCR.
- The Charte matches the Journal officiel website's own HTML copy word for word, apart from headings and a few slips; this record keeps the printed words (`tools/verify.py`).
- The Journal officiel's issues with a text layer, up to n° 2026-12 spécial of 27 October 2026, were searched: those after the Constitution for a change to it or to the Charte (`tools/verify.py`), and those from July 2019 for a law amending the Code civil (`tools/scan.py`); none was found.

## What it does not show

- **Issues that could not be searched.** Thirty issues listed from July 2019 to 2022 are image scans, and one listed issue (2025-11 spécial n° 2) returns an error; an amendment printed only there would be missed.
- **The end of the Charte.** Article 196 of the Constitution keeps the organs of the transition until the new institutions are installed; no Journal officiel text dates that, so the Charte has no closing commit and still reads as current.
- **Earlier constitutions** (among them those of 2010 and 2020; the 2020 issues are scans) and the other codes and laws.
- **Headings** of the Constitution and the Charte are left out (each file starts with "# Article N"); the Code civil's are in `plan.md`. Promulgation decrees and signature lines are left out.
- **Texts published only as scanned images**: no OCR.

## Sources

| Source | Kind | Past versions | Notes |
| --- | --- | --- | --- |
| [Journal officiel de la République de Guinée](https://journal-officiel.sgg.gov.gn) (Secrétariat général du Gouvernement) | Official gazette, one PDF per issue | no | The Constitution (n° 2025-12, numéro spécial 3) and the Charte (n° 2021-11); every later issue searched for amendments |
| [Codes en vigueur](https://journal-officiel.sgg.gov.gn/fr/textes-officiels/les-codes-consolides.html) (same site) | The codes in force, as Journal officiel issues | no | The Code civil: Journal officiel numéro spécial of August 2019, pages 02 to 85 |

## Licence

See [`LICENSE`](LICENSE). The texts are official legal texts of the Republic of Guinea, from the Journal officiel de la République de Guinée (Secrétariat général du Gouvernement), reproduced with that attribution; the Journal officiel publishes no licence for them, and their copyright status is not confirmed. Lexifina's own contributions (the arrangement, commit messages, tables and tools) are CC0 1.0.

No AI model wrote, translated or corrected legal text, and none runs when the history is built; the scripts were written by Claude Code running Claude Opus 5.5 (see [`REPRODUCE.md`](REPRODUCE.md)).

## En français

L'histoire du droit guinéen dans git : un fichier par article, chaque version enregistrée au jour de son entrée en vigueur, avec pour auteur le texte qui l'a faite. Le dépôt contient trois textes, chacun tel qu'adopté : la Constitution adoptée par le référendum du 21 septembre 2025, en vigueur depuis sa promulgation le 26 septembre 2025 ; la Charte de la Transition du 27 septembre 2021, en vigueur depuis sa signature ; et le Code civil (Loi L/2019/035/AN du 4 juillet 2019), en vigueur depuis sa promulgation le 26 juillet 2019. Aucune loi modificative n'a été trouvée dans les numéros du Journal officiel parus jusqu'au n° 2026-12 spécial du 27 octobre 2026, hormis trente numéros numérisés en image qui n'ont pas pu être examinés. L'article 196 de la Constitution maintient les organes de la Transition jusqu'à l'installation des nouvelles institutions ; aucune date de fin de la Charte n'est donc enregistrée ici. Texte en vigueur à une date : `python tools/en_vigueur_au.py 2026-01-01 constitution 44`.

## More

From [lexifina/global-law](https://github.com/lexifina/global-law):

- [FEATURES.md](https://github.com/lexifina/global-law/blob/main/FEATURES.md): every feature, and what every corpus must support (`git blame`, `law.py`, the MCP tools)
- [FAQ.md](https://github.com/lexifina/global-law/blob/main/FAQ.md): questions and answers · [CONTRIBUTING.md](https://github.com/lexifina/global-law/blob/main/CONTRIBUTING.md): proposing changes · [MCP.md](https://github.com/lexifina/global-law/blob/main/MCP.md): the MCP server · [REPRODUCE.md](https://github.com/lexifina/global-law/blob/main/REPRODUCE.md): how it was built · [CHANGELOG.md](https://github.com/lexifina/global-law/blob/main/CHANGELOG.md)
- [FRESHNESS.md](https://github.com/lexifina/global-law/blob/main/FRESHNESS.md): how current each corpus is · [Monitoring](https://github.com/lexifina/global-law/tree/main/monitoring): whether updates are running · [WATCHING.md](https://github.com/lexifina/global-law/blob/main/WATCHING.md): how each official source is watched for changes
- [performance/](https://github.com/lexifina/global-law/tree/main/performance): how fast the tools are, measured
- [visualisations/](https://github.com/lexifina/global-law/tree/main/visualisations): charts and bridges across the world's law
- [Vulnerabilities](https://github.com/lexifina/global-law/tree/main/vulnerabilities): mistakes in legislation as published
