# prompt-listener

> **Ein Fork-Master-Template, keine geteilte Abhängigkeit.** Ein versioniertes
> Master-Muster zur Analyse von Mensch-KI-Interaktionen: forke es, divergiere
> bewusst, registriere deinen Fork — der Master bleibt sauber, dein Fork lebt
> sein eigenes Leben.

[English version](README.md)

## Was es ist

Zwei Bausteine für Prompt-/Session-Forschung, im Kern stdlib-only:

1. **`prompt_analyzer.py`** — 5-Stufen-Pipeline über Agent-Session-Logs
   (JSONL): Roh-Extraktion → Themenfilter → LLM-Klassifikation
   (Typ/Thema/Zweck/Absicht/Methode) → Aggregation je Einheit → Statistik.
   Stufe 0–1 läuft ohne Abhängigkeiten (`--dry-run`); Stufe 2–4 nutzt einen
   LLM-Runner als **optionalen Nachbarn** (erkannt, nie vorausgesetzt).
2. **`schema/agent_event_v2.py`** — 850 Zeilen stdlib-only Provenienz-Schema
   (AgentEvent-Kern + 18 Sub-Ledger: Quelle, Autorität, Trust-Boundary,
   Tool-/MCP-Kontext, Memory-Einfluss, geplante vs. ausgeführte Aktion,
   Gate-Entscheidung, Review-Status) plus JSON-Schema und Tests. Eigenständig
   nützlich, wo „wer hat was auf welcher Autorität ausgelöst" festzuhalten ist.

## Das Template-Modell

Dieses Repo beantwortet eine echte Governance-Frage: *Was, wenn ein Konsument
die Logik ganz anders braucht?* Dann ist ein geteilter Import das falsche
Werkzeug — **stattdessen den Master forken**:

- Der **Master** ist versioniert, getestet und wird gepflegt.
- Ein **Fork** divergiert frei und wird vom Master *nicht* nachgezogen.
- Einzige Pflicht: eine Zeile in [`FORKS.md`](FORKS.md) (wo, wann, warum der
  Zweck divergiert). Ein Audit liest das als *deklarierte Divergenz* statt
  stiller Kopie.

Importieren, solange der Zweck gleich bleibt; forken, wenn er divergiert.

## Schnellstart

```bash
python prompt_analyzer.py session.jsonl --dry-run          # Stufe 0–1, ohne Abhängigkeiten
python prompt_analyzer.py session.jsonl --dry-run --agent-events-output out/events.jsonl
python -m pytest -q                                        # 14 Tests
```

## Provenienz

Ausgekapselt 2026-08-16 aus dem AI-LAB-Forschungsprojekt (das Korpora und
Ergebnisse privat behält und als Forschungs-Arbeitskopie weiterlebt — Fork #2
im Register). Erster registrierter Fork: TOM-lms `corpus_extract.py`
(Nutzermodell-Bau). Methoden-Paper: „Prompt-Archaeology" (research line).

## Lizenz

MIT.
