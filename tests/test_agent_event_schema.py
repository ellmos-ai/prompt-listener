"""Tests fuer das AgentEvent-v2-Schema (`schema/agent_event_v2.py`).

Reine Struktur-/Serialisierungstests -- kein Enforcement- oder Wirksamkeitstest.
"""

import json
from dataclasses import fields
from pathlib import Path

import pytest

from schema.agent_event_v2 import (
    ActorKind,
    AdaptiveAttackRun,
    AdviceFrontLedger,
    AgentEvent,
    AttestationStatus,
    AutomatedAttackerProfile,
    ContextAuthorizationLedger,
    InstructionHierarchyLevel,
    LeakChannel,
    LeakChannelRecord,
    LongHorizonEpisode,
    McpCapabilityAttestation,
    McpClientSecurityProfile,
    PolicyProjectionLedger,
    ProvenanceEdge,
    ProvenanceEdgeKind,
    ProvenanceGraph,
    ProvenanceNode,
    ProvenanceNodeKind,
    RegressionTestCase,
    ReviewStatus,
    ScannerFinding,
    SecurityGameAssessment,
    ShadowTailLedger,
    SkillSupplyChainCertificate,
    SourceChannel,
    ToolCallBoundaryGate,
    ToolCallRiskCategory,
    ToolLifecycleLedger,
    ToolcallAttribution,
    Transport,
    TrustBoundary,
    UtilitySecurityBalance,
    json_schema,
)

SCHEMA_PATH = Path(__file__).parent.parent / "schema" / "agent_event_v2.schema.json"


def _build_full_agent_event() -> AgentEvent:
    """Ein voll befuelltes AgentEvent inkl. aller Sub-Ledger (a-r)."""
    return AgentEvent(
        event_id="evt-0001",
        session_id="sess-0001",
        turn_index=3,
        actor_kind=ActorKind.AGENT,
        source_channel=SourceChannel.TOOL_RESULT,
        origin_kind="mcp_tool_output",
        message_origin="external_mcp_server",
        trust_boundary=TrustBoundary.UNTRUSTED,
        transport=Transport.STDIO,
        mcp_server_id="mcp-server-1",
        mcp_tool_name="fetch_url",
        mcp_capability_claims=["network_read"],
        tool_manifest_hash="deadbeef",
        tool_description_hash="cafef00d",
        resource_uri_hash="abc123",
        memory_read_ids=["mem-1"],
        memory_write_ids=["mem-2"],
        requested_action="fetch remote resource",
        planned_action="fetch remote resource",
        executed_action="fetch remote resource",
        external_effect="network_call",
        attestation_status=AttestationStatus.UNATTESTED,
        review_status=ReviewStatus.REVIEW_REQUIRED,
        source_authority="developer_project",
        instruction_privilege="low",
        capability_scope=["fs_read"],
        context_reentry=True,
        handoff_id="handoff-1",
        instruction_hierarchy_level=InstructionHierarchyLevel.TOOL_OUTPUT,
        override_attempt_flag=True,
        policy_projection=PolicyProjectionLedger(
            authorized_observations=["obs-1"],
            authorized_capabilities=["cap-1"],
            projection_applied=True,
            capability_restriction_applied=True,
            model_visible_untrusted_channel=False,
            output_validation_result="passed",
            security_game=SecurityGameAssessment(
                instruction_integrity="held",
                retrieval_confidentiality="held",
                capability_integrity="held",
            ),
            permitted_leakage_scope="none",
        ),
        toolcall_attribution=ToolcallAttribution(
            proposed_tool_call="fetch_url",
            user_intent_support="high",
            untrusted_observation_support="low",
            counterfactual_without_untrusted_observation="would_not_occur",
            shadow_replay_pass=True,
            causal_driver="user_intent",
            attribution_confidence=0.9,
            tool_call_allowed=True,
            manual_review_required=False,
        ),
        adaptive_attack_run=AdaptiveAttackRun(
            optimizer_loop="loop-1",
            diagnoser_label="diag-1",
            payload_generation_history=["p1", "p2"],
            best_attack_variant="p2",
            adaptive_asr_delta=0.1,
            defense_degradation=0.05,
            attack_budget="10_queries",
            heldout_attack_family="family-a",
        ),
        context_authorization=ContextAuthorizationLedger(
            context_dependent_task=True,
            context_dependency_allowed=True,
            runtime_observation_source="tool_output",
            runtime_observation_trust="medium",
            context_suppression_risk="low",
            context_use_justification="required_for_task",
            context_hijack_indicator=False,
            trustworthiness_utility_latency_tradeoff="acceptable",
        ),
        long_horizon_episode=LongHorizonEpisode(
            episode_id="ep-1",
            turn_span="1-5",
            attack_stage="reconnaissance",
            objective_shift="none",
            state_delta="none",
            memory_write_delta="none",
            tool_chain_delta="none",
            task_injection_flag=False,
            intent_hijacking_flag=False,
            objective_drifting_flag=False,
            memory_poisoning_flag=False,
        ),
        skill_supply_chain_certificate=SkillSupplyChainCertificate(
            skill_file_hash="hash-1",
            skill_origin="local",
            declared_capabilities=["read_file"],
            executable_surface="python",
            hidden_instruction_flag=False,
            context_dependent_attack_flag=False,
            harmful_action_surface="none",
            authorization_framework_required=False,
            skill_review_status="reviewed_ok",
        ),
        mcp_client_security_profile=McpClientSecurityProfile(
            mcp_client_id="client-1",
            tool_surface_id="surface-1",
            static_validation="present",
            parameter_visibility="full",
            injection_detection="present",
            user_warning_surface="present",
            execution_sandbox="present",
            audit_logging="present",
            cross_tool_poisoning_risk="low",
            hidden_parameter_risk="low",
            unauthorized_tool_invocation_risk="low",
        ),
        tool_lifecycle_ledger=ToolLifecycleLedger(
            registration_origin="server_start",
            registration_time="2026-07-04T00:00:00Z",
            origin_binding="bound",
            lifecycle_consistency="consistent",
            third_party_script_surface="none",
            tool_hijack_flag=False,
            tool_framing_flag=False,
            metadata_role_drift="none",
            traceable_registration_log="log-ref-1",
        ),
        automated_attacker_profile=AutomatedAttackerProfile(
            attack_optimizer="greedy_coordinate_gradient",
            attacker_model="open_weight",
            attacker_safety_tuning="none",
            task_universal_flag=False,
            heldout_task_transfer="untested",
            ood_domain_transfer="untested",
            frontier_transfer_status="untested",
            compute_budget="low",
            attack_cost="low",
        ),
        leak_channel_record=LeakChannelRecord(leak_channel=LeakChannel.TOOL_ARGUMENT),
        utility_security_balance=UtilitySecurityBalance(
            task_success=True,
            attack_success=False,
            false_block=False,
            false_pass=False,
            utility_under_attack="high",
            over_refusal=False,
            recovery_possible=True,
            manual_review_cost="low",
        ),
        advice_front_ledger=AdviceFrontLedger(
            reference_source="p_vs_np_ledger",
            same_run_reference_risk=False,
            advice_scope="none",
            matched_control_id="ctrl-1",
            heldout_attack_family="family-a",
            positive_control_status="triggered",
            negative_control_status="not_triggered",
            tail_after_allowances="none",
        ),
        shadow_tail_ledger=ShadowTailLedger(
            provenance_node_ref="node-1",
            tool_or_mcp_channel="mcp-server-1",
            attestation_ref="attest-1",
            advice_source="none",
            tail_sink="none",
            effective_channel_rank=1.0,
            source_repair_status="repaired",
        ),
        provenance_graph=ProvenanceGraph(
            nodes=[
                ProvenanceNode(node_id="n1", kind=ProvenanceNodeKind.USER_PROMPT, label="prompt"),
                ProvenanceNode(node_id="n2", kind=ProvenanceNodeKind.TOOL_OUTPUT, label="output"),
            ],
            edges=[
                ProvenanceEdge(source_node_id="n1", target_node_id="n2", kind=ProvenanceEdgeKind.TRIGGERED_ACTION),
            ],
            trusted_evidence_missing=False,
        ),
        tool_call_boundary_gate=ToolCallBoundaryGate(
            rbase_rules=["no_shell"],
            rtask_rules=["no_network_without_confirm"],
            risk_categories=[ToolCallRiskCategory.NETWORK],
            confirmed_before_first_risky_use=True,
            checked_per_toolcall=True,
            llm_signal_only=False,
        ),
        mcp_capability_attestation=McpCapabilityAttestation(
            declared_capabilities=["network_read"],
            observed_capabilities=["network_read"],
            authentication="present",
            signature_or_attestation="none",
            origin_tagging="present",
            message_integrity="present",
            transport=Transport.STDIO,
            privilege_escalation_delta="none",
        ),
        scanner_findings=[
            ScannerFinding(
                scanner_name="mcp-scanner",
                scanner_version="1.0",
                rule_id="rule-1",
                finding_type="static",
                severity="low",
                evidence_span="line 1",
                server_config_path="/config.json",
                offline_scan=True,
                needs_manual_review=False,
            )
        ],
        regression_test_case=RegressionTestCase(
            attack_id="attack-1",
            source="AgentDojo",
            attack_class="tool_misuse",
            expected_gate="block",
            actual_gate="block",
            leak=False,
            tool_misuse=False,
            memory_poisoning=False,
            state_change=False,
            task_success=True,
            attack_success=False,
            false_positive=False,
            false_negative=False,
        ),
    )


def test_full_agent_event_to_dict_and_json_dumps():
    event = _build_full_agent_event()
    as_dict = event.to_dict()

    # Enums werden zu ihrem Wert serialisiert, keine Enum-Instanzen im Output
    assert as_dict["actor_kind"] == "agent"
    assert as_dict["trust_boundary"] == "untrusted"
    assert as_dict["policy_projection"]["security_game"]["instruction_integrity"] == "held"
    assert as_dict["provenance_graph"]["nodes"][0]["kind"] == "user_prompt"
    assert as_dict["leak_channel_record"]["leak_channel"] == "tool_argument"

    # muss vollstaendig JSON-serialisierbar sein
    dumped = json.dumps(as_dict, ensure_ascii=False)
    assert isinstance(dumped, str)
    reloaded = json.loads(dumped)
    assert reloaded["event_id"] == "evt-0001"


def test_enum_rejects_fantasy_value():
    with pytest.raises(ValueError):
        TrustBoundary("does_not_exist")
    with pytest.raises(ValueError):
        LeakChannel("made_up_channel")
    with pytest.raises(ValueError):
        ActorKind("not_a_real_actor")


def test_json_schema_contains_core_field_names():
    schema = json_schema()
    assert schema["type"] == "object"
    properties = schema["properties"]

    core_fields = [f.name for f in fields(AgentEvent)]
    for name in core_fields:
        assert name in properties, f"Kernfeld '{name}' fehlt im JSON-Schema"

    # Enum-Feld muss als string+enum abgebildet sein
    assert set(properties["trust_boundary"]["type"]) == {"string", "null"}
    assert set(properties["trust_boundary"]["enum"]) == {
        *(e.value for e in TrustBoundary),
        None,
    }

    # verschachtelte Sub-Ledger muessen als object-Schema mit eigenen properties auftauchen
    assert set(properties["policy_projection"]["type"]) == {"object", "null"}
    assert "security_game" in properties["policy_projection"]["properties"]

    # Pflichtfelder ohne Default muessen als required markiert sein
    assert "event_id" in schema.get("required", [])
    assert "session_id" in schema.get("required", [])


def test_schema_file_exists_and_is_parsable():
    assert SCHEMA_PATH.exists(), f"Schema-Datei fehlt: {SCHEMA_PATH}"
    with SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert data["title"] == "AgentEvent"
    assert "event_id" in data["properties"]
