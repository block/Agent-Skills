#!/usr/bin/env python3
"""Deterministic preproduction contracts for product-video-pipeline."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("PyYAML is required: install pyyaml or run in the Codex workspace runtime.") from exc


VERSION = "1.1.0"
PLAN_DIRNAME = "video-plan"
CONTRACT_FILES = (
    "intake-state.yaml",
    "reference-board.yaml",
    "script.yaml",
    "ae-candidates.yaml",
    "asset-request.yaml",
)
ALL_SOURCE_FILES = CONTRACT_FILES + ("production-authorization.yaml",)
TEMPLATES = {
    "intake-state.template.yaml": "intake-state.yaml",
    "reference-board.template.yaml": "reference-board.yaml",
    "script.template.yaml": "script.yaml",
    "ae-candidates.template.yaml": "ae-candidates.yaml",
    "asset-request.template.yaml": "asset-request.yaml",
    "production-authorization.template.yaml": "production-authorization.yaml",
}
PASSING_DECISION_STATES = {
    "confirmed",
    "defaulted_by_user_delegation",
    "not_applicable",
}
USER_DECISION_STATES = {
    "confirmed",
    "defaulted_by_user_delegation",
}
PROHIBITED_AIGC_ROLES = {
    "evidence",
    "brand_identity",
    "exact_copy",
    "person_or_voice",
}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}
AE_EXTENSIONS = {".aep", ".aet"}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML object")
    return data


def dump_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    with temporary.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, allow_unicode=True, sort_keys=False, width=100)
    temporary.replace(path)


def dump_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    temporary.replace(path)


def canonical_json(data: Any) -> bytes:
    return json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def hash_data(data: Any) -> str:
    return hashlib.sha256(canonical_json(data)).hexdigest()


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def plan_root(project_root: Path) -> Path:
    return project_root.resolve() / PLAN_DIRNAME


def project_slug(project_root: Path) -> str:
    raw = project_root.resolve().name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return slug or f"video-{uuid.uuid4().hex[:8]}"


def load_contracts(project_root: Path) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    plan = plan_root(project_root)
    contracts: dict[str, dict[str, Any]] = {}
    issues: list[dict[str, Any]] = []
    for filename in ALL_SOURCE_FILES:
        path = plan / filename
        if not path.exists():
            add_issue(
                issues,
                "E_CONTRACT_MISSING",
                "core",
                filename,
                True,
                f"Missing canonical contract: {filename}",
                f"Run init or create {path}.",
            )
            continue
        try:
            contracts[filename] = load_yaml(path)
        except Exception as exc:
            add_issue(
                issues,
                "E_CONTRACT_PARSE",
                "core",
                filename,
                True,
                str(exc),
                "Fix YAML syntax and keep the document root as an object.",
            )
    return contracts, issues


def add_issue(
    issues: list[dict[str, Any]],
    code: str,
    stage: str,
    path: str,
    blocking: bool,
    message: str,
    fix: str,
) -> None:
    issues.append(
        {
            "code": code,
            "stage": stage,
            "path": path,
            "blocking": blocking,
            "message": message,
            "fix": fix,
        }
    )


def decision_value(decision: Any) -> Any:
    return decision.get("value") if isinstance(decision, dict) else None


def decision_state(decision: Any) -> str | None:
    return decision.get("state") if isinstance(decision, dict) else None


def receipt_is_user(decision: Any) -> bool:
    if not isinstance(decision, dict):
        return False
    receipt = decision.get("receipt")
    return (
        isinstance(receipt, dict)
        and receipt.get("actor") == "user"
        and bool(str(receipt.get("quote") or "").strip())
    )


def require_decision(
    issues: list[dict[str, Any]],
    decision: Any,
    stage: str,
    path: str,
    *,
    allowed_values: set[Any] | None = None,
    allow_not_applicable: bool = False,
) -> bool:
    state = decision_state(decision)
    value = decision_value(decision)
    passing = state in PASSING_DECISION_STATES
    if state == "not_applicable" and not allow_not_applicable:
        passing = False
    if not passing:
        add_issue(
            issues,
            "E_CONFIRMATION_MISSING",
            stage,
            path,
            True,
            f"Decision is not confirmed (state={state!r}).",
            "Ask the user, preserve the exact reply, and set a confirmed decision state.",
        )
        return False
    if state in USER_DECISION_STATES and not receipt_is_user(decision):
        add_issue(
            issues,
            "E_RECEIPT_MISSING",
            stage,
            path,
            True,
            "Confirmed/defaulted decision has no user receipt.",
            "Record actor=user and the exact confirmation or delegation quote.",
        )
        passing = False
    if allowed_values is not None and value not in allowed_values:
        add_issue(
            issues,
            "E_DECISION_VALUE",
            stage,
            path,
            True,
            f"Unsupported value: {value!r}.",
            f"Use one of: {sorted(str(item) for item in allowed_values)}.",
        )
        passing = False
    return passing


def validate_project(
    project_root: Path,
    stage: str,
    *,
    include_authorization: bool = True,
) -> dict[str, Any]:
    contracts, issues = load_contracts(project_root)
    if any(issue["blocking"] for issue in issues):
        return report_for(project_root, stage, issues)

    intake = contracts["intake-state.yaml"]
    references = contracts["reference-board.yaml"]
    script = contracts["script.yaml"]
    ae = contracts["ae-candidates.yaml"]
    assets = contracts["asset-request.yaml"]
    authorization = contracts["production-authorization.yaml"]

    validate_identity(issues, contracts)
    validate_intake(issues, intake)

    if stage in {"preproduction", "production", "delivery", "all"}:
        validate_references(issues, intake, references, script)
        validate_script(issues, intake, script)
        validate_effect_references(issues, intake, references, script)
        production_checks = stage in {"production", "delivery", "all"}
        validate_ae(issues, ae, references, script, production=production_checks)
        validate_assets(issues, assets, production=production_checks)

    if stage in {"production", "delivery", "all"}:
        if include_authorization:
            validate_authorization(issues, project_root, intake, references, script, ae, assets, authorization)

    if stage in {"delivery", "all"}:
        validate_delivery(issues, project_root)

    return report_for(project_root, stage, issues)


def validate_identity(
    issues: list[dict[str, Any]],
    contracts: dict[str, dict[str, Any]],
) -> None:
    identities = {
        (data.get("project_id"), data.get("preproduction_revision"))
        for data in contracts.values()
    }
    if len(identities) != 1:
        add_issue(
            issues,
            "E_IDENTITY_MISMATCH",
            "core",
            "/",
            True,
            f"Contracts disagree on project_id/revision: {sorted(str(item) for item in identities)}",
            "Align project_id and preproduction_revision across every canonical contract.",
        )
    for filename, data in contracts.items():
        if data.get("schema_version") != "1.0":
            add_issue(
                issues,
                "E_SCHEMA_VERSION",
                "core",
                filename,
                True,
                f"Unsupported schema_version: {data.get('schema_version')!r}",
                "Use schema_version 1.0 or migrate the contract.",
            )


def validate_intake(issues: list[dict[str, Any]], intake: dict[str, Any]) -> None:
    stage = "intake"
    decisions = intake.get("decisions")
    if not isinstance(decisions, dict):
        add_issue(issues, "E_SCHEMA", stage, "intake.decisions", True, "Missing decisions object.", "Restore the intake template.")
        return

    required = (
        "video_type",
        "primary_goal",
        "audience",
        "platforms",
        "canvas",
        "duration",
        "language",
        "narration",
        "captions",
        "deliverables",
        "aigc_policy",
    )
    for key in required:
        require_decision(issues, decisions.get(key), stage, f"intake.decisions.{key}")

    video_type = decision_value(decisions.get("video_type"))
    if video_type not in {"tutorial", "promo", "hybrid"}:
        add_issue(
            issues,
            "E_VIDEO_TYPE",
            stage,
            "intake.decisions.video_type.value",
            True,
            f"Unsupported video type: {video_type!r}.",
            "Choose tutorial, promo, or hybrid.",
        )
    if video_type == "hybrid":
        require_decision(
            issues,
            decisions.get("hybrid_priority"),
            stage,
            "intake.decisions.hybrid_priority",
            allowed_values={"conversion_first", "learning_success_first"},
        )

    platforms = decision_value(decisions.get("platforms"))
    if not isinstance(platforms, list) or not platforms:
        add_issue(
            issues,
            "E_PLATFORM",
            stage,
            "intake.decisions.platforms.value",
            True,
            "At least one platform is required.",
            "Record the primary platform and any derivatives.",
        )

    canvas = decision_value(decisions.get("canvas"))
    if not isinstance(canvas, dict):
        add_issue(issues, "E_CANVAS", stage, "intake.decisions.canvas.value", True, "Canvas must be an object.", "Set width, height, orientation, and aspect_ratio.")
    else:
        width, height = canvas.get("width"), canvas.get("height")
        orientation = canvas.get("orientation")
        if not isinstance(width, int) or width <= 0 or not isinstance(height, int) or height <= 0:
            add_issue(issues, "E_CANVAS", stage, "intake.decisions.canvas.value", True, "Canvas dimensions must be positive integers.", "Confirm target width and height.")
        elif orientation == "vertical" and width >= height:
            add_issue(issues, "E_CANVAS_ORIENTATION", stage, "intake.decisions.canvas.value.orientation", True, "Vertical orientation conflicts with dimensions.", "Use width < height or change orientation.")
        elif orientation == "horizontal" and width <= height:
            add_issue(issues, "E_CANVAS_ORIENTATION", stage, "intake.decisions.canvas.value.orientation", True, "Horizontal orientation conflicts with dimensions.", "Use width > height or change orientation.")
        elif orientation == "square" and width != height:
            add_issue(issues, "E_CANVAS_ORIENTATION", stage, "intake.decisions.canvas.value.orientation", True, "Square orientation conflicts with dimensions.", "Use equal width and height or change orientation.")

    duration = decision_value(decisions.get("duration"))
    if not isinstance(duration, dict):
        add_issue(issues, "E_DURATION", stage, "intake.decisions.duration.value", True, "Duration must be an object.", "Set min_ms, target_ms, and max_ms.")
    else:
        minimum, target, maximum = duration.get("min_ms"), duration.get("target_ms"), duration.get("max_ms")
        if not all(isinstance(item, int) and item > 0 for item in (minimum, target, maximum)):
            add_issue(issues, "E_DURATION", stage, "intake.decisions.duration.value", True, "Duration values must be positive integers.", "Set min_ms <= target_ms <= max_ms.")
        elif not minimum <= target <= maximum:
            add_issue(issues, "E_DURATION_ORDER", stage, "intake.decisions.duration.value", True, "Duration envelope is inconsistent.", "Set min_ms <= target_ms <= max_ms.")


def validate_references(
    issues: list[dict[str, Any]],
    intake: dict[str, Any],
    references: dict[str, Any],
    script: dict[str, Any],
) -> None:
    stage = "P2"
    video_type = decision_value(intake.get("decisions", {}).get("video_type"))
    group = references.get("whole_film")
    if not isinstance(group, dict):
        add_issue(issues, "E_SCHEMA", stage, "references.whole_film", True, "Missing whole_film group.", "Restore the reference template.")
        return
    route_decision = group.get("route")
    if video_type == "tutorial":
        state = decision_state(route_decision)
        value = decision_value(route_decision)
        if state not in PASSING_DECISION_STATES or value not in {None, "none", "not_applicable"}:
            add_issue(
                issues,
                "E_REFERENCE_ROUTE",
                stage,
                "references.whole_film.route",
                False,
                "Tutorial references are optional; current route is unresolved or promotional.",
                "Confirm none/not_applicable unless references materially help the tutorial.",
            )
        return

    route_ok = require_decision(
        issues,
        route_decision,
        stage,
        "references.whole_film.route",
        allowed_values={"user_provided", "agent_search", "none"},
    )
    if not route_ok:
        return
    route = decision_value(route_decision)
    entries = group.get("entries") if isinstance(group.get("entries"), list) else []
    selected_ids = set(group.get("selected_ids") or [])
    selected = [entry for entry in entries if entry.get("reference_id") in selected_ids]

    if route == "agent_search":
        require_decision(
            issues,
            group.get("search_authorization"),
            stage,
            "references.whole_film.search_authorization",
            allowed_values={True},
        )
    if route in {"user_provided", "agent_search"} and not selected:
        add_issue(
            issues,
            "E_REFERENCE_SELECTION",
            stage,
            "references.whole_film.selected_ids",
            True,
            "Reference route requires at least one selected whole-film reference.",
            "Add candidates and let the user select the direction.",
        )
    for entry in selected:
        if entry.get("kind") != "whole_film":
            add_issue(issues, "E_REFERENCE_KIND", stage, f"references.{entry.get('reference_id')}", True, "Selected whole-film reference has the wrong kind.", "Use kind=whole_film and an RF-* ID.")
        if not entry.get("transferable_grammar") or not entry.get("do_not_copy") or not entry.get("novelty_delta"):
            add_issue(
                issues,
                "E_ORIGINALITY",
                stage,
                f"references.{entry.get('reference_id')}",
                True,
                "Selected reference lacks transferable grammar, do-not-copy notes, or novelty delta.",
                "Document all three before script lock.",
            )
    if route == "none" and not script.get("creative_direction_id"):
        add_issue(
            issues,
            "E_ORIGINAL_DIRECTION",
            stage,
            "script.creative_direction_id",
            True,
            "No external reference was selected and no original direction is recorded.",
            "Offer original treatments and record the chosen direction.",
        )


def script_ids(script: dict[str, Any]) -> tuple[set[str], set[str], dict[str, dict[str, Any]]]:
    unit_ids: set[str] = set()
    effect_ids: set[str] = set()
    effect_map: dict[str, dict[str, Any]] = {}
    for unit in script.get("units") or []:
        unit_id = unit.get("unit_id")
        if isinstance(unit_id, str):
            unit_ids.add(unit_id)
        for effect in unit.get("effect_needs") or []:
            effect_id = effect.get("effect_need_id")
            if isinstance(effect_id, str):
                effect_ids.add(effect_id)
                effect_map[effect_id] = effect
    return unit_ids, effect_ids, effect_map


def validate_script(
    issues: list[dict[str, Any]],
    intake: dict[str, Any],
    script: dict[str, Any],
) -> None:
    stage = "P3"
    require_decision(issues, script.get("approval"), stage, "script.approval", allowed_values={"approved"})
    expected_type = decision_value(intake.get("decisions", {}).get("video_type"))
    if script.get("video_type") != expected_type:
        add_issue(issues, "E_SCRIPT_TYPE", stage, "script.video_type", True, "Script video_type differs from intake.", "Align the script with the confirmed type.")
    units = script.get("units")
    if not isinstance(units, list) or not units:
        add_issue(issues, "E_SCRIPT_EMPTY", stage, "script.units", True, "Approved script has no units.", "Create timed script units before approval.")
        return
    total = script.get("total_duration_ms")
    duration = decision_value(intake.get("decisions", {}).get("duration")) or {}
    if not isinstance(total, int) or total <= 0:
        add_issue(issues, "E_SCRIPT_DURATION", stage, "script.total_duration_ms", True, "Script duration is missing.", "Set a positive total_duration_ms.")
    elif isinstance(duration, dict):
        minimum, maximum = duration.get("min_ms"), duration.get("max_ms")
        if isinstance(minimum, int) and isinstance(maximum, int) and not minimum <= total <= maximum:
            add_issue(issues, "E_SCRIPT_DURATION", stage, "script.total_duration_ms", True, "Script duration falls outside the confirmed envelope.", "Revise timing or reconfirm the duration envelope.")

    claims = {claim.get("claim_id"): claim for claim in script.get("claims") or []}
    for claim_id, claim in claims.items():
        if claim.get("status") not in {"verified", "concept_labeled"}:
            add_issue(issues, "E_CLAIM_UNVERIFIED", stage, f"script.claims.{claim_id}", True, "Claim is not verified or concept-labeled.", "Provide evidence, label it as concept, or remove it.")
        if claim.get("status") == "verified" and not claim.get("source_truth"):
            add_issue(issues, "E_CLAIM_SOURCE", stage, f"script.claims.{claim_id}.source_truth", True, "Verified claim has no source truth.", "Record a traceable truth source.")
    seen_units: set[str] = set()
    seen_effects: set[str] = set()
    for unit in units:
        unit_id = unit.get("unit_id")
        if not unit_id or unit_id in seen_units:
            add_issue(
                issues,
                "E_SCRIPT_ID",
                stage,
                "script.units",
                True,
                f"Missing or duplicate script unit ID: {unit_id!r}.",
                "Assign each unit a unique SU-* ID.",
            )
        elif isinstance(unit_id, str):
            seen_units.add(unit_id)
        for effect in unit.get("effect_needs") or []:
            effect_id = effect.get("effect_need_id")
            if not effect_id or effect_id in seen_effects:
                add_issue(
                    issues,
                    "E_EFFECT_ID",
                    stage,
                    f"script.units.{unit_id}.effect_needs",
                    True,
                    f"Missing or duplicate effect-need ID: {effect_id!r}.",
                    "Assign each effect need a unique EN-* ID.",
                )
            elif isinstance(effect_id, str):
                seen_effects.add(effect_id)
        time_range = unit.get("time_range_ms")
        if (
            not isinstance(time_range, dict)
            or not isinstance(time_range.get("in_ms"), int)
            or not isinstance(time_range.get("out_ms"), int)
            or time_range["in_ms"] >= time_range["out_ms"]
        ):
            add_issue(
                issues,
                "E_SCRIPT_TIME",
                stage,
                f"script.units.{unit.get('unit_id')}.time_range_ms",
                True,
                "Script unit needs a valid time range.",
                "Set integer in_ms < out_ms within total_duration_ms.",
            )
        elif isinstance(total, int) and time_range["out_ms"] > total:
            add_issue(
                issues,
                "E_SCRIPT_TIME",
                stage,
                f"script.units.{unit.get('unit_id')}.time_range_ms",
                True,
                "Script unit extends beyond total_duration_ms.",
                "Adjust the unit or total duration.",
            )
        for claim_id in unit.get("claim_ids") or []:
            if claim_id not in claims:
                add_issue(issues, "E_CLAIM_REF", stage, f"script.units.{unit.get('unit_id')}.claim_ids", True, f"Unknown claim ID: {claim_id}", "Add the claim or remove the reference.")


def validate_effect_references(
    issues: list[dict[str, Any]],
    intake: dict[str, Any],
    references: dict[str, Any],
    script: dict[str, Any],
) -> None:
    stage = "P3.5"
    video_type = decision_value(intake.get("decisions", {}).get("video_type"))
    group = references.get("effects")
    if not isinstance(group, dict):
        add_issue(issues, "E_SCHEMA", stage, "references.effects", True, "Missing effects group.", "Restore the reference template.")
        return
    _, effect_ids, effect_map = script_ids(script)
    needs_reference = {
        effect_id
        for effect_id, effect in effect_map.items()
        if effect.get("reference_requirement") == "required"
    }
    high_cost = any(bool(effect.get("high_cost")) for effect in effect_map.values())

    route_decision = group.get("route")
    allowed = {"user_provided", "agent_search", "none", "not_needed"}
    if video_type == "tutorial" and not effect_ids:
        if decision_state(route_decision) == "not_applicable":
            return
    require_decision(issues, route_decision, stage, "references.effects.route", allowed_values=allowed, allow_not_applicable=True)
    route = decision_value(route_decision)

    if route == "agent_search":
        require_decision(
            issues,
            group.get("search_authorization"),
            stage,
            "references.effects.search_authorization",
            allowed_values={True},
        )

    entries = group.get("entries") if isinstance(group.get("entries"), list) else []
    selected_ids = set(group.get("selected_ids") or [])
    selected = [entry for entry in entries if entry.get("reference_id") in selected_ids]
    covered_effects: set[str] = set()
    unit_ids, _, _ = script_ids(script)
    for entry in selected:
        ref_id = entry.get("reference_id")
        if entry.get("kind") != "effect":
            add_issue(issues, "E_EFFECT_REF_KIND", stage, f"references.{ref_id}", True, "Selected effect reference has the wrong kind.", "Use kind=effect and an FX-* ID.")
        time_range = entry.get("source_time_range_ms")
        if not isinstance(time_range, dict) or not isinstance(time_range.get("in_ms"), int) or not isinstance(time_range.get("out_ms"), int) or time_range["in_ms"] >= time_range["out_ms"]:
            add_issue(issues, "E_EFFECT_REF_TIME", stage, f"references.{ref_id}.source_time_range_ms", True, "Effect reference needs an exact valid time range.", "Record in_ms < out_ms.")
        for unit_id in entry.get("script_unit_ids") or []:
            if unit_id not in unit_ids:
                add_issue(issues, "E_EFFECT_REF_TARGET", stage, f"references.{ref_id}.script_unit_ids", True, f"Unknown script unit: {unit_id}", "Point the effect reference to an existing script unit.")
        for effect_id in entry.get("effect_need_ids") or []:
            if effect_id not in effect_ids:
                add_issue(issues, "E_EFFECT_REF_TARGET", stage, f"references.{ref_id}.effect_need_ids", True, f"Unknown effect need: {effect_id}", "Point the effect reference to an existing effect need.")
            else:
                covered_effects.add(effect_id)
        if not entry.get("borrowed_mechanic") or not entry.get("do_not_copy"):
            add_issue(issues, "E_EFFECT_REF_DETAIL", stage, f"references.{ref_id}", True, "Effect reference lacks a concrete mechanic or do-not-copy boundary.", "Describe observable mechanics and exclusions.")

    missing = sorted(needs_reference - covered_effects)
    if missing:
        add_issue(issues, "E_EFFECT_REF_REQUIRED", stage, "references.effects.selected_ids", True, f"Required effect references are missing for: {missing}", "Select FX references or revise the script requirement with user approval.")
    if route in {"user_provided", "agent_search"} and (needs_reference or high_cost) and not selected:
        add_issue(issues, "E_EFFECT_REF_SELECTION", stage, "references.effects.selected_ids", True, "Effect-reference route requires selected entries.", "Add shot-specific candidates and let the user select.")
    if route == "not_needed" and (needs_reference or high_cost):
        add_issue(issues, "E_EFFECT_ROUTE_CONFLICT", stage, "references.effects.route", True, "Effect references are marked not_needed while the script requires or flags high-cost effects.", "Add effect references or revise the effect needs.")


def validate_ae(
    issues: list[dict[str, Any]],
    ae: dict[str, Any],
    references: dict[str, Any],
    script: dict[str, Any],
    *,
    production: bool,
) -> None:
    stage = "production" if production else "P4"
    require_decision(
        issues,
        ae.get("mode"),
        stage,
        "ae.mode",
        allowed_values={"none", "library", "custom_ae", "deterministic_rebuild"},
        allow_not_applicable=True,
    )
    mode = decision_value(ae.get("mode"))
    if mode in {None, "none"}:
        return
    preview_library = ae.get("preview_library") or {}
    if mode in {"library", "custom_ae"}:
        if preview_library.get("state") != "indexed":
            add_issue(
                issues,
                "E_AE_PREVIEW_LIBRARY",
                stage,
                "ae.preview_library.state",
                True,
                "AE selection requires a user-uploaded preview-video library that has been indexed.",
                "Ask the user to upload the material preview videos, run index-ae, then record state=indexed.",
            )
        if preview_library.get("provided_by") != "user":
            add_issue(
                issues,
                "E_AE_PREVIEW_PROVIDER",
                stage,
                "ae.preview_library.provided_by",
                True,
                "The AE preview library was not recorded as user-provided.",
                "Request the user's preview-video files and record provided_by=user.",
            )
        if not isinstance(preview_library.get("preview_count"), int) or preview_library.get("preview_count", 0) < 1:
            add_issue(
                issues,
                "E_AE_PREVIEW_EMPTY",
                stage,
                "ae.preview_library.preview_count",
                True,
                "The uploaded preview library contains no indexed videos.",
                "Upload at least one playable preview video and regenerate the index.",
            )
        if not preview_library.get("index_path"):
            add_issue(
                issues,
                "E_AE_PREVIEW_INDEX",
                stage,
                "ae.preview_library.index_path",
                True,
                "The preview-library index path is missing.",
                "Run index-ae and record the generated YAML index path.",
            )
    candidates = ae.get("candidates") if isinstance(ae.get("candidates"), list) else []
    selected = [candidate for candidate in candidates if candidate.get("selection") == "selected"]
    if mode in {"library", "custom_ae"} and not selected:
        add_issue(issues, "E_AE_SELECTION", stage, "ae.candidates", True, "AE mode requires at least one selected candidate.", "Present candidates and record the user's selection.")
        return

    selected_fx = set(references.get("effects", {}).get("selected_ids") or [])
    _, effect_ids, effect_map = script_ids(script)
    covered_effects: set[str] = set()
    for candidate in selected:
        candidate_id = candidate.get("candidate_id")
        preview = candidate.get("preview") or {}
        if not preview.get("path"):
            add_issue(
                issues,
                "E_AE_CANDIDATE_PREVIEW",
                stage,
                f"ae.{candidate_id}.preview",
                True,
                "Selected AE candidate has no user-uploaded preview video.",
                "Link the selected candidate to an indexed preview file.",
            )
        for ref_id in candidate.get("effect_reference_ids") or []:
            if ref_id not in selected_fx:
                add_issue(issues, "E_AE_EFFECT_REF", stage, f"ae.{candidate_id}.effect_reference_ids", True, f"AE candidate points to an unselected effect reference: {ref_id}", "Select the FX reference or remove the link.")
        for effect_id in candidate.get("effect_need_ids") or []:
            if effect_id not in effect_ids:
                add_issue(issues, "E_AE_EFFECT_NEED", stage, f"ae.{candidate_id}.effect_need_ids", True, f"Unknown effect need: {effect_id}", "Point the candidate to an existing effect need.")
            else:
                covered_effects.add(effect_id)

        source = candidate.get("source_package") or {}
        fallback = candidate.get("fallback") or {}
        fallback_acceptance = fallback.get("acceptance")
        fallback_accepted = (
            decision_state(fallback_acceptance) in USER_DECISION_STATES
            and receipt_is_user(fallback_acceptance)
            and decision_value(fallback_acceptance) in {True, "accepted", "approved"}
        )
        if source.get("state") != "present" and not fallback_accepted:
            add_issue(
                issues,
                "E_AE_SOURCE_REQUIRED",
                stage,
                f"ae.{candidate_id}.source_package",
                True,
                "Selected candidate has no present source package and no accepted fallback.",
                "After the user selects the preview, request its matching collected AE project; otherwise obtain explicit fallback acceptance.",
            )
        if candidate.get("rights", {}).get("commercial_reuse") != "approved":
            add_issue(issues, "E_AE_RIGHTS", stage, f"ae.{candidate_id}.rights", True, "Selected AE candidate lacks approved commercial reuse rights.", "Verify the template/project license.")
        scan_state = candidate.get("dependencies", {}).get("scan_state")
        if production and source.get("state") == "present" and scan_state != "passed":
            add_issue(issues, "E_AE_DEPENDENCY", stage, f"ae.{candidate_id}.dependencies", True, "AE source dependencies have not passed inspection.", "Check AE version, plugins, fonts, Footage, expressions, and color space.")

    must_have_effects = {
        effect_id
        for effect_id, effect in effect_map.items()
        if effect.get("criticality") == "must_have" and effect.get("high_cost")
    }
    if mode in {"library", "custom_ae"}:
        missing = sorted(must_have_effects - covered_effects)
        if missing:
            add_issue(issues, "E_AE_COVERAGE", stage, "ae.candidates", True, f"Must-have high-cost effect needs are uncovered: {missing}", "Assign a selected candidate or choose deterministic_rebuild.")


def validate_assets(
    issues: list[dict[str, Any]],
    assets: dict[str, Any],
    *,
    production: bool,
) -> None:
    stage = "production" if production else "P5"
    items = assets.get("assets")
    if not isinstance(items, list) or not items:
        add_issue(issues, "E_ASSET_LIST_EMPTY", stage, "assets.assets", True, "Every video requires an asset request, but the list is empty.", "Derive assets from script units, claims, selected AE candidates, brand needs, audio, and delivery.")
        return
    seen: set[str] = set()
    for item in items:
        asset_id = item.get("asset_id")
        if not asset_id or asset_id in seen:
            add_issue(issues, "E_ASSET_ID", stage, "assets.assets", True, f"Missing or duplicate asset ID: {asset_id!r}", "Assign a unique AS-* ID.")
            continue
        seen.add(asset_id)
        provider = item.get("accepted_provider")
        if item.get("requiredness") == "must_have":
            if provider == "pending":
                add_issue(issues, "E_ASSET_PROVIDER", stage, f"assets.{asset_id}.accepted_provider", True, "Must-have asset has no accepted provider.", "Confirm responsibility in a user-facing batch.")
            require_decision(issues, item.get("provider_acceptance"), stage, f"assets.{asset_id}.provider_acceptance")
        if item.get("user_can_provide") == "yes" and item.get("user_will_provide") == "yes":
            if provider not in {"user", "project_existing"} and not item.get("provider_override_reason"):
                add_issue(issues, "E_USER_SOURCE_PRIORITY", stage, f"assets.{asset_id}.accepted_provider", True, "User can and will provide this asset, but another source was assigned.", "Prefer the user/project asset or record explicit substitution approval.")

        factuality = item.get("factuality_role")
        if provider == "aigc":
            policy = item.get("aigc_policy") or {}
            if factuality in PROHIBITED_AIGC_ROLES or policy.get("prohibited") is True:
                add_issue(issues, "E_AIGC_PROHIBITED", stage, f"assets.{asset_id}", True, f"AIGC cannot fulfill factuality role {factuality!r}.", "Use verified user/project evidence or deterministic exact composition.")
            if policy.get("allowed_by_user") is not True or not receipt_is_user(policy.get("consent")):
                add_issue(issues, "E_AIGC_CONSENT", stage, f"assets.{asset_id}.aigc_policy", True, "AIGC provider lacks explicit scoped user consent.", "Record the allowed scope and exact consent quote.")

        if production and item.get("requiredness") == "must_have":
            if item.get("status") not in {"available", "approved"}:
                add_issue(issues, "E_ASSET_NOT_READY", stage, f"assets.{asset_id}.status", True, "Must-have asset is not ready.", "Obtain, validate, or replace it before production.")
            rights = item.get("rights_privacy") or {}
            if rights.get("rights_status") not in {"approved", "not_applicable"}:
                add_issue(issues, "E_ASSET_RIGHTS", stage, f"assets.{asset_id}.rights_privacy.rights_status", True, "Must-have asset rights are unresolved.", "Verify rights or replace the asset.")
            if rights.get("privacy_status") not in {"approved", "not_applicable"}:
                add_issue(issues, "E_ASSET_PRIVACY", stage, f"assets.{asset_id}.rights_privacy.privacy_status", True, "Must-have asset privacy review is unresolved.", "Mask only sensitive data and approve the remaining evidence.")


def bundle_data(
    intake: dict[str, Any],
    references: dict[str, Any],
    script: dict[str, Any],
    ae: dict[str, Any],
    assets: dict[str, Any],
) -> dict[str, Any]:
    return {
        "intake-state.yaml": intake,
        "reference-board.yaml": references,
        "script.yaml": script,
        "ae-candidates.yaml": ae,
        "asset-request.yaml": assets,
    }


def validate_authorization(
    issues: list[dict[str, Any]],
    project_root: Path,
    intake: dict[str, Any],
    references: dict[str, Any],
    script: dict[str, Any],
    ae: dict[str, Any],
    assets: dict[str, Any],
    authorization: dict[str, Any],
) -> None:
    stage = "P6"
    if authorization.get("status") != "approved":
        add_issue(issues, "E_AUTHORIZATION_MISSING", stage, "authorization.status", True, "Production authorization is not approved.", "Show the current confirmation card and obtain explicit user approval.")
        return
    receipt = authorization.get("receipt")
    if not isinstance(receipt, dict) or receipt.get("actor") != "user" or not str(receipt.get("quote") or "").strip():
        add_issue(issues, "E_AUTH_RECEIPT", stage, "authorization.receipt", True, "Approved authorization has no exact user receipt.", "Record the user's exact production approval.")

    current_bundle = hash_data(bundle_data(intake, references, script, ae, assets))
    if authorization.get("bundle_sha256") != current_bundle:
        add_issue(issues, "E_AUTH_STALE", stage, "authorization.bundle_sha256", True, "Authorization no longer matches current preproduction contracts.", "Re-render the confirmation card and obtain renewed approval.")

    card = authorization.get("confirmation_card") or {}
    card_path = card.get("path")
    if not card_path:
        add_issue(issues, "E_CONFIRMATION_CARD", stage, "authorization.confirmation_card", True, "Authorization has no confirmation-card record.", "Render and present the card before approval.")
    else:
        path = plan_root(project_root) / Path(card_path).name
        if not path.exists() or card.get("sha256") != hash_file(path):
            add_issue(issues, "E_CONFIRMATION_CARD", stage, "authorization.confirmation_card.sha256", True, "Confirmation card is missing or changed.", "Render and present the current card, then renew approval.")
    if authorization.get("unresolved_blockers"):
        add_issue(issues, "E_BLOCKERS_PRESENT", stage, "authorization.unresolved_blockers", True, "Authorization contains unresolved blockers.", "Resolve blockers; accepted risks cannot override them.")

    lock_path = plan_root(project_root) / "intake.lock.json"
    if not lock_path.exists():
        add_issue(issues, "E_LOCK_MISSING", stage, "intake.lock.json", True, "Preproduction lock is missing.", "Regenerate the lock after current approval.")
    else:
        try:
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            if lock.get("bundle_sha256") != current_bundle:
                add_issue(issues, "E_LOCK_STALE", stage, "intake.lock.json", True, "Preproduction lock is stale.", "Renew authorization and regenerate the lock.")
            auth_hash = hash_data(authorization)
            if lock.get("authorization_hash") != auth_hash:
                add_issue(issues, "E_LOCK_STALE", stage, "intake.lock.json.authorization_hash", True, "Lock does not match the authorization record.", "Regenerate the lock.")
        except Exception as exc:
            add_issue(issues, "E_LOCK_PARSE", stage, "intake.lock.json", True, str(exc), "Regenerate the lock.")


def validate_delivery(issues: list[dict[str, Any]], project_root: Path) -> None:
    plan = plan_root(project_root)
    qa_path = plan / "qa-report.json"
    manifest_path = plan / "delivery-manifest.json"
    if not qa_path.exists():
        add_issue(issues, "E_QA_MISSING", "delivery", "qa-report.json", True, "Delivery QA report is missing.", "Run profile-driven automated and manual QA.")
    else:
        try:
            qa = json.loads(qa_path.read_text(encoding="utf-8"))
            if qa.get("status") != "pass":
                add_issue(issues, "E_QA_FAILED", "delivery", "qa-report.json", True, f"QA status is {qa.get('status')!r}.", "Resolve hard failures and obtain acceptance.")
        except Exception as exc:
            add_issue(issues, "E_QA_PARSE", "delivery", "qa-report.json", True, str(exc), "Write a valid JSON QA report.")
    if not manifest_path.exists():
        add_issue(issues, "E_DELIVERY_MANIFEST", "delivery", "delivery-manifest.json", True, "Delivery manifest is missing.", "Record final files, hashes, sources, and reproduction commands.")


def report_for(project_root: Path, stage: str, issues: list[dict[str, Any]]) -> dict[str, Any]:
    blockers = [issue for issue in issues if issue["blocking"]]
    warnings = [issue for issue in issues if not issue["blocking"]]
    return {
        "tool_version": VERSION,
        "project_root": str(project_root.resolve()),
        "stage": stage,
        "status": "blocked" if blockers else "pass",
        "blocking_count": len(blockers),
        "warning_count": len(warnings),
        "issues": issues,
        "validated_at": now_iso(),
    }


def initialize_project(project_root: Path, project_id: str | None) -> int:
    root = project_root.resolve()
    plan = plan_root(root)
    plan.mkdir(parents=True, exist_ok=True)
    identifier = project_id or project_slug(root)
    assets = skill_root() / "assets"
    created: list[str] = []
    skipped: list[str] = []
    for template_name, output_name in TEMPLATES.items():
        source = assets / template_name
        target = plan / output_name
        if target.exists():
            skipped.append(output_name)
            continue
        data = load_yaml(source)
        data["project_id"] = identifier
        if output_name == "intake-state.yaml":
            data["updated_at"] = now_iso()
        dump_yaml(target, data)
        created.append(output_name)
    print(f"Initialized {plan}")
    if created:
        print("Created: " + ", ".join(created))
    if skipped:
        print("Preserved existing: " + ", ".join(skipped))
    return 0


def md_cell(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, list):
        return "<br>".join(str(item).replace("|", "\\|") for item in value) or "—"
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def render_reference_board(plan: Path, references: dict[str, Any]) -> None:
    lines = ["# Reference board", ""]
    for key, title in (("whole_film", "Whole-film references"), ("effects", "Effect references")):
        group = references.get(key) or {}
        lines.extend(
            [
                f"## {title}",
                "",
                f"- Route: `{decision_value(group.get('route'))}`",
                f"- Route state: `{decision_state(group.get('route'))}`",
                f"- Selected: {', '.join(group.get('selected_ids') or []) or '—'}",
                "",
                "| ID | Source | Time | Target | Borrow / transfer | Do not copy | Novelty / fallback | Rights | Selection |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for entry in group.get("entries") or []:
            source = entry.get("source") or {}
            time_range = entry.get("source_time_range_ms")
            time_text = "—" if not time_range else f"{time_range.get('in_ms')}–{time_range.get('out_ms')} ms"
            target = list(entry.get("script_unit_ids") or []) + list(entry.get("effect_need_ids") or [])
            borrow = entry.get("borrowed_mechanic") or entry.get("transferable_grammar") or []
            novelty = entry.get("fallback") or entry.get("novelty_delta") or []
            rights = entry.get("rights") or {}
            lines.append(
                "| "
                + " | ".join(
                    md_cell(value)
                    for value in (
                        entry.get("reference_id"),
                        source.get("value"),
                        time_text,
                        target,
                        borrow,
                        entry.get("do_not_copy"),
                        novelty,
                        rights.get("reference_use"),
                        entry.get("selection"),
                    )
                )
                + " |"
            )
        lines.append("")
    (plan / "reference-board.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_script(plan: Path, script: dict[str, Any]) -> None:
    lines = [
        "# Script",
        "",
        f"- Type: `{script.get('video_type')}`",
        f"- Version: `{script.get('version')}`",
        f"- Approval: `{decision_state(script.get('approval'))}` / `{decision_value(script.get('approval'))}`",
        f"- Duration: `{script.get('total_duration_ms')}` ms",
        f"- CTA: {script.get('cta') or '—'}",
        "",
        "| Unit | Time | Narrative job | Visible copy | Voiceover | Proof | Assets | Effects |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for unit in script.get("units") or []:
        time_range = unit.get("time_range_ms") or {}
        effects = [
            f"{effect.get('effect_need_id')}:{effect.get('effect_type')}"
            for effect in unit.get("effect_needs") or []
        ]
        lines.append(
            "| "
            + " | ".join(
                md_cell(value)
                for value in (
                    unit.get("unit_id"),
                    f"{time_range.get('in_ms')}–{time_range.get('out_ms')} ms",
                    unit.get("narrative_job"),
                    unit.get("visible_copy"),
                    unit.get("voiceover"),
                    unit.get("proof"),
                    unit.get("asset_implications"),
                    effects,
                )
            )
            + " |"
        )
    (plan / "script.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_ae_board(plan: Path, ae: dict[str, Any]) -> None:
    preview_library = ae.get("preview_library") or {}
    lines = [
        "# AE candidate board",
        "",
        f"- Mode: `{decision_value(ae.get('mode'))}`",
        f"- Mode state: `{decision_state(ae.get('mode'))}`",
        f"- User preview library: `{preview_library.get('state')}`",
        f"- Preview provider: `{preview_library.get('provided_by')}`",
        f"- Indexed previews: `{preview_library.get('preview_count')}`",
        f"- Preview index: `{preview_library.get('index_path')}`",
        "",
        "| Candidate | Preview | Script / effect use | Selection | Source | Dependencies | Rights | Fallback |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for candidate in ae.get("candidates") or []:
        dependencies = candidate.get("dependencies") or {}
        dependency_text = [
            f"scan={dependencies.get('scan_state')}",
            f"AE={dependencies.get('ae_version')}",
            f"plugins={','.join(dependencies.get('plugins') or []) or 'none'}",
            f"fonts={','.join(dependencies.get('fonts') or []) or 'none'}",
        ]
        fallback = candidate.get("fallback") or {}
        lines.append(
            "| "
            + " | ".join(
                md_cell(value)
                for value in (
                    f"{candidate.get('candidate_id')} {candidate.get('title') or ''}".strip(),
                    (candidate.get("preview") or {}).get("path"),
                    list(candidate.get("script_unit_ids") or [])
                    + list(candidate.get("effect_need_ids") or [])
                    + list(candidate.get("effect_reference_ids") or []),
                    candidate.get("selection"),
                    (candidate.get("source_package") or {}).get("state"),
                    dependency_text,
                    (candidate.get("rights") or {}).get("commercial_reuse"),
                    [
                        fallback.get("method"),
                        fallback.get("quality_delta"),
                        decision_state(fallback.get("acceptance")),
                    ],
                )
            )
            + " |"
        )
    (plan / "ae-candidate-board.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_asset_list(plan: Path, assets: dict[str, Any]) -> None:
    groups = [
        "USER_STRONGLY_RECOMMENDED",
        "USER_PREFERRED",
        "AGENT_SOURCE_AFTER_APPROVAL",
        "AGENT_CREATE_DETERMINISTIC",
        "AIGC_FALLBACK_WITH_CONSENT",
    ]
    lines = ["# Asset request list", ""]
    all_items = assets.get("assets") or []
    for group in groups:
        items = [item for item in all_items if item.get("recommendation_tier") == group]
        lines.extend(
            [
                f"## {group}",
                "",
                "| ID | Required | Purpose | Spec | User can / will | Accepted provider | Status | Fallback |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for item in items:
            lines.append(
                "| "
                + " | ".join(
                    md_cell(value)
                    for value in (
                        item.get("asset_id"),
                        item.get("requiredness"),
                        item.get("purpose"),
                        item.get("spec"),
                        f"{item.get('user_can_provide')} / {item.get('user_will_provide')}",
                        item.get("accepted_provider"),
                        item.get("status"),
                        item.get("fallback"),
                    )
                )
                + " |"
            )
        if not items:
            lines.append("| — | — | — | — | — | — | — | — |")
        lines.append("")
    lines.extend(
        [
            "## User response",
            "",
            "Please mark each relevant group or item as: 我能提供 / 我无法提供 / 需要 Agent 协助 / 暂不确定。",
            "",
        ]
    )
    (plan / "asset-request-list.md").write_text("\n".join(lines), encoding="utf-8")


def summary_value(decisions: dict[str, Any], key: str) -> Any:
    decision = decisions.get(key)
    return decision_value(decision)


def render_confirmation(
    project_root: Path,
    intake: dict[str, Any],
    references: dict[str, Any],
    script: dict[str, Any],
    ae: dict[str, Any],
    assets: dict[str, Any],
) -> Path:
    plan = plan_root(project_root)
    report = validate_project(project_root, "preproduction", include_authorization=False)
    decisions = intake.get("decisions") or {}
    items = assets.get("assets") or []
    user_items = [
        item
        for item in items
        if item.get("recommendation_tier") in {"USER_STRONGLY_RECOMMENDED", "USER_PREFERRED"}
    ]
    ready_user_items = [item for item in user_items if item.get("status") in {"available", "approved"}]
    selected_ae = [
        candidate.get("candidate_id")
        for candidate in ae.get("candidates") or []
        if candidate.get("selection") == "selected"
    ]
    blockers = [issue for issue in report["issues"] if issue["blocking"]]
    lines = [
        "# Production confirmation",
        "",
        f"- 视频类型：{summary_value(decisions, 'video_type') or '—'}",
        f"- 唯一目标：{summary_value(decisions, 'primary_goal') or '—'}",
        f"- 受众：{summary_value(decisions, 'audience') or '—'}",
        f"- 平台：{summary_value(decisions, 'platforms') or '—'}",
        f"- 画幅：{summary_value(decisions, 'canvas') or '—'}",
        f"- 时长：{summary_value(decisions, 'duration') or '—'}",
        f"- 整片参考：{references.get('whole_film', {}).get('selected_ids') or decision_value(references.get('whole_film', {}).get('route')) or '—'}",
        f"- 脚本：{script.get('script_id')} v{script.get('version')} / {decision_value(script.get('approval'))}",
        f"- 特效参考：{references.get('effects', {}).get('selected_ids') or decision_value(references.get('effects', {}).get('route')) or '—'}",
        f"- AE / 动效：{decision_value(ae.get('mode')) or '—'}；候选 {selected_ae or '—'}",
        f"- 用户优先素材：{len(user_items)} 项；已到位 {len(ready_user_items)} 项",
        f"- AIGC：{summary_value(decisions, 'aigc_policy') or '—'}",
        "",
        "## Blocking items",
        "",
    ]
    if blockers:
        lines.extend(
            f"- `{issue['code']}` {issue['path']}: {issue['message']}"
            for issue in blockers
        )
    else:
        lines.append("- 无")
    lines.extend(
        [
            "",
            "## Authorization request",
            "",
            "请确认以上范围、选择、素材责任和 AIGC 边界。若同意，请明确回复“按以上确认，开始制作”或等价的清晰授权。",
            "",
        ]
    )
    output = plan / "production-confirmation.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def render_project(project_root: Path) -> int:
    contracts, issues = load_contracts(project_root)
    if any(issue["blocking"] for issue in issues):
        for issue in issues:
            print(f"{issue['code']}: {issue['message']}", file=sys.stderr)
        return 1
    plan = plan_root(project_root)
    render_reference_board(plan, contracts["reference-board.yaml"])
    render_script(plan, contracts["script.yaml"])
    render_ae_board(plan, contracts["ae-candidates.yaml"])
    render_asset_list(plan, contracts["asset-request.yaml"])
    render_confirmation(
        project_root,
        contracts["intake-state.yaml"],
        contracts["reference-board.yaml"],
        contracts["script.yaml"],
        contracts["ae-candidates.yaml"],
        contracts["asset-request.yaml"],
    )
    print(f"Rendered user-facing boards in {plan}")
    return 0


def write_lock(project_root: Path, contracts: dict[str, dict[str, Any]]) -> Path:
    plan = plan_root(project_root)
    source_bundle = {
        filename: contracts[filename]
        for filename in CONTRACT_FILES
    }
    authorization = contracts["production-authorization.yaml"]
    input_hashes = {
        filename: hash_data(data)
        for filename, data in source_bundle.items()
    }
    intake = contracts["intake-state.yaml"]
    references = contracts["reference-board.yaml"]
    script = contracts["script.yaml"]
    ae = contracts["ae-candidates.yaml"]
    assets = contracts["asset-request.yaml"]
    lock = {
        "schema_version": "1.0",
        "project_id": intake.get("project_id"),
        "preproduction_revision": intake.get("preproduction_revision"),
        "created_at": now_iso(),
        "tool_version": VERSION,
        "input_hashes": input_hashes,
        "bundle_sha256": hash_data(source_bundle),
        "authorization_hash": hash_data(authorization),
        "resolved_snapshot": {
            "video_type": decision_value(intake.get("decisions", {}).get("video_type")),
            "primary_goal": decision_value(intake.get("decisions", {}).get("primary_goal")),
            "platforms": decision_value(intake.get("decisions", {}).get("platforms")),
            "canvas": decision_value(intake.get("decisions", {}).get("canvas")),
            "whole_film_reference_ids": references.get("whole_film", {}).get("selected_ids") or [],
            "effect_reference_ids": references.get("effects", {}).get("selected_ids") or [],
            "script_id": script.get("script_id"),
            "script_version": script.get("version"),
            "ae_mode": decision_value(ae.get("mode")),
            "ae_candidate_ids": [
                candidate.get("candidate_id")
                for candidate in ae.get("candidates") or []
                if candidate.get("selection") == "selected"
            ],
            "asset_providers": {
                item.get("asset_id"): item.get("accepted_provider")
                for item in assets.get("assets") or []
            },
            "aigc_policy": decision_value(intake.get("decisions", {}).get("aigc_policy")),
        },
    }
    path = plan / "intake.lock.json"
    dump_json(path, lock)
    return path


def authorize_project(
    project_root: Path,
    approved_by: str,
    confirmation: str,
    basis: str,
) -> int:
    if approved_by != "user":
        print("Authorization must be approved by the user.", file=sys.stderr)
        return 2
    if not confirmation.strip():
        print("Exact user confirmation text is required.", file=sys.stderr)
        return 2
    preflight = validate_project(project_root, "preproduction", include_authorization=False)
    if preflight["blocking_count"]:
        print(json.dumps(preflight, ensure_ascii=False, indent=2))
        return 1

    render_project(project_root)
    contracts, issues = load_contracts(project_root)
    if any(issue["blocking"] for issue in issues):
        return 1
    plan = plan_root(project_root)
    card_path = plan / "production-confirmation.md"
    intake = contracts["intake-state.yaml"]
    references = contracts["reference-board.yaml"]
    script = contracts["script.yaml"]
    ae = contracts["ae-candidates.yaml"]
    assets = contracts["asset-request.yaml"]
    authorization = contracts["production-authorization.yaml"]

    source_bundle = bundle_data(intake, references, script, ae, assets)
    authorization.update(
        {
            "authorization_id": f"AUTH-{uuid.uuid4().hex[:12]}",
            "status": "approved",
            "basis": basis,
            "bundle_sha256": hash_data(source_bundle),
            "confirmation_card": {
                "path": card_path.name,
                "sha256": hash_file(card_path),
                "presented_at": now_iso(),
            },
            "receipt": {
                "actor": "user",
                "task_id": None,
                "message_id": None,
                "quote": confirmation.strip(),
                "recorded_at": now_iso(),
            },
            "unresolved_blockers": [],
            "aigc_boundary_snapshot": decision_value(intake.get("decisions", {}).get("aigc_policy")) or {},
            "authorized_at": now_iso(),
            "revocation": {"revoked_at": None, "reason": None},
        }
    )
    auth_path = plan / "production-authorization.yaml"
    dump_yaml(auth_path, authorization)
    contracts["production-authorization.yaml"] = authorization
    lock_path = write_lock(project_root, contracts)
    print(f"Recorded scoped user authorization: {auth_path}")
    print(f"Created preproduction lock: {lock_path}")
    return 0


def revoke_project(project_root: Path, reason: str) -> int:
    path = plan_root(project_root) / "production-authorization.yaml"
    if not path.exists():
        print(f"Missing {path}", file=sys.stderr)
        return 1
    authorization = load_yaml(path)
    authorization["status"] = "revoked"
    authorization["revocation"] = {
        "revoked_at": now_iso(),
        "reason": reason,
    }
    dump_yaml(path, authorization)
    print(f"Revoked authorization: {reason}")
    return 0


def normalize_stem(path: Path) -> str:
    stem = path.stem.lower()
    return re.sub(r"[^a-z0-9]+", " ", stem).strip()


def probe_video(path: Path) -> dict[str, Any]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate",
        "-of",
        "json",
        str(path),
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        payload = json.loads(result.stdout)
        duration = payload.get("format", {}).get("duration")
        video_stream = next(
            (stream for stream in payload.get("streams", []) if stream.get("codec_type") == "video"),
            {},
        )
        return {
            "duration_seconds": float(duration) if duration is not None else None,
            "width": video_stream.get("width"),
            "height": video_stream.get("height"),
            "frame_rate": video_stream.get("r_frame_rate"),
            "codec": video_stream.get("codec_name"),
            "probe_error": None,
        }
    except Exception as exc:
        return {
            "duration_seconds": None,
            "width": None,
            "height": None,
            "frame_rate": None,
            "codec": None,
            "probe_error": str(exc),
        }


def extract_thumbnail(video: Path, output: Path, duration: float | None) -> str | None:
    output.parent.mkdir(parents=True, exist_ok=True)
    seek = max((duration or 1.0) * 0.25, 0.1)
    command = [
        "ffmpeg",
        "-v",
        "error",
        "-y",
        "-ss",
        f"{seek:.3f}",
        "-i",
        str(video),
        "-frames:v",
        "1",
        "-vf",
        "scale=640:-2",
        str(output),
    ]
    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        return str(output)
    except Exception:
        return None


def source_matches(preview: Path, sources: list[Path]) -> list[dict[str, Any]]:
    preview_stem = normalize_stem(preview)
    scored: list[tuple[float, Path]] = []
    for source in sources:
        score = difflib.SequenceMatcher(None, preview_stem, normalize_stem(source)).ratio()
        if score >= 0.35:
            scored.append((score, source))
    return [
        {"path": str(path), "name_similarity": round(score, 3)}
        for score, path in sorted(scored, key=lambda item: item[0], reverse=True)[:5]
    ]


def index_ae_library(library_root: Path, output: Path, thumbnails: Path | None) -> int:
    root = library_root.resolve()
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2
    files = [path for path in root.rglob("*") if path.is_file()]
    previews = sorted(path for path in files if path.suffix.lower() in VIDEO_EXTENSIONS)
    sources = sorted(path for path in files if path.suffix.lower() in AE_EXTENSIONS)
    entries: list[dict[str, Any]] = []
    for index, preview in enumerate(previews, start=1):
        probe = probe_video(preview)
        thumb_path = None
        if thumbnails is not None:
            safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", preview.stem)
            thumb_path = extract_thumbnail(
                preview,
                thumbnails.resolve() / f"{index:04d}-{safe_name}.jpg",
                probe.get("duration_seconds"),
            )
        entries.append(
            {
                "preview_id": f"PV-{index:04d}",
                "path": str(preview),
                "relative_path": str(preview.relative_to(root)),
                "sha256": hash_file(preview),
                "thumbnail": thumb_path,
                **probe,
                "source_candidates": source_matches(preview, sources),
                "decision": "unreviewed",
            }
        )
    data = {
        "schema_version": "1.0",
        "tool_version": VERSION,
        "library_root": str(root),
        "indexed_at": now_iso(),
        "preview_count": len(previews),
        "source_project_count": len(sources),
        "source_projects": [
            {
                "path": str(path),
                "relative_path": str(path.relative_to(root)),
                "sha256": hash_file(path),
            }
            for path in sources
        ],
        "previews": entries,
    }
    dump_yaml(output.resolve(), data)

    markdown = [
        "# AE library index",
        "",
        f"- Root: `{root}`",
        f"- Preview videos: {len(previews)}",
        f"- AE source projects: {len(sources)}",
        "",
        "| ID | Thumbnail | Preview | Duration | Size | Source candidates | Review |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in entries:
        source_text = [
            f"{Path(match['path']).name} ({match['name_similarity']})"
            for match in entry["source_candidates"]
        ]
        markdown.append(
            "| "
            + " | ".join(
                md_cell(value)
                for value in (
                    entry["preview_id"],
                    entry["thumbnail"],
                    entry["relative_path"],
                    entry["duration_seconds"],
                    f"{entry['width']}×{entry['height']}",
                    source_text,
                    entry["decision"],
                )
            )
            + " |"
        )
    output.with_suffix(".md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    print(f"Indexed {len(previews)} previews and {len(sources)} AE source projects.")
    print(f"Wrote {output.resolve()} and {output.with_suffix('.md').resolve()}")
    return 0


def print_report(report: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return
    print(f"{report['status'].upper()}: {report['blocking_count']} blockers, {report['warning_count']} warnings")
    for issue in report["issues"]:
        level = "BLOCK" if issue["blocking"] else "WARN"
        print(f"[{level}] {issue['code']} {issue['path']}: {issue['message']}")
        print(f"       Fix: {issue['fix']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize canonical video-plan contracts")
    init_parser.add_argument("project_root", type=Path)
    init_parser.add_argument("--project-id")

    render_parser = subparsers.add_parser("render", help="Render user-facing Markdown boards")
    render_parser.add_argument("project_root", type=Path)

    validate_parser = subparsers.add_parser("validate", help="Validate contracts and cross-file invariants")
    validate_parser.add_argument("project_root", type=Path)
    validate_parser.add_argument(
        "--stage",
        choices=["intake", "preproduction", "production", "delivery", "all"],
        default="preproduction",
    )
    validate_parser.add_argument("--json", action="store_true")
    validate_parser.add_argument("--output", type=Path)

    authorize_parser = subparsers.add_parser("authorize", help="Record explicit scoped user authorization and lock inputs")
    authorize_parser.add_argument("project_root", type=Path)
    authorize_parser.add_argument("--approved-by", required=True, choices=["user"])
    authorize_parser.add_argument("--confirmation", required=True)
    authorize_parser.add_argument(
        "--basis",
        choices=["explicit_user", "delegated_defaults", "scoped_revision"],
        default="explicit_user",
    )

    revoke_parser = subparsers.add_parser("revoke", help="Revoke production authorization")
    revoke_parser.add_argument("project_root", type=Path)
    revoke_parser.add_argument("--reason", required=True)

    guard_parser = subparsers.add_parser("guard-production", help="Fail if production authorization or lock is missing/stale")
    guard_parser.add_argument("project_root", type=Path)
    guard_parser.add_argument("--json", action="store_true")

    index_parser = subparsers.add_parser(
        "index-ae",
        help="Index user-uploaded AE preview videos and any matching source projects",
    )
    index_parser.add_argument("library_root", type=Path)
    index_parser.add_argument("--output", type=Path, required=True)
    index_parser.add_argument("--thumbnails", type=Path)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "init":
        return initialize_project(args.project_root, args.project_id)
    if args.command == "render":
        return render_project(args.project_root)
    if args.command == "validate":
        report = validate_project(args.project_root, args.stage)
        if args.output:
            dump_json(args.output.resolve(), report)
        print_report(report, args.json)
        return 1 if report["blocking_count"] else 0
    if args.command == "authorize":
        return authorize_project(args.project_root, args.approved_by, args.confirmation, args.basis)
    if args.command == "revoke":
        return revoke_project(args.project_root, args.reason)
    if args.command == "guard-production":
        report = validate_project(args.project_root, "production")
        print_report(report, args.json)
        return 1 if report["blocking_count"] else 0
    if args.command == "index-ae":
        return index_ae_library(args.library_root, args.output, args.thumbnails)
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
