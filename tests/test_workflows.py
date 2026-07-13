from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import json
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script_module(relative: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {relative}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_script(relative: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / relative), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class WorkflowTests(unittest.TestCase):
    def test_skill_validation_passes(self) -> None:
        result = run_script("scripts/validate_skills.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_initialize_validate_and_create_chapter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "novel"
            result = run_script(
                "skills/novel-project/scripts/init_novel_project.py",
                "--output", str(project),
                "--title", "测试之书",
                "--genre", "玄幻",
                "--premise", "一个小人物改变世界",
                "--author", "测试作者",
                "--profile", "longform",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((project / "00-书核" / "作品总表.md").exists())
            self.assertTrue((project / "20-大纲" / "分卷" / "volume-01.md").exists())
            self.assertTrue((project / "10-设定" / "地点" / "地点模板.md").exists())
            self.assertTrue((project / "10-设定" / "势力" / "势力模板.md").exists())
            self.assertIn("测试之书", (project / "00-书核" / "作品总表.md").read_text(encoding="utf-8"))

            validation = run_script("scripts/validate_novel_project.py", str(project))
            self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)

            chapter = run_script(
                "scripts/create_chapter.py", str(project), "--chapter", "4", "--name", "新章",
            )
            self.assertEqual(chapter.returncode, 0, chapter.stdout + chapter.stderr)
            self.assertTrue((project / "30-正文" / "第一卷-初入江湖" / "第004章-新章.md").exists())
            self.assertTrue((project / "20-大纲" / "节拍卡" / "chapter-004.md").exists())
            self.assertIn(
                "第004章-新章",
                (project / "90-运行" / "当前进度.md").read_text(encoding="utf-8"),
            )
            cockpit = (project / "90-运行" / "连载驾驶舱.md").read_text(encoding="utf-8")
            self.assertEqual(cockpit.count("| Ch 4 |"), 1)

    def test_install_requires_force_and_uninstall_works(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = run_script("scripts/install.py", "--target-dir", tmp)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertTrue((Path(tmp) / "novel-skills" / "skills" / "novel-studio" / "SKILL.md").exists())

            conflict = run_script("scripts/install.py", "--target-dir", tmp)
            self.assertNotEqual(conflict.returncode, 0)

            forced = run_script("scripts/install.py", "--target-dir", tmp, "--force")
            self.assertEqual(forced.returncode, 0, forced.stdout + forced.stderr)

            uninstall = run_script("scripts/uninstall.py", "--target-dir", tmp)
            self.assertEqual(uninstall.returncode, 0, uninstall.stdout + uninstall.stderr)
            self.assertFalse((Path(tmp) / "novel-skills").exists())

    def test_project_profiles_use_progressive_scaffolding(self) -> None:
        counts = {}
        with tempfile.TemporaryDirectory() as tmp:
            for profile in ("minimal", "serial", "longform"):
                project = Path(tmp) / profile
                result = run_script(
                    "skills/novel-project/scripts/init_novel_project.py",
                    "--output", str(project), "--title", profile,
                    "--genre", "测试", "--premise", "测试前提",
                    "--profile", profile,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                counts[profile] = len(list(project.rglob("*.*")))
            self.assertLess(counts["minimal"], counts["serial"])
            self.assertLess(counts["serial"], counts["longform"])

            validation = run_script("scripts/validate_novel_project.py", str(Path(tmp) / "minimal"))
            self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)
            self.assertNotIn("可选文件缺失", validation.stdout)
            self.assertNotIn("缺少连载驾驶舱", validation.stdout)
            self.assertFalse((Path(tmp) / "minimal" / "90-运行" / "连载驾驶舱.md").exists())

            minimal_chapter = run_script(
                "scripts/create_chapter.py", str(Path(tmp) / "minimal"),
                "--chapter", "1", "--name", "试写",
            )
            self.assertEqual(minimal_chapter.returncode, 0, minimal_chapter.stdout + minimal_chapter.stderr)
            self.assertTrue((Path(tmp) / "minimal" / "30-正文" / "章节" / "第001章-试写.md").exists())
            support = Path(tmp) / "minimal" / "20-大纲" / "节拍卡" / "chapter-001.md"
            self.assertIn("写作模式", support.read_text(encoding="utf-8"))

    def test_create_chapter_builds_missing_beat_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "novel"
            (project / "30-正文" / "第一卷-测试").mkdir(parents=True)
            result = run_script("scripts/create_chapter.py", str(project), "--chapter", "1")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((project / "30-正文" / "第一卷-测试" / "第001章.md").exists())
            self.assertTrue((project / "20-大纲" / "节拍卡" / "chapter-001.md").exists())

    def test_long_project_recommends_foretext_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "novel"
            volume = project / "30-正文" / "第一卷-测试"
            volume.mkdir(parents=True)
            for chapter in range(1, 102):
                (volume / f"第{chapter:03d}章.md").write_text("# 测试\n", encoding="utf-8")
            result = run_script("scripts/validate_novel_project.py", str(project), "--check-consistency")
            self.assertIn("建议补建 `90-运行/前文索引.md`", result.stdout)

    def test_export_uses_numeric_chapter_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "novel"
            volume = project / "30-正文" / "第一卷-测试"
            volume.mkdir(parents=True)
            (volume / "第010章.md").write_text("# 第010章\n\n第十章内容。\n", encoding="utf-8")
            (volume / "第002章.md").write_text("# 第002章\n\n第二章内容。\n", encoding="utf-8")
            output = Path(tmp) / "export.md"
            result = run_script("scripts/export_novel.py", str(project), "--output", str(output))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            exported = output.read_text(encoding="utf-8")
            self.assertLess(exported.index("第002章"), exported.index("第010章"))

    def test_chapter_risk_regression_cases(self) -> None:
        scanner = load_script_module("scripts/evaluate_chapter.py", "evaluate_chapter")
        fixture = ROOT / "skills/novel-quality/assets/evals/chapter-risk-cases.json"
        cases = json.loads(fixture.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases), 10)
        for case in cases:
            with self.subTest(case=case["id"]):
                report = scanner.scan_text(case["text"], case["profile"])
                codes = {risk["code"] for risk in report["risks"]}
                self.assertTrue(set(case["expect_present"]).issubset(codes), codes)
                self.assertTrue(set(case["expect_absent"]).isdisjoint(codes), codes)

    def test_chapter_scanner_has_no_composite_grade(self) -> None:
        scanner = load_script_module("scripts/evaluate_chapter.py", "evaluate_chapter_no_grade")
        report = scanner.scan_text("门开了。雨落进来。")
        self.assertNotIn("score", report)
        self.assertNotIn("grade", report)
        self.assertIn("disclaimer", report)

    def test_build_context_pack_uses_previous_chapter_tail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "novel"
            init = run_script(
                "skills/novel-project/scripts/init_novel_project.py",
                "--output", str(project),
                "--title", "上下文测试",
                "--genre", "悬疑",
                "--premise", "一把失踪的钥匙",
            )
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            previous = project / "30-正文" / "第一卷-初入江湖" / "第003章.md"
            previous.write_text("# 第003章\n\n前文开头。\n\n钥匙落进井里。\n", encoding="utf-8")
            character = project / "10-设定" / "角色" / "沈砚.md"
            character.write_text("# 沈砚\n\n他从不轻易许诺。\n", encoding="utf-8")
            beat = project / "20-大纲" / "节拍卡" / "chapter-004.md"
            beat.write_text("# chapter-004\n\n沈砚来到井边寻找钥匙。\n", encoding="utf-8")
            output = project / "90-运行" / "context.md"
            result = run_script(
                "scripts/build_context_pack.py", str(project),
                "--chapter", "4", "--output", str(output),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            text = output.read_text(encoding="utf-8")
            self.assertIn("钥匙落进井里", text)
            self.assertIn("作品总表", text)
            self.assertIn("他从不轻易许诺", text)
            self.assertIn("写前最后确认", text)
            self.assertLess(text.index("本章节拍卡"), text.index("作品总表"))

    def test_writing_eval_manifest_and_blind_packets(self) -> None:
        manifest = ROOT / "skills/novel-writing/assets/evals/writing-cases.json"
        cases = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual({case["mode"] for case in cases}, {
            "商业连载", "类型长篇", "文学叙事", "短篇", "探索起草",
        })
        with tempfile.TemporaryDirectory() as tmp:
            result = run_script("scripts/prepare_writing_evals.py", "--output", tmp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for case in cases:
                prompt = (Path(tmp) / "prompts" / f"{case['id']}.md").read_text(encoding="utf-8")
                scorecard = (Path(tmp) / "scorecards" / f"{case['id']}.md").read_text(encoding="utf-8")
                self.assertNotIn("失败信号", prompt)
                self.assertNotIn(case["failure_signals"][0], prompt)
                self.assertIn(case["failure_signals"][0], scorecard)


if __name__ == "__main__":
    unittest.main()
