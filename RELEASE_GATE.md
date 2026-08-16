# Release Gate: prompt-listener

## Status

```
+------------------------------------------+
|                                          |
|          STATUS: UNLOCKED                |
|                                          |
+------------------------------------------+
```

> **LOCKED** = Repository must remain private.
> **UNLOCKED** = Repository may be set to public.

---

## Gate run 2026-08-16

`final_gate_check.py --repo-path .` → **10 PASS, 0 FAIL, 0 WARN — exit 0**
(process `MODULES/RELEASE_PROCESS.md` v1.0)

## Notes

- **Cut of the extraction:** tool core only (analyzer, stage0, schema, tests,
  fixture corpus). Research data (`_results/`, `_sources/`) and the lab's
  maturity-gate artefacts stay in the AI-LAB project (gitignored here); the
  lab-specific gate test was removed from this repo's suite.
- Stale personal path in the analyzer docstring (old llmauto location)
  replaced by a neutral optional-neighbour note.
- Role: **fork-master template** — forks diverge freely, sole duty is a
  FORKS.md entry (declared divergence). No fork synchronisation by design.
- Test suite: 14 passed (synthetic fixtures only, no network, no API key for
  stages 0–1).
- Reviewed by: Claude Code (fable-5), 2026-08-16
