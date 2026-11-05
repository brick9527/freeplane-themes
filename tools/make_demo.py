#!/usr/bin/env python
"""Build the demo maps in demos/ from the themes in themes/.

A Freeplane theme is just a map whose styles live in <map_styles>. To preview a
theme we take the theme file, keep its hooks/styles, give the root node a real
title and hang a sample tree below it.

Three things this script gets right, because all are easy to get wrong by hand:

* a style defined as <stylenode TEXT="X"> is referenced from a node with
  STYLE_REF="X" (literal name -> StyleString). LOCALIZED_STYLE_REF is for
  translated keys such as styles.important -> StyleTranslatedObject; pointing it
  at a literal name silently resolves to nothing.
* AutomaticEdgeColor (RULE="ON_BRANCH_CREATION") colours edges when a branch is
  created, not when a file is loaded, so the demo sets edge colours explicitly.
  In the card demo the branch order matches edgeColorConfiguration, and each
  branch uses the card style of the same colour - the 9th branch repeats the 1st.
* a zoom factor keeps nine branches inside one screenshot (card demo only).

Usage:  python tools/make_demo.py .
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CARD_TREE = (
    "年度产品计划",
    [
        ("产品规划", "#4c7fd1", "色卡1 蓝", [("竞品分析", []), ("版本路线图", [])]),
        ("技术方案", "#df684c", "色卡2 朱", [("架构升级", []), ("性能优化", [])]),
        ("市场推广", "#6fae5a", "色卡3 绿", [("内容营销", []), ("渠道投放", [])]),
        ("团队安排", "#e8a33d", "色卡4 橙", [("招聘 3 人", []), ("培训计划", [])]),
        ("客户成功", "#6c5b9e", "色卡5 紫", [("客户回访", [])]),
        ("预算管控", "#2a9d8f", "色卡6 青", [("人力成本", [])]),
        ("风险清单", "#e06c9f", "色卡7 粉", [("供应商延期", [])]),
        ("里程碑", "#55707f", "色卡8 灰蓝", [("Q1 发布", [])]),
        ("年度复盘", "#4c7fd1", "色卡1 蓝", [("数据回顾", [])]),
    ],
)

# text-only theme: no cards, only the Tag pill on one branch
TEXT_TREE = (
    "年度产品计划",
    [
        ("产品规划", "#df684c", "styles.important", [("竞品分析", []), ("版本路线图", [])]),
        ("技术方案", "#4c7fd1", "Tag", [("架构升级", []), ("性能优化", [])]),
        ("市场推广", "#6fae5a", None, [("内容营销", []), ("渠道投放", [])]),
        ("团队安排", "#e8a33d", None, [("招聘 3 人", []), ("培训", [])]),
    ],
)

DEMOS = {
    # theme: (tree, style reference attribute, zoom)
    "xmind-classic": (CARD_TREE, "STYLE_REF", "0.75"),
    "xmind-zen": (TEXT_TREE, None, None),
}


def esc(value: str) -> str:
    return (value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                 .replace('"', "&quot;"))


class Builder:
    def __init__(self) -> None:
        self.counter = 0

    def node(self, name, color="", style=None, children=(), indent=1, attr="STYLE_REF") -> str:
        self.counter += 1
        attrs = f'TEXT="{esc(name)}"'
        if style:
            # translated keys go through LOCALIZED_STYLE_REF, literal names through STYLE_REF
            key = "LOCALIZED_STYLE_REF" if style.startswith(("styles.", "AutomaticLayout.")) else attr
            attrs += f' {key}="{esc(style)}"'
        attrs += f' ID="ID_17{self.counter:08d}"'
        pad = "  " * indent
        body = f'<edge COLOR="{color}"/>' if color else ""
        for child_name, grandchildren in children:
            body += self.node(child_name, color, None, grandchildren, indent + 1, attr)
        if body:
            return f'{pad}<node {attrs}>{body}{pad}</node>\n'
        return f'{pad}<node {attrs}/>\n'


def build(theme: str, root: Path) -> Path:
    tree, attr, zoom = DEMOS[theme]
    src = (root / "themes" / f"{theme}.mm").read_text(encoding="utf-8")
    match = re.search(r"<node\b[^>]*>", src)
    if not match:
        raise SystemExit(f"{theme}: no root node found")

    open_tag = match.group(0)
    new_tag = open_tag.replace('LOCALIZED_TEXT="new_mindmap"', f'TEXT="{esc(tree[0])}"')
    if new_tag == open_tag:
        raise SystemExit(f"{theme}: root node has no LOCALIZED_TEXT=\"new_mindmap\" to replace")

    body = src[match.end(0):src.rindex("</node>")]
    if zoom:
        body = re.sub(r'(<hook NAME="MapStyle"[^>]*)>', r'\1 zoom="%s">' % zoom, body, count=1)

    builder = Builder()
    children = "".join(
        builder.node(name, color, style, kids, attr=attr or "STYLE_REF")
        for name, color, style, kids in tree[1]
    )
    out = src[:match.start(0)] + new_tag + "\n" + body + children + "</node>" + \
        src[src.rindex("</node>") + len("</node>"):]

    dst = root / "demos" / f"{theme}-demo.mm"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out, encoding="utf-8", newline="\n")
    return dst


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else ".").resolve()
    for theme in DEMOS:
        print("wrote", build(theme, root))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
