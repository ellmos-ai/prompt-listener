# Security Policy / Sicherheitsrichtlinie

## Supported Versions / Unterstützte Versionen

| Version | Supported / Unterstützt |
| ------- | ----------------------- |
| 1.0.x   | :white_check_mark:      |
| < 1.0   | :x:                     |

---

## English Security Policy

### Core Security & Data Privacy Principles

`prompt-listener` is a modular template and analysis pipeline for post-hoc prompt and session evaluation. It is built with clear boundaries and local privacy guarantees:

1. **Post-Hoc Analysis Only (No Live Monitoring):**
   - `prompt-listener` evaluates static, user-provided session log files (JSONL) after a session has ended.
   - It contains no daemons, no background hooks, and no mechanisms to inspect live terminal sessions or track user activity.

2. **Zero Network Egress by Default (Stages 0–1):**
   - Extraction of raw prompts (Stage 0) and keyword/topic filtering (Stage 1) operate strictly with standard library tools, requiring zero network access and zero credentials.
   - Classification stages (Stages 2–4) only invoke language model endpoints if explicitly configured with an optional local runner or API client.

3. **Credential & Secret Protection:**
   - Secrets, tokens, or API keys are never embedded in the code or fixtures.
   - Configuration files with credentials (e.g. `~/.config/prompt_analyzer/config.json`) must reside in user-private storage and are excluded from git.

### Reporting a Vulnerability

If you identify a security vulnerability in `prompt-listener`, please report it privately:

1. **GitHub Security Advisory (Preferred):** Open a private security advisory at [ellmos-ai/prompt-listener Security Advisories](https://github.com/ellmos-ai/prompt-listener/security/advisories).
2. **Email Contacts:** Send findings to `security@open-bricks.org` and `security@ellmos.ai` (CC: `lukas@open-bricks.org`, `support@lukasgeiger.com`).

**Service Level Agreement (SLA):**
- **Acknowledgment:** Within 48 hours.
- **Triage & Status Assessment:** Within 5 business days.
- **Remediation & Fix Release:** Handled with priority according to verified testing.

Please do not open public issues or public pull requests for potential security vulnerabilities.

---

## Deutsche Sicherheitsrichtlinie (German)

### Grundsätze zu Sicherheit und Datenschutz

`prompt-listener` dient der nachträglichen Auswertung von Prompt- und Session-Protokollen. Das Modul unterliegt strikten Sicherheits- und Isolationsregeln:

1. **Ausschließlich nachträgliche Analyse (Kein Live-Monitoring):**
   - `prompt-listener` liest ausschließlich vom Nutzer explizit übergebene Protokolldateien (JSONL) vergangener Sessions aus.
   - Es enthält keinerlei Mechanismen zur Live-Überwachung von Benutzereingaben, Tastaturanschlägen oder aktiven Entwicklungsumgebungen.

2. **Vollständige Netzwerklosigkeit im Standardbetrieb (Stufe 0–1):**
   - Die Rohdaten-Extraktion (Stufe 0) und thematische Filterung (Stufe 1) nutzen ausschließlich die Python-Standardbibliothek und erfordern weder Netzwerkzugriff noch Anmeldedaten.
   - Nachgelagerte Klassifikationen (Stufe 2–4) greifen nur dann auf Sprachmodelle zu, wenn ein externer Runner oder API-Schlüssel vom Anwender ausdrücklich bereitgestellt wird.

3. **Schutz von Schlüsseln und vertraulichen Daten:**
   - API-Schlüssel oder Tokens werden niemals im Repository gespeichert.
   - Etwaige Konfigurationsdateien verbleiben im lokalen Benutzerverzeichnis und werden über `.gitignore` vom Versionsmanagement ausgeschlossen.

### Melden von Sicherheitslücken

Sollten Sie eine Sicherheitslücke in `prompt-listener` entdecken, melden Sie diese bitte vertraulich:

1. **GitHub Security Advisory (Bevorzugt):** Erstellen Sie einen vertraulichen Hinweis unter [ellmos-ai/prompt-listener Security Advisories](https://github.com/ellmos-ai/prompt-listener/security/advisories).
2. **E-Mail-Kontakt:** Senden Sie die Dokumentation an `security@open-bricks.org` und `security@ellmos.ai` (CC: `lukas@open-bricks.org`, `support@lukasgeiger.com`).

**Reaktionszeiten (SLA):**
- **Eingangsbestätigung:** Innerhalb von 48 Stunden.
- **Ersteinschätzung & Status:** Innerhalb von 5 Werktagen.
- **Korrektur & Veröffentlichung:** Zeitnah nach Verifikation der Sicherheitsmaßnahme.
