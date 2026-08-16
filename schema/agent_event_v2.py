"""AgentEvent v2 -- konsolidiertes Datenschema fuer Agenten-/Prompt-Sicherheitsaudits.

DATENSCHEMA (v2-Spezifikation gemaess `TODO.md`, P0-Block "AgentEvent-Schema vor
RawPrompt-Erweiterung festlegen" (Ideen-Check 2026-05-26) plus die nachfolgenden
P0/P1-Ergaenzungen aus den Forschungsstaenden 2026-05-16, 2026-06-03, 2026-06-04
(P-vs-NP-Transfer), BSD-Transfer 2026-05-26 und 2026-06-30. Konsolidiert die bis
dahin ueber mehrere `TODO.md`-Bloecke verstreuten Feldlisten in ein einziges,
operatives Artefakt -- als Vorbereitung fuer die geplante `RawPrompt`-Erweiterung,
NICHT als deren Ersatz.

KEIN ENFORCEMENT: Dieses Modul definiert nur Datenstrukturen. Es liest, schreibt,
blockiert oder bewertet keine echten Tool-Calls, Prompts oder MCP-Server. Ob ein
Feld in einer echten Pipeline befuellt, geprueft oder durchgesetzt wird, ist nicht
Teil dieses Moduls.

KEIN WIRKSAMKEITSNACHWEIS: Die Feldnamen operationalisieren Architekturmuster aus
Preprints und Community-Scannern (u. a. AgentSecBench, IterInject, AttriGuard,
AgentLeak, AgentPI, AgentLAB, Skill-Inject, MCP-Client-Vergleichsstudien,
WebMCP-Tool-Lifecycle-Preprints, AgentDojo-basierte automatisierte Angreifer,
Cisco mcp-scanner/Secure-Hulk). Das Vorhandensein eines Feldes belegt keine
gemessene Security-Wirksamkeit einer Methode -- siehe `GAPS.md`/`TODO.md` fuer den
Status "vorlaeufige Preprint-Evidenz, nicht repliziert".

Reine stdlib-Implementierung (dataclasses + Enums), keine externen Abhaengigkeiten.
"""

import dataclasses
import json
from dataclasses import dataclass, field, fields
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, get_args, get_origin

# ---------------------------------------------------------------------------
# Serialisierungs-Hilfsfunktionen
# ---------------------------------------------------------------------------


def _to_dict_value(value: Any) -> Any:
    """Rekursive Konvertierung: Enum -> .value, Dataclass -> dict, Liste/Dict -> rekursiv."""
    if isinstance(value, Enum):
        return value.value
    if is_agent_event_dataclass(value):
        return value.to_dict()
    if isinstance(value, (list, tuple)):
        return [_to_dict_value(v) for v in value]
    if isinstance(value, dict):
        return {k: _to_dict_value(v) for k, v in value.items()}
    return value


def is_agent_event_dataclass(value: Any) -> bool:
    """True, wenn `value` eine Instanz eines Dataclasses aus diesem Modul ist."""
    return dataclasses.is_dataclass(value) and not isinstance(value, type)


class _ToDictMixin:
    """Stellt `to_dict()` fuer alle Dataclasses dieses Moduls bereit (Enums -> .value)."""

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for f in fields(self):  # type: ignore[arg-type]
            result[f.name] = _to_dict_value(getattr(self, f.name))
        return result


# ---------------------------------------------------------------------------
# Geschlossene Vokabulare (str-Enums)
#
# Wo `TODO.md`/`GAPS.md` explizite Werte nennen, werden genau diese uebernommen.
# Wo die Semantik unterspezifiziert ist, wird konservativ ein Vokabular abgeleitet
# und um `other` erweitert (siehe Docstring je Enum).
# ---------------------------------------------------------------------------


class ActorKind(str, Enum):
    """Wer hat das Ereignis ausgeloest.

    Semantik im TODO unterspezifiziert: `actor_kind` wird im P0-Block
    "AgentEvent-Schema" (Ideen-Check 2026-05-26) nur als Feldname genannt, ohne
    Wertvokabular. Werte konservativ aus `GAPS.md` G1 abgeleitet (dieselbe
    Unterscheidung, die dort fuer Provenienz gefordert wird).
    """

    HUMAN = "human"
    AGENT = "agent"
    TOOL = "tool"
    MCP_SERVER = "mcp_server"
    SYSTEM = "system"
    SKILL = "skill"
    MEMORY = "memory"
    RETRIEVED_CONTENT = "retrieved_content"
    OTHER = "other"


class SourceChannel(str, Enum):
    """Herkunftskanal einer Nachricht/eines Events.

    Werte aus `GAPS.md` G1: "Unterscheidung zwischen User, System/Developer,
    Agent, Toolresultat, RAG-Content, Skill, Memory und MCP-Output".
    """

    USER = "user"
    SYSTEM_DEVELOPER = "system_developer"
    AGENT = "agent"
    TOOL_RESULT = "tool_result"
    RAG_CONTENT = "rag_content"
    SKILL = "skill"
    MEMORY = "memory"
    MCP_OUTPUT = "mcp_output"
    OTHER = "other"


class TrustBoundary(str, Enum):
    """Werte wortwoertlich aus `GAPS.md` G2 uebernommen."""

    TRUSTED = "trusted"
    UNTRUSTED = "untrusted"
    EXTERNAL = "external"
    INTERNAL = "internal"
    PRIVILEGED = "privileged"
    LOWER_PRIVILEGE = "lower_privilege"
    CROSS_BOUNDARY = "cross_boundary"
    OTHER = "other"


class Transport(str, Enum):
    """MCP-Transporttyp, aus `TODO.md` P1 2026-05-26 / bestaetigt P1 2026-06-03."""

    STDIO = "stdio"
    SSE = "sse"
    STREAMABLE_HTTP = "streamable_http"
    OTHER = "other"


class InstructionHierarchyLevel(str, Enum):
    """Autoritaetsebenen aus `TODO.md` P0 2026-05-16 "Instruction-Hierarchy-Ledger"."""

    SYSTEM_POLICY = "system_policy"
    DEVELOPER_PROJECT = "developer_project"
    USER = "user"
    AGENT = "agent"
    TOOL_OUTPUT = "tool_output"
    RETRIEVED_CONTENT = "retrieved_content"
    SKILL_PLUGIN = "skill_plugin"
    MEMORY = "memory"


class LeakChannel(str, Enum):
    """Werte aus `TODO.md` P1 2026-06-03 "Multi-Agent-Leak- und State-Channel-Ledger"."""

    OUTPUT = "output"
    INTER_AGENT_MESSAGE = "inter_agent_message"
    SHARED_MEMORY = "shared_memory"
    TOOL_ARGUMENT = "tool_argument"
    HANDOFF = "handoff"
    LOG_REENTRY = "log_reentry"
    RESOURCE_WRITE = "resource_write"
    PERSISTENT_STATE_CHANGE = "persistent_state_change"


class ToolCallRiskCategory(str, Enum):
    """Startregeln aus `TODO.md` P0 2026-05-26 "Tool-Call-Boundary-Gate"."""

    WRITE = "write"
    DELETE = "delete"
    SHELL = "shell"
    NETWORK = "network"
    TOKEN_SECRET = "token_secret"
    STDIO_MCP_START = "stdio_mcp_start"
    UNKNOWN_REMOTE_SERVER = "unknown_remote_server"
    PATH_OUTSIDE_PROJECT = "path_outside_project"
    EXFILTRATION_TARGET = "exfiltration_target"
    OTHER = "other"


class ProvenanceNodeKind(str, Enum):
    """Node-Typen aus `TODO.md` P0 2026-05-26 "Provenienzgraph / prompt_certificate"."""

    USER_PROMPT = "user_prompt"
    TOOL_DESCRIPTION = "tool_description"
    TOOL_OUTPUT = "tool_output"
    RESOURCE = "resource"
    MEMORY = "memory"
    SKILL = "skill"
    MCP_SERVER = "mcp_server"
    DECISION = "decision"


class ProvenanceEdgeKind(str, Enum):
    """Edge-Typen aus `TODO.md` P0 2026-05-26 "Provenienzgraph / prompt_certificate"."""

    READ_BY = "read_by"
    SUMMARIZED_INTO = "summarized_into"
    USED_AS_EVIDENCE = "used_as_evidence"
    TRIGGERED_ACTION = "triggered_action"


class AttestationStatus(str, Enum):
    """Semantik im TODO unterspezifiziert: `attestation_status` wird im P0-Block
    "AgentEvent-Schema" (Ideen-Check 2026-05-26) nur als Feldname genannt.
    Konservatives Vokabular, kompatibel mit dem separat definierten
    `McpCapabilityAttestation`-Ledger (Buchstabe p).
    """

    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"
    ATTESTED_VALID = "attested_valid"
    ATTESTED_INVALID = "attested_invalid"
    UNATTESTED = "unattested"


class ReviewStatus(str, Enum):
    """Semantik im TODO unterspezifiziert: `review_status` wird im P0-Block
    "AgentEvent-Schema" (Ideen-Check 2026-05-26) nur als Feldname genannt.
    Vokabular angelehnt an die "harte Blocks vs. weiche Review-Flags"-Trennung
    aus dem System-Medizin-Transfer 2026-05-17 (`TODO.md`).
    """

    PENDING = "pending"
    NOT_REQUIRED = "not_required"
    REVIEW_REQUIRED = "review_required"
    REVIEWED_OK = "reviewed_ok"
    REVIEWED_FLAGGED = "reviewed_flagged"


class RegressionCaseRole(str, Enum):
    """Rolle eines synthetischen Regression-Fixtures.

    Das Vokabular trennt sichtbare Positivangriffe, harmlose gematchte
    Kontrollen und reine Advice-/Label-Leak-Diagnostik.  Keine Rolle ist ein
    gemessenes Wirksamkeitsergebnis.
    """

    POSITIVE_ATTACK = "positive_attack"
    BENIGN_CONTROL = "benign_control"
    ADVICE_LEAK_CONTROL = "advice_leak_control"


class FixtureSplit(str, Enum):
    """Vorab festgelegter Fixture-Split; kein nachtraegliches Testset-Tuning."""

    DEVELOPMENT = "development"
    HELDOUT = "heldout"


class GateDecision(str, Enum):
    """Erwartete Designentscheidung eines Fixtures, nicht ausgefuehrtes Gate."""

    ALLOW = "allow"
    REVIEW = "review"
    BLOCK = "block"


# ---------------------------------------------------------------------------
# Kleine Hilfs-Dataclasses (innerhalb von Ledgern referenziert)
# ---------------------------------------------------------------------------


@dataclass
class SecurityGameAssessment(_ToDictMixin):
    """Drei-Dimensionen-Bewertung aus `TODO.md` P0 2026-06-03 (`security_game`-Feld
    des Policy-Projection-Ledgers): `instruction_integrity`,
    `retrieval_confidentiality`, `capability_integrity`.

    Werte als Freitext-Verdikt gefuehrt (TODO nennt keine geschlossene Werteliste,
    z. B. "held"/"broken"/"unknown").
    """

    instruction_integrity: str = ""
    retrieval_confidentiality: str = ""
    capability_integrity: str = ""


@dataclass
class ProvenanceNode(_ToDictMixin):
    """Ein Knoten im Provenienzgraphen, siehe `ProvenanceGraph`."""

    node_id: str = ""
    kind: Optional[ProvenanceNodeKind] = None
    label: str = ""


@dataclass
class ProvenanceEdge(_ToDictMixin):
    """Eine Kante im Provenienzgraphen, siehe `ProvenanceGraph`."""

    source_node_id: str = ""
    target_node_id: str = ""
    kind: Optional[ProvenanceEdgeKind] = None


# ---------------------------------------------------------------------------
# Sub-Ledger (a-r) -- je mit Quellenverweis auf den TODO.md-Block im Docstring
# ---------------------------------------------------------------------------


@dataclass
class PolicyProjectionLedger(_ToDictMixin):
    """(a) Quelle: `TODO.md` P0 2026-06-03 "Security-Game-/Policy-Projection-Ledger
    in `AgentEvent` aufnehmen".
    """

    authorized_observations: List[str] = field(default_factory=list)
    authorized_capabilities: List[str] = field(default_factory=list)
    projection_applied: Optional[bool] = None
    capability_restriction_applied: Optional[bool] = None
    model_visible_untrusted_channel: Optional[bool] = None
    output_validation_result: str = ""
    security_game: Optional[SecurityGameAssessment] = None
    permitted_leakage_scope: str = ""


@dataclass
class ToolcallAttribution(_ToDictMixin):
    """(b) Quelle: `TODO.md` P0 2026-06-03 "Kausale Toolcall-Attribution als
    Gate-Protokoll spezifizieren".
    """

    proposed_tool_call: str = ""
    user_intent_support: str = ""
    untrusted_observation_support: str = ""
    counterfactual_without_untrusted_observation: str = ""
    shadow_replay_pass: Optional[bool] = None
    causal_driver: str = ""
    attribution_confidence: Optional[float] = None
    tool_call_allowed: Optional[bool] = None
    manual_review_required: Optional[bool] = None


@dataclass
class AdaptiveAttackRun(_ToDictMixin):
    """(c) Quelle: `TODO.md` P0 2026-06-03 "Regressionstest-Harness um adaptive
    Angriffslaeufe erweitern".
    """

    optimizer_loop: str = ""
    diagnoser_label: str = ""
    payload_generation_history: List[str] = field(default_factory=list)
    best_attack_variant: str = ""
    adaptive_asr_delta: Optional[float] = None
    defense_degradation: Optional[float] = None
    attack_budget: str = ""
    heldout_attack_family: str = ""


@dataclass
class ContextAuthorizationLedger(_ToDictMixin):
    """(d) Quelle: `TODO.md` P0 2026-06-30 "Context-dependent Authorization Ledger
    ergaenzen" (siehe auch `GAPS.md` G15).
    """

    context_dependent_task: Optional[bool] = None
    context_dependency_allowed: Optional[bool] = None
    runtime_observation_source: str = ""
    runtime_observation_trust: str = ""
    context_suppression_risk: str = ""
    context_use_justification: str = ""
    context_hijack_indicator: Optional[bool] = None
    trustworthiness_utility_latency_tradeoff: str = ""


@dataclass
class LongHorizonEpisode(_ToDictMixin):
    """(e) Quelle: `TODO.md` P0 2026-06-30 "Long-Horizon Episode Ledger bauen"
    (siehe auch `GAPS.md` G16).

    Die frueheren Testklassen aus P1 2026-05-26 (`intent_hijacking`,
    `tool_chaining`, `task_injection`, `objective_drifting`, `memory_poisoning`)
    werden ueber die vier `*_flag`-Felder plus `tool_chain_delta` abgedeckt;
    kein separates `tool_chaining_flag`, da der 2026-06-30-Block dieses Feld
    nicht mehr fuehrt.
    """

    episode_id: str = ""
    turn_span: str = ""
    attack_stage: str = ""
    objective_shift: str = ""
    state_delta: str = ""
    memory_write_delta: str = ""
    tool_chain_delta: str = ""
    task_injection_flag: Optional[bool] = None
    intent_hijacking_flag: Optional[bool] = None
    objective_drifting_flag: Optional[bool] = None
    memory_poisoning_flag: Optional[bool] = None


@dataclass
class SkillSupplyChainCertificate(_ToDictMixin):
    """(f) Quelle: `TODO.md` P0/P1 2026-06-30 "Skill-Supply-Chain Certificate fuer
    Skill-Load-Events" (siehe auch `GAPS.md` G17).
    """

    skill_file_hash: str = ""
    skill_origin: str = ""
    declared_capabilities: List[str] = field(default_factory=list)
    executable_surface: str = ""
    hidden_instruction_flag: Optional[bool] = None
    context_dependent_attack_flag: Optional[bool] = None
    harmful_action_surface: str = ""
    authorization_framework_required: Optional[bool] = None
    skill_review_status: str = ""


@dataclass
class McpClientSecurityProfile(_ToDictMixin):
    """(g) Quelle: `TODO.md` P1 2026-06-30 "MCP-Client Security Profile ergaenzen"
    (siehe auch `GAPS.md` G18).

    `mcp_client_id`/`tool_surface_id` sind im TODO nicht als eigene Feldnamen
    genannt, aber durch "Pro Client/Toolsurface speichern" als Schluessel
    impliziert -- daher hier als Identifikationsfelder ergaenzt.
    """

    mcp_client_id: str = ""
    tool_surface_id: str = ""
    static_validation: str = ""
    parameter_visibility: str = ""
    injection_detection: str = ""
    user_warning_surface: str = ""
    execution_sandbox: str = ""
    audit_logging: str = ""
    cross_tool_poisoning_risk: str = ""
    hidden_parameter_risk: str = ""
    unauthorized_tool_invocation_risk: str = ""


@dataclass
class ToolLifecycleLedger(_ToDictMixin):
    """(h) Quelle: `TODO.md` P1/P2 2026-06-30 "WebMCP Tool-Lifecycle-Ledger
    vorbereiten" (siehe auch `GAPS.md` G19).
    """

    registration_origin: str = ""
    registration_time: str = ""
    origin_binding: str = ""
    lifecycle_consistency: str = ""
    third_party_script_surface: str = ""
    tool_hijack_flag: Optional[bool] = None
    tool_framing_flag: Optional[bool] = None
    metadata_role_drift: str = ""
    traceable_registration_log: str = ""


@dataclass
class AutomatedAttackerProfile(_ToDictMixin):
    """(i) Quelle: `TODO.md` P1 2026-06-30 "Automated-Attacker Profile in den
    Harness aufnehmen" (siehe auch `GAPS.md` G20).
    """

    attack_optimizer: str = ""
    attacker_model: str = ""
    attacker_safety_tuning: str = ""
    task_universal_flag: Optional[bool] = None
    heldout_task_transfer: str = ""
    ood_domain_transfer: str = ""
    frontier_transfer_status: str = ""
    compute_budget: str = ""
    attack_cost: str = ""


@dataclass
class LeakChannelRecord(_ToDictMixin):
    """(j) Quelle: `TODO.md` P1 2026-06-03 "Multi-Agent-Leak- und
    State-Channel-Ledger ergaenzen" (siehe auch `GAPS.md` G12).

    Bewusst minimal gehalten: Der TODO-Block spezifiziert ausschliesslich das
    erweiterte `leak_channel`-Vokabular, keine weiteren Begleitfelder. Es wird
    nichts ueber den TODO-Text hinaus erfunden.
    """

    leak_channel: Optional[LeakChannel] = None


@dataclass
class UtilitySecurityBalance(_ToDictMixin):
    """(k) Quelle: `TODO.md` P1 2026-06-03 "Utility-Security-Bilanz verpflichtend
    machen".
    """

    task_success: Optional[bool] = None
    attack_success: Optional[bool] = None
    false_block: Optional[bool] = None
    false_pass: Optional[bool] = None
    utility_under_attack: str = ""
    over_refusal: Optional[bool] = None
    recovery_possible: Optional[bool] = None
    manual_review_cost: str = ""


@dataclass
class AdviceFrontLedger(_ToDictMixin):
    """(l) Quelle: `TODO.md` P-vs-NP-Transfer 2026-06-04 "Advice-/Front-/
    Heldout-Ledger fuer AgentEvents".
    """

    reference_source: str = ""
    same_run_reference_risk: Optional[bool] = None
    advice_scope: str = ""
    matched_control_id: str = ""
    heldout_attack_family: str = ""
    positive_control_status: str = ""
    negative_control_status: str = ""
    tail_after_allowances: str = ""


@dataclass
class ShadowTailLedger(_ToDictMixin):
    """(m) Quelle: `TODO.md` BSD-Transfer 2026-05-26 "AgentEvent-Shadow-Tail".

    Die Prosa-Konzepte "Provenienzknoten", "Tool-/MCP-Kanal" und "Attestation"
    sind im Quelltext nicht als Backtick-Feldnamen gefuehrt und wurden hier in
    snake_case-Feldnamen uebersetzt (`provenance_node_ref`, `tool_or_mcp_channel`,
    `attestation_ref`). Die Backtick-Felder `advice_source`, `tail_sink` und
    `source_repair_status` sowie der "effektive Kanalrang" (`effective_channel_rank`)
    sind woertlich/direkt uebernommen.
    """

    provenance_node_ref: str = ""
    tool_or_mcp_channel: str = ""
    attestation_ref: str = ""
    advice_source: str = ""
    tail_sink: str = ""
    effective_channel_rank: Optional[float] = None
    source_repair_status: str = ""


@dataclass
class ProvenanceGraph(_ToDictMixin):
    """(n) Quelle: `TODO.md` P0 2026-05-26 "Provenienzgraph / `prompt_certificate`
    als Pflichtartefakt bauen".
    """

    nodes: List[ProvenanceNode] = field(default_factory=list)
    edges: List[ProvenanceEdge] = field(default_factory=list)
    trusted_evidence_missing: Optional[bool] = None


@dataclass
class ToolCallBoundaryGate(_ToDictMixin):
    """(o) Quelle: `TODO.md` P0 2026-05-26 "Tool-Call-Boundary-Gate als
    deterministische Schicht spezifizieren".

    `llm_signal_only` = True bedeutet: Diese Gate-Entscheidung beruhte nur auf
    einem LLM-Erkennungssignal, nicht auf einer der deterministischen
    `rbase_rules`/`rtask_rules` -- entspricht der TODO-Warnung "LLM-Erkennung nur
    als Signal, nicht als alleinige Grenze". Default `False` (deterministische
    Regel vorhanden).
    """

    rbase_rules: List[str] = field(default_factory=list)
    rtask_rules: List[str] = field(default_factory=list)
    risk_categories: List[ToolCallRiskCategory] = field(default_factory=list)
    confirmed_before_first_risky_use: Optional[bool] = None
    checked_per_toolcall: Optional[bool] = None
    llm_signal_only: bool = False


@dataclass
class McpCapabilityAttestation(_ToDictMixin):
    """(p) Quelle: `TODO.md` P1 2026-05-26 "MCP-Capability- und
    Attestation-Ledger ergaenzen".
    """

    declared_capabilities: List[str] = field(default_factory=list)
    observed_capabilities: List[str] = field(default_factory=list)
    authentication: str = ""
    signature_or_attestation: str = ""
    origin_tagging: str = ""
    message_integrity: str = ""
    transport: Optional[Transport] = None
    privilege_escalation_delta: str = ""


@dataclass
class ScannerFinding(_ToDictMixin):
    """(q) Quelle: `TODO.md` P1 2026-05-26 "MCP-Scanner-Adapter vorbereiten"."""

    scanner_name: str = ""
    scanner_version: str = ""
    rule_id: str = ""
    finding_type: str = ""
    severity: str = ""
    evidence_span: str = ""
    server_config_path: str = ""
    offline_scan: Optional[bool] = None
    needs_manual_review: Optional[bool] = None


@dataclass
class RegressionTestCase(_ToDictMixin):
    """(r) Versionierter Vertrag fuer synthetische Regression-Fixtures.

    Quelle: `TODO.md` P1 2026-05-16 "Regressionstest-Harness bauen" sowie
    `PL-R2-002` / TASKPLAN #327.  Die Felder beschreiben Testdesign und
    erwartetes Verhalten.  Leere Ergebnisfelder bedeuten, dass noch kein
    Defense-/Enforcement-Harness ausgefuehrt wurde.
    """

    attack_id: str = ""
    fixture_version: str = ""
    case_role: Optional[RegressionCaseRole] = None
    split: Optional[FixtureSplit] = None
    source: str = ""
    provenance_ref: str = ""
    attack_class: str = ""
    event_form: str = ""
    event_payload: Dict[str, Any] = field(default_factory=dict)
    expected_gate: Optional[GateDecision] = None
    actual_gate: str = ""
    leak_channel: Optional[LeakChannel] = None
    matched_control_id: str = ""
    heldout_attack_family: str = ""
    same_run_reference_risk: Optional[bool] = None
    label_visible_to_system_under_test: Optional[bool] = None
    falsification_hint: str = ""
    leak: Optional[bool] = None
    tool_misuse: Optional[bool] = None
    memory_poisoning: Optional[bool] = None
    state_change: Optional[bool] = None
    task_success: Optional[bool] = None
    attack_success: Optional[bool] = None
    false_positive: Optional[bool] = None
    false_negative: Optional[bool] = None


# ---------------------------------------------------------------------------
# Kern-Dataclass AgentEvent
# ---------------------------------------------------------------------------


@dataclass
class AgentEvent(_ToDictMixin):
    """Kern-Event des v2-Datenschemas.

    Quellen (siehe je Feldgruppe unten):
    - `TODO.md` P0 2026-05-26 "AgentEvent-Schema vor RawPrompt-Erweiterung
      festlegen" (Kernfelder `event_id` .. `review_status`).
    - `TODO.md` P0 2026-05-16 "v2-Datenschema planen und implementieren":
      nur die nicht bereits durch die Kernfelder abgedeckten Provenienz-/
      Autoritaetsfelder `source_authority`, `instruction_privilege`,
      `capability_scope`, `context_reentry`, `handoff_id`. Die im selben Block
      genannten `source_channel`/`origin_kind`/`trust_boundary` sind bereits
      Kernfelder; `tool_or_agent_origin` ueberschneidet sich mit
      `actor_kind`/`mcp_tool_name` und `memory_write` mit `memory_write_ids` --
      beide bewusst NICHT dupliziert (siehe Abdeckungsbericht der Auftragsantwort).
    - `TODO.md` P0 2026-05-16 "Instruction-Hierarchy-Ledger ergaenzen":
      `instruction_hierarchy_level`, `override_attempt_flag`.

    KEIN ENFORCEMENT, KEIN WIRKSAMKEITSNACHWEIS -- siehe Moduldocstring.
    """

    # --- Pflichtidentitaet ---
    event_id: str
    session_id: str

    # --- Kernfelder P0 2026-05-26 ---
    turn_index: Optional[int] = None
    actor_kind: Optional[ActorKind] = None
    source_channel: Optional[SourceChannel] = None
    origin_kind: Optional[str] = None
    message_origin: Optional[str] = None
    trust_boundary: Optional[TrustBoundary] = None
    transport: Optional[Transport] = None
    mcp_server_id: str = ""
    mcp_tool_name: str = ""
    mcp_capability_claims: List[str] = field(default_factory=list)
    tool_manifest_hash: str = ""
    tool_description_hash: str = ""
    resource_uri_hash: str = ""
    memory_read_ids: List[str] = field(default_factory=list)
    memory_write_ids: List[str] = field(default_factory=list)
    requested_action: str = ""
    planned_action: str = ""
    executed_action: str = ""
    external_effect: Optional[str] = None
    attestation_status: Optional[AttestationStatus] = None
    review_status: Optional[ReviewStatus] = None

    # --- Provenienz-/Autoritaetsfelder P0 2026-05-16 (v2-Datenschema) ---
    source_authority: Optional[str] = None
    instruction_privilege: Optional[str] = None
    capability_scope: List[str] = field(default_factory=list)
    context_reentry: Optional[bool] = None
    handoff_id: Optional[str] = None

    # --- Instruction-Hierarchy-Ledger P0 2026-05-16 ---
    instruction_hierarchy_level: Optional[InstructionHierarchyLevel] = None
    override_attempt_flag: Optional[bool] = None

    # --- Optionale Sub-Ledger (a-r), je Quellenverweis im jeweiligen Dataclass-Docstring ---
    policy_projection: Optional[PolicyProjectionLedger] = None
    toolcall_attribution: Optional[ToolcallAttribution] = None
    adaptive_attack_run: Optional[AdaptiveAttackRun] = None
    context_authorization: Optional[ContextAuthorizationLedger] = None
    long_horizon_episode: Optional[LongHorizonEpisode] = None
    skill_supply_chain_certificate: Optional[SkillSupplyChainCertificate] = None
    mcp_client_security_profile: Optional[McpClientSecurityProfile] = None
    tool_lifecycle_ledger: Optional[ToolLifecycleLedger] = None
    automated_attacker_profile: Optional[AutomatedAttackerProfile] = None
    leak_channel_record: Optional[LeakChannelRecord] = None
    utility_security_balance: Optional[UtilitySecurityBalance] = None
    advice_front_ledger: Optional[AdviceFrontLedger] = None
    shadow_tail_ledger: Optional[ShadowTailLedger] = None
    provenance_graph: Optional[ProvenanceGraph] = None
    tool_call_boundary_gate: Optional[ToolCallBoundaryGate] = None
    mcp_capability_attestation: Optional[McpCapabilityAttestation] = None
    scanner_findings: List[ScannerFinding] = field(default_factory=list)
    regression_test_case: Optional[RegressionTestCase] = None


# ---------------------------------------------------------------------------
# JSON-Schema-Bau (kein externes Paket)
# ---------------------------------------------------------------------------

_ENUM_TYPES = (
    ActorKind,
    SourceChannel,
    TrustBoundary,
    Transport,
    InstructionHierarchyLevel,
    LeakChannel,
    ToolCallRiskCategory,
    ProvenanceNodeKind,
    ProvenanceEdgeKind,
    AttestationStatus,
    ReviewStatus,
    RegressionCaseRole,
    FixtureSplit,
    GateDecision,
)

_DATACLASS_TYPES = (
    SecurityGameAssessment,
    ProvenanceNode,
    ProvenanceEdge,
    PolicyProjectionLedger,
    ToolcallAttribution,
    AdaptiveAttackRun,
    ContextAuthorizationLedger,
    LongHorizonEpisode,
    SkillSupplyChainCertificate,
    McpClientSecurityProfile,
    ToolLifecycleLedger,
    AutomatedAttackerProfile,
    LeakChannelRecord,
    UtilitySecurityBalance,
    AdviceFrontLedger,
    ShadowTailLedger,
    ProvenanceGraph,
    ToolCallBoundaryGate,
    McpCapabilityAttestation,
    ScannerFinding,
    RegressionTestCase,
    AgentEvent,
)


def _unwrap_optional(tp: Any) -> Any:
    """Entfernt `Optional[X]` (= `Union[X, None]`) und liefert `X` zurueck."""
    if get_origin(tp) is Union:
        args = [a for a in get_args(tp) if a is not type(None)]
        if len(args) == 1:
            return args[0]
    return tp


def _type_to_schema(tp: Any) -> Dict[str, Any]:
    """Bildet einen einzelnen Python-Typ (aus einer dataclass-Annotation) auf ein
    minimales JSON-Schema-Fragment ab. Keine externen Pakete, nur `typing`.
    """
    if get_origin(tp) is Union and type(None) in get_args(tp):
        inner_types = [arg for arg in get_args(tp) if arg is not type(None)]
        if len(inner_types) == 1:
            nullable_schema = _type_to_schema(inner_types[0])
            schema_type = nullable_schema.get("type")
            if isinstance(schema_type, str):
                nullable_schema["type"] = [schema_type, "null"]
            elif isinstance(schema_type, list) and "null" not in schema_type:
                nullable_schema["type"] = [*schema_type, "null"]
            if "enum" in nullable_schema and None not in nullable_schema["enum"]:
                nullable_schema["enum"] = [*nullable_schema["enum"], None]
            return nullable_schema

    tp = _unwrap_optional(tp)
    origin = get_origin(tp)

    if origin in (list, List):
        (item_type,) = get_args(tp) or (Any,)
        return {"type": "array", "items": _type_to_schema(item_type)}

    if origin in (dict, Dict):
        args = get_args(tp)
        value_type = args[1] if len(args) == 2 else Any
        return {"type": "object", "additionalProperties": _type_to_schema(value_type)}

    if isinstance(tp, type) and issubclass(tp, _ENUM_TYPES):
        return {"type": "string", "enum": [e.value for e in tp]}

    if isinstance(tp, type) and issubclass(tp, _DATACLASS_TYPES):
        return _dataclass_to_schema(tp)

    if tp is bool:
        return {"type": "boolean"}
    if tp is int:
        return {"type": "integer"}
    if tp is float:
        return {"type": "number"}
    if tp is str:
        return {"type": "string"}

    # Any / unaufgeloester Typ: permissives Schema
    return {}


def _dataclass_to_schema(cls: Any) -> Dict[str, Any]:
    """Baut ein JSON-Schema-Objekt fuer eine einzelne Dataclass per `dataclasses.fields`."""
    properties: Dict[str, Any] = {}
    required: List[str] = []
    for f in fields(cls):
        properties[f.name] = _type_to_schema(f.type)
        has_default = f.default is not dataclasses.MISSING or f.default_factory is not dataclasses.MISSING  # type: ignore[misc]
        if not has_default:
            required.append(f.name)
    schema: Dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema


def json_schema() -> Dict[str, Any]:
    """Baut das JSON-Schema-Dict fuer `AgentEvent` (inkl. aller Sub-Ledger)
    per `dataclasses.fields` -- ohne externes Paket.
    """
    schema = _dataclass_to_schema(AgentEvent)
    schema["$schema"] = "http://json-schema.org/draft-07/schema#"
    schema["title"] = "AgentEvent"
    schema["description"] = (
        "AgentEvent v2 -- Datenschema (kein Enforcement, kein Wirksamkeitsnachweis). "
        "Siehe schema/agent_event_v2.py Moduldocstring."
    )
    return schema


if __name__ == "__main__":
    out_path = Path(__file__).parent / "agent_event_v2.schema.json"
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(json_schema(), fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"JSON-Schema geschrieben nach: {out_path}")
