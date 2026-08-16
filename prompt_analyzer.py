#!/usr/bin/env python3
"""
Prompt-Analyzer: Automatische 5-Stufen-Pipeline für Research-Sessions
=====================================================================
Liest Claude Code JSONL Session-Logs, extrahiert Prompts,
klassifiziert sie per Haiku und erzeugt die 5-Stufen-Analyse.

Nutzung:
    PYTHONIOENCODING=utf-8 python prompt_analyzer.py <session.jsonl> [--project regress]
    PYTHONIOENCODING=utf-8 python prompt_analyzer.py <session.jsonl> --topics "V1,V2,Regress,CORE"
    PYTHONIOENCODING=utf-8 python prompt_analyzer.py <session.jsonl> --dry-run  # nur extrahieren, nicht klassifizieren

Klassifikation (Stufe 2-4) nutzt einen LLM-Runner als OPTIONALEN Nachbarn
    (erkannt, nie vorausgesetzt -- z. B. das llmauto-Paket aus MarbleRun oder
    ein eigener Anthropic-Client). Ohne ihn laeuft alles bis Stufe 1 (--dry-run).

Output (im gleichen Verzeichnis wie die JSONL oder --output-dir):
    prompt-protocol.md                  (Stufe 0: Rohdaten)
    filtered-prompt-protocol.md         (Stufe 1: themenfiltriert)
    categorized-prompt-protocol.md      (Stufe 2: klassifiziert)
    aggregated-prompt-protocol.md       (Stufe 3: pro Analyse)
    statistical-prompt-aggregation.md   (Stufe 4: Statistik)

Voraussetzungen:
    pip install anthropic
    ANTHROPIC_API_KEY in Umgebung oder ~/.config/prompt_analyzer/config.json
"""

import json
import sys
import os
import re
import argparse
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from collections import Counter, defaultdict
from typing import Optional

from stage0_agent_event import (
    extract_agent_events_from_jsonl,
    validate_agent_event_payload,
    write_agent_events_jsonl,
)

# ---------------------------------------------------------------------------
# Datenmodell
# ---------------------------------------------------------------------------

PROMPT_TYPES = {
    "SP": "Startprompt",
    "NT": "Nachfrage-Thema",
    "NM": "Nachfrage-Methode",
    "NS": "Nachfrage-Steuerung",
    "KO": "Korrektur",
    "BE": "Bestätigung",
    "RA": "Richtungsänderung",
    "MP": "Meta-Prompt",
}

@dataclass
class RawPrompt:
    """Stufe 0: Rohdaten"""
    id: str
    timestamp: str
    sender: str          # human / assistant / tool
    text: str
    text_short: str = ""
    word_count: int = 0
    session_id: str = ""
    is_agent_prompt: bool = False
    agent_name: str = ""

@dataclass
class CategorizedPrompt(RawPrompt):
    """Stufe 2: Klassifiziert"""
    topic: str = ""
    type_code: str = ""      # SP/NT/NM/NS/KO/BE/RA/MP
    purpose: str = ""
    intent: str = ""
    method_triggered: str = ""
    consequence: str = ""
    result: str = ""
    confidence: float = 1.0
    is_turning_point: bool = False

# ---------------------------------------------------------------------------
# Stufe 0: JSONL Extraktion
# ---------------------------------------------------------------------------

def extract_prompts_from_jsonl(jsonl_path: Path) -> list[RawPrompt]:
    """Liest JSONL und extrahiert alle Human-Messages und Agent-Prompts."""
    prompts = []
    session_id = jsonl_path.stem
    h_counter = 0
    a_counter = 0

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Human messages (Claude Code format: type="user", message.role="user")
            is_user = False
            text = ""
            if entry.get("type") == "user":
                msg = entry.get("message", {})
                if isinstance(msg, dict) and msg.get("role") == "user":
                    content = msg.get("content", "")
                    if isinstance(content, list):
                        text = " ".join(
                            b.get("text", "") for b in content
                            if isinstance(b, dict) and b.get("type") == "text"
                        )
                    elif isinstance(content, str):
                        text = content
                    is_user = True
            elif entry.get("type") == "human" or entry.get("role") == "human":
                if isinstance(entry.get("message"), str):
                    text = entry["message"]
                elif isinstance(entry.get("content"), list):
                    text = " ".join(
                        b.get("text", "") for b in entry["content"]
                        if isinstance(b, dict) and b.get("type") == "text"
                    )
                elif isinstance(entry.get("content"), str):
                    text = entry["content"]
                is_user = True

            if is_user:

                if text and len(text.strip()) > 0:
                    text = text.strip()
                    # Skip system messages and tool results
                    if text.startswith("<system-reminder>") or text.startswith("<task-notification>"):
                        continue
                    h_counter += 1
                    words = text.split()
                    prompts.append(RawPrompt(
                        id=f"H{h_counter:03d}",
                        timestamp=entry.get("timestamp", ""),
                        sender="human",
                        text=text,
                        text_short=" ".join(words[:15]) + ("..." if len(words) > 15 else ""),
                        word_count=len(words),
                        session_id=session_id,
                    ))

            # Agent prompts (in tool_use blocks, Claude Code: type="assistant")
            msg_for_agent = entry.get("message", {}) if entry.get("type") == "assistant" else entry
            if entry.get("type") == "assistant" or entry.get("role") == "assistant":
                content = msg_for_agent.get("content", []) if isinstance(msg_for_agent, dict) else []
                if isinstance(content, list):
                    for block in content:
                        if (isinstance(block, dict) and
                            block.get("type") == "tool_use" and
                            block.get("name") == "Agent"):
                            agent_input = block.get("input", {})
                            prompt_text = agent_input.get("prompt", "")
                            agent_name = agent_input.get("name", agent_input.get("description", ""))
                            if prompt_text:
                                a_counter += 1
                                words = prompt_text.split()
                                prompts.append(RawPrompt(
                                    id=f"A{a_counter:03d}",
                                    timestamp=entry.get("timestamp", ""),
                                    sender="assistant",
                                    text=prompt_text,
                                    text_short=" ".join(words[:15]) + ("..." if len(words) > 15 else ""),
                                    word_count=len(words),
                                    session_id=session_id,
                                    is_agent_prompt=True,
                                    agent_name=str(agent_name),
                                ))

    return prompts

# ---------------------------------------------------------------------------
# Stufe 1: Themenfilter
# ---------------------------------------------------------------------------

def filter_by_topics(prompts: list[RawPrompt], topics: list[str]) -> list[RawPrompt]:
    """Filtert Prompts nach Themen-Keywords."""
    if not topics:
        return prompts
    pattern = re.compile("|".join(re.escape(t) for t in topics), re.IGNORECASE)
    return [p for p in prompts if pattern.search(p.text)]

# ---------------------------------------------------------------------------
# Stufe 2: Klassifikation per Haiku
# ---------------------------------------------------------------------------

CLASSIFICATION_SYSTEM_PROMPT = """Du bist ein Forschungsmethodiker der Prompts in KI-gestützter Forschung klassifiziert.

Für jeden Prompt, antworte als JSON mit diesen Feldern:
- topic: Thema (z.B. "V1-Schutzstufenmodell", "Definitionsdivergenz", "Review", "Meta")
- type_code: SP/NT/NM/NS/KO/BE/RA/MP
  SP=Startprompt (neue Analyse), NT=Nachfrage-Thema, NM=Nachfrage-Methode,
  NS=Nachfrage-Steuerung, KO=Korrektur, BE=Bestätigung, RA=Richtungsänderung, MP=Meta-Prompt
- purpose: Was soll erreicht werden? (1 Satz)
- intent: Strategische Absicht (Erkenntnisgewinn/QS/Nachsteuerung/Richtungswechsel)
- method_triggered: Ausgelöste Methode (WebSearch/Multi-Agent/Review/Edit/keine)
- consequence: Unmittelbare Folge (1 Satz)
- is_turning_point: true/false (fundamentaler Richtungswechsel?)

Antworte NUR als JSON. Kein Markdown, kein Text drumherum."""

def classify_prompts_batch(prompts: list[RawPrompt], llmauto_path: str = "") -> list[CategorizedPrompt]:
    """Klassifiziert Prompts in Batches per llmauto pipe (Haiku)."""
    import subprocess
    import tempfile

    # llmauto Pfad bestimmen
    if not llmauto_path:
        llmauto_path = os.path.expanduser("~") + "/OneDrive/.AI/.OS/llmauto"
    if not os.path.exists(llmauto_path):
        print(f"FEHLER: llmauto nicht gefunden unter {llmauto_path}")
        print("Nutze --llmauto-path oder --dry-run")
        sys.exit(1)

    categorized = []
    batch_size = 15  # 15 Prompts pro Aufruf (Haiku-freundlich)

    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i + batch_size]
        prompt_list = "\n".join(
            f"[{p.id}] ({p.sender}): {p.text[:500]}"
            for p in batch
        )

        full_prompt = (
            CLASSIFICATION_SYSTEM_PROMPT + "\n\n"
            f"Klassifiziere diese {len(batch)} Prompts:\n\n{prompt_list}\n\n"
            "Antworte als JSON-Array mit einem Objekt pro Prompt."
        )

        try:
            # Prompt in Temp-Datei schreiben (für lange Prompts)
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tf:
                tf.write(full_prompt)
                tf_path = tf.name

            result = subprocess.run(
                [sys.executable, "-m", "llmauto", "pipe", "-f", tf_path, "--model", "claude-haiku-4-5-20251001"],
                capture_output=True, text=True, encoding="utf-8",
                cwd=llmauto_path,
                env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONPATH": llmauto_path},
                timeout=120,
            )
            os.unlink(tf_path)

            result_text = result.stdout.strip()
            if result.returncode != 0:
                raise RuntimeError(f"llmauto error: {result.stderr[:200]}")

            # Parse JSON (mit Toleranz für Markdown-Wrapper)
            if result_text.startswith("```"):
                result_text = re.sub(r"^```\w*\n?", "", result_text)
                result_text = re.sub(r"\n?```$", "", result_text)
            classifications = json.loads(result_text)

            for p, c in zip(batch, classifications):
                categorized.append(CategorizedPrompt(
                    **{k: v for k, v in asdict(p).items() if k in RawPrompt.__dataclass_fields__},
                    topic=c.get("topic", ""),
                    type_code=c.get("type_code", ""),
                    purpose=c.get("purpose", ""),
                    intent=c.get("intent", ""),
                    method_triggered=c.get("method_triggered", ""),
                    consequence=c.get("consequence", ""),
                    is_turning_point=c.get("is_turning_point", False),
                ))
        except Exception as e:
            print(f"  Warnung: Batch {i//batch_size + 1} Klassifikation fehlgeschlagen: {e}")
            for p in batch:
                categorized.append(CategorizedPrompt(
                    **{k: v for k, v in asdict(p).items() if k in RawPrompt.__dataclass_fields__},
                    topic="UNKLASSIFIZIERT",
                    type_code="??",
                ))

        print(f"  Batch {i//batch_size + 1}/{(len(prompts) + batch_size - 1) // batch_size} klassifiziert ({len(batch)} Prompts)")

    return categorized

# ---------------------------------------------------------------------------
# Stufe 3: Aggregation pro Analyse
# ---------------------------------------------------------------------------

def aggregate_by_topic(categorized: list[CategorizedPrompt]) -> dict:
    """Gruppiert Prompts nach Thema und berechnet Kennzahlen pro Gruppe."""
    groups = defaultdict(list)
    for p in categorized:
        groups[p.topic].append(p)

    aggregated = {}
    for topic, prompts in sorted(groups.items(), key=lambda x: -len(x[1])):
        types = Counter(p.type_code for p in prompts)
        aggregated[topic] = {
            "count": len(prompts),
            "types": dict(types),
            "startprompts": [p for p in prompts if p.type_code == "SP"],
            "corrections": [p for p in prompts if p.type_code == "KO"],
            "turning_points": [p for p in prompts if p.is_turning_point],
            "methods": Counter(p.method_triggered for p in prompts if p.method_triggered),
            "human_count": sum(1 for p in prompts if p.sender == "human"),
            "agent_count": sum(1 for p in prompts if p.sender == "assistant"),
        }
    return aggregated

# ---------------------------------------------------------------------------
# Stufe 4: Statistik
# ---------------------------------------------------------------------------

def compute_statistics(categorized: list[CategorizedPrompt], aggregated: dict) -> dict:
    """Berechnet übergreifende Kennzahlen."""
    human_prompts = [p for p in categorized if p.sender == "human"]
    agent_prompts = [p for p in categorized if p.sender == "assistant"]

    type_dist = Counter(p.type_code for p in human_prompts)
    total_h = len(human_prompts) or 1

    confirmations = type_dist.get("BE", 0)
    corrections = type_dist.get("KO", 0)
    bk_ratio = round(confirmations / max(corrections, 1), 2)

    startprompts = type_dist.get("SP", 0)
    proactive = startprompts + type_dist.get("NM", 0) + type_dist.get("RA", 0)
    reactive = confirmations + corrections + type_dist.get("NT", 0)
    pr_ratio = round(proactive / max(reactive, 1), 2)

    turning_points = [p for p in categorized if p.is_turning_point]
    tp_types = Counter(p.type_code for p in turning_points)

    word_counts = [p.word_count for p in human_prompts]
    tp_word_counts = [p.word_count for p in turning_points if p.sender == "human"]

    topics_by_corrections = {
        topic: data["types"].get("KO", 0) / max(data["human_count"], 1)
        for topic, data in aggregated.items()
    }

    return {
        "total_prompts": len(categorized),
        "human_prompts": len(human_prompts),
        "agent_prompts": len(agent_prompts),
        "type_distribution": {
            code: f"{count} ({round(count/total_h*100, 1)}%)"
            for code, count in sorted(type_dist.items(), key=lambda x: -x[1])
        },
        "bk_ratio": bk_ratio,
        "proactive_reactive_ratio": pr_ratio,
        "turning_points_count": len(turning_points),
        "turning_point_types": dict(tp_types),
        "median_word_count": sorted(word_counts)[len(word_counts)//2] if word_counts else 0,
        "median_tp_word_count": sorted(tp_word_counts)[len(tp_word_counts)//2] if tp_word_counts else 0,
        "topics_by_size": {t: d["count"] for t, d in sorted(aggregated.items(), key=lambda x: -x[1]["count"])[:10]},
        "topics_highest_correction_rate": dict(sorted(topics_by_corrections.items(), key=lambda x: -x[1])[:5]),
    }

# ---------------------------------------------------------------------------
# Markdown-Output
# ---------------------------------------------------------------------------

def write_stufe0(prompts: list[RawPrompt], path: Path):
    lines = [
        "# Prompt-Protokoll (Stufe 0: Rohdaten)\n",
        f"> Automatisch generiert am {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        f"> {len(prompts)} Prompts extrahiert\n\n",
        "| # | Sender | Wörter | Prompt (Kurzform) |\n",
        "|---|--------|--------|-------------------|\n",
    ]
    for p in prompts:
        sender = "🧑" if p.sender == "human" else "🤖"
        lines.append(f"| {p.id} | {sender} | {p.word_count} | {p.text_short} |\n")
    path.write_text("".join(lines), encoding="utf-8")

def write_stufe1(prompts: list[RawPrompt], path: Path):
    lines = [
        "# Gefiltertes Prompt-Protokoll (Stufe 1: Themenfilter)\n",
        f"> {len(prompts)} projektrelevante Prompts\n\n",
        "| # | Sender | Wörter | Prompt (Kurzform) |\n",
        "|---|--------|--------|-------------------|\n",
    ]
    for p in prompts:
        sender = "🧑" if p.sender == "human" else "🤖"
        lines.append(f"| {p.id} | {sender} | {p.word_count} | {p.text_short} |\n")
    path.write_text("".join(lines), encoding="utf-8")

def write_stufe2(categorized: list[CategorizedPrompt], path: Path):
    lines = [
        "# Kategorisiertes Prompt-Protokoll (Stufe 2: Klassifikation)\n",
        f"> {len(categorized)} Prompts klassifiziert\n\n",
        "| # | Thema | Typ | Zweck | Absicht | Methode | Folge | WP |\n",
        "|---|-------|-----|-------|---------|---------|-------|----|" + "\n",
    ]
    for p in categorized:
        tp = "⭐" if p.is_turning_point else ""
        lines.append(f"| {p.id} | {p.topic} | {p.type_code} | {p.purpose} | {p.intent} | {p.method_triggered} | {p.consequence} | {tp} |\n")
    path.write_text("".join(lines), encoding="utf-8")

def write_stufe3(aggregated: dict, path: Path):
    lines = [
        "# Aggregiertes Prompt-Protokoll (Stufe 3: Pro Analyse)\n\n",
    ]
    for topic, data in sorted(aggregated.items(), key=lambda x: -x[1]["count"]):
        lines.append(f"## {topic}\n\n")
        lines.append(f"- **Prompts gesamt:** {data['count']} ({data['human_count']} Human, {data['agent_count']} Agent)\n")
        lines.append(f"- **Typen:** {', '.join(f'{k}={v}' for k, v in sorted(data['types'].items(), key=lambda x: -x[1]))}\n")
        if data["startprompts"]:
            lines.append(f"- **Startprompt:** \"{data['startprompts'][0].text_short}\"\n")
        if data["corrections"]:
            lines.append(f"- **Korrekturen:** {len(data['corrections'])}\n")
        if data["turning_points"]:
            lines.append(f"- **Wendepunkte:** {len(data['turning_points'])}\n")
        if data["methods"]:
            lines.append(f"- **Methoden:** {', '.join(f'{k} ({v}×)' for k, v in data['methods'].most_common(5))}\n")
        lines.append("\n")
    path.write_text("".join(lines), encoding="utf-8")

def write_stufe4(stats: dict, path: Path):
    lines = [
        "# Statistische Prompt-Aggregation (Stufe 4: Kennzahlen)\n",
        f"> Automatisch generiert am {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n",
        "## Gesamtzahlen\n\n",
        f"- **Prompts gesamt:** {stats['total_prompts']}\n",
        f"- **Human-Prompts:** {stats['human_prompts']}\n",
        f"- **Agent-Prompts:** {stats['agent_prompts']}\n\n",
        "## Typ-Verteilung (Human)\n\n",
        "| Typ | Anzahl (%) |\n|-----|------------|\n",
    ]
    for code, val in stats["type_distribution"].items():
        name = PROMPT_TYPES.get(code, code)
        lines.append(f"| {code} ({name}) | {val} |\n")
    lines.extend([
        f"\n## Mensch-Maschine-Dynamik\n\n",
        f"- **B:K-Verhältnis:** {stats['bk_ratio']}:1",
        f" {'(kaum Zustimmungs-Bias)' if stats['bk_ratio'] < 2 else '(möglicher Zustimmungs-Bias)'}\n",
        f"- **Proaktiv:Reaktiv:** {stats['proactive_reactive_ratio']}:1",
        f" {'(menschliche Führung)' if stats['proactive_reactive_ratio'] > 1.5 else '(KI-getrieben)'}\n",
        f"- **Wendepunkte:** {stats['turning_points_count']}\n",
        f"- **Wendepunkt-Typen:** {stats['turning_point_types']}\n",
        f"- **Median Wortanzahl (alle):** {stats['median_word_count']}\n",
        f"- **Median Wortanzahl (Wendepunkte):** {stats['median_tp_word_count']}\n\n",
        f"## Top-10 Themen nach Prompt-Anzahl\n\n",
        "| Thema | Prompts |\n|-------|--------|\n",
    ])
    for topic, count in stats["topics_by_size"].items():
        lines.append(f"| {topic} | {count} |\n")
    lines.extend([
        f"\n## Höchste Korrekturrate nach Thema\n\n",
        "| Thema | Korrekturrate |\n|-------|---------------|\n",
    ])
    for topic, rate in stats["topics_highest_correction_rate"].items():
        lines.append(f"| {topic} | {rate:.1%} |\n")
    path.write_text("".join(lines), encoding="utf-8")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Prompt-Analyzer: 5-Stufen-Pipeline für Research-Sessions"
    )
    parser.add_argument("jsonl", help="Pfad zur JSONL Session-Datei")
    parser.add_argument("--topics", help="Kommagetrennte Filter-Keywords (z.B. 'V1,V2,Regress,CORE')")
    parser.add_argument("--project", help="Projekt-Kurzname (setzt vordefinierte Topics)", choices=["regress"])
    parser.add_argument("--output-dir", help="Ausgabeverzeichnis (Default: neben JSONL)")
    parser.add_argument("--dry-run", action="store_true", help="Nur extrahieren, nicht klassifizieren")
    parser.add_argument(
        "--agent-events-output",
        help="AgentEvent-v2-JSONL-Ausgabe (Default: <output-dir>/agent-events-v2.jsonl)",
    )
    parser.add_argument(
        "--agent-events-dry-run",
        action="store_true",
        help="AgentEvents erzeugen und validieren, aber keine AgentEvent-Datei schreiben",
    )
    parser.add_argument("--llmauto-path", help="Pfad zu llmauto (Default: ~/.AI/.OS/llmauto)",
                        default=os.path.expanduser("~") + "/OneDrive/.AI/.OS/llmauto")
    args = parser.parse_args()

    jsonl_path = Path(args.jsonl)
    if not jsonl_path.exists():
        print(f"FEHLER: {jsonl_path} nicht gefunden.")
        sys.exit(1)

    output_dir = Path(args.output_dir) if args.output_dir else jsonl_path.parent / f"prompt-analyse-{jsonl_path.stem[:8]}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Vordefinierte Projekte
    topic_presets = {
        "regress": ["Regress", "V1", "V2", "CORE", "§106", "Ribbat", "Studie", "ST-001", "PP-003",
                     "Wirtschaftlichkeit", "Zertifikat", "Formfehler", "Einzelfall", "Auffälligkeit",
                     "Bayern", "SpiFa", "BMG", "Prüfung"],
    }
    topics = []
    if args.project:
        topics = topic_presets[args.project]
    elif args.topics:
        topics = [t.strip() for t in args.topics.split(",")]

    # Stufe 0: Extraktion
    print(f"📥 Stufe 0: Extrahiere Prompts aus {jsonl_path.name} ({jsonl_path.stat().st_size / 1024 / 1024:.1f} MB)...")
    all_prompts = extract_prompts_from_jsonl(jsonl_path)
    print(f"   → {len(all_prompts)} Prompts extrahiert ({sum(1 for p in all_prompts if p.sender == 'human')} Human, {sum(1 for p in all_prompts if p.is_agent_prompt)} Agent)")
    write_stufe0(all_prompts, output_dir / "prompt-protocol.md")

    agent_events = extract_agent_events_from_jsonl(jsonl_path)
    for event in agent_events:
        validate_agent_event_payload(event.to_dict())
    if args.agent_events_dry_run:
        print(f"   → {len(agent_events)} AgentEvents validiert (kein Export)")
    else:
        agent_events_path = (
            Path(args.agent_events_output)
            if args.agent_events_output
            else output_dir / "agent-events-v2.jsonl"
        )
        write_agent_events_jsonl(agent_events, agent_events_path)
        print(f"   → {len(agent_events)} AgentEvents nach {agent_events_path} exportiert")

    # Stufe 1: Filter
    if topics:
        print(f"🔍 Stufe 1: Filtere nach {len(topics)} Keywords...")
        filtered = filter_by_topics(all_prompts, topics)
        pct = len(filtered)/len(all_prompts)*100 if all_prompts else 0
        print(f"   → {len(filtered)} projektrelevante Prompts ({pct:.0f}%)")
    else:
        filtered = all_prompts
        print(f"ℹ️  Stufe 1: Kein Filter — alle {len(filtered)} Prompts übernommen")
    write_stufe1(filtered, output_dir / "filtered-prompt-protocol.md")

    if args.dry_run:
        print(f"\n✅ Dry-run abgeschlossen. Stufe 0+1 in {output_dir}/")
        return

    # Stufe 2: Klassifikation per llmauto
    print(f"🏷️  Stufe 2: Klassifiziere {len(filtered)} Prompts per llmauto/Haiku...")
    categorized = classify_prompts_batch(filtered, llmauto_path=args.llmauto_path)
    write_stufe2(categorized, output_dir / "categorized-prompt-protocol.md")

    # Stufe 3: Aggregation
    print("📊 Stufe 3: Aggregiere nach Thema...")
    aggregated = aggregate_by_topic(categorized)
    print(f"   → {len(aggregated)} Analyseeinheiten")
    write_stufe3(aggregated, output_dir / "aggregated-prompt-protocol.md")

    # Stufe 4: Statistik
    print("📈 Stufe 4: Berechne Statistiken...")
    stats = compute_statistics(categorized, aggregated)
    write_stufe4(stats, output_dir / "statistical-prompt-aggregation.md")

    print(f"\n✅ Pipeline abgeschlossen. 5 Dateien in {output_dir}/")
    print(f"   Prompts: {stats['total_prompts']} ({stats['human_prompts']} Human, {stats['agent_prompts']} Agent)")
    print(f"   Themen: {len(aggregated)}")
    print(f"   B:K-Verhältnis: {stats['bk_ratio']}:1")
    print(f"   Wendepunkte: {stats['turning_points_count']}")

if __name__ == "__main__":
    main()
