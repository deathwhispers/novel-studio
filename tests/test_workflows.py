from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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


if __name__ == "__main__":
    unittest.main()
