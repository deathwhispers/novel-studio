from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import json
import importlib.util
import os
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
            chapter_text = (project / "30-正文" / "第一卷-初入江湖" / "第004章-新章.md").read_text(encoding="utf-8")
            beat_text = (project / "20-大纲" / "节拍卡" / "chapter-004.md").read_text(encoding="utf-8")
            self.assertIn("当前状态：未起草", chapter_text)
            self.assertIn("## 正文", chapter_text)
            self.assertIn("写作模式：商业连载", chapter_text)
            self.assertIn("写作模式：商业连载", beat_text)
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
            minimal_config = (Path(tmp) / "minimal" / "90-运行" / "项目配置.md").read_text(encoding="utf-8")
            self.assertIn("模板档位：minimal", minimal_config)
            self.assertIn("写作模式：探索起草", minimal_config)
            self.assertIn("连载工具：停用", minimal_config)
            self.assertTrue((Path(tmp) / "serial" / "20-大纲" / "升级阶梯.md").exists())

            serial_cockpit = Path(tmp) / "serial" / "90-运行" / "连载驾驶舱.md"
            serial_cockpit.unlink()
            serial_validation = run_script("scripts/validate_novel_project.py", str(Path(tmp) / "serial"))
            self.assertNotEqual(serial_validation.returncode, 0)
            self.assertIn("连载工具已启用", serial_validation.stdout)

            minimal_chapter = run_script(
                "scripts/create_chapter.py", str(Path(tmp) / "minimal"),
                "--chapter", "1", "--name", "试写",
            )
            self.assertEqual(minimal_chapter.returncode, 0, minimal_chapter.stdout + minimal_chapter.stderr)
            self.assertTrue((Path(tmp) / "minimal" / "30-正文" / "章节" / "第001章-试写.md").exists())
            support = Path(tmp) / "minimal" / "20-大纲" / "节拍卡" / "chapter-001.md"
            self.assertIn("写作模式", support.read_text(encoding="utf-8"))

    def test_mode_controls_serial_tools_independently_from_profile(self) -> None:
        serial_assets = (
            "20-大纲/前3章逐章技法.md", "20-大纲/前30章留存期管理.md",
            "20-大纲/升级阶梯.md", "20-大纲/首卷发射台.md",
            "20-大纲/首章杀手锏集合.md", "90-运行/连载驾驶舱.md",
            "90-运行/连载工作流.md",
        )
        with tempfile.TemporaryDirectory() as tmp:
            literary = Path(tmp) / "literary"
            result = run_script(
                "skills/novel-project/scripts/init_novel_project.py",
                "--output", str(literary), "--title", "文学长篇", "--genre", "文学",
                "--premise", "一家人的记忆", "--profile", "longform", "--mode", "文学叙事",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for relative in serial_assets:
                self.assertFalse((literary / relative).exists(), relative)
            config = (literary / "90-运行" / "项目配置.md").read_text(encoding="utf-8")
            self.assertIn("连载工具：停用", config)
            validation = run_script("scripts/validate_novel_project.py", str(literary))
            self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)
            self.assertNotIn("缺少核心文件：90-运行/连载驾驶舱.md", validation.stdout)

            enabled = Path(tmp) / "enabled"
            result = run_script(
                "skills/novel-project/scripts/init_novel_project.py",
                "--output", str(enabled), "--title", "实验连载", "--genre", "文学",
                "--premise", "分章发布", "--profile", "minimal", "--mode", "文学叙事",
                "--enable-serial-tools",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for relative in serial_assets:
                self.assertTrue((enabled / relative).exists(), relative)
            self.assertIn("连载工具：启用", (enabled / "90-运行" / "项目配置.md").read_text(encoding="utf-8"))

    def test_validator_rejects_present_but_invalid_project_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "novel"
            result = run_script(
                "skills/novel-project/scripts/init_novel_project.py",
                "--output", str(project), "--title", "坏配置", "--genre", "测试",
                "--premise", "测试", "--profile", "minimal",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            (project / "90-运行" / "项目配置.md").write_text(
                "# 项目配置\n\n- 模板档位：deep\n- 写作模式：随便写\n- 配置版本：99\n- 连载工具：也许\n",
                encoding="utf-8",
            )
            validation = run_script("scripts/validate_novel_project.py", str(project))
            self.assertNotEqual(validation.returncode, 0)
            self.assertIn("项目配置的模板档位非法", validation.stdout)
            self.assertIn("项目配置的写作模式非法", validation.stdout)
            self.assertIn("项目配置版本不支持", validation.stdout)
            self.assertIn("项目配置的连载工具值非法", validation.stdout)

    def test_create_chapter_builds_missing_beat_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "novel"
            (project / "30-正文" / "第一卷-测试").mkdir(parents=True)
            result = run_script("scripts/create_chapter.py", str(project), "--chapter", "1")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((project / "30-正文" / "第一卷-测试" / "第001章.md").exists())
            self.assertTrue((project / "20-大纲" / "节拍卡" / "chapter-001.md").exists())
            chapter = (project / "30-正文" / "第一卷-测试" / "第001章.md").read_text(encoding="utf-8")
            beat = (project / "20-大纲" / "节拍卡" / "chapter-001.md").read_text(encoding="utf-8")
            self.assertIn("## 正文", chapter)
            self.assertNotIn("写作模式：商业连载", chapter)
            self.assertIn("- 写作模式：\n", beat)

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
        malformed = scanner.scan_text("---\ntitle: 未闭合\n正文仍然必须被扫描。")
        self.assertGreater(malformed["metrics"]["chinese_chars"], 0)

    def test_chapter_scanner_evidence_uses_original_file_lines(self) -> None:
        scanner = load_script_module("scripts/evaluate_chapter.py", "evaluate_original_lines")
        text = (
            "---\n"
            "title: 元数据不应计入正文\n"
            "author: 测试\n"
            "---\n"
            "# 章节标题不应计入正文\n"
            "\n"
            "他意识到门已经锁上。\n"
            "她明白今夜无法离开。\n"
            "这意味着他们必须等待。\n"
            "也就是说，他们别无选择。\n"
        )
        report = scanner.scan_text(text)
        risk = next(item for item in report["risks"] if item["code"] == "explain_density")
        self.assertEqual(risk["evidence"][0]["line"], 7)
        self.assertNotIn("元数据不应计入正文", scanner.body_text(text))
        self.assertNotIn("章节标题不应计入正文", scanner.body_text(text))

    def test_chapter_scanner_rejects_invalid_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text('{"max_modifier_ratio": "很多"}', encoding="utf-8")
            project = Path(tmp) / "novel"
            chapter_dir = project / "30-正文"
            chapter_dir.mkdir(parents=True)
            (chapter_dir / "第001章.md").write_text("门开了。雨落进来。", encoding="utf-8")
            result = run_script(
                "scripts/evaluate_chapter.py", str(project),
                "--chapter", "第001章", "--config", str(bad),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("必须是数字或 null", result.stderr)

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
            previous.write_text(
                "# 第003章\n\n## 正文\n\n前文开头。\n\n钥匙落进井里。\n\n"
                "## 写后短记\n\n这段短记不能冒充正文结尾。\n",
                encoding="utf-8",
            )
            character = project / "10-设定" / "角色" / "沈砚.md"
            character.write_text("# 沈砚\n\n他从不轻易许诺。\n", encoding="utf-8")
            beat = project / "20-大纲" / "节拍卡" / "chapter-004.md"
            beat.write_text("# chapter-004\n\n沈砚来到井边寻找钥匙。\n", encoding="utf-8")
            delta = project / "90-运行" / "章节增量" / "chapter-003.md"
            delta.write_text("# chapter-003 状态增量\n\n- 关系变化：沈砚开始怀疑债主。\n", encoding="utf-8")
            output = project / "90-运行" / "context.md"
            result = run_script(
                "scripts/build_context_pack.py", str(project),
                "--chapter", "4", "--max-chars", "5000", "--output", str(output),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            text = output.read_text(encoding="utf-8")
            self.assertIn("钥匙落进井里", text)
            self.assertIn("作品总表", text)
            self.assertIn("他从不轻易许诺", text)
            self.assertIn("沈砚开始怀疑债主", text)
            self.assertNotIn("这段短记不能冒充正文结尾", text)
            self.assertIn("写前最后确认", text)
            self.assertLess(text.index("作品总表"), text.index("本章节拍卡"))
            self.assertLessEqual(len(text), 5000)

    def test_context_pack_skips_placeholder_chapters_and_uses_task_entities(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "novel"
            init = run_script(
                "skills/novel-project/scripts/init_novel_project.py",
                "--output", str(project), "--title", "占位测试",
                "--genre", "文学", "--premise", "旧屋相见", "--profile", "minimal",
            )
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            chapter_dir = project / "30-正文" / "章节"
            (chapter_dir / "第001章.md").write_text("# 第一章\n\n## 正文\n\n父亲把旧表放回抽屉。\n", encoding="utf-8")
            (chapter_dir / "第002章.md").write_text("# 第二章\n\n当前状态：未起草\n\n## 正文\n", encoding="utf-8")
            role = project / "10-设定" / "角色" / "周禾.md"
            role.write_text("# 周禾\n\n她总先收起坏掉的东西。\n", encoding="utf-8")
            output = project / "90-运行" / "context.md"
            result = run_script(
                "scripts/build_context_pack.py", str(project), "--chapter", "3",
                "--task", "周禾回到旧屋", "--output", str(output),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            text = output.read_text(encoding="utf-8")
            self.assertIn("父亲把旧表放回抽屉", text)
            self.assertIn("她总先收起坏掉的东西", text)
            self.assertNotIn("当前状态：未起草", text)

            generic = project / "90-运行" / "generic-context.md"
            generic_result = run_script(
                "scripts/build_context_pack.py", str(project), "--chapter", "3",
                "--task", "主角回到旧屋", "--output", str(generic),
            )
            self.assertEqual(generic_result.returncode, 0, generic_result.stdout + generic_result.stderr)
            self.assertNotIn("角色卡：主角", generic.read_text(encoding="utf-8"))

    def test_context_pack_preserves_core_sources_and_hard_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "novel"
            init = run_script(
                "skills/novel-project/scripts/init_novel_project.py",
                "--output", str(project), "--title", "预算测试",
                "--genre", "类型", "--premise", "一轮红月", "--profile", "minimal",
            )
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            (project / "90-运行" / "项目配置.md").write_text(
                "# 项目配置\n\n- 模板档位：minimal\n- 写作模式：文学叙事\n", encoding="utf-8"
            )
            (project / "00-书核" / "作品总表.md").write_text(
                "# 作品总表\n\n作品承诺：追问记忆是否可靠。\n", encoding="utf-8"
            )
            (project / "10-设定" / "硬设定.md").write_text(
                "# 硬设定\n\n月亮始终是红色。\n", encoding="utf-8"
            )
            (project / "90-运行" / "当前进度.md").write_text(
                "# 当前进度\n\n- 当前章节：第002章\n", encoding="utf-8"
            )
            (project / "20-大纲" / "节拍卡" / "chapter-002.md").write_text(
                "# 长节拍\n\n" + "局部计划。" * 1000, encoding="utf-8"
            )
            context_builder = load_script_module("scripts/build_context_pack.py", "context_hard_limit")
            for budget in (800, 1000, 1500, 18000):
                with self.subTest(budget=budget):
                    pack = context_builder.build_context_pack(project, 2, max_chars=budget)
                    self.assertLessEqual(len(pack), budget)
                    self.assertIn("文学叙事", pack)
                    self.assertIn("追问记忆是否可靠", pack)
                    self.assertIn("月亮始终是红色", pack)
                    self.assertIn("当前章节：第002章", pack)

    def test_writing_eval_manifest_and_blind_packets(self) -> None:
        manifest = ROOT / "skills/novel-writing/assets/evals/writing-cases.json"
        cases = json.loads(manifest.read_text(encoding="utf-8"))
        modes = {
            "商业连载", "类型长篇", "文学叙事", "短篇", "探索起草",
        }
        self.assertGreaterEqual(len(cases), 25)
        self.assertEqual({case["mode"] for case in cases}, modes)
        for mode in modes:
            self.assertGreaterEqual(sum(case["mode"] == mode for case in cases), 5)
        self.assertEqual({case["difficulty"] for case in cases}, {"standard", "adversarial"})
        for case in cases:
            self.assertIsInstance(case["capabilities"], list)
            self.assertTrue(case["capabilities"])
            self.assertTrue(all(isinstance(item, str) and item.strip() for item in case["capabilities"]))
        capability_coverage = {item for case in cases for item in case["capabilities"]}
        self.assertTrue({
            "对话", "行动空间", "人物选择", "信息控制", "voice", "结尾",
            "类型兑现", "歧义", "压缩", "探索",
        }.issubset(capability_coverage))
        with tempfile.TemporaryDirectory() as tmp:
            writer = Path(tmp) / "writer"
            evaluator = Path(tmp) / "evaluator"
            result = run_script(
                "scripts/prepare_writing_evals.py",
                "--writer-output", str(writer), "--evaluator-output", str(evaluator),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            public_fields = {"id", "mode", "difficulty", "capabilities"}
            writer_manifest = json.loads((writer / "manifest.json").read_text(encoding="utf-8"))
            evaluator_manifest = json.loads((evaluator / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(writer_manifest, evaluator_manifest)
            self.assertTrue(all(set(item) == public_fields for item in writer_manifest))
            for case in cases:
                prompt = (writer / f"{case['id']}.md").read_text(encoding="utf-8")
                scorecard = (evaluator / f"{case['id']}.md").read_text(encoding="utf-8")
                self.assertNotIn("失败信号", prompt)
                for signal in case["failure_signals"]:
                    self.assertNotIn(signal, prompt)
                self.assertIn(case["must_preserve"][0], prompt)
                self.assertIn(case["difficulty"], prompt)
                self.assertIn(case["capabilities"][0], prompt)
                self.assertIn(case["mode"], scorecard)
                self.assertIn(case["context"], scorecard)
                self.assertIn(case["task"], scorecard)
                self.assertIn(case["must_preserve"][0], scorecard)
                self.assertIn(case["difficulty"], scorecard)
                self.assertIn(case["capabilities"][0], scorecard)
                for signal in case["failure_signals"]:
                    self.assertIn(signal, scorecard)
            stale = run_script(
                "scripts/prepare_writing_evals.py",
                "--writer-output", str(writer), "--evaluator-output", str(evaluator),
            )
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn("输出目录必须为空", stale.stderr)

            nested = run_script(
                "scripts/prepare_writing_evals.py",
                "--writer-output", str(Path(tmp) / "nested"),
                "--evaluator-output", str(Path(tmp) / "nested" / "evaluator"),
            )
            self.assertNotEqual(nested.returncode, 0)
            self.assertIn("互不包含", nested.stderr)

            invalid_manifest = Path(tmp) / "invalid.json"
            invalid_case = dict(cases[0])
            invalid_case["capabilities"] = []
            invalid_manifest.write_text(json.dumps([invalid_case], ensure_ascii=False), encoding="utf-8")
            invalid = run_script("scripts/prepare_writing_evals.py", "--manifest", str(invalid_manifest))
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("能力、保留项和失败信号", invalid.stderr)

    def test_voice_review_packet_and_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sample_one = root / "approved-one.md"
            sample_two = root / "approved-two.md"
            candidate = root / "candidate.md"
            output = root / "review.md"
            sample_one.write_text("甲" * 700, encoding="utf-8")
            sample_two.write_text("他先看门，再回答。\n压力来时，他把解释压成短句。", encoding="utf-8")
            candidate_text = "她没有回答，先把窗扣按紧。\n然后才问：你从哪里来？"
            candidate.write_text(candidate_text, encoding="utf-8")

            result = run_script(
                "scripts/prepare_voice_review.py",
                "--sample", str(sample_one), "--sample", str(sample_two),
                "--candidate", str(candidate), "--mode", "文学叙事",
                "--intent", "人物在压力下延迟回答", "--sample-max-chars", "500",
                "--output", str(output),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            packet = output.read_text(encoding="utf-8")
            self.assertIn(str(sample_one.resolve()), packet)
            self.assertIn(str(sample_two.resolve()), packet)
            self.assertIn(str(candidate.resolve()), packet)
            self.assertIn(candidate_text, packet)
            self.assertIn("甲" * 500, packet)
            self.assertNotIn("甲" * 501, packet)
            self.assertIn("原文 700 字符，收入 500 字符，已截断", packet)
            for dimension in (
                "注意力对象", "判断方式", "信息与回避策略", "叙述距离", "句法节奏", "压力下变化",
            ):
                self.assertIn(dimension, packet)
            for classification in ("保持", "合理变化", "无依据漂移"):
                self.assertIn(classification, packet)
            self.assertIn("不要输出综合分、相似度或自动改写稿", packet)

            duplicate = run_script(
                "scripts/prepare_voice_review.py",
                "--sample", str(sample_one), "--sample", str(sample_one),
                "--candidate", str(candidate), "--mode", "短篇", "--output", str(root / "duplicate.md"),
            )
            self.assertNotEqual(duplicate.returncode, 0)
            self.assertIn("样本不能重复", duplicate.stderr)

            same_candidate = run_script(
                "scripts/prepare_voice_review.py",
                "--sample", str(sample_one), "--sample", str(sample_two),
                "--candidate", str(sample_one), "--mode", "短篇", "--output", str(root / "same.md"),
            )
            self.assertNotEqual(same_candidate.returncode, 0)
            self.assertIn("不能同时作为", same_candidate.stderr)

            empty = root / "empty.md"
            empty.write_text(" \n", encoding="utf-8")
            empty_result = run_script(
                "scripts/prepare_voice_review.py",
                "--sample", str(sample_one), "--sample", str(empty),
                "--candidate", str(candidate), "--mode", "探索起草", "--output", str(root / "empty-review.md"),
            )
            self.assertNotEqual(empty_result.returncode, 0)
            self.assertIn("不能为空", empty_result.stderr)

    def test_writing_sequence_packets_and_boundaries(self) -> None:
        manifest = ROOT / "skills/novel-writing/assets/evals/writing-sequences.json"
        sequences = json.loads(manifest.read_text(encoding="utf-8"))
        modes = {"商业连载", "类型长篇", "文学叙事", "短篇", "探索起草"}
        self.assertGreaterEqual(len(sequences), 5)
        self.assertEqual({sequence["mode"] for sequence in sequences}, modes)
        coverage = {capability for sequence in sequences for capability in sequence["capabilities"]}
        self.assertTrue({"状态继承", "远距离回声", "模式稳定", "voice", "不擅增canon"} <= coverage)
        for sequence in sequences:
            self.assertGreaterEqual(len(sequence["turns"]), 4)
            self.assertIn(sequence["turns"][0]["id"], sequence["turns"][-1]["recall_from"])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            writer = root / "writer"
            evaluator = root / "evaluator"
            result = run_script(
                "scripts/prepare_writing_sequences.py",
                "--writer-output", str(writer), "--evaluator-output", str(evaluator),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            writer_manifest = json.loads((writer / "manifest.json").read_text(encoding="utf-8"))
            evaluator_manifest = json.loads((evaluator / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(writer_manifest, evaluator_manifest)
            self.assertTrue(all(set(item) == {"id", "mode", "capabilities", "turns"} for item in writer_manifest))

            for sequence in sequences:
                review = (evaluator / f"{sequence['id']}.md").read_text(encoding="utf-8")
                self.assertIn(sequence["initial_context"], review)
                self.assertIn("按轮次顺序读取全部候选正文与状态增量", review)
                self.assertIn("不输出综合分", review)
                for index, turn in enumerate(sequence["turns"]):
                    prompt = (writer / sequence["id"] / f"{turn['id']}.md").read_text(encoding="utf-8")
                    self.assertIn(sequence["initial_context"], prompt)
                    self.assertIn(turn["task"], prompt)
                    for signal in turn["failure_signals"]:
                        self.assertNotIn(signal, prompt)
                        self.assertIn(signal, review)
                    if index:
                        self.assertIn("先按顺序读取或粘贴此前所有候选输出与状态增量", prompt)
                final_prompt = (
                    writer / sequence["id"] / f"{sequence['turns'][-1]['id']}.md"
                ).read_text(encoding="utf-8")
                self.assertIn(sequence["turns"][0]["id"], final_prompt)

            stale = run_script(
                "scripts/prepare_writing_sequences.py",
                "--writer-output", str(writer), "--evaluator-output", str(evaluator),
            )
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn("输出目录必须为空", stale.stderr)
            nested = run_script(
                "scripts/prepare_writing_sequences.py",
                "--writer-output", str(root / "nested"),
                "--evaluator-output", str(root / "nested" / "evaluator"),
            )
            self.assertNotEqual(nested.returncode, 0)
            self.assertIn("互不包含", nested.stderr)

            invalid_reference = json.loads(json.dumps(sequences, ensure_ascii=False))
            invalid_reference[0]["turns"][-1]["recall_from"] = ["missing-turn"]
            invalid_path = root / "invalid-reference.json"
            invalid_path.write_text(json.dumps(invalid_reference, ensure_ascii=False), encoding="utf-8")
            invalid = run_script("scripts/prepare_writing_sequences.py", "--manifest", str(invalid_path))
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("非法或非前序轮次引用", invalid.stderr)

            duplicate_turn = json.loads(json.dumps(sequences, ensure_ascii=False))
            duplicate_turn[0]["turns"][1]["id"] = duplicate_turn[0]["turns"][0]["id"]
            duplicate_path = root / "duplicate-turn.json"
            duplicate_path.write_text(json.dumps(duplicate_turn, ensure_ascii=False), encoding="utf-8")
            duplicate = run_script("scripts/prepare_writing_sequences.py", "--manifest", str(duplicate_path))
            self.assertNotEqual(duplicate.returncode, 0)
            self.assertIn("重复轮次 id", duplicate.stderr)

    def test_revision_eval_packets_and_anonymous_pair(self) -> None:
        manifest = ROOT / "skills/novel-writing/assets/evals/revision-cases.json"
        cases = json.loads(manifest.read_text(encoding="utf-8"))
        modes = {"商业连载", "类型长篇", "文学叙事", "短篇", "探索起草"}
        self.assertGreaterEqual(len(cases), 10)
        self.assertEqual({case["mode"] for case in cases}, modes)
        self.assertEqual({case["difficulty"] for case in cases}, {"standard", "adversarial"})
        for mode in modes:
            self.assertGreaterEqual(sum(case["mode"] == mode for case in cases), 2)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            writer = root / "writer"
            evaluator = root / "evaluator"
            prepared = run_script(
                "scripts/prepare_revision_evals.py",
                "--writer-output", str(writer), "--evaluator-output", str(evaluator),
            )
            self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)
            self.assertEqual(
                json.loads((writer / "manifest.json").read_text(encoding="utf-8")),
                json.loads((evaluator / "manifest.json").read_text(encoding="utf-8")),
            )
            for case in cases:
                prompt = (writer / f"{case['id']}.md").read_text(encoding="utf-8")
                rubric = (evaluator / f"{case['id']}.md").read_text(encoding="utf-8")
                self.assertIn(case["original"], prompt)
                self.assertIn(case["revision_goal"], prompt)
                self.assertIn(case["must_preserve"][0], prompt)
                for signal in case["failure_signals"]:
                    self.assertNotIn(signal, prompt)
                    self.assertIn(signal, rubric)
                self.assertIn("不预先宣称新版本更好", rubric)

            stale = run_script(
                "scripts/prepare_revision_evals.py",
                "--writer-output", str(writer), "--evaluator-output", str(evaluator),
            )
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn("输出目录必须为空", stale.stderr)
            nested = run_script(
                "scripts/prepare_revision_evals.py",
                "--writer-output", str(root / "nested"),
                "--evaluator-output", str(root / "nested" / "evaluator"),
            )
            self.assertNotEqual(nested.returncode, 0)
            self.assertIn("互不包含", nested.stderr)

            case = cases[0]
            candidate_text = "债主第三次拍门。沈砚看了一眼滴水的檐口，没有许诺，只问对方愿不愿先验那只钱袋。"
            candidate = root / "candidate.md"
            candidate.write_text(candidate_text, encoding="utf-8")

            def make_pair(suffix: str, revision_path: Path = candidate):
                review = root / f"review-{suffix}.md"
                key = root / f"key-{suffix}.json"
                result = run_script(
                    "scripts/prepare_revision_pair.py",
                    "--case-id", case["id"], "--revision", str(revision_path),
                    "--seed", "fixed-seed", "--review-output", str(review), "--key-output", str(key),
                )
                return result, review, key

            first, first_review, first_key = make_pair("one")
            second, second_review, second_key = make_pair("two")
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            first_review_text = first_review.read_text(encoding="utf-8")
            self.assertEqual(first_review_text, second_review.read_text(encoding="utf-8"))
            self.assertEqual(
                json.loads(first_key.read_text(encoding="utf-8"))["candidates"],
                json.loads(second_key.read_text(encoding="utf-8"))["candidates"],
            )
            self.assertIn(case["original"], first_review_text)
            self.assertIn(candidate_text, first_review_text)
            self.assertIn("候选 A", first_review_text)
            self.assertIn("候选 B", first_review_text)
            self.assertIn("持平", first_review_text)
            self.assertNotIn('"identity"', first_review_text)
            self.assertNotIn('"original"', first_review_text)
            self.assertNotIn('"revision"', first_review_text)
            key_data = json.loads(first_key.read_text(encoding="utf-8"))
            self.assertEqual(
                {item["identity"] for item in key_data["candidates"].values()},
                {"original", "revision"},
            )

            same_text = root / "same-text.md"
            same_text.write_text(case["original"], encoding="utf-8")
            same, same_review, _ = make_pair("same", same_text)
            self.assertEqual(same.returncode, 0, same.stdout + same.stderr)
            self.assertIn("相同文本允许持平", same_review.read_text(encoding="utf-8"))

            collision = run_script(
                "scripts/prepare_revision_pair.py",
                "--case-id", case["id"], "--revision", str(candidate), "--seed", "x",
                "--review-output", str(candidate), "--key-output", str(root / "collision.json"),
            )
            self.assertNotEqual(collision.returncode, 0)
            self.assertIn("输出不能覆盖", collision.stderr)

    def test_document_contracts_and_script_permissions(self) -> None:
        for relative in ("README.md", "DEPLOYMENT.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn("默认每章 2000-2500", text)
            self.assertNotIn("强制执行完整", text)
        self.assertTrue(os.access(ROOT / "scripts/evaluate_chapter.py", os.X_OK))
        technique_dir = ROOT / "skills/novel-writing/references/写作技法库"
        technique_files = sorted(technique_dir.glob("*.md"))
        self.assertEqual(len(technique_files), 11)
        retired = (
            "每场战斗至少 1 个不可逆代价", "网文开篇 1000 字必须",
            "一段有效对话至少有 3 段", "章尾必须有发动机",
        )
        combined = "\n".join(path.read_text(encoding="utf-8") for path in technique_files)
        for phrase in retired:
            self.assertNotIn(phrase, combined)
        live_check = (ROOT / "skills/novel-writing/references/写中即时检查卡.md").read_text(encoding="utf-8")
        self.assertNotIn("主动争取什么", live_check)
        self.assertIn("争取、维持、回避、拖延，还是观察", live_check)


if __name__ == "__main__":
    unittest.main()
