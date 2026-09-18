# Changelog

## [1.0.3] - 2026-09-18

- **CI-Matrix- & Workflow-Härtung (Pfad A):** Vollständige Bereitstellung von GitHub Actions Workflows (`.github/workflows/`): `ci.yml` mit Multi-OS-Matrix (`ubuntu-latest`, `windows-latest`) über Python 3.10, 3.11, 3.12 und 3.13, Least-Privilege `contents: read`, Concurrency `cancel-in-progress: true` und 15-Minuten-Timeout; `stale.yml` (actions/stale@v9, täglicher Cron um 01:30 UTC, 10m Timeout); `welcome.yml` (actions/first-interaction@v3, 5m Timeout).
- **Multi-Host Cloud-Sync-, Lock- & Cache-Schutz:** `.gitignore` gehärtet gegen Multi-Host Konfliktdateien (`*conflicted copy*`, `*-ASUS*`, `*-ASUS-GEI*`, `*-WORKSTATION*`, `*-WORKSTATION-LG*`, `*-Mac Studio*`), systemweite Locks (`LOCK`, `LOCK.*`, `LOCK*.txt`, `LOCK.permissions.json`, `LOCK.user.*`, `LOCK.until.*`, `LOCK.condition.*`) und Build-/Tool-Caches (`uv.lock`, `.hypothesis/`, `.turbo/`, `.coverage*`).
- **PEP 621 Standardisierung & Packaging:** `pyproject.toml` um `build-system` (`setuptools>=61.0`), `license-files = ["LICENSE", "THIRD_PARTY_LICENSES.md"]`, Keywords, Classifiers für Python 3.10-3.13, standardisierte Ecosystem-URLs (`Homepage`, `Documentation`, `Repository`, `Issues`, `Bug Tracker`, `Changelog`, `Security`, `Third-Party Licenses`, `Parent Organization`, `Umbrella Ecosystem`, `Marketing Log`, `LLM Ready`) sowie `[tool.pytest.ini_options]` (`minversion = "7.0"`, `norecursedirs`) erweitert.
- **Rechtliche Absicherung (§ 521 BGB Gefälligkeitsrecht):** Gesetzlicher Haftungshinweis für unentgeltliche Bereitstellung in `README_de.md` und `README.md` verankert.
- **Dritte-Partei-Audit & Invarianten:** Re-Audit in `THIRD_PARTY_LICENSES.md` per 2026-09-18 (0 externe Runtime-Dependencies, 100% Python stdlib PSF-2.0, Zero-Copyleft, RunAsInvoker, Affirmation von `INV-LOCAL-01` bis `INV-SLA-10`).
- **Vertragstests & Metadaten-Härtung:** `tests/test_metadata.py` um automatisierte Contract-Tests erweitert (CI-Workflow Concurrency/Timeouts/Permissions, Gitignore-Muster, PEP 621 Metadaten/URLs/Pytest-Optionen, gesetzlicher Haftungshinweis gem. § 521 BGB und UTF-8-Integrität, Drittanbieter-Audit & SLA-Parität).
- **Manifest-Synchronisation:** Synchrone Version `1.0.3` über alle Manifeste und Dokumente (`pyproject.toml`, `ellmos-module.v2.json`, `llms.txt`, `CHANGELOG.md`, `THIRD_PARTY_LICENSES.md`, `MARKETING-LOG.txt`).

## [1.0.2] - 2026-09-14

- **Discoverability & Visual Architecture (Pfad B):** Zweisprachige Shields.io Badges (Python 3.10+, MIT, Tests 25 bestanden | 100% grün, Zero Network Egress, Schema AgentEvent v2, Architektur Zellmodell / Fork-Master).
- **Mermaid-Architektur- & Sequenzdiagramme:** Visuelle Systemarchitektur (`flowchart TD`) der 5 Pipeline-Stufen und des `AgentEvent v2`-Ledgers sowie Sequenzdiagramm (`sequenceDiagram` mit `autonumber`) zur Post-Hoc-Sitzungsanalyse mit striktem Mermaid-Syntax-Quoting (`HOOK-BANNER-ASSET-01`).
- **12-Punkte Zweisprachige Navigation:** Vollständige Anker-Parität zwischen `README.md` und `README_de.md`.
- **Zielgruppen- & SEO-Architektur:** 4 Zielgruppen-Personas (`[PERSONA-01]` bis `[PERSONA-04]`) und High-Intent Suchbegriffe zweisprachig eingepflegt.
- **10-Dimensionen-Vergleichsmatrix:** Strukturierter Vergleich gegenüber 4 Alternativen (Live-Telemetrie, Cloud-Tracing wie Langfuse/Phoenix, Ad-hoc Grep, Generisches OTEL), gemappt auf Invarianten `INV-LOCAL-01` bis `INV-SLA-10`.
- **Third-Party Lizenz-Audit (`THIRD_PARTY_LICENSES.md`):** Vollständiges SPDX-Inventar, Zero-Copyleft-Zertifizierung und Affirmation von 10 Governance- & Laufzeit-Invarianten.
- **Standardisierung:** `pyproject.toml` um PEP 621 URLs und `addopts = "-ra -v"` erweitert; Versionsharmonisierung auf `1.0.2` über alle Manifeste (`pyproject.toml`, `ellmos-module.v2.json`, `llms.txt`, `CHANGELOG.md`, `TODO.md`).
- **Vertragstests:** Neue automatisierte Testsuite `tests/test_metadata.py` zur Verifikation von Navigationsparität, Badges, Mermaid-Syntax, Personas, Vergleichsmatrix, Lizenz-Audit und Manifest-Konsistenz (Testbestand von 19 auf 25 Tests erhöht, 100% grün).

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
