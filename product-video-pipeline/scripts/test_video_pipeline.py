#!/usr/bin/env python3

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from video_pipeline import (
    authorize_project,
    dump_yaml,
    index_ae_library,
    initialize_project,
    load_yaml,
    plan_root,
    render_project,
    validate_project,
)


def receipt(quote: str = "确认") -> dict:
    return {
        "actor": "user",
        "task_id": "test-task",
        "message_id": "test-message",
        "quote": quote,
        "recorded_at": "2026-07-30T12:00:00+08:00",
    }


def confirmed(value, quote: str = "确认") -> dict:
    return {
        "value": value,
        "state": "confirmed",
        "receipt": receipt(quote),
        "rationale": None,
        "updated_at": "2026-07-30T12:00:00+08:00",
    }


def not_applicable(value=None) -> dict:
    return {
        "value": value,
        "state": "not_applicable",
        "receipt": None,
        "rationale": None,
        "updated_at": "2026-07-30T12:00:00+08:00",
    }


class PipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="product-video-pipeline-")
        self.project = Path(self.temporary.name) / "demo-project"
        self.project.mkdir()
        self.assertEqual(initialize_project(self.project, "demo-project"), 0)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def contract(self, name: str) -> tuple[Path, dict]:
        path = plan_root(self.project) / name
        return path, load_yaml(path)

    def write(self, name: str, data: dict) -> None:
        dump_yaml(plan_root(self.project) / name, data)

    def complete_tutorial(self) -> None:
        _, intake = self.contract("intake-state.yaml")
        decisions = intake["decisions"]
        decisions["video_type"] = confirmed("tutorial", "教程视频")
        decisions["primary_goal"] = confirmed("让新用户完成一次真实创建")
        decisions["audience"] = confirmed("首次使用者")
        decisions["hybrid_priority"] = not_applicable()
        decisions["platforms"] = confirmed(["douyin"])
        decisions["canvas"] = confirmed(
            {
                "width": 1080,
                "height": 1920,
                "orientation": "vertical",
                "aspect_ratio": "9:16",
            }
        )
        decisions["duration"] = confirmed(
            {"min_ms": 25000, "target_ms": 30000, "max_ms": 35000}
        )
        decisions["language"] = confirmed("zh-CN")
        decisions["narration"] = confirmed("human_or_tts")
        decisions["captions"] = confirmed("burned_in")
        decisions["deliverables"] = confirmed(["master_mp4"])
        decisions["aigc_policy"] = confirmed(
            {
                "mode": "ask_per_asset",
                "allowed_categories": [],
                "prohibited_categories": ["real_ui", "real_product_result", "logo"],
            }
        )
        intake["stages"] = {
            "P0": "confirmed",
            "P1": "confirmed",
            "P2": "not_applicable",
            "P3": "confirmed",
            "P3_5": "not_applicable",
            "P4": "confirmed",
            "P5": "confirmed",
            "P6": "awaiting_user",
        }
        self.write("intake-state.yaml", intake)

        _, references = self.contract("reference-board.yaml")
        references["whole_film"]["route"] = not_applicable()
        references["effects"]["route"] = not_applicable()
        self.write("reference-board.yaml", references)

        _, script = self.contract("script.yaml")
        script.update(
            {
                "video_type": "tutorial",
                "approval": confirmed("approved", "脚本确认"),
                "total_duration_ms": 30000,
                "claims": [],
                "cta": None,
                "units": [
                    {
                        "unit_id": "SU-01",
                        "time_range_ms": {"in_ms": 0, "out_ms": 30000},
                        "narrative_job": "展示完整真实操作",
                        "visible_copy": "创建完成",
                        "voiceover": "按步骤完成创建。",
                        "claim_ids": [],
                        "proof": "真实 UI 完成状态",
                        "emotion": "清晰",
                        "action": "跟随操作",
                        "asset_implications": ["真实竖屏录屏"],
                        "effect_needs": [],
                    }
                ],
            }
        )
        self.write("script.yaml", script)

        _, ae = self.contract("ae-candidates.yaml")
        ae["mode"] = confirmed("none", "教程不使用 AE")
        self.write("ae-candidates.yaml", ae)

        _, assets = self.contract("asset-request.yaml")
        assets["assets"] = [
            {
                "asset_id": "AS-UI-01",
                "asset_kind": "screen_recording",
                "purpose": "证明真实创建结果",
                "script_unit_ids": ["SU-01"],
                "ae_candidate_ids": [],
                "requiredness": "must_have",
                "recommendation_tier": "USER_STRONGLY_RECOMMENDED",
                "recommended_provider": "user",
                "accepted_provider": "user",
                "provider_acceptance": confirmed("user", "我能提供录屏"),
                "user_can_provide": "yes",
                "user_will_provide": "yes",
                "why_user_provided": "真实 UI 不能生成",
                "provider_override_reason": None,
                "spec": "1080x1920 clean recording",
                "status": "approved",
                "artifact_ref": {
                    "path": "assets/real-ui.mp4",
                    "sha256": None,
                    "media_type": "video/mp4",
                },
                "fallback": "Use a verified fixture recording",
                "factuality_role": "evidence",
                "aigc_policy": {
                    "prohibited": True,
                    "allowed_by_user": False,
                    "consent": not_applicable(False),
                    "allowed_scope": None,
                },
                "rights_privacy": {
                    "rights_status": "approved",
                    "privacy_status": "approved",
                    "notes": "Mask token only",
                },
            }
        ]
        self.write("asset-request.yaml", assets)

    def complete_promo_with_effect(self) -> None:
        self.complete_tutorial()
        _, intake = self.contract("intake-state.yaml")
        intake["decisions"]["video_type"] = confirmed("promo", "宣传片")
        self.write("intake-state.yaml", intake)

        _, references = self.contract("reference-board.yaml")
        references["whole_film"]["route"] = confirmed("none", "不用外部整片参考")
        references["effects"]["route"] = confirmed("user_provided", "我提供特效参考")
        self.write("reference-board.yaml", references)

        _, script = self.contract("script.yaml")
        script["video_type"] = "promo"
        script["creative_direction_id"] = "DIR-ORIGINAL-01"
        script["cta"] = "立即体验"
        script["claims"] = [
            {
                "claim_id": "CL-01",
                "text": "完成创建",
                "proof_type": "real_output",
                "source_truth": "真实产品完成页",
                "status": "verified",
            }
        ]
        script["units"][0]["claim_ids"] = ["CL-01"]
        script["units"][0]["effect_needs"] = [
            {
                "effect_need_id": "EN-01",
                "effect_type": "particle_convergence",
                "criticality": "must_have",
                "reference_requirement": "required",
                "high_cost": True,
                "preferred_tools": ["After Effects"],
            }
        ]
        self.write("script.yaml", script)

        _, ae = self.contract("ae-candidates.yaml")
        ae["mode"] = confirmed("deterministic_rebuild", "用确定性方式重建")
        self.write("ae-candidates.yaml", ae)

    def test_default_project_is_blocked(self) -> None:
        report = validate_project(self.project, "intake")
        self.assertEqual(report["status"], "blocked")
        self.assertGreater(report["blocking_count"], 0)
        self.assertIn("E_CONFIRMATION_MISSING", {issue["code"] for issue in report["issues"]})

    def test_complete_tutorial_authorizes_and_guards(self) -> None:
        self.complete_tutorial()
        report = validate_project(self.project, "preproduction")
        self.assertEqual(report["status"], "pass", report["issues"])
        self.assertEqual(render_project(self.project), 0)
        self.assertTrue((plan_root(self.project) / "asset-request-list.md").exists())
        self.assertEqual(
            authorize_project(
                self.project,
                "user",
                "按以上确认，开始制作",
                "explicit_user",
            ),
            0,
        )
        production = validate_project(self.project, "production")
        self.assertEqual(production["status"], "pass", production["issues"])
        self.assertTrue((plan_root(self.project) / "intake.lock.json").exists())

    def test_whole_film_reference_cannot_replace_effect_reference(self) -> None:
        self.complete_promo_with_effect()
        report = validate_project(self.project, "preproduction")
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("E_EFFECT_REF_REQUIRED", codes)

    def test_library_mode_requires_user_uploaded_indexed_previews(self) -> None:
        self.complete_tutorial()
        _, ae = self.contract("ae-candidates.yaml")
        ae["mode"] = confirmed("library", "从我的素材预览库选择")
        self.write("ae-candidates.yaml", ae)
        report = validate_project(self.project, "preproduction")
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("E_AE_PREVIEW_LIBRARY", codes)
        self.assertIn("E_AE_PREVIEW_PROVIDER", codes)
        self.assertIn("E_AE_PREVIEW_EMPTY", codes)
        self.assertIn("E_AE_PREVIEW_INDEX", codes)

    def test_selected_preview_requires_matching_source_package(self) -> None:
        self.complete_tutorial()
        _, ae = self.contract("ae-candidates.yaml")
        ae["mode"] = confirmed("library", "从我的素材预览库选择")
        ae["preview_library"] = {
            "state": "indexed",
            "provided_by": "user",
            "root_path": "uploads/ae-previews",
            "index_path": "video-plan/ae-library-index.yaml",
            "preview_count": 1,
            "uploaded_at": "2026-07-30T12:00:00+08:00",
            "indexed_at": "2026-07-30T12:01:00+08:00",
            "notes": "User uploaded one preview.",
        }
        ae["candidates"] = [
            {
                "candidate_id": "AE-01",
                "title": "Particle convergence",
                "preview": {
                    "path": "uploads/ae-previews/particle.mp4",
                    "sha256": None,
                    "media_type": "video/mp4",
                },
                "preview_time_range_ms": {"in_ms": 0, "out_ms": 1000},
                "script_unit_ids": ["SU-01"],
                "effect_need_ids": [],
                "effect_reference_ids": [],
                "role": "atmosphere",
                "selection": "selected",
                "replacement_fields": ["copy", "color"],
                "source_package": {
                    "state": "requested",
                    "path": None,
                    "sha256": None,
                },
                "dependencies": {
                    "scan_state": "pending",
                    "ae_version": None,
                    "plugins": [],
                    "fonts": [],
                    "footage": [],
                    "expressions": [],
                    "color_space": None,
                },
                "rights": {
                    "reference_use": "inspiration_only",
                    "commercial_reuse": "approved",
                    "evidence": "Test fixture",
                },
                "fallback": {
                    "method": "deterministic 2D rebuild",
                    "tool": "Remotion",
                    "quality_delta": "less depth",
                    "acceptance": not_applicable(),
                },
            }
        ]
        self.write("ae-candidates.yaml", ae)
        report = validate_project(self.project, "preproduction")
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("E_AE_SOURCE_REQUIRED", codes)
        self.assertNotIn("E_AE_PREVIEW_LIBRARY", codes)

    def test_aigc_cannot_replace_user_evidence(self) -> None:
        self.complete_tutorial()
        _, assets = self.contract("asset-request.yaml")
        item = assets["assets"][0]
        item["accepted_provider"] = "aigc"
        item["provider_acceptance"] = confirmed("aigc", "用 AI 替代")
        item["aigc_policy"] = {
            "prohibited": False,
            "allowed_by_user": True,
            "consent": confirmed(True, "允许 AI"),
            "allowed_scope": "all",
        }
        self.write("asset-request.yaml", assets)
        report = validate_project(self.project, "preproduction")
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("E_USER_SOURCE_PRIORITY", codes)
        self.assertIn("E_AIGC_PROHIBITED", codes)

    def test_changed_canvas_invalidates_authorization(self) -> None:
        self.complete_tutorial()
        self.assertEqual(
            authorize_project(
                self.project,
                "user",
                "按以上确认，开始制作",
                "explicit_user",
            ),
            0,
        )
        _, intake = self.contract("intake-state.yaml")
        intake["decisions"]["canvas"]["value"]["height"] = 2048
        self.write("intake-state.yaml", intake)
        report = validate_project(self.project, "production")
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("E_AUTH_STALE", codes)
        self.assertIn("E_LOCK_STALE", codes)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg required")
    def test_ae_index_records_preview_and_source(self) -> None:
        library = Path(self.temporary.name) / "ae-library"
        library.mkdir()
        preview = library / "particle-convergence-preview.mp4"
        source = library / "particle-convergence.aep"
        source.write_text("test source placeholder", encoding="utf-8")
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "color=c=blue:s=320x240:d=1",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(preview),
            ],
            check=True,
        )
        output = plan_root(self.project) / "ae-library-index.yaml"
        thumbs = plan_root(self.project) / "ae-thumbnails"
        self.assertEqual(index_ae_library(library, output, thumbs), 0)
        index = load_yaml(output)
        self.assertEqual(index["preview_count"], 1)
        self.assertEqual(index["source_project_count"], 1)
        self.assertTrue(index["previews"][0]["source_candidates"])
        self.assertTrue(Path(index["previews"][0]["thumbnail"]).exists())


if __name__ == "__main__":
    unittest.main()
