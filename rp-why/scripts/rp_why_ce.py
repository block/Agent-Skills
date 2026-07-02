"""
rp-why Configuration Effectiveness (CE): AGENTS.md adherence measurement.

CE measures alignment between declared agent configuration and observed
collaboration patterns. Provides empirical grounding for the ADT
(Agentic Delegation Trust) dimension.

Phase 1: Implicit command detection and scoring.

Imported by: goose_skill.py, rp_why_baseline.py
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple


CE_VERSION_FILE = "ce_config_versions.json"


class InstructionCategory(Enum):
    IMPLICIT_COMMAND = "implicit_command"
    FORMATTING_RULE = "formatting_rule"
    BOUNDARY = "boundary_declaration"
    WORKFLOW_PATTERN = "workflow_pattern"
    VERIFICATION = "verification_step"
    ROUTING = "routing_rule"


class CEBand(Enum):
    MISCONFIGURED = "Misconfigured"
    UNDER_EFFECTIVE = "Under-effective"
    DEVELOPING = "Developing"
    WELL_TUNED = "Well-tuned"
    OPTIMIZED = "Optimized"


@dataclass
class ImplicitCommand:
    trigger: str
    expected_action: str
    source_file: str
    source_line: int
    token_cost: int = 0

    def __post_init__(self):
        self.token_cost = len(f"{self.trigger} {self.expected_action}") // 4


@dataclass
class CommandExecution:
    trigger_found: bool
    run_id: str
    message_index: int
    expected_signals: List[str]
    detected_signals: List[str]
    score: float
    override_detected: bool = False


@dataclass
class CommandReport:
    command: ImplicitCommand
    executions: List[CommandExecution]
    total_opportunities: int
    success_rate: float
    is_dead: bool


@dataclass
class ConfigVersion:
    file_path: str
    content_hash: str
    first_seen: str
    last_measured: str
    run_count: int
    ce_score: Optional[float]


@dataclass
class CEReport:
    overall_score: float
    band: str
    confidence: str
    command_reports: List[CommandReport]
    dead_commands: List[ImplicitCommand]
    token_waste_pct: float
    total_instructions: int
    measured_instructions: int
    config_version: Optional[str] = None
    nudge: str = ""
    reflection: str = ""
    adt_quadrant: str = ""


IMPLICIT_COMMAND_FINGERPRINTS: dict = {
    "proceed": {
        "positive_signals": [
            r"tool_call_present",
            r"no_question_in_response",
        ],
        "negative_signals": [
            r"would you like",
            r"shall I",
            r"do you want",
            r"should I",
            r"let me know if",
        ],
    },
    "status?": {
        "positive_signals": [
            r"git status",
            r"git log",
            r"branch",
            r"commit",
        ],
        "negative_signals": [],
    },
    "deploy": {
        "positive_signals": [
            r"npm run build",
            r"blockcell",
            r"deploy",
            r"upload",
        ],
        "negative_signals": [],
    },
    "sync": {
        "positive_signals": [
            r"git pull",
            r"git push",
            r"git add",
            r"git commit",
        ],
        "negative_signals": [],
    },
    "merged": {
        "positive_signals": [
            r"what was built",
            r"world model",
            r"accomplishment",
            r"unlocks",
            r"convention",
        ],
        "negative_signals": [],
    },
    "refresh the emulator": {
        "positive_signals": [
            r"force-stop",
            r"adb",
            r"install",
            r"launch",
        ],
        "negative_signals": [],
    },
    "commit and send to emulator": {
        "positive_signals": [
            r"git add",
            r"git commit",
            r"build",
            r"install",
        ],
        "negative_signals": [],
    },
    "start the dev server": {
        "positive_signals": [
            r"npm run dev",
            r"port 3000",
        ],
        "negative_signals": [],
    },
    "check comments": {
        "positive_signals": [
            r"google doc",
            r"comment",
            r"annotation",
            r"edit",
        ],
        "negative_signals": [],
    },
    "check annotations": {
        "positive_signals": [
            r"google doc",
            r"comment",
            r"annotation",
        ],
        "negative_signals": [],
    },
    "monitor ci": {
        "positive_signals": [
            r"status check",
            r"pass",
            r"fail",
            r"pending",
            r"CI",
        ],
        "negative_signals": [],
    },
}

CE_BAND_NUDGES: dict = {
    CEBand.OPTIMIZED.value: [
        "Configuration is well-tuned. Look for new workflows to encode.",
        "High adherence across the board. Consider whether any instructions can compress into higher-level principles.",
        "Your config is earning its token cost. What's the next implicit command that would save you keystrokes?",
    ],
    CEBand.WELL_TUNED.value: [
        "Strong foundation. The instructions below 80% adherence are your growth edge.",
        "Consider: are the underperforming instructions unclear to the LLM, or do they address rare situations?",
        "One targeted edit to your weakest instruction could move CE significantly.",
    ],
    CEBand.DEVELOPING.value: [
        "Some instructions land, others drift. Focus on the top 3 that fire most often and make those airtight.",
        "Try rephrasing instructions that score below 50% - the LLM may need a different framing.",
        "Dead instructions are costing tokens without return. Move situational commands to project-level configs.",
    ],
    CEBand.UNDER_EFFECTIVE.value: [
        "Significant gap between intent and behavior. Start with implicit commands - are the triggers unambiguous?",
        "Consider: is the AGENTS.md too long? Context window pressure can cause the LLM to drop instructions.",
        "Pick the 5 most important instructions and make them bulletproof. Let the rest go for now.",
    ],
    CEBand.MISCONFIGURED.value: [
        "The configuration is not serving the workflow. Consider starting fresh with only the instructions you use daily.",
        "Most instructions are not firing. This often means the config has grown beyond what the LLM can reliably hold.",
        "Focus on boundaries and implicit commands only. Everything else is noise until those two categories work.",
    ],
}

CE_BAND_REFLECTIONS: dict = {
    CEBand.OPTIMIZED.value: "What new workflow could benefit from being encoded in your config?",
    CEBand.WELL_TUNED.value: "Which underperforming instruction matters most to your daily flow?",
    CEBand.DEVELOPING.value: "If you could only keep 5 instructions, which 5 would they be?",
    CEBand.UNDER_EFFECTIVE.value: "Is the config trying to do too much? What can you let go of?",
    CEBand.MISCONFIGURED.value: "What does the agent need to know on day one to serve you well?",
}

ADT_CE_QUADRANT_NUDGES: dict = {
    "Reckless Trust": "Delegating heavily but the agent is not following instructions reliably. Audit which boundaries are holding.",
    "Earned Autonomy": "Trust is justified by data. Configuration is proven. Safe to extend into new delegation patterns.",
    "Justified Caution": "Not delegating much, and the config isn't working anyway. Fix the config before trying to delegate more.",
    "Ready to Trust": "Configuration is proven reliable but delegation hasn't caught up. This is a growth edge - safe to extend autonomy.",
}


def get_ce_band(score: float) -> str:
    if score >= 0.85:
        return CEBand.OPTIMIZED.value
    elif score >= 0.7:
        return CEBand.WELL_TUNED.value
    elif score >= 0.5:
        return CEBand.DEVELOPING.value
    elif score >= 0.3:
        return CEBand.UNDER_EFFECTIVE.value
    else:
        return CEBand.MISCONFIGURED.value


def get_confidence_label(run_count: int) -> str:
    if run_count >= 20:
        return "Very High"
    elif run_count >= 13:
        return "High"
    elif run_count >= 6:
        return "Moderate"
    else:
        return "Low (insufficient data)"


def calculate_adt_ce_quadrant(adt_zone: str, ce_score: float) -> str:
    high_adt_zones = {"Frontier", "Growing"}
    low_adt_zones = {"Expected", "Thinking Ahead", "Underutilizing", "Overpowered"}

    if adt_zone in high_adt_zones and ce_score < 0.5:
        return "Reckless Trust"
    elif adt_zone in high_adt_zones and ce_score >= 0.5:
        return "Earned Autonomy"
    elif adt_zone in low_adt_zones and ce_score < 0.5:
        return "Justified Caution"
    elif adt_zone in low_adt_zones and ce_score >= 0.5:
        return "Ready to Trust"
    return "Earned Autonomy"


def hash_file(path: str) -> Optional[str]:
    try:
        with open(path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]
    except (FileNotFoundError, PermissionError):
        return None


def find_agents_md_files() -> List[str]:
    paths = []
    config_path = os.path.expanduser("~/.config/goose/AGENTS.md")
    if os.path.isfile(config_path):
        paths.append(config_path)

    agents_home = os.path.expanduser("~/.agents/AGENTS.md")
    if os.path.isfile(agents_home):
        paths.append(agents_home)

    cwd = os.getcwd()
    cwd_agents = os.path.join(cwd, "AGENTS.md")
    if os.path.isfile(cwd_agents):
        paths.append(cwd_agents)

    return paths


def parse_implicit_commands(file_path: str) -> List[ImplicitCommand]:
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except (FileNotFoundError, PermissionError):
        return []

    commands = []
    in_implicit_table = False
    table_started = False

    for i, line in enumerate(lines):
        if "implicit command" in line.lower() or "implicit commands" in line.lower():
            in_implicit_table = True
            continue

        if in_implicit_table:
            if line.strip().startswith("|") and "---" in line:
                table_started = True
                continue

            if table_started and line.strip().startswith("|"):
                cells = [c.strip() for c in line.split("|")]
                cells = [c for c in cells if c]
                if len(cells) >= 2:
                    trigger = cells[0].strip('"').strip("'").strip("`").strip()
                    action = cells[1].strip()
                    if trigger and action and trigger.lower() != "phrase":
                        triggers = [t.strip().strip('"').strip("'").lower()
                                    for t in trigger.split("/")]
                        for t in triggers:
                            if t:
                                commands.append(ImplicitCommand(
                                    trigger=t,
                                    expected_action=action,
                                    source_file=file_path,
                                    source_line=i + 1,
                                ))
            elif table_started and not line.strip().startswith("|"):
                in_implicit_table = False
                table_started = False

    return commands


def detect_command_in_run(
    command: ImplicitCommand,
    msg_sequence: List[dict],
    run_id: str = "",
) -> List[CommandExecution]:
    executions = []
    trigger = command.trigger.lower().strip()

    for i, msg in enumerate(msg_sequence):
        if msg.get("role") != "user":
            continue

        text = msg.get("text", "").lower().strip()

        is_match = (text == trigger or text.rstrip("?!.") == trigger.rstrip("?!."))

        if not is_match and trigger == "#n complete":
            is_match = bool(re.match(r'^#\d+ complete$', text))

        if not is_match and trigger in ("done", "sent"):
            is_match = text in ("done", "sent", "done.", "sent.")

        if is_match:
            fingerprints = IMPLICIT_COMMAND_FINGERPRINTS.get(trigger, {})
            positive = fingerprints.get("positive_signals", [])
            negative = fingerprints.get("negative_signals", [])

            response_text = ""
            has_tool_call = False
            for j in range(i + 1, min(i + 6, len(msg_sequence))):
                next_msg = msg_sequence[j]
                if next_msg.get("role") == "assistant":
                    if next_msg.get("type") == "toolRequest":
                        has_tool_call = True
                        tool_info = next_msg.get("tool_name", "") + " " + next_msg.get("tool_args", "")
                        response_text += " " + tool_info.lower()
                    elif next_msg.get("type") == "text":
                        response_text += " " + next_msg.get("text", "").lower()
                    break
                elif next_msg.get("role") == "assistant_continued":
                    if next_msg.get("type") == "toolRequest":
                        has_tool_call = True
                        tool_info = next_msg.get("tool_name", "") + " " + next_msg.get("tool_args", "")
                        response_text += " " + tool_info.lower()
                    elif next_msg.get("type") == "text":
                        response_text += " " + next_msg.get("text", "").lower()

            detected = []
            for signal in positive:
                if signal == "tool_call_present":
                    if has_tool_call:
                        detected.append(signal)
                elif signal == "no_question_in_response":
                    if "?" not in response_text[:200]:
                        detected.append(signal)
                elif re.search(signal, response_text):
                    detected.append(signal)

            override = False
            for neg in negative:
                if re.search(neg, response_text):
                    override = True
                    break

            if positive:
                score = len(detected) / len(positive)
            else:
                score = 1.0 if not override else 0.0

            if override:
                score = max(0.0, score - 0.3)

            executions.append(CommandExecution(
                trigger_found=True,
                run_id=run_id,
                message_index=i,
                expected_signals=positive,
                detected_signals=detected,
                score=score,
                override_detected=override,
            ))

    return executions


def load_runs_from_db(limit: int = 20) -> List[dict]:
    import sqlite3
    db_path = Path.home() / ".local" / "share" / "goose" / "sessions" / "sessions.db"
    if not db_path.exists():
        return []

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id FROM sessions
        ORDER BY created_at DESC LIMIT ?
    ''', (limit,))
    run_ids = [row[0] for row in cursor.fetchall()]

    runs_data = []
    for sid in run_ids:
        cursor.execute('''
            SELECT role, content_json FROM messages
            WHERE run_id = ?
            ORDER BY created_timestamp ASC
        ''', (sid,))

        messages = []
        for role, content_json in cursor.fetchall():
            content = json.loads(content_json) if content_json else []
            for item in content:
                item_type = item.get("type", "")
                if item_type == "text" and item.get("text", "").strip():
                    messages.append({
                        "role": role,
                        "type": "text",
                        "text": item.get("text", ""),
                    })
                elif item_type == "toolRequest":
                    tc = item.get("toolCall", {})
                    messages.append({
                        "role": "assistant",
                        "type": "toolRequest",
                        "tool_name": tc.get("name", ""),
                        "tool_args": json.dumps(tc.get("arguments", {}))[:500],
                    })
                elif item_type == "toolResponse":
                    pass

        runs_data.append({
            "run_id": sid,
            "messages": messages,
        })

    conn.close()
    return runs_data


def compute_ce_report(
    commands: List[ImplicitCommand],
    runs_data: List[dict],
    adt_zone: str = "Expected",
) -> CEReport:
    command_reports = []
    dead_commands = []
    total_token_cost = sum(c.token_cost for c in commands)
    dead_token_cost = 0

    for command in commands:
        all_executions = []

        for run_data in runs_data:
            msg_list = run_data.get("messages", [])
            run_id = run_data.get("run_id", "")

            execs = detect_command_in_run(
                command, msg_list, run_id
            )
            all_executions.extend(execs)

        total_opps = len(all_executions)
        is_dead = total_opps == 0

        if is_dead:
            dead_commands.append(command)
            dead_token_cost += command.token_cost
            success_rate = 0.0
        elif total_opps < 3:
            success_rate = sum(e.score for e in all_executions) / total_opps
        else:
            success_rate = sum(e.score for e in all_executions) / total_opps

        command_reports.append(CommandReport(
            command=command,
            executions=all_executions,
            total_opportunities=total_opps,
            success_rate=success_rate,
            is_dead=is_dead,
        ))

    live_reports = [r for r in command_reports if not r.is_dead and r.total_opportunities >= 3]

    if live_reports:
        overall_score = sum(r.success_rate for r in live_reports) / len(live_reports)
    elif command_reports:
        all_with_data = [r for r in command_reports if not r.is_dead]
        if all_with_data:
            overall_score = sum(r.success_rate for r in all_with_data) / len(all_with_data)
        else:
            overall_score = 0.0
    else:
        overall_score = 0.0

    dead_penalty = 0.3 * (dead_token_cost / total_token_cost) if total_token_cost > 0 else 0.0
    overall_score = max(0.0, overall_score - dead_penalty)

    token_waste_pct = (dead_token_cost / total_token_cost * 100) if total_token_cost > 0 else 0.0

    band = get_ce_band(overall_score)
    confidence = get_confidence_label(len(runs_data))
    quadrant = calculate_adt_ce_quadrant(adt_zone, overall_score)

    import random
    nudge = random.choice(CE_BAND_NUDGES.get(band, ["Run more analysis cycles for better data."]))
    reflection = CE_BAND_REFLECTIONS.get(band, "What could you explore more deeply?")

    return CEReport(
        overall_score=overall_score,
        band=band,
        confidence=confidence,
        command_reports=command_reports,
        dead_commands=dead_commands,
        token_waste_pct=token_waste_pct,
        total_instructions=len(commands),
        measured_instructions=len(live_reports),
        nudge=nudge,
        reflection=reflection,
        adt_quadrant=quadrant,
    )


def format_ce_report(report: CEReport) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append(" CONFIGURATION EFFECTIVENESS (CE) REPORT")
    lines.append(f" Confidence: {report.confidence}")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f" Overall CE Score: {report.overall_score:.2f} ({report.band})")
    lines.append(f" ADT x CE Quadrant: {report.adt_quadrant}")
    lines.append("")

    lines.append(" IMPLICIT COMMANDS")
    lines.append("-" * 60)

    for cr in report.command_reports:
        if cr.is_dead:
            status = "DEAD"
            icon = "\u25cb"
        elif cr.success_rate >= 0.8:
            icon = "\u2713"
            status = f"{cr.total_opportunities}/{cr.total_opportunities}"
        elif cr.success_rate >= 0.5:
            icon = "~"
            successes = int(cr.success_rate * cr.total_opportunities)
            status = f"{successes}/{cr.total_opportunities}"
        else:
            icon = "\u2717"
            successes = int(cr.success_rate * cr.total_opportunities)
            status = f"{successes}/{cr.total_opportunities}"

        trigger_display = f'"{cr.command.trigger}"'
        if cr.is_dead:
            lines.append(f" {icon} {trigger_display:<28} 0 opportunities (dead)")
        else:
            rate_str = f"({cr.success_rate:.2f})"
            lines.append(f" {icon} {trigger_display:<28} {status} fires  {rate_str}")

    if report.dead_commands:
        lines.append("")
        dead_cost = sum(c.token_cost for c in report.dead_commands)
        lines.append(f" DEAD INSTRUCTIONS (Cost: ~{dead_cost} tokens per run)")
        lines.append("-" * 60)
        for dc in report.dead_commands:
            lines.append(f" - \"{dc.trigger}\" (~{dc.token_cost} tokens)")

    lines.append("")
    lines.append(f" Token waste: {report.token_waste_pct:.1f}% of config tokens on untriggered instructions")
    lines.append("")
    lines.append(" GROWTH NUDGE")
    lines.append("-" * 60)
    lines.append(f" {report.nudge}")
    lines.append("")
    lines.append(f" {report.reflection}")
    lines.append("")

    if report.adt_quadrant in ADT_CE_QUADRANT_NUDGES:
        lines.append(" ADT x CE INSIGHT")
        lines.append("-" * 60)
        lines.append(f" {ADT_CE_QUADRANT_NUDGES[report.adt_quadrant]}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def load_config_versions(data_dir: str) -> List[dict]:
    version_file = os.path.join(data_dir, CE_VERSION_FILE)
    if os.path.isfile(version_file):
        with open(version_file, 'r') as f:
            return json.load(f)
    return []


def save_config_version(data_dir: str, version: ConfigVersion):
    versions = load_config_versions(data_dir)
    versions.append(asdict(version))
    version_file = os.path.join(data_dir, CE_VERSION_FILE)
    os.makedirs(data_dir, exist_ok=True)
    with open(version_file, 'w') as f:
        json.dump(versions, f, indent=2)


def check_config_changed(data_dir: str) -> Tuple[bool, Optional[str]]:
    agents_files = find_agents_md_files()
    if not agents_files:
        return False, None

    current_hashes = []
    for fp in agents_files:
        h = hash_file(fp)
        if h:
            current_hashes.append(h)

    combined_hash = hashlib.sha256(
        "|".join(sorted(current_hashes)).encode()
    ).hexdigest()[:16]

    versions = load_config_versions(data_dir)
    if not versions:
        return True, combined_hash

    last_hash = versions[-1].get("content_hash", "")
    if last_hash != combined_hash:
        return True, combined_hash

    return False, combined_hash
