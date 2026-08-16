"""Deterministische Nicht-Angriffs-Tests fuer den Stufe-0-Adapter."""

import json
import os
import subprocess
import sys
from pathlib import Path

from stage0_agent_event import (
    extract_agent_events_from_jsonl,
    read_agent_events_jsonl,
    validate_agent_event_payload,
    write_agent_events_jsonl,
)


PROJECT = Path(__file__).parent.parent
FIXTURE = Path(__file__).parent / "fixtures" / "stage0_non_attack.jsonl"


def _utf8_subprocess_env():
    """CLI-Tests auf Windows unabhaengig von der aktiven OEM-Codepage halten."""

    return {**os.environ, "PYTHONIOENCODING": "utf-8"}


def test_fixture_maps_human_agent_tool_and_mcp_without_text_guessing():
    events = extract_agent_events_from_jsonl(FIXTURE)
    payloads = [event.to_dict() for event in events]

    assert len(events) == 6
    assert [payload["actor_kind"] for payload in payloads] == [
        "human",
        "agent",
        "agent",
        "tool",
        "agent",
        "mcp_server",
    ]
    assert payloads[0]["source_channel"] == "user"
    assert payloads[3]["source_channel"] == "tool_result"
    assert payloads[5]["source_channel"] == "mcp_output"
    assert payloads[2]["requested_action"] == "Read"
    assert payloads[3]["executed_action"] == "Read"
    assert payloads[4]["mcp_server_id"] == "catalog"
    assert payloads[4]["mcp_tool_name"] == "lookup"
    assert payloads[5]["mcp_tool_name"] == "lookup"
    assert all(payload["trust_boundary"] is None for payload in payloads)
    assert all(payload["attestation_status"] == "unknown" for payload in payloads)
    assert all(payload["review_status"] == "pending" for payload in payloads)
    assert all("Bitte" not in json.dumps(payload, ensure_ascii=False) for payload in payloads)


def test_ids_are_deterministic_and_missing_session_is_explicit(tmp_path):
    fixture = tmp_path / "unknown-session.jsonl"
    fixture.write_text('{"type":"assistant","message":{"role":"assistant","content":"OK"}}\n', encoding="utf-8")

    first = extract_agent_events_from_jsonl(fixture)
    second = extract_agent_events_from_jsonl(fixture)

    assert [event.event_id for event in first] == [event.event_id for event in second]
    assert first[0].session_id == "unknown"
    assert first[0].turn_index is None
    assert first[0].trust_boundary is None
    assert first[0].message_origin == "jsonl:unknown-session.jsonl:line:1:slot:0"


def test_jsonl_export_validates_and_roundtrips(tmp_path):
    events = extract_agent_events_from_jsonl(FIXTURE)
    output = tmp_path / "agent-events.jsonl"

    assert write_agent_events_jsonl(events, output) == 6
    payloads = read_agent_events_jsonl(output)

    assert len(payloads) == 6
    assert payloads == [event.to_dict() for event in events]
    for payload in payloads:
        validate_agent_event_payload(payload)


def test_cli_agent_event_dry_run_does_not_write_event_export(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT / "prompt_analyzer.py"),
            str(FIXTURE),
            "--output-dir",
            str(tmp_path),
            "--dry-run",
            "--agent-events-dry-run",
        ],
        cwd=PROJECT,
        text=True,
        capture_output=True,
        check=False,
        encoding="utf-8",
        env=_utf8_subprocess_env(),
    )

    assert result.returncode == 0, result.stderr
    assert "6 AgentEvents validiert (kein Export)" in result.stdout
    assert not (tmp_path / "agent-events-v2.jsonl").exists()
    assert (tmp_path / "prompt-protocol.md").exists()


def test_cli_exports_agent_events_by_default(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT / "prompt_analyzer.py"),
            str(FIXTURE),
            "--output-dir",
            str(tmp_path),
            "--dry-run",
        ],
        cwd=PROJECT,
        text=True,
        capture_output=True,
        check=False,
        encoding="utf-8",
        env=_utf8_subprocess_env(),
    )

    assert result.returncode == 0, result.stderr
    assert len(read_agent_events_jsonl(tmp_path / "agent-events-v2.jsonl")) == 6


def test_top_level_tool_use_and_result_are_not_double_counted(tmp_path):
    fixture = tmp_path / "top-level-tools.jsonl"
    fixture.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "type": "tool_use",
                        "session_id": "sess-top",
                        "id": "call-1",
                        "name": "mcp__my_server__lookup_item",
                        "capability_claims": ["catalog_read"],
                    }
                ),
                json.dumps(
                    {
                        "type": "mcp_result",
                        "session_id": "sess-top",
                        "tool_use_id": "call-1",
                        "mcp_server_id": "my_server",
                        "mcp_tool_name": "lookup_item",
                        "content": "found",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    payloads = [event.to_dict() for event in extract_agent_events_from_jsonl(fixture)]

    assert len(payloads) == 2
    assert payloads[0]["mcp_server_id"] == "my_server"
    assert payloads[0]["mcp_tool_name"] == "lookup_item"
    assert payloads[0]["mcp_capability_claims"] == ["catalog_read"]
    assert payloads[1]["actor_kind"] == "mcp_server"
    assert payloads[1]["executed_action"] == "lookup_item"
