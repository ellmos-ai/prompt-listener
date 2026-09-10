"""Tests für prompt_analyzer.py (Stufe 0–4 Pipeline-Funktionen & CLI)."""

import json
import subprocess
import sys
from pathlib import Path

from prompt_analyzer import (
    PROMPT_TYPES,
    CategorizedPrompt,
    RawPrompt,
    compute_statistics,
    extract_prompts_from_jsonl,
    filter_by_topics,
    write_stufe0,
    write_stufe1,
    write_stufe4,
)

FIXTURE = Path(__file__).parent / "fixtures" / "stage0_non_attack.jsonl"


def test_prompt_data_models_and_types_contract():
    raw = RawPrompt(
        id="P-001",
        timestamp="2026-09-10T10:00:00Z",
        sender="human",
        text="Analysiere bitte das Projekt.",
        text_short="Analysiere...",
        word_count=4,
    )
    assert raw.id == "P-001"
    assert raw.word_count == 4
    assert not raw.is_agent_prompt

    cat = CategorizedPrompt(
        id="P-002",
        timestamp="2026-09-10T10:01:00Z",
        sender="human",
        text="Korrigiere den Pfad.",
        type_code="KO",
        topic="Pfad",
        is_turning_point=True,
    )
    assert cat.type_code == "KO"
    assert cat.is_turning_point is True
    assert "KO" in PROMPT_TYPES
    assert PROMPT_TYPES["KO"] == "Korrektur"
    assert set(PROMPT_TYPES.keys()) >= {"SP", "NT", "NM", "NS", "KO", "BE", "RA", "MP"}


def test_extract_prompts_from_jsonl(tmp_path):
    session_file = tmp_path / "test_session.jsonl"
    lines = [
        json.dumps({
            "type": "user",
            "message": {
                "role": "user",
                "content": [{"type": "text", "text": "Erstelle eine neue Funktion."}],
            },
            "timestamp": "2026-09-10T10:00:00Z",
        }),
        json.dumps({
            "type": "user",
            "message": {
                "role": "user",
                "content": "<system-reminder>Ignore this system text</system-reminder>",
            },
            "timestamp": "2026-09-10T10:00:05Z",
        }),
        json.dumps({
            "type": "human",
            "message": "Zweiter Prompt zur Validierung.",
            "timestamp": "2026-09-10T10:01:00Z",
        }),
        json.dumps({
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": "Ich kümmere mich darum.",
            },
            "timestamp": "2026-09-10T10:02:00Z",
        }),
    ]
    session_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    prompts = extract_prompts_from_jsonl(session_file)
    assert len(prompts) == 2
    assert prompts[0].sender == "human"
    assert "Erstelle eine neue Funktion." in prompts[0].text
    assert prompts[1].text == "Zweiter Prompt zur Validierung."


def test_filter_by_topics():
    prompts = [
        RawPrompt(id="1", timestamp="", sender="human", text="Implementiere den Cache"),
        RawPrompt(id="2", timestamp="", sender="human", text="Fixe den Bug in der GUI"),
        RawPrompt(id="3", timestamp="", sender="human", text="Schreibe Tests für den Cache"),
    ]

    filtered = filter_by_topics(prompts, ["cache"])
    assert len(filtered) == 2
    assert [p.id for p in filtered] == ["1", "3"]

    filtered_gui = filter_by_topics(prompts, ["gui"])
    assert len(filtered_gui) == 1
    assert filtered_gui[0].id == "2"


def test_compute_statistics_and_write_artifacts(tmp_path):
    prompts = [
        CategorizedPrompt(
            id="H-001",
            timestamp="2026-09-10T10:00:00Z",
            sender="human",
            text="Initialer Start des Auftrags",
            word_count=5,
            topic="Setup",
            type_code="SP",
            is_turning_point=False,
        ),
        CategorizedPrompt(
            id="H-002",
            timestamp="2026-09-10T10:05:00Z",
            sender="human",
            text="Nein das ist falsch, bitte korrigieren",
            word_count=6,
            topic="Setup",
            type_code="KO",
            is_turning_point=True,
        ),
        CategorizedPrompt(
            id="H-003",
            timestamp="2026-09-10T10:10:00Z",
            sender="human",
            text="Ja genau, das passt jetzt so",
            word_count=6,
            topic="Validierung",
            type_code="BE",
            is_turning_point=False,
        ),
    ]

    from prompt_analyzer import aggregate_by_topic

    aggregated = aggregate_by_topic(prompts)
    stats = compute_statistics(prompts, aggregated)
    assert stats["total_prompts"] == 3
    assert stats["human_prompts"] == 3
    assert stats["turning_points_count"] == 1
    assert stats["bk_ratio"] == 1.0  # 1 BE : 1 KO

    # Verify writing stufe0, stufe1, stufe4
    out_s0 = tmp_path / "prompt-protocol.md"
    write_stufe0(prompts, out_s0)
    assert out_s0.exists()
    content_s0 = out_s0.read_text(encoding="utf-8")
    assert "H-001" in content_s0

    out_s1 = tmp_path / "filtered-prompt-protocol.md"
    write_stufe1(prompts, out_s1)
    assert out_s1.exists()

    out_s4 = tmp_path / "statistical-prompt-aggregation.md"
    write_stufe4(stats, out_s4)
    assert out_s4.exists()
    content_s4 = out_s4.read_text(encoding="utf-8")
    assert "Gesamtzahlen" in content_s4
    assert "Mensch-Maschine-Dynamik" in content_s4


def test_cli_dry_run_executes_cleanly_without_encoding_error(tmp_path):
    out_dir = tmp_path / "analysis_out"
    repo_root = Path(__file__).parent.parent
    cmd = [
        sys.executable,
        str(repo_root / "prompt_analyzer.py"),
        str(FIXTURE),
        "--dry-run",
        "--output-dir",
        str(out_dir),
    ]

    res = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, encoding="utf-8")
    assert res.returncode == 0, f"STDOUT: {res.stdout}\nSTDERR: {res.stderr}"
    assert (out_dir / "prompt-protocol.md").exists()
    assert (out_dir / "filtered-prompt-protocol.md").exists()
    assert (out_dir / "agent-events-v2.jsonl").exists()
