# Changelog

## [1.0.1] - 2026-09-10

- **Fix (Windows Console Encoding):** `prompt_analyzer.py` rekonfiguriert Standardausgaben (`sys.stdout`/`sys.stderr`) auf UTF-8 mit Fallback (`errors="replace"`), um `UnicodeEncodeError` bei Terminal-Ausgaben mit Emojis auf Windows-Konsolen (`cp1252`) zuverlässig zu verhindern.
- **Fix (Linter / Hygiene):** 5 Ruff-Lint-Warnungen in `prompt_analyzer.py` behoben (unbenutzte Imports `dataclasses.field`, `typing.Optional`, redundante `f`-Präfixe entfernt).
- **Tests:** Neue Test-Suite `tests/test_prompt_analyzer.py` ergänzt (Datenmodelle, Extraktion, Themen-Filterung, Kennzahlenberechnung, Artefakterzeugung und CLI-Trockenlauf `--dry-run`), Testbestand von 14 auf 19 Tests erhöht (100% bestanden).
- **Security:** `SECURITY.md` (DE/EN) nach P-006-Standard ergänzt (Sicherheitsrichtlinie, post-hoc Analyseprinzip, lokale Datenisolation, SLA).
- **Katalog-Standardisierung:** `ellmos-module.v2.json` auf Version `1.0.1` und `source_of_truth.type: "git-repository"` mit GitHub-Remote retypisiert, um `runtime_source` und `commit_sha` im `.MODULES`-Katalog nahtlos aufzulösen.

## [1.0.0] - 2026-08-16

Erstveroeffentlichung als **Fork-Master-Template** (Nutzerentscheid 2026-08-16:
eigenes Repo als versioniertes Master-Muster, dessen Logik schnell forkbar ist;
Forks divergieren bewusst und werden nur in FORKS.md registriert).

- Werkzeug-Kern ausgekapselt aus `.RESEARCH/.LAB/_AI-LAB/prompt-listener`
  (Erstanwendung Regress-Melder 04/2026; Methodik: Prompt-Archaeology):
  prompt_analyzer.py (5 Stufen), stage0_agent_event.py, schema/agent_event_v2
  (+ JSON Schema), fixture_corpus, 14 Tests.
- Forschungsdaten (_results/, _sources/) und Reife-Gates bleiben im Lab.
- FORKS.md-Register mit den zwei bekannten Forks (TOM-lm corpus_extract,
  AI-LAB-Arbeitskopie).
- Veralteten llmauto-Pfad im Docstring durch neutrale Nachbar-Formulierung
  ersetzt (llmauto lebt heute als Paket in MarbleRun).
