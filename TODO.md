# TODO — prompt-listener (Fork-Master)

## STATUS

| Category | Status | Notes |
|----------|--------|-------|
| Secrets | :green_circle: OK | 0 Secrets in getrackten Dateien; AST- und Text-Scan sauber |
| Private Data (PII) | :green_circle: OK | 0 personenbezogene Entwicklerdaten oder PII in getrackten Dateien |
| Hardcoded Paths | :green_circle: OK | Keine hardcodierten Entwickler-Pfade (<HOME>/...); portable relative Pfade |
| Database Files | :green_circle: OK | 0 `.db` oder SQLite-Dateien im Repository getrackt |
| .env Files | :green_circle: OK | 0 `.env`-Dateien getrackt; `.gitignore` schützt Umgebungsvariablen |
| BACH Internals | :green_circle: OK | 0 BACH-interne Dokumente; eigenständiges, portables Werkzeug |
| .gitignore | :green_circle: OK | Alle Pflichtmuster (`__pycache__`, `*.pyc`, `.env`, `*.db`, etc.) gehärtet |
| Language & Parity | :green_circle: OK | Englisches `README.md`, zweisprachiges deutsches `README_de.md`, echte Umlaute |
| LICENSE & SBOM | :green_circle: OK | MIT-Lizenz, Level 1 SBOM (`THIRD_PARTY_LICENSES.md`), PEP 639 Metadaten |
| Overall | **PASS (10/10 Gates)** | `final_gate_check.py` 10 PASS, 0 FAIL, 0 WARN; Pytest grün |

**Audit-Datum:** 2026-11-07 (Geprüft durch Antigravity / Gemini worker via `[AI_MODULES_CARE]`)<br>
**Gate-Check-Ergebnis:** 10 PASS, 0 FAIL, 0 WARN (READY FOR PUBLIC RELEASE)<br>
**Testsuite-Status:** 32/32 Pytest-Tests bestanden (100% grün auf Windows)<br>
**Rolle:** Fork-Master-Template: Forks divergieren frei, Pflicht ist nur der `FORKS.md`-Eintrag<br>
**Typisierung & PEP 561:** `schema/py.typed` verankert, Trove-Classifier `"Typing :: Typed"`<br>
**Stand:** 2026-11-07 · Version 1.0.3

## Offen

- [ ] compare-race-Export-Adapter (Race-Artefakte → Stufe-0-JSONL) — Eintrag
      liegt im compare-race-TODO; bei Bau hier als Konsument oder Fork führen.
- [ ] Stufe-2-Runner-Probe formalisieren (marblerun/llmauto per enabled_probe
      statt PYTHONPATH-Konvention).

## Bewusst nicht gebaut

- **Fork-Synchronisierung** — Forks leben eigenständig (Template-Modell).
- **Forschungs-Reife-Gates** (evidence_gate) — Projektsteuerung des Labs,
  nicht Werkzeug-Substanz.

## Abgeschlossene Aufgaben

- [x] **TASK-PL-01: Final Gate Check Härtung (10/10 PASS), PEP 561 py.typed & TODO STATUS-Harmonisierung (v1.0.3)** (`effort=low`, `scope=hygiene`, priority `high`).
  - **Ergebnis:** False-Positive im Secret-Scanner von `final_gate_check.py` Gate 6 für `ToolCallRiskCategory.TOKEN_SECRET` in `schema/agent_event_v2.py` behoben; PEP 561 Marker `schema/py.typed` angelegt und in `pyproject.toml` als Package-Data sowie Trove-Classifier `"Typing :: Typed"` registriert; `TODO.md` mit standardisierter 10-Gate `## STATUS`-Tabelle, Stand 2026-11-07 und Testbestand (32/32 grün) aktualisiert; Vertragstests in `tests/test_metadata.py` erweitert.
