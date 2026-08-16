# prompt-listener

> **Eine zweckscharfe Funktionseinheit — wie eine Zelle.** Ihr einer Zweck:
> Prompts aus Agent-Sessions einsammeln und auswerten, und die Daten an
> beliebige Verwerter weitergeben (Workflow-Auswertung, Aktivitätsmuster,
> Nutzermodelle, Race-Auswertung). Gut geeignet als **Import** (ganz oder
> teilweise, als Datenlieferant) — und, wenn dein Zweck wirklich aus dieser
> Einheit herausdivergiert, als **Fork-Master**: forken, bewusst divergieren,
> Fork in FORKS.md registrieren.

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

Die volle Leiter: **Voll-Import** (Zweck identisch) → **partieller Import**
(nur die benötigten Teile nutzen — legitim, solange die *Funktionseinheit*
trägt; Kapseln sollten genau dafür breit und teilnutzbar gebaut sein) →
**Fork** (erst wenn der Zweck wirklich aus der Funktionseinheit
herausdivergiert). Teilnutzung ist nie ein Fork-Grund.

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
