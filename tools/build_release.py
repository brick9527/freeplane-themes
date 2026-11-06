#!/usr/bin/env python
"""Assemble the packages that a GitHub Release publishes.

Everything a release ships is produced here, so the workflow stays thin and the
same command runs locally:

    python tools/build_release.py --tag v1.0.0 --out dist

Output in ``--out`` (default ``dist/``):

    <theme>.mm                               one file per theme, ready for templates/
    lucide-icons-<version>.addon.mm          the Lucide icon add-on (see addons/lucide-icons/)
    freeplane-themes-<version>-themes.zip    all themes + licence + attribution notice
    freeplane-themes-<version>-full.zip      whole project (themes, demos, previews, docs, tools)
    freeplane-themes-<version>-source.zip    git archive of the tag
    freeplane-themes-<version>-source.tar.gz git archive of the tag
    SHA256SUMS.txt                           SHA-256 of every file above

and the release body (``--notes``, default ``release-notes.md``).

The tag has to be a semver tag (``v1.2.3``, ``1.2.3``); a version with a
``-suffix`` becomes a pre-release. Archiving is done with ``git archive``, and
the zips written here use a fixed timestamp, so re-running the same tag yields
the same bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_icon_addon import build_addon, check as check_addon  # noqa: E402  (needs the sys.path line above)

# One line per theme in the release notes. A theme missing here still gets
# packaged; it only shows up with the fallback description.
THEME_DESCRIPTIONS = {
    "xmind-classic": "XMind 经典：中央深色胶囊 + 一级彩色卡片（8 色卡）+ 分支色描边",
    "xmind-zen": "XMind 现代：纯白底、无边框，文字 + 粗彩色曲线",
    "ember-night": "深色：深底 + 层级配色 + 语义样式（Callout / Todo / Done / Quote）",
    "ember-day": "浅色：与 ember-night 同色系",
}

# copied into the top of the packaged folders
TOP_LEVEL_FILES = ("README.md", "README.en.md", "LICENSE", "LICENSE-CC-BY-4.0.txt")
CONTENT_DIRS = ("themes", "demos", "previews", "docs", "tools", "addons")

SEMVER = re.compile(
    r"^(?P<core>"
    r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z.-]+)?"
    r"(?:\+[0-9A-Za-z.-]+)?"
    r")$"
)

ZIP_TIME = (1980, 1, 1, 0, 0, 0)


class BuildError(SystemExit):
    """Reported as a build failure, not as a traceback."""

    def __init__(self, message: str) -> None:
        super().__init__(f"error: {message}")


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise BuildError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def repo_slug(root: Path) -> str | None:
    """owner/name of this repository: CI env first, otherwise the origin remote."""
    if (slug := os.environ.get("GITHUB_REPOSITORY")):
        return slug
    try:
        url = git(root, "remote", "get-url", "origin")
    except BuildError:
        return None
    match = re.search(r"github\.com[:/]([^/\s]+/[^/\s]+?)(?:\.git)?$", url)
    return match.group(1) if match else None


def parse_tag(tag: str) -> tuple[str, bool]:
    """Return (version, is_prerelease) for a semver tag, with or without a leading v."""
    version = tag.strip()[1:] if tag.strip()[:1] in ("v", "V") else tag.strip()
    match = SEMVER.match(version)
    if not match:
        raise BuildError(
            f"tag {tag!r} is not semver - use v1.2.3 / 1.2.3 / v1.2.3-rc.1"
        )
    return version, "-" in version


def make_zip(destination: Path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o644 << 16
            archive.writestr(info, entries[name])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 16), b""):
            digest.update(block)
    return digest.hexdigest()


def project_files(root: Path) -> dict[str, Path]:
    """Every human-readable file of the project, keyed by its relative path."""
    files: dict[str, Path] = {}
    for directory in CONTENT_DIRS:
        for path in sorted((root / directory).rglob("*")):
            if not path.is_file() or path.name.startswith("."):
                continue
            if "__pycache__" in path.parts:
                continue
            files[path.relative_to(root).as_posix()] = path
    for name in TOP_LEVEL_FILES:
        files[name] = root / name
    return files


def notice_text(version: str, slug: str | None) -> str:
    repo_line = f"https://github.com/{slug}" if slug else ""
    return f"""\
Freeplane 脑图主题 / Freeplane mind-map themes — {version}
{repo_line}

Copyright (c) 2026 brick9527

本包内的主题（*.mm）、演示图、截图与文档按 CC BY 4.0 授权，也可选择按 GPL-2.0 使用。
再分发时请保留上面的仓库地址与本署名，并注明是否做过修改。许可全文见
LICENSE-CC-BY-4.0.txt；脚本与 CI 配置按 GPL-2.0 授权，全文见 LICENSE。
图标 add-on 里的图标来自 Lucide，按 ISC 授权（部分源自 Feather 的按 MIT），
许可全文见 addons\\lucide-icons\\LICENSE-lucide.txt，也已整篇写进 .addon.mm。

安装：把 .mm 放进 Freeplane 用户目录下的 templates\\ 文件夹
（工具 → 打开用户目录），再用「文件 → 从模板新建导图…」并选择「用户模板 (*.mm)」。

Install: drop the .mm files into the templates folder of Freeplane's user
directory (Tools -> Open user directory), then File -> New map from template...
and pick "User templates (*.mm)".

Themes, demo maps, screenshots and docs are CC BY 4.0 (or GPL-2.0 at your
option); the scripts are GPL-2.0. The icons in the add-on come from Lucide and
are ISC licensed (Feather-derived ones MIT); the full licence text sits in the
add-on's own license node, so the single .addon.mm file carries it too.
"""


def build(root: Path, out: Path, tag: str, notes_path: Path) -> tuple[str, bool]:
    version, prerelease = parse_tag(tag)

    try:
        git(root, "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}")
    except BuildError:
        raise BuildError(f"tag {tag!r} does not exist in this repository - push it first")

    themes = sorted((root / "themes").glob("*.mm"))
    if not themes:
        raise BuildError("no .mm theme found in themes/ - nothing to publish")
    for theme in themes:
        if theme.stem not in THEME_DESCRIPTIONS:
            print(
                f"warning: {theme.name} has no entry in THEME_DESCRIPTIONS - "
                "it ships with the fallback description in the release notes",
                file=sys.stderr,
            )

    slug = repo_slug(root)
    out.mkdir(parents=True, exist_ok=True)
    stamp = f"freeplane-themes-{version}"

    # --- individual theme files, straight from themes/ ---------------------
    for theme in themes:
        (out / theme.name).write_bytes(theme.read_bytes())

    # --- themes.zip: flat, so extraction lands .mm files in templates/ ----
    theme_entries = {theme.name: theme.read_bytes() for theme in themes}
    theme_entries["NOTICE.txt"] = notice_text(version, slug).encode("utf-8")
    for name in ("README.md", "LICENSE", "LICENSE-CC-BY-4.0.txt"):
        theme_entries[name] = (root / name).read_bytes()
    make_zip(out / f"{stamp}-themes.zip", theme_entries)

    # --- Lucide icon add-on: built from addons/lucide-icons/ + pinned Lucide commit
    addon = build_addon(root, out, version)
    if check_addon(addon) != 0:
        raise SystemExit(f"the icon add-on failed its self check: {addon}")

    # --- full.zip: the whole project, under a versioned folder -------------
    full_entries: dict[str, bytes] = {
        f"{stamp}/{relative}": path.read_bytes()
        for relative, path in project_files(root).items()
    }
    full_entries[f"{stamp}/NOTICE.txt"] = notice_text(version, slug).encode("utf-8")
    make_zip(out / f"{stamp}-full.zip", full_entries)

    # --- source archives, straight from git -------------------------------
    for extension, archive_format in (("zip", "zip"), ("tar.gz", "tar.gz")):
        git(
            root,
            "archive",
            f"--format={archive_format}",
            f"--prefix={stamp}/",
            f"--output={out / f'{stamp}-source.{extension}'}",
            tag,
        )

    # --- checksums --------------------------------------------------------
    # the notes file is the release body, not a downloadable asset
    assets = sorted(
        p
        for p in out.iterdir()
        if p.is_file() and p.name != "SHA256SUMS.txt" and p.resolve() != notes_path.resolve()
    )
    checksum_lines = [f"{sha256(path)}  {path.name}" for path in assets]
    (out / "SHA256SUMS.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8", newline="\n")

    # --- release body -----------------------------------------------------
    notes = release_notes(root, tag, version, prerelease, slug, [p.name for p in assets])
    notes_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.write_text(notes, encoding="utf-8", newline="\n")

    print(f"tag       : {tag}")
    print(f"version   : {version}{'  (pre-release)' if prerelease else ''}")
    print(f"themes    : {', '.join(theme.stem for theme in themes)}")
    for path in assets:
        print(f"asset     : {path.name:48} {path.stat().st_size:>9,} bytes")
    print(f"checksums : {out / 'SHA256SUMS.txt'}")
    print(f"notes     : {notes_path}")
    return version, prerelease


def release_notes(
    root: Path,
    tag: str,
    version: str,
    prerelease: bool,
    slug: str | None,
    asset_names: list[str],
) -> str:
    themes = sorted((root / "themes").glob("*.mm"))
    theme_count = len(themes)
    commit_date = git(root, "log", "-1", "--format=%cs", tag)
    # peel the tag: `rev-parse <tag>` would print the tag object for annotated tags
    commit = git(root, "rev-parse", "--short", f"{tag}^{{commit}}")

    try:
        previous = git(root, "describe", "--tags", "--abbrev=0", f"{tag}^")
    except BuildError:
        previous = None

    lines: list[str] = []
    lines.append(f"# Freeplane 脑图主题 {version}")
    lines.append("")
    meta = [f"`{tag}`", commit_date, f"{theme_count} 套主题", f"commit `{commit}`"]
    if slug:
        meta.append(f"[仓库](https://github.com/{slug})")
    lines.append(" · ".join(meta))
    lines.append("")

    lines.append("## 下载 / Downloads")
    lines.append("")
    lines.append("| 文件 | 内容 |")
    lines.append("| --- | --- |")
    for name in asset_names:
        lines.append(f"| `{name}` | {describe_asset(name, version, theme_count)} |")
    lines.append(f"| `SHA256SUMS.txt` | {describe_asset('SHA256SUMS.txt', version, theme_count)} |")
    lines.append("")
    lines.append(
        "只想用其中一套：下载对应的 `*.mm`。"
        "想一次装好模板：`-themes.zip`，解压后把 `.mm` 直接放进 Freeplane 的 `templates\\`。"
        "想看源码或自己改：`-full.zip`，或 GitHub 自动附带的 `Source code (zip)` / `Source code (tar.gz)`。"
    )
    lines.append("")

    lines.append("## 主题 / Themes")
    lines.append("")
    lines.append("| 主题 | 文件 | 风格 |")
    lines.append("| --- | --- | --- |")
    for theme in themes:
        description = THEME_DESCRIPTIONS.get(theme.stem, "自定义主题")
        lines.append(f"| `{theme.stem}` | `{theme.name}` | {description} |")
    lines.append("")
    lines.append("效果预览见仓库的 `previews/*.png`，可编辑的演示图在 `demos/` 下。")
    lines.append("")
    lines.append("`.mm` 是 `freeplane 1.9.8` 格式，Freeplane 1.11 / 1.12 / 1.13 均可读取。")
    lines.append("")

    lines.append("## 安装 / Install")
    lines.append("")
    lines.append("```")
    lines.append("工具 → 打开用户目录            (Tools → Open user directory)")
    lines.append("  └─ templates\\              ← 把 .mm 放进去")
    lines.append("文件 → 从模板新建导图…        (File → New map from template…)")
    lines.append("  └─ 文件类型选「用户模板 (*.mm)」")
    lines.append("```")
    lines.append("")
    lines.append("Windows 也可以一条命令装好：`tools\\install_themes.ps1`；")
    lines.append("已有导图想换风格：`格式 → 管理样式 → 替换导图样式为…`。")
    lines.append("")

    lines.append("## 图标包 / Icons add-on")
    lines.append("")
    lines.append("`lucide-icons-*.addon.mm` 是独立的 add-on，把 [Lucide](https://lucide.dev) 全套矢量图标")
    lines.append("装进 Freeplane 的用户图标目录（`icons/lucide/`），按 Lucide 的分类分成一个个子组。")
    lines.append("")
    lines.append("```")
    lines.append("文件 → 打开导图…          选中 lucide-icons-*.addon.mm")
    lines.append("工具 → 插件 → 插件安装器   (Tools → Plugins → Add-on installer) → 安装 → 重启")
    lines.append("图标面板 → lucide 分组 → notifications / files / arrows / text …")
    lines.append("```")
    lines.append("")
    lines.append("安装器读的是「当前打开那张导图」根节点上的 name / version / author / freeplaneVersionFrom，")
    lines.append("所以要先把这个 `.addon.mm` 当普通导图打开，它不会自己弹文件选择框。")
    lines.append("")
    lines.append("图标名就是「lucide/分类/文件名」，样式或节点上写 `<icon BUILTIN=\"lucide/notifications/check\"/>`。")
    lines.append("图标放在 `lucide/` 子目录，不覆盖任何内置图标；但它只在本机生效 ——")
    lines.append("把带这些图标的导图发给没装 add-on 的人，图标会缺失。细节见 `docs/icons.md`。")
    lines.append("")

    lines.append("## 变更 / Changes")
    lines.append("")
    if previous:
        lines.append(f"自 `{previous}` 起：")
        lines.append("")
        lines.extend(changelog(root, previous, tag) or ["- （无提交记录差异）"])
        if slug:
            lines.append("")
            lines.append(f"[完整对比](https://github.com/{slug}/compare/{previous}...{tag})")
    else:
        lines.append(f"首个发布版本 `{tag}`，包含以下提交：")
        lines.append("")
        lines.extend(changelog(root, None, tag))
    lines.append("")

    lines.append("## 校验 / Verify")
    lines.append("")
    lines.append("```bash")
    lines.append("sha256sum -c SHA256SUMS.txt        # Linux / macOS")
    lines.append("Get-FileHash * -Algorithm SHA256   # Windows PowerShell")
    lines.append("```")
    lines.append("")
    lines.append("每个 `.mm` 都过了 `tools/validate_theme.py`；`demos/` 与当前主题一致。")
    lines.append("")

    lines.append("## 许可 / License")
    lines.append("")
    lines.append(
        "`themes/`、`demos/`、`previews/`、`docs/` 按 **CC BY 4.0** 授权（也可选择 GPL-2.0），"
        "再分发请保留仓库链接与 `Copyright (c) 2026 brick9527`，并注明是否修改。"
    )
    lines.append("`tools/`、`.github/` 按 **GPL-2.0-only** 授权。详见包内 `LICENSE` 与 `LICENSE-CC-BY-4.0.txt`。")
    lines.append(
        "图标 add-on 里的图标来自 Lucide，按 **ISC** 授权（部分源自 Feather 的按 MIT），"
        "见 `addons/lucide-icons/LICENSE-lucide.txt`；打包脚本同样是 GPL-2.0。"
    )
    lines.append(
        "许可全文已整篇写进 `.addon.mm` 的 `license` 节点（安装时的许可确认框就是它），"
        "所以只下载这一个文件也带着完整许可。"
    )
    lines.append("")
    if prerelease:
        lines.append("> 预发布版本：接口与文件名可能还会调整。")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("### English")
    lines.append("")
    lines.append(f"Freeplane mind-map themes, packaged for `{tag}` ({theme_count} themes).")
    lines.append("")
    lines.append("- `*.mm` — one file per theme; drop it into Freeplane's `templates/` folder.")
    lines.append(
        "- `lucide-icons-<version>.addon.mm` — Lucide icon add-on "
        "(open it as a map, then Tools → Plugins → Add-on installer)."
    )
    lines.append(f"- `-themes.zip` — all themes plus the licence and the attribution notice.")
    lines.append("- `-full.zip` — the whole project (themes, demos, previews, docs, tools).")
    lines.append("- `-source.zip` / `-source.tar.gz` — `git archive` of the tag.")
    lines.append("- `SHA256SUMS.txt` — SHA-256 of every file above.")
    lines.append("")
    lines.append(
        "Install: Tools → Open user directory → put the `.mm` files into `templates/`, then\n"
        "File → New map from template… and pick “User templates (*.mm)”."
    )
    lines.append("")
    lines.append(
        "Themes, demo maps, screenshots and docs are CC BY 4.0 (or GPL-2.0, your choice); "
        "the scripts are GPL-2.0. See `README.en.md` inside the packages."
    )
    lines.append("")
    return "\n".join(lines)


def describe_asset(name: str, version: str, theme_count: int) -> str:
    if name.endswith(".addon.mm"):
        return "Lucide 图标 add-on，装完图标面板里多出 `lucide` 分组"
    if name.endswith(".mm"):
        return "单套主题模板，放进 `templates\\` 即可用"
    if name.endswith("-themes.zip"):
        return f"{theme_count} 套主题 + NOTICE + 许可，解压后 `.mm` 直接落进 `templates\\`"
    if name.endswith("-full.zip"):
        return "完整工程：主题 / 演示图 / 预览图 / 文档 / 工具 / 许可"
    if name.endswith("-source.zip") or name.endswith("-source.tar.gz"):
        return f"`git archive` 导出的 {version} 源码包（含 CI 配置）"
    if name == "SHA256SUMS.txt":
        return "上面所有文件的 SHA-256 校验值"
    return ""


def changelog(root: Path, previous: str | None, tag: str) -> list[str]:
    arguments = ["log", "--no-merges", "--pretty=format:- %s (`%h`)"]
    if previous:
        arguments.append(f"{previous}..{tag}")
    else:
        arguments.append("--reverse")
        arguments.append(tag)
    output = git(root, *arguments)
    return [line for line in output.splitlines() if line.strip()]


def prune(out: Path) -> None:
    """Remove earlier build output so no stale version is uploaded alongside."""
    if not out.is_dir():
        return
    for path in out.iterdir():
        if path.is_file() and (
            path.name.endswith((".mm", ".zip", ".tar.gz")) or path.name == "SHA256SUMS.txt"
        ):
            path.unlink()


def write_github_output(version: str, prerelease: bool, tag: str) -> None:
    target = os.environ.get("GITHUB_OUTPUT")
    if not target:
        return
    with open(target, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"tag={tag}\n")
        handle.write(f"version={version}\n")
        handle.write(f"prerelease={'true' if prerelease else 'false'}\n")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tag", default=os.environ.get("GITHUB_REF_NAME"), help="tag to package (default: $GITHUB_REF_NAME)")
    parser.add_argument("--out", default="dist", help="output folder for the assets (default: dist)")
    parser.add_argument("--notes", default="release-notes.md", help="where to write the release body")
    parser.add_argument(
        "--parse-only",
        action="store_true",
        help="only check that the tag is semver and report version/prerelease, build nothing",
    )
    options = parser.parse_args(argv[1:])

    if not options.tag:
        print("error: no tag given and $GITHUB_REF_NAME is not set", file=sys.stderr)
        return 2

    if options.parse_only:
        version, prerelease = parse_tag(options.tag)
        print(f"tag={options.tag} version={version} prerelease={str(prerelease).lower()}")
        write_github_output(version, prerelease, options.tag)
        return 0

    root = Path(__file__).resolve().parent.parent
    out = Path(options.out)
    if out.resolve() == root:
        print("error: --out must not be the repository root", file=sys.stderr)
        return 2

    prune(out)
    version, prerelease = build(root, out, options.tag, Path(options.notes))
    write_github_output(version, prerelease, options.tag)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
