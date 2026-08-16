"""Deterministischer JSONL-zu-:class:`AgentEvent`-Adapter fuer Stufe 0.

Der Adapter liest ausschliesslich strukturierte JSON-Felder. Er klassifiziert
keinen Prompttext, erkennt keine Angriffe und trifft keine Enforcement-
Entscheidung. Nicht beobachtete Werte bleiben leer/``None`` oder werden mit
den vorhandenen Schemawerten ``unknown``/``pending`` markiert.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Optional

from schema.agent_event_v2 import (
    ActorKind,
    AgentEvent,
    AttestationStatus,
    ReviewStatus,
    SourceChannel,
    TrustBoundary,
    json_schema,
)


_MCP_TOOL_RE = re.compile(r"^mcp__(?P<server>.+?)__(?P<tool>.+)$")


def _first_string(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value:
            return value
    return ""


def _first_int(*values: Any) -> Optional[int]:
    for value in values:
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    return None


def _enum_or_none(enum_type: type, value: Any) -> Any:
    if not isinstance(value, str) or not value:
        return None
    try:
        return enum_type(value)
    except ValueError:
        return enum_type.OTHER


def _source_slug(path: Path) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", path.stem).strip("-").lower()
    return (slug or "jsonl")[:40]


def _event_identity(path: Path, line_number: int, slot: int) -> tuple[str, str]:
    source_ref = f"jsonl:{path.name}:line:{line_number}:slot:{slot}"
    event_id = f"evt-{_source_slug(path)}-{line_number:06d}-{slot:02d}"
    return event_id, source_ref


def _session_id(entry: Mapping[str, Any], message: Mapping[str, Any]) -> str:
    return _first_string(
        entry.get("session_id"),
        entry.get("sessionId"),
        message.get("session_id"),
        message.get("sessionId"),
    ) or "unknown"


def _mcp_parts(name: str, data: Mapping[str, Any]) -> tuple[str, str]:
    server_id = _first_string(data.get("mcp_server_id"), data.get("server_id"))
    tool_name = _first_string(data.get("mcp_tool_name"), name)
    match = _MCP_TOOL_RE.match(name)
    if match:
        server_id = server_id or match.group("server")
        tool_name = match.group("tool")
    return server_id, tool_name


def _is_mcp(kind: str, name: str, data: Mapping[str, Any]) -> bool:
    return (
        kind in {"mcp", "mcp_output", "mcp_result"}
        or bool(_first_string(data.get("mcp_server_id"), data.get("server_id")))
        or bool(_MCP_TOOL_RE.match(name))
        or data.get("source_channel") == SourceChannel.MCP_OUTPUT.value
    )


def _base_event(
    *,
    path: Path,
    line_number: int,
    slot: int,
    entry: Mapping[str, Any],
    message: Mapping[str, Any],
    actor_kind: ActorKind,
    source_channel: SourceChannel,
    origin_kind: str,
) -> AgentEvent:
    event_id, source_ref = _event_identity(path, line_number, slot)
    trust = _enum_or_none(
        TrustBoundary,
        entry.get("trust_boundary", message.get("trust_boundary")),
    )
    return AgentEvent(
        event_id=event_id,
        session_id=_session_id(entry, message),
        turn_index=_first_int(
            entry.get("turn_index"),
            entry.get("turnIndex"),
            message.get("turn_index"),
            message.get("turnIndex"),
        ),
        actor_kind=actor_kind,
        source_channel=source_channel,
        origin_kind=origin_kind or "unknown",
        message_origin=source_ref,
        trust_boundary=trust,
        attestation_status=AttestationStatus.UNKNOWN,
        review_status=ReviewStatus.PENDING,
        source_authority=(
            _first_string(entry.get("source_authority"), message.get("source_authority"))
            or None
        ),
        instruction_privilege=(
            _first_string(
                entry.get("instruction_privilege"),
                message.get("instruction_privilege"),
            )
            or None
        ),
    )


def _message_event(
    *,
    path: Path,
    line_number: int,
    slot: int,
    entry: Mapping[str, Any],
    message: Mapping[str, Any],
    role: str,
) -> AgentEvent:
    role_map = {
        "user": (ActorKind.HUMAN, SourceChannel.USER),
        "human": (ActorKind.HUMAN, SourceChannel.USER),
        "assistant": (ActorKind.AGENT, SourceChannel.AGENT),
        "agent": (ActorKind.AGENT, SourceChannel.AGENT),
        "system": (ActorKind.SYSTEM, SourceChannel.SYSTEM_DEVELOPER),
        "developer": (ActorKind.SYSTEM, SourceChannel.SYSTEM_DEVELOPER),
    }
    actor, channel = role_map.get(role, (ActorKind.OTHER, SourceChannel.OTHER))
    return _base_event(
        path=path,
        line_number=line_number,
        slot=slot,
        entry=entry,
        message=message,
        actor_kind=actor,
        source_channel=channel,
        origin_kind=f"{role or 'unknown'}_message",
    )


def _tool_use_event(
    *,
    path: Path,
    line_number: int,
    slot: int,
    entry: Mapping[str, Any],
    message: Mapping[str, Any],
    block: Mapping[str, Any],
) -> AgentEvent:
    name = _first_string(block.get("name"), block.get("tool_name"))
    mcp = _is_mcp("tool_use", name, block)
    server_id, tool_name = _mcp_parts(name, block)
    event = _base_event(
        path=path,
        line_number=line_number,
        slot=slot,
        entry=entry,
        message=message,
        actor_kind=ActorKind.AGENT,
        source_channel=SourceChannel.AGENT,
        origin_kind="mcp_tool_use" if mcp else "tool_use",
    )
    event.mcp_server_id = server_id if mcp else ""
    event.mcp_tool_name = tool_name or name
    event.requested_action = name
    event.planned_action = name
    event.handoff_id = _first_string(block.get("id"), block.get("tool_use_id")) or None
    claims = block.get("capability_claims", block.get("capability_scope", []))
    if isinstance(claims, list):
        event.capability_scope = [str(item) for item in claims]
        if mcp:
            event.mcp_capability_claims = [str(item) for item in claims]
    block_trust = _enum_or_none(TrustBoundary, block.get("trust_boundary"))
    if block_trust is not None:
        event.trust_boundary = block_trust
    return event


def _tool_result_event(
    *,
    path: Path,
    line_number: int,
    slot: int,
    entry: Mapping[str, Any],
    message: Mapping[str, Any],
    block: Mapping[str, Any],
    tool_names: Mapping[str, str],
) -> AgentEvent:
    tool_use_id = _first_string(block.get("tool_use_id"), block.get("id"))
    name = _first_string(
        block.get("name"),
        block.get("tool_name"),
        block.get("mcp_tool_name"),
        entry.get("mcp_tool_name"),
        tool_names.get(tool_use_id),
    )
    kind = _first_string(block.get("type"), entry.get("type")).lower()
    mcp = _is_mcp(kind, name, block) or _is_mcp(kind, name, entry)
    server_id, tool_name = _mcp_parts(name, {**entry, **block})
    event = _base_event(
        path=path,
        line_number=line_number,
        slot=slot,
        entry=entry,
        message=message,
        actor_kind=ActorKind.MCP_SERVER if mcp else ActorKind.TOOL,
        source_channel=SourceChannel.MCP_OUTPUT if mcp else SourceChannel.TOOL_RESULT,
        origin_kind="mcp_result" if mcp else "tool_result",
    )
    event.mcp_server_id = server_id if mcp else ""
    event.mcp_tool_name = tool_name or name
    event.executed_action = name or tool_name
    event.handoff_id = tool_use_id or None
    block_trust = _enum_or_none(TrustBoundary, block.get("trust_boundary"))
    if block_trust is not None:
        event.trust_boundary = block_trust
    return event


def _iter_entry_events(
    path: Path,
    line_number: int,
    entry: Mapping[str, Any],
    tool_names: dict[str, str],
) -> Iterator[AgentEvent]:
    message_value = entry.get("message")
    message: Mapping[str, Any] = message_value if isinstance(message_value, dict) else {}
    entry_type = _first_string(entry.get("type"), entry.get("role")).lower()
    role = _first_string(message.get("role"), entry.get("role"), entry_type).lower()
    content = message.get("content", entry.get("content"))
    slot = 0
    emitted = False

    if entry_type in {"tool_use", "mcp_tool_use"}:
        event = _tool_use_event(
            path=path,
            line_number=line_number,
            slot=slot,
            entry=entry,
            message=message,
            block=entry,
        )
        if event.handoff_id:
            tool_names[event.handoff_id] = event.requested_action
        yield event
        return

    if entry_type in {"tool", "tool_result", "result", "mcp", "mcp_result", "mcp_output"}:
        yield _tool_result_event(
            path=path,
            line_number=line_number,
            slot=slot,
            entry=entry,
            message=message,
            block=entry,
            tool_names=tool_names,
        )
        return

    if isinstance(content, str):
        yield _message_event(
            path=path,
            line_number=line_number,
            slot=slot,
            entry=entry,
            message=message,
            role=role,
        )
        slot += 1
        emitted = True
    elif isinstance(content, list):
        for block_value in content:
            if not isinstance(block_value, dict):
                continue
            block_type = _first_string(block_value.get("type")).lower()
            if block_type in {"tool_use", "mcp_tool_use"}:
                event = _tool_use_event(
                    path=path,
                    line_number=line_number,
                    slot=slot,
                    entry=entry,
                    message=message,
                    block=block_value,
                )
                if event.handoff_id:
                    tool_names[event.handoff_id] = event.requested_action
                yield event
                slot += 1
                emitted = True
            elif block_type in {"tool_result", "mcp_result", "mcp_output"}:
                yield _tool_result_event(
                    path=path,
                    line_number=line_number,
                    slot=slot,
                    entry=entry,
                    message=message,
                    block=block_value,
                    tool_names=tool_names,
                )
                slot += 1
                emitted = True
            elif block_type in {"text", "input_text", "output_text"}:
                yield _message_event(
                    path=path,
                    line_number=line_number,
                    slot=slot,
                    entry=entry,
                    message=message,
                    role=role,
                )
                slot += 1
                emitted = True

    if not emitted:
        yield _message_event(
            path=path,
            line_number=line_number,
            slot=slot,
            entry=entry,
            message=message,
            role=role,
        )


def extract_agent_events_from_jsonl(jsonl_path: Path) -> list[AgentEvent]:
    """Mappt jede parsebare JSONL-Zeile auf mindestens ein strukturelles Event."""

    events: list[AgentEvent] = []
    tool_names: dict[str, str] = {}
    with jsonl_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(entry, dict):
                continue
            events.extend(_iter_entry_events(jsonl_path, line_number, entry, tool_names))
    return events


def _validate_value(value: Any, schema: Mapping[str, Any], path: str) -> None:
    expected = schema.get("type")
    if isinstance(expected, list):
        if value is None and "null" in expected:
            return
        expected = next((item for item in expected if item != "null"), None)
    if expected == "object":
        if not isinstance(value, dict):
            raise ValueError(f"{path}: object erwartet")
        for required in schema.get("required", []):
            if required not in value:
                raise ValueError(f"{path}.{required}: Pflichtfeld fehlt")
        properties = schema.get("properties", {})
        for key, child in value.items():
            if key in properties:
                _validate_value(child, properties[key], f"{path}.{key}")
    elif expected == "array":
        if not isinstance(value, list):
            raise ValueError(f"{path}: array erwartet")
        item_schema = schema.get("items", {})
        for index, item in enumerate(value):
            _validate_value(item, item_schema, f"{path}[{index}]")
    elif expected == "string" and not isinstance(value, str):
        raise ValueError(f"{path}: string erwartet")
    elif expected == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
        raise ValueError(f"{path}: integer erwartet")
    elif expected == "number" and (not isinstance(value, (int, float)) or isinstance(value, bool)):
        raise ValueError(f"{path}: number erwartet")
    elif expected == "boolean" and not isinstance(value, bool):
        raise ValueError(f"{path}: boolean erwartet")

    allowed = schema.get("enum")
    if allowed is not None and value not in allowed:
        raise ValueError(f"{path}: Wert {value!r} nicht im Vokabular")


def validate_agent_event_payload(payload: Mapping[str, Any]) -> None:
    """Validiert ein serialisiertes Event gegen das stdlib-generierte Schema."""

    _validate_value(dict(payload), json_schema(), "$event")


def write_agent_events_jsonl(events: Iterable[AgentEvent], output_path: Path) -> int:
    """Validiert und exportiert AgentEvents als UTF-8-JSONL."""

    payloads = [event.to_dict() for event in events]
    for payload in payloads:
        validate_agent_event_payload(payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for payload in payloads:
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
    return len(payloads)


def read_agent_events_jsonl(input_path: Path) -> list[dict[str, Any]]:
    """Liest einen Export zurueck und validiert jede Zeile erneut."""

    payloads: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"Zeile {line_number}: JSON-Objekt erwartet")
            validate_agent_event_payload(payload)
            payloads.append(payload)
    return payloads
