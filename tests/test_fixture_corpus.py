"""Vertragstests fuer PL-R2-002; keine Defense-/Wirksamkeitstests."""

import copy
import json

import pytest

from fixture_corpus import DEFAULT_CORPUS_PATH, load_fixture_corpus
from schema.agent_event_v2 import FixtureSplit, GateDecision, RegressionCaseRole


def test_corpus_is_versioned_synthetic_and_contract_complete():
    corpus = load_fixture_corpus()

    assert corpus.corpus_id == "PL-R2-002-v1"
    assert corpus.schema_version == "1.0.0"
    assert len(corpus.cases) == 9
    assert "no security efficacy" in corpus.claim_ceiling.lower()
    assert all(case.fixture_version == corpus.schema_version for case in corpus.cases)
    assert all(case.actual_gate == "" for case in corpus.cases)
    assert all(case.attack_success is None for case in corpus.cases)
    assert all(case.event_payload["synthetic"] is True for case in corpus.cases)


def test_controls_heldout_and_advice_leak_are_precommitted():
    corpus = load_fixture_corpus()
    roles = [case.case_role for case in corpus.cases]

    assert roles.count(RegressionCaseRole.POSITIVE_ATTACK) == 4
    assert roles.count(RegressionCaseRole.BENIGN_CONTROL) == 4
    assert roles.count(RegressionCaseRole.ADVICE_LEAK_CONTROL) == 1

    heldout = [case for case in corpus.cases if case.split is FixtureSplit.HELDOUT]
    assert [case.attack_id for case in heldout] == ["pl-fixture-007-skill-injection"]
    assert heldout[0].heldout_attack_family == "skill_supply_chain_injection"
    assert heldout[0].label_visible_to_system_under_test is False

    advice = [case for case in corpus.cases if case.case_role is RegressionCaseRole.ADVICE_LEAK_CONTROL]
    assert len(advice) == 1
    assert advice[0].same_run_reference_risk is True
    assert advice[0].label_visible_to_system_under_test is True
    assert advice[0].expected_gate is GateDecision.REVIEW


def test_positive_attacks_have_existing_benign_matched_controls():
    corpus = load_fixture_corpus()
    by_id = {case.attack_id: case for case in corpus.cases}

    for case in corpus.cases:
        if case.case_role is RegressionCaseRole.POSITIVE_ATTACK:
            assert by_id[case.matched_control_id].case_role is RegressionCaseRole.BENIGN_CONTROL


def test_loader_rejects_duplicate_ids_and_prepopulated_results(tmp_path):
    raw = json.loads(DEFAULT_CORPUS_PATH.read_text(encoding="utf-8"))
    duplicate = copy.deepcopy(raw)
    duplicate["cases"][1]["attack_id"] = duplicate["cases"][0]["attack_id"]
    duplicate_path = tmp_path / "duplicate.json"
    duplicate_path.write_text(json.dumps(duplicate), encoding="utf-8")
    with pytest.raises(ValueError, match="eindeutig"):
        load_fixture_corpus(duplicate_path)

    prefilled = copy.deepcopy(raw)
    prefilled["cases"][0]["actual_gate"] = "block"
    prefilled_path = tmp_path / "prefilled.json"
    prefilled_path.write_text(json.dumps(prefilled), encoding="utf-8")
    with pytest.raises(ValueError, match="vor Harnesslauf"):
        load_fixture_corpus(prefilled_path)
