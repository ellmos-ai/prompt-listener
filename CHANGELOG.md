# Changelog

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
