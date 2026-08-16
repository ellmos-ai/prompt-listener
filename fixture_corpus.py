"""Loader und fail-closed Vertrag fuer den synthetischen PL-R2-002-Korpus.

Das Modul validiert ausschliesslich Fixture-Metadaten. Es erkennt keine
Angriffe, blockiert keine Aktionen und misst keine Defense-Wirksamkeit.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Mapping

from schema.agent_event_v2 import (
    FixtureSplit,
    GateDecision,
    LeakChannel,
    RegressionCaseRole,
    RegressionTestCase,
)


DEFAULT_CORPUS_PATH = Path(__file__).parent / "tests" / "fixtures" / "regression_fixture_corpus_v1.json"
_RESULT_FIELDS = {
    "actual_gate",
    "leak",
    "tool_misuse",
    "memory_poisoning",
    "state_change",
    "task_success",
    "attack_success",
    "false_positive",
    "false_negative",
}


@dataclass(frozen=True)
class FixtureCorpus:
    corpus_id: str
    schema_version: str
    claim_ceiling: str
    cases: tuple[RegressionTestCase, ...]


def _require_text(payload: Mapping[str, Any], key: str, context: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}.{key}: nichtleerer String erforderlich")
    return value


def _optional_bool(payload: Mapping[str, Any], key: str, context: str) -> bool | None:
    value = payload.get(key)
    if value is not None and not isinstance(value, bool):
        raise ValueError(f"{context}.{key}: boolean oder null erforderlich")
    return value


def _case_from_payload(payload: Mapping[str, Any], index: int) -> RegressionTestCase:
    context = f"cases[{index}]"
    known_fields = {item.name for item in fields(RegressionTestCase)}
    unknown_fields = sorted(set(payload) - known_fields)
    if unknown_fields:
        raise ValueError(f"{context}: unbekannte Felder {unknown_fields}")

    event_payload = payload.get("event_payload")
    if not isinstance(event_payload, dict):
        raise ValueError(f"{context}.event_payload: Objekt erforderlich")
    if event_payload.get("synthetic") is not True:
        raise ValueError(f"{context}.event_payload.synthetic: muss true sein")
    payload_text = event_payload.get("payload_text")
    if not isinstance(payload_text, str) or not payload_text.startswith("[SYNTHETIC FIXTURE]"):
        raise ValueError(f"{context}.event_payload.payload_text: inertes Fixture-Präfix fehlt")

    for result_field in _RESULT_FIELDS:
        value = payload.get(result_field)
        if result_field == "actual_gate":
            if value not in (None, ""):
                raise ValueError(f"{context}.{result_field}: Ergebnis vor Harnesslauf unzulässig")
        elif value is not None:
            raise ValueError(f"{context}.{result_field}: Ergebnis vor Harnesslauf unzulässig")

    return RegressionTestCase(
        attack_id=_require_text(payload, "attack_id", context),
        fixture_version=_require_text(payload, "fixture_version", context),
        case_role=RegressionCaseRole(_require_text(payload, "case_role", context)),
        split=FixtureSplit(_require_text(payload, "split", context)),
        source=_require_text(payload, "source", context),
        provenance_ref=_require_text(payload, "provenance_ref", context),
        attack_class=_require_text(payload, "attack_class", context),
        event_form=_require_text(payload, "event_form", context),
        event_payload=dict(event_payload),
        expected_gate=GateDecision(_require_text(payload, "expected_gate", context)),
        actual_gate="",
        leak_channel=(LeakChannel(payload["leak_channel"]) if payload.get("leak_channel") else None),
        matched_control_id=str(payload.get("matched_control_id", "")),
        heldout_attack_family=str(payload.get("heldout_attack_family", "")),
        same_run_reference_risk=_optional_bool(payload, "same_run_reference_risk", context),
        label_visible_to_system_under_test=_optional_bool(
            payload, "label_visible_to_system_under_test", context
        ),
        falsification_hint=_require_text(payload, "falsification_hint", context),
    )


def load_fixture_corpus(path: Path = DEFAULT_CORPUS_PATH) -> FixtureCorpus:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Korpuswurzel muss ein Objekt sein")
    corpus_id = _require_text(raw, "corpus_id", "corpus")
    schema_version = _require_text(raw, "schema_version", "corpus")
    claim_ceiling = _require_text(raw, "claim_ceiling", "corpus")
    raw_cases = raw.get("cases")
    if not isinstance(raw_cases, list) or not 5 <= len(raw_cases) <= 10:
        raise ValueError("corpus.cases: 5 bis 10 Fixtures erforderlich")
    if not all(isinstance(item, dict) for item in raw_cases):
        raise ValueError("corpus.cases: jedes Fixture muss ein Objekt sein")

    cases = tuple(_case_from_payload(item, index) for index, item in enumerate(raw_cases))
    ids = [case.attack_id for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("corpus.cases: attack_id muss eindeutig sein")
    known_ids = set(ids)
    for case in cases:
        if case.matched_control_id and case.matched_control_id not in known_ids:
            raise ValueError(f"{case.attack_id}: matched_control_id verweist ins Leere")
        if case.matched_control_id == case.attack_id:
            raise ValueError(f"{case.attack_id}: Selbst-Matching ist unzulässig")
        if case.case_role is RegressionCaseRole.POSITIVE_ATTACK and not case.matched_control_id:
            raise ValueError(f"{case.attack_id}: Positivangriff braucht gematchte Kontrolle")

    roles = {case.case_role for case in cases}
    if RegressionCaseRole.POSITIVE_ATTACK not in roles or RegressionCaseRole.BENIGN_CONTROL not in roles:
        raise ValueError("Korpus braucht Positivangriffe und benigne Kontrollen")
    if not any(
        case.split is FixtureSplit.HELDOUT
        and case.case_role is RegressionCaseRole.POSITIVE_ATTACK
        and case.heldout_attack_family
        and case.label_visible_to_system_under_test is False
        for case in cases
    ):
        raise ValueError("Korpus braucht eine labelblinde Heldout-Angriffsfamilie")
    if not any(
        case.case_role is RegressionCaseRole.ADVICE_LEAK_CONTROL
        and case.same_run_reference_risk is True
        and case.label_visible_to_system_under_test is True
        and case.expected_gate is GateDecision.REVIEW
        for case in cases
    ):
        raise ValueError("Korpus braucht einen sichtbaren Same-run-/Advice-Leak-Diagnosefall")

    return FixtureCorpus(
        corpus_id=corpus_id,
        schema_version=schema_version,
        claim_ceiling=claim_ceiling,
        cases=cases,
    )


if __name__ == "__main__":
    corpus = load_fixture_corpus()
    print(
        json.dumps(
            {
                "corpus_id": corpus.corpus_id,
                "schema_version": corpus.schema_version,
                "case_count": len(corpus.cases),
                "roles": sorted({case.case_role.value for case in corpus.cases if case.case_role}),
                "heldout_ids": [case.attack_id for case in corpus.cases if case.split is FixtureSplit.HELDOUT],
                "claim_ceiling": corpus.claim_ceiling,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
