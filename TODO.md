# TODO — prompt-listener (Fork-Master)

## STATUS

| Category | Status |
|---|---|
| Tests | 14 passed (Werkzeug-Kern; Forschungs-Gate-Tests bleiben im Lab) |
| Sprachstufe (P-006) | Core: README DE+EN; Code/CLI englischsprachige Struktur, deutsche Pipeline-Ausgaben (Forschungssprache — bewusst) |
| Rolle | Fork-Master-Template: Forks divergieren frei, Pflicht ist nur der FORKS.md-Eintrag |
| Bewusste Entscheidung | Keine Rückkonsolidierung von Forks (User 2026-08-16); Forschungsdaten bleiben im Lab |

Stand: 2026-08-16 · Version 1.0.0

## Offen

- [ ] compare-race-Export-Adapter (Race-Artefakte → Stufe-0-JSONL) — Eintrag
      liegt im compare-race-TODO; bei Bau hier als Konsument oder Fork führen.
- [ ] Stufe-2-Runner-Probe formalisieren (marblerun/llmauto per enabled_probe
      statt PYTHONPATH-Konvention).

## Bewusst nicht gebaut

- **Fork-Synchronisierung** — Forks leben eigenständig (Template-Modell).
- **Forschungs-Reife-Gates** (evidence_gate) — Projektsteuerung des Labs,
  nicht Werkzeug-Substanz.
