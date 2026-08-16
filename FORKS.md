# Fork-Register — wer stammt von diesem Master ab

> Dieses Repo ist eine **Fork-Quelle** (versioniertes Master-Muster), keine
> geteilte Abhängigkeit: Wer die Logik anders braucht, **forkt und divergiert
> bewusst** — einzige Pflicht ist der Eintrag hier (Herkunfts-Deklaration).
> Der Master wird gepflegt; Forks leben eigenständig weiter und werden vom
> Master **nicht** nachgezogen.

| # | Fork | Ort | Abgezweigt | Zweck-Divergenz |
|---|---|---|---|---|
| 1 | TOM-lm `corpus_extract.py` | `<privat> _control-center/_TOM-lm/_tool/` | vor 2026-06 (aus `prompt_analyzer.py`) | Nutzermodell-Bau statt Session-Klassifikation: Korpus-Modus, Multi-Source, Outcome-Link |
| 2 | AI-LAB-Forschungsexemplar | `<privat> .RESEARCH/.LAB/_AI-LAB/prompt-listener/` | 2026-08-16 (Ursprungsort; Master wurde von dort ausgekapselt) | Forschungs-Arbeitskopie mit Korpora/Ergebnissen (`_results/`, `_sources/` — bleiben privat) |

## Eintragsregel

Neuer Fork = neue Zeile: Ort, Datum, ein Satz Zweck-Divergenz. Mehr nicht —
kein Rückführungsversprechen, keine Sync-Pflicht. Ein Audit liest diese Tabelle
als Legitimation der Doppelstruktur (deklarierte Divergenz statt stiller Kopie).
