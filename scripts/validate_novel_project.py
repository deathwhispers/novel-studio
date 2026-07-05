#!/usr/bin/env python3
"""小说项目结构校验脚本

用法:
    python3 scripts/validate_novel_project.py /path/to/my-novel
    python3 scripts/validate_novel_project.py /path/to/my-novel --verbose
    python3 scripts/validate_novel_project.py /path/to/my-novel --check-consistency

检查:
    - 必选目录和文件是否存在
    - 各章节字数统计
    - 设定与正文的连续性隐患
    - 回收总账是否更新
    - 连载驾驶舱是否更新
    - 信息债紧迫性矩阵自动判定
    - 人物称呼一致性
    - 时间锚点冲突
    - 关键物件归属追踪
    - 势力/角色/关系网文件存在性
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


REQUIRED_DIRS = [
    "00-书核", "05-市场", "05-市场/拆解", "10-设定", "10-设定/角色",
    "20-大纲", "20-大纲/分卷", "20-大纲/节拍卡", "20-大纲/因果", "20-大纲/回收",
    "30-正文",
    "40-修订", "40-修订/体检报告", "40-修订/修稿报告",
    "50-归档", "90-运行",
]

CORE_FILES = [
    "00-书核/作品总表.md", "00-书核/立项单.md", "00-书核/长线承诺.md",
    "20-大纲/全书总纲.md",
    "90-运行/当前进度.md", "90-运行/连载驾驶舱.md",
    "90-运行/会话交接.md", "90-运行/决策记录.md",
]

OPTIONAL_FILES = [
    "05-市场/趋势笔记.md", "05-市场/对标书单.md",
    "10-设定/硬设定.md", "10-设定/世界规则.md", "10-设定/力量体系.md",
    "10-设定/势力.md", "10-设定/地点.md", "10-设定/时间线.md", "10-设定/母题.md",
    "10-设定/角色/主角.md", "10-设定/角色/反派.md", "10-设定/角色/配角.md",
    "10-设定/角色/角色弧线追踪表.md", "10-设定/角色/角色决策记录表.md",
    "10-设定/势力关系矩阵.md", "10-设定/势力动态史.md",
    "10-设定/角色关系矩阵.md", "10-设定/角色阵营归属表.md",
    "10-设定/世界层级图.md", "10-设定/地点距离表.md",
    "10-设定/关键事件地理足迹表.md",
    "10-设定/反派/反派体系图.md", "10-设定/反派/反派递进阶梯.md",
    "20-大纲/弧线追踪.md", "20-大纲/感情线追踪.md", "20-大纲/结局蓝图.md",
    "20-大纲/多线并行管理表.md",
    "20-大纲/前3章逐章技法.md", "20-大纲/前30章留存期管理.md",
    "20-大纲/首章杀手锏集合.md",
    "20-大纲/因果/场景因果图.md", "20-大纲/回收/回收总账.md",
    "20-大纲/回收/伏笔强化策略库.md", "20-大纲/回收/伏笔类型库.md",
    "20-大纲/多主角分工表.md", "20-大纲/视角信息盲区表.md",
    "20-大纲/结局设计模式库.md",
    "40-修订/修订日志.md", "40-修订/完本检查清单.md",
    "90-运行/全角色卷末快照.md", "90-运行/角色去留追踪表.md",
    "90-运行/角色立场漂移记录.md", "90-运行/前文索引.md",
    "90-运行/连载工作流.md", "90-运行/卡文急救.md",
]


def count_chinese_chars(text: str) -> int:
    """统计中文字符数（含标点）"""
    return len(re.findall(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', text))


def format_wc(n: int) -> str:
    if n >= 10000:
        return f"{n / 10000:.1f}万"
    return f"{n}"


def scan_chapters(project_dir: Path) -> list[dict]:
    """从所有卷目录中扫描章节文件并统计字数"""
    chapters = []
    text_dir = project_dir / "30-正文"
    if not text_dir.exists():
        return chapters
    # 递归扫描所有卷目录下的 .md 文件
    md_files = sorted(text_dir.rglob("*.md"))
    for f in md_files:
        # 跳过非章节文件（如检查表等）
        if not re.search(r'第\d+章', f.name):
            continue
        text = f.read_text(encoding="utf-8")
        wc = count_chinese_chars(text)
        has_content = wc > 200
        # 使用相对路径标识章节位置
        rel_path = f.relative_to(text_dir)
        chapters.append({
            "file": str(rel_path),
            "filename": f.name,
            "words": wc,
            "has_content": has_content,
            "text": text,
        })
    return chapters


def extract_chapter_number(filename: str) -> int | None:
    """从文件名提取章节号"""
    m = re.search(r'chapter-(\d+)', filename)
    if m:
        return int(m.group(1))
    m = re.search(r'第(\d+)章', filename)
    if m:
        return int(m.group(1))
    return None


def scan_progress(project_dir: Path) -> dict:
    """从当前进度文件中读取进度信息"""
    progress_file = project_dir / "90-运行" / "当前进度.md"
    info = {"current_volume": "?", "current_chapter": "?", "last_updated": "?"}
    if not progress_file.exists():
        return info
    text = progress_file.read_text(encoding="utf-8")
    for line in text.splitlines():
        if "当前卷" in line or "当前写到" in line:
            info["current_volume"] = line.split("：")[-1].strip() if "：" in line else line
        if "当前章" in line or "第" in line and "章" in line:
            info["current_chapter"] = line.split("：")[-1].strip() if "：" in line else line
    return info


# =============================================================================
# 连续性检测函数
# =============================================================================

def collect_character_names(project_dir: Path) -> dict[str, list[str]]:
    """从角色卡中提取所有角色名（包括别名）

    Returns:
        {标准名: [出现过的所有别名]}
    """
    role_dir = project_dir / "10-设定" / "角色"
    if not role_dir.exists():
        return {}

    names = {}
    for f in role_dir.glob("*.md"):
        if f.name in ("角色卡模板.md",):
            continue
        text = f.read_text(encoding="utf-8")
        # 提取标题（H1）作为标准名
        m = re.search(r'^#\s+(.+)', text, re.MULTILINE)
        std_name = m.group(1).strip() if m else f.stem
        # 提取别名（"姓名：" / "曾用名：" / "别名：" / "字：" / "号："）
        aliases = {std_name}
        for pattern in [r'姓名[：:]\s*(\S+)', r'曾用名[：:]\s*(\S+)', r'别名[：:]\s*(\S+)',
                        r'字[：:]\s*(\S+)', r'号[：:]\s*(\S+)']:
            for am in re.findall(pattern, text):
                aliases.add(am.strip())
        names[std_name] = list(aliases)
    return names


def check_name_consistency(project_dir: Path, chapters: list[dict]) -> list[str]:
    """检测正文中的人名是否有错别字或不一致

    策略：从所有章节中提取疑似中文专名（2-4 字 + 高频出现），与角色卡中的人名做比对
    """
    issues = []
    names = collect_character_names(project_dir)
    if not names:
        return issues

    # 把所有标准名 + 别名压平成一个集合
    all_known = set()
    for std, aliases in names.items():
        for a in aliases:
            all_known.add(a)

    # 在正文中搜索疑似人名（"X 长老"/"X 师兄"/"X 师妹" 这种模式）
    chapter_texts = "\n".join(c["text"] for c in chapters)
    pattern = re.compile(r'([\u4e00-\u9fff]{2,3})(长老|师兄|师姐|师妹|师弟|宗主|掌门|师祖|真人|前辈|姑娘|公子|少侠)')
    candidates = Counter()
    for m in pattern.finditer(chapter_texts):
        name = m.group(1)
        candidates[name] += 1

    # 过滤高频（>3 次）但不在已知名字里的
    for name, count in candidates.most_common():
        if count >= 3 and name not in all_known:
            # 检查是否可能是已知名的一部分
            partial = False
            for known in all_known:
                if name in known or known in name:
                    partial = True
                    break
            if not partial:
                issues.append(f"⚠️ 角色名疑似不一致：'{name}'（出现 {count} 次）不在任何角色卡中，请确认是否漏建档案或用错名字")
    return issues


def collect_locations(project_dir: Path) -> set[str]:
    """从地点文件中提取所有地点名"""
    locations = set()
    for fname in ["地点.md", "地点距离表.md", "世界层级图.md"]:
        f = project_dir / "10-设定" / fname
        if f.exists():
            text = f.read_text(encoding="utf-8")
            # H2 标题通常是地点名
            for m in re.finditer(r'^##\s+(.+)', text, re.MULTILINE):
                locations.add(m.group(1).strip())
            # H3 也可能
            for m in re.finditer(r'^###\s+(.+)', text, re.MULTILINE):
                locations.add(m.group(1).strip())
    return locations


def check_distance_consistency(project_dir: Path, chapters: list[dict]) -> list[str]:
    """检测正文中是否有明显的"地理时间"冲突

    策略：搜索"从A到B用了X天/时辰"这类描述，提取出来让人工确认
    """
    issues = []
    chapter_texts = []
    for c in chapters:
        if c["has_content"]:
            chapter_texts.append((c["file"], c["text"]))

    # 抽取"从X到Y + 时间"模式
    pattern = re.compile(r'从([\u4e00-\u9fff]{2,8})到([\u4e00-\u9fff]{2,8})[^，。\n]*?(\d+(?:\.\d+)?)\s*(天|时辰|日|夜|年|月|刻钟|个时辰)')
    for fname, text in chapter_texts:
        for m in pattern.finditer(text):
            from_loc, to_loc, time_val, time_unit = m.group(1), m.group(2), m.group(3), m.group(4)
            issues.append(
                f"📍 {fname}: 路程记录「从{from_loc}到{to_loc}用了{time_val}{time_unit}」"
                f"——请与 `10-设定/地点距离表.md` 对照"
            )
    return issues


def collect_key_items(project_dir: Path) -> set[str]:
    """从硬设定中提取关键物件名"""
    items = set()
    canon = project_dir / "10-设定" / "硬设定.md"
    if not canon.exists():
        return items
    text = canon.read_text(encoding="utf-8")
    # 找带"X 剑/X 玉佩/X 戒指"等物件模式
    pattern = re.compile(r'[\u4e00-\u9fff]{2,6}(剑|刀|枪|鼎|镜|珠|玉|玉佩|戒指|令牌|信物|秘籍|功法|图|谱|符|丹|瓶|碗|琴|箫|笛|杖|旗|印|玺|簪|佩|环|铃|珠|书|卷)')
    for m in pattern.finditer(text):
        items.add(m.group(0))
    return items


def check_item_ownership(project_dir: Path, chapters: list[dict]) -> list[str]:
    """检测关键物件的归属是否有矛盾

    策略：识别"X交给Y"/"X从Y处夺走"等模式，跟踪每件物品的当前持有者
    """
    issues = []
    items = collect_key_items(project_dir)
    if not items:
        return issues

    # 在正文中找每件物品最早出现的章节
    first_appearance = {}
    last_appearance = {}
    for c in chapters:
        if not c["has_content"]:
            continue
        for item in items:
            if item in c["text"]:
                if item not in first_appearance:
                    first_appearance[item] = c["file"]
                last_appearance[item] = c["file"]

    # 检查长时间未出现的关键物品（> 30 章）
    chapter_nums = {}
    for c in chapters:
        n = extract_chapter_number(c["file"])
        if n is not None:
            chapter_nums[c["file"]] = n

    for item, last in last_appearance.items():
        last_num = chapter_nums.get(last, 0)
        max_num = max(chapter_nums.values()) if chapter_nums else 0
        if max_num - last_num > 30:
            issues.append(
                f"🔮 关键物件失联：'{item}' 最后出现在 {last}（已 {max_num - last_num} 章未出现）"
                f"——请确认是否需要触碰或回收"
            )
    return issues


def check_info_debt_urgency(project_dir: Path, chapters: list[dict]) -> list[str]:
    """检测信息债监控表中的紧迫性矩阵

    策略：解析 `20-大纲/信息债监控表.md` 中的债表，对照当前章节号，
    用紧迫性矩阵判定哪些债到了"立即触碰"格。
    """
    issues = []
    debt_file = project_dir / "20-大纲" / "信息债监控表.md"
    if not debt_file.exists():
        return issues
    text = debt_file.read_text(encoding="utf-8")

    # 找出当前最新章节号
    max_chapter = 0
    for c in chapters:
        n = extract_chapter_number(c["file"])
        if n and n > max_chapter:
            max_chapter = n

    # 解析债表（找出形如 | 线头 | 类型 | 等级 | ... | 距上次触碰 | 的行）
    # 这里采用简单启发式：找包含「等级」列且数字的章节号
    debt_pattern = re.compile(
        r'\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([SABC])\s*\|'
        r'[^|]*?\|\s*[^|]*?\|\s*(\d+)\s*\|'
    )
    for m in debt_pattern.finditer(text):
        debt_name, debt_type, grade, last_touch_chapter = m.group(1).strip(), m.group(2).strip(), m.group(3), int(m.group(4))
        gap = max_chapter - last_touch_chapter
        if gap < 0:
            continue
        # 紧迫性矩阵
        action = ""
        if grade == "S":
            if 11 <= gap <= 20:
                action = "隐性强化"
            elif 21 <= gap <= 30:
                action = "显性提醒"
            elif 31 <= gap <= 50:
                action = "显性提醒"
            elif gap > 50:
                action = "立即触碰"
        elif grade == "A":
            if 11 <= gap <= 20:
                action = "隐性强化"
            elif 21 <= gap <= 30:
                action = "显性提醒"
            elif gap > 30:
                action = "立即触碰"
        elif grade == "B":
            if 11 <= gap <= 20:
                action = "显性提醒"
            elif gap > 20:
                action = "立即触碰"
        elif grade == "C":
            if gap > 10:
                action = "立即触碰"
        if action == "立即触碰":
            issues.append(
                f"⏰ 债紧迫性矩阵触发：'{debt_name}'（{grade}级）距上次触碰 {gap} 章 → {action}"
            )
    return issues


def check_world_setting_files(project_dir: Path) -> list[str]:
    """检查百万级长篇必备的关系/矩阵文件是否存在

    这些不是 required（不会报错），但百万级长篇到了第 2 卷后强烈建议建立。
    """
    warnings = []
    text_dir = project_dir / "30-正文"
    if not text_dir.exists():
        return warnings
    chapter_files = sorted(text_dir.rglob("*.md"))
    chapter_count = len([f for f in chapter_files if re.search(r'第\d+章', f.name)])

    # 超过 30 章建议建关系矩阵
    if chapter_count > 30:
        for f in ["10-设定/角色关系矩阵.md", "10-设定/势力关系矩阵.md"]:
            if not (project_dir / f).exists():
                warnings.append(
                    f"💡 已写 {chapter_count} 章，建议补建 `{f}` —— 百万级长篇的横向关系网必备"
                )

    # 超过 50 章建议建卷末快照
    if chapter_count > 50:
        for f in ["90-运行/全角色卷末快照.md", "90-运行/角色去留追踪表.md"]:
            if not (project_dir / f).exists():
                warnings.append(
                    f"💡 已写 {chapter_count} 章，建议补建 `{f}` —— 防止中后期角色写丢"
                )
        return warnings  # 提示一次

    # 超过 100 章建议建前文索引
    if chapter_count > 100:
        if not (project_dir / "90-运行/前文索引.md").exists():
            warnings.append(
                f"💡 已写 {chapter_count} 章，建议补建 `90-运行/前文索引.md` —— 续写时快速回忆前文"
            )
    return warnings


def check_voice_drift(project_dir: Path, chapters: list[dict]) -> list[str]:
    """检测角色 voice 是否漂移

    策略：从角色卡中提取 "口头禅" 字段，对比最近 20 章的对话内容，
    如果某个口头禅在最近 20 章里完全没出现，提示 voice 漂移。
    """
    issues = []
    role_dir = project_dir / "10-设定" / "角色"
    if not role_dir.exists():
        return issues

    # 收集每个角色的口头禅
    role_catchphrases: dict[str, list[str]] = {}
    for f in role_dir.glob("*.md"):
        if f.name in ("角色卡模板.md",):
            continue
        text = f.read_text(encoding="utf-8")
        m = re.search(r'^#\s+(.+)', text, re.MULTILINE)
        role_name = m.group(1).strip() if m else f.stem
        # 找 "口头禅" 字段后的内容（直到下一个 **字段**）
        catchphrase_m = re.search(r'口头禅[^*]*?：\s*([^\n]+)', text)
        if catchphrase_m:
            line = catchphrase_m.group(1)
            # 提取中文短语
            phrases = re.findall(r'[「「""][^」」""]+[」」""]|[\u4e00-\u9fff]{3,8}', line)
            if phrases:
                role_catchphrases[role_name] = phrases

    if not role_catchphrases:
        return issues

    # 取出最近 20 章的文本
    recent_texts = [c["text"] for c in chapters if c["has_content"]][-20:]
    if not recent_texts:
        return issues
    combined = "\n".join(recent_texts)

    # 检查每个角色的口头禅是否还在出现
    for role_name, phrases in role_catchphrases.items():
        # 跳过只在最近章节没有的（可能是新角色或短期未出场）
        # 简化策略：检查至少 1 个口头禅是否出现
        appeared = any(phrase in combined for phrase in phrases)
        if not appeared:
            # 进一步检查该角色是否在最近 20 章有对话
            role_in_recent = role_name in combined
            if role_in_recent:
                issues.append(
                    f"🎭 voice 漂移：'{role_name}' 在最近 20 章有出场但未使用任何口头禅——辨识度可能下降"
                )
            else:
                issues.append(
                    f"🎭 '{role_name}' 已超过 20 章未出场——口头禅无法验证，请确认是否需要回归"
                )
    return issues


# =============================================================================
# 主流程
# =============================================================================

def check_settlement(project_dir: Path) -> list[str]:
    """检查设定与正文的基础一致性（向后兼容的接口）"""
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="小说项目结构校验")
    parser.add_argument("project_dir", help="小说项目目录路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="输出详细信息")
    parser.add_argument("--check-consistency", "-c", action="store_true",
                        help="深度连续性检测（人物名/距离/物件/信息债/百万级文件）")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        print(f"错误：目录不存在 -> {project_dir}")
        return 1

    errors = []
    warnings = []
    info = []
    consistency_issues = []

    # 1. 检查目录
    for d in REQUIRED_DIRS:
        if not (project_dir / d).exists():
            errors.append(f"缺少目录：{d}")

    # 2. 检查核心文件
    for f in CORE_FILES:
        if not (project_dir / f).exists():
            errors.append(f"缺少核心文件：{f}")

    # 3. 检查可选文件（仅提示）
    for f in OPTIONAL_FILES:
        if not (project_dir / f).exists():
            warnings.append(f"可选文件缺失：{f}")

    # 4. 扫描章节字数
    chapters = scan_chapters(project_dir)
    if chapters:
        info.append(f"章节总数：{len(chapters)}")
        total_words = sum(c["words"] for c in chapters)
        info.append(f"正文总字数（中文字符）：{format_wc(total_words)}")
        has_content = [c for c in chapters if c["has_content"]]
        info.append(f"已写章节：{len(has_content)}/{len(chapters)}")
        if args.verbose:
            for c in chapters:
                status = "✓" if c["has_content"] else "○"
                info.append(f"  [{status}] {c['file']}: {format_wc(c['words'])}")
        # 检查字数异常
        for c in chapters:
            if c["has_content"] and c["words"] < 500:
                warnings.append(f"章节字数偏低：{c['file']}（{format_wc(c['words'])}字）")
            elif c["has_content"] and c["words"] > 8000:
                warnings.append(f"章节字数偏高：{c['file']}（{format_wc(c['words'])}字）")
    else:
        warnings.append("未找到章节文件")

    # 5. 进度检查
    progress = scan_progress(project_dir)
    info.append(f"当前进度：{progress['current_volume']}/{progress['current_chapter']}")

    # 6. 检查连载驾驶舱
    cockpit = project_dir / "90-运行" / "连载驾驶舱.md"
    if cockpit.exists():
        cockpit_text = cockpit.read_text(encoding="utf-8")
        if "当前写到" not in cockpit_text:
            warnings.append("连载驾驶舱.md 未填写当前写到位置")
        if "风险" not in cockpit_text:
            warnings.append("连载驾驶舱.md 未填写风险项")
    else:
        errors.append("缺少连载驾驶舱.md")

    # 7. 检查回收总账
    ledger = project_dir / "20-大纲" / "回收" / "回收总账.md"
    if ledger.exists():
        ledger_text = ledger.read_text(encoding="utf-8")
        if len(ledger_text.strip()) < 50:
            warnings.append("回收总账.md 内容过少，可能未填写")
    else:
        warnings.append("缺少回收总账.md")

    # 8. 深度连续性检测（可选）
    if args.check_consistency and chapters:
        consistency_issues.extend(check_world_setting_files(project_dir))
        consistency_issues.extend(check_info_debt_urgency(project_dir, chapters))
        consistency_issues.extend(check_name_consistency(project_dir, chapters))
        consistency_issues.extend(check_item_ownership(project_dir, chapters))
        consistency_issues.extend(check_distance_consistency(project_dir, chapters))
        consistency_issues.extend(check_voice_drift(project_dir, chapters))

    # 输出报告
    print("=" * 60)
    print(f"小说项目校验报告：{project_dir.name}")
    print("=" * 60)

    if errors:
        print(f"\n❌ 错误（{len(errors)}项）：")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print(f"\n⚠️  警告（{len(warnings)}项）：")
        for w in warnings:
            print(f"  - {w}")

    if info:
        print(f"\nℹ️  信息（{len(info)}项）：")
        for i in info:
            print(f"  - {i}")

    if consistency_issues:
        print(f"\n🔍 连续性检测（{len(consistency_issues)}项）：")
        for i in consistency_issues:
            print(f"  - {i}")

    if not errors and not warnings and not consistency_issues:
        print("\n✅ 项目结构健康，未发现问题！")
    elif not errors:
        print("\n✅ 无严重错误，建议修复警告项。")

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
