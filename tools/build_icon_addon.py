#!/usr/bin/env python
"""Build the Lucide icon add-on (``lucide-icons-<version>.addon.mm``).

The add-on installs Lucide's SVG icon set into Freeplane's user icon folder::

    <userdir>/icons/lucide/<category>/<name>.svg

Freeplane scans that folder on start, so after installing (and restarting) the
icon panel grows a ``lucide`` group with one sub group per Lucide category. Icons
inside a sub folder get the icon name ``lucide/<category>/<name>`` - e.g. a
stylenode would reference ``lucide/status/check``.

Everything here is derived from the pinned Lucide commit in
``addons/lucide-icons/addon.json``; the source archive is downloaded once and
cached under ``.cache/lucide/<commit>/``.

Usage::

    python tools/build_icon_addon.py --version 0.1.0 --out dist
    python tools/build_icon_addon.py --version 0.1.0 --out dist --lucide-archive lucide.zip
    python tools/build_icon_addon.py --check-only dist/lucide-icons-v0.1.0.addon.mm

The add-on map format is the one ``installScriptAddOn.groovy`` expects:
mandatory root attributes (``name``/``version``/``author``/``freeplaneVersionFrom``),
one mandatory child node per key, and a ``zips`` branch whose child holds a
base64 encoded zip that is unpacked into the Freeplane user directory.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

ADDON_DIR = Path("addons") / "lucide-icons"
DEFAULT_CACHE = Path(".cache") / "lucide"
# fixed timestamp -> rebuilding the same input yields the same bytes
ZIP_TIME = (1980, 1, 1, 0, 0, 0)
MISC_CATEGORY = "misc"


class BuildError(SystemExit):
    """Reported as a build failure, not as a traceback."""

    def __init__(self, message: str) -> None:
        super().__init__(f"error: {message}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 16), b""):
            digest.update(block)
    return digest.hexdigest()


# --------------------------------------------------------------------------- #
# Lucide sources
# --------------------------------------------------------------------------- #
def load_meta(root: Path) -> dict:
    path = root / ADDON_DIR / "addon.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise BuildError(f"{path} is missing")
    except json.JSONDecodeError as error:
        raise BuildError(f"{path} is not valid JSON: {error}")


def source_dir(root: Path, meta: dict, cache_dir: Path) -> Path:
    return cache_dir / meta["lucide"]["commit"]


def _looks_complete(directory: Path) -> bool:
    icons = directory / "icons"
    return (
        (directory / "LICENSE").is_file()
        and icons.is_dir()
        and len(list(icons.glob("*.svg"))) > 1000
        and (directory / "categories").is_dir()
    )


def _extract(archive: Path, destination: Path) -> None:
    """Keep only what the add-on needs: icon svgs, icon metadata, categories, licence."""
    wanted: dict[str, bytes] = {}
    with zipfile.ZipFile(archive) as bundle:
        prefix = bundle.namelist()[0].split("/")[0] + "/"
        for name in bundle.namelist():
            if not name.startswith(prefix):
                continue
            relative = name[len(prefix) :]
            if (
                relative.startswith("icons/")
                and relative.endswith((".svg", ".json"))
                or relative.startswith("categories/")
                and relative.endswith(".json")
                or relative == "LICENSE"
            ):
                wanted[relative] = bundle.read(name)
    if not wanted:
        raise BuildError(f"{archive} does not look like a Lucide source archive")
    destination.mkdir(parents=True, exist_ok=True)
    for relative, data in wanted.items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def ensure_sources(
    root: Path,
    meta: dict,
    *,
    cache_dir: Path,
    local_archive: Path | None,
) -> Path:
    directory = source_dir(root, meta, cache_dir)
    if _looks_complete(directory):
        return directory
    if local_archive:
        if not local_archive.is_file():
            raise BuildError(f"lucide archive {local_archive} does not exist")
        print(f"extracting {local_archive.name} -> {directory}")
        _extract(local_archive, directory)
        return directory

    url = meta["lucide"]["archive"].format(commit=meta["lucide"]["commit"])
    print(f"downloading {url}")
    archive = cache_dir / f"lucide-{meta['lucide']['commit'][:12]}.zip"
    archive.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "freeplane-themes-build"})
    try:
        with urllib.request.urlopen(request, timeout=180) as response, archive.open("wb") as handle:
            while chunk := response.read(1 << 16):
                handle.write(chunk)
    except Exception as error:  # network, DNS, 404 ...
        raise BuildError(
            f"could not download Lucide: {error}\n"
            "       offline? pass --lucide-archive <lucide.zip>, or copy an existing "
            f"cache to {directory}"
        )
    _extract(archive, directory)
    return directory


def collect_icons(sources: Path) -> tuple[dict[str, list[str]], dict[str, bytes], list[str]]:
    """Return (category -> icon names, zip entries, warnings).

    Lucide metadata lets one icon inherit the categories of another via
    ``"$extends:<icon>"``; those have to be resolved before an icon can be filed.
    """
    category_files = sorted((sources / "categories").glob("*.json"))
    known = {path.stem for path in category_files}
    icons_dir = sources / "icons"

    declared: dict[str, list[str]] = {}
    for svg in sorted(icons_dir.glob("*.svg")):
        meta_path = icons_dir / f"{svg.stem}.json"
        if meta_path.is_file():
            declared[svg.stem] = json.loads(meta_path.read_text(encoding="utf-8")).get("categories", [])

    def resolved(slug: str, seen: frozenset[str] = frozenset()) -> list[str]:
        """The icon's categories, following ``$extends`` once per icon."""
        if slug in seen or slug not in declared:
            return []
        seen = seen | {slug}
        direct = [
            name for name in declared[slug] if not name.startswith("$") and name in known
        ]
        inherited: list[str] = []
        for entry in declared[slug]:
            if entry.startswith("$extends:"):
                for name in resolved(entry[len("$extends:") :], seen):
                    if name not in inherited:
                        inherited.append(name)
        return direct + inherited

    entries: dict[str, bytes] = {}
    groups: dict[str, list[str]] = {name: [] for name in sorted(known)}
    groups[MISC_CATEGORY] = []
    warnings: list[str] = []

    for svg in sorted(icons_dir.glob("*.svg")):
        if svg.stem not in declared:
            warnings.append(f"{svg.name}: no metadata, filed under {MISC_CATEGORY}")
            category = MISC_CATEGORY
        else:
            candidates = resolved(svg.stem)
            if candidates:
                category = candidates[0]
            else:
                warnings.append(f"{svg.name}: no known category, filed under {MISC_CATEGORY}")
                category = MISC_CATEGORY
        destination = f"icons/lucide/{category}/{svg.name}"
        entries[destination] = svg.read_bytes()
        groups[category].append(svg.stem)

    groups = {name: icons for name, icons in groups.items() if icons}
    return groups, entries, warnings


def make_zip(entries: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o644 << 16
            archive.writestr(info, entries[name])
    return buffer.getvalue()


# --------------------------------------------------------------------------- #
# .addon.mm rendering
# --------------------------------------------------------------------------- #
def xml_text(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def xml_attr(value: str) -> str:
    return xml_text(value).replace('"', "&quot;").replace("\n", "&#xa;")


def attribute(name: str, value: str, indent: str) -> str:
    return f'{indent}<attribute NAME="{xml_attr(name)}" VALUE="{xml_attr(value)}"/>'


def render_map(
    *,
    version: str,
    meta: dict,
    payload: bytes,
    entries: dict[str, bytes],
    groups: dict[str, list[str]],
) -> str:
    addon_name = meta["name"]
    titles = meta["title"]
    category_count = len(groups)
    icon_count = len(entries)
    body_b64 = base64.b64encode(payload).decode("ascii")

    description = meta["description"].format(
        icon_count=icon_count,
        category_count=category_count,
        lucide_commit=meta["lucide"]["commit"][:12],
    ).strip()
    license_text = (meta["license_text"]).strip()

    lines: list[str] = []
    add = lines.append
    add('<?xml version="1.0" encoding="UTF-8"?>')
    add('<map version="1.9.8">')
    add(
        f'<node TEXT="{xml_attr(titles["zh_CN"])}" FOLDED="false" '
        f'LINK="{xml_attr(meta["homepage"])}">'
    )
    add('  <font SIZE="16" BOLD="true"/>')
    add(attribute("name", addon_name, "  "))
    add(attribute("version", f"v{version}", "  "))
    add(attribute("author", meta["author"], "  "))
    add(attribute("freeplaneVersionFrom", meta["freeplaneVersionFrom"], "  "))
    add(attribute("freeplaneVersionTo", "", "  "))

    # description / license: the installer reads exactly one child node each
    add('  <node TEXT="description" POSITION="left">')
    add(f'    <node TEXT="{xml_attr(description)}"/>')
    add("  </node>")

    add('  <node TEXT="changes" FOLDED="true" POSITION="left">')
    add(f'    <node TEXT="v{version}" FOLDED="true">')
    add(
        f'      <node TEXT="{xml_attr(f"{icon_count} 个 Lucide 图标，{category_count} 个分类")}"/>'
    )
    add("    </node>")
    add("  </node>")

    add('  <node TEXT="license" FOLDED="true" POSITION="left">')
    add(f'    <node TEXT="{xml_attr(license_text)}"/>')
    add("  </node>")

    # leaf nodes: empty preferences / properties / scripts are all accepted
    add('  <node TEXT="preferences.xml" POSITION="left"/>')
    add('  <node TEXT="default.properties" POSITION="left"/>')

    add('  <node TEXT="translations" POSITION="left">')
    for locale, title in titles.items():
        add(f'    <node TEXT="{xml_attr(locale)}">')
        add(attribute("addons.${name}", title, "      "))
        add("    </node>")
    add("  </node>")

    add('  <node TEXT="scripts" POSITION="left"/>')

    add('  <node TEXT="zips" POSITION="right">')
    add('    <node TEXT="icons" FOLDED="true">')
    add(f'      <node TEXT="{body_b64}"/>')
    add("    </node>")
    add("  </node>")

    add('  <node TEXT="deinstall" POSITION="left">')
    for name in sorted(entries):
        add(attribute("delete", f"${{installationbase}}/{name}", "    "))
    add("  </node>")

    add("</node>")
    add("</map>")
    return "\n".join(lines) + "\n"


def build_addon(
    root: Path,
    out: Path,
    version: str,
    *,
    cache_dir: Path | None = None,
    local_archive: Path | None = None,
    categories: list[str] | None = None,
) -> Path:
    meta = load_meta(root)
    sources = ensure_sources(
        root,
        meta,
        cache_dir=cache_dir or root / DEFAULT_CACHE,
        local_archive=local_archive,
    )
    groups, entries, warnings = collect_icons(sources)
    if not entries:
        raise BuildError(f"no icon found under {sources / 'icons'}")

    if categories:
        wanted = {name.strip() for name in categories if name.strip()}
        unknown = sorted(wanted - set(groups))
        if unknown:
            raise BuildError(
                f"unknown category {', '.join(unknown)} - known: {', '.join(sorted(groups))}"
            )
        groups = {name: icons for name, icons in groups.items() if name in wanted}
        entries = {
            name: data for name, data in entries.items() if name.split("/")[2] in wanted
        }
        if not entries:
            raise BuildError("--categories filtered out every icon")

    payload = make_zip(entries)
    document = render_map(version=version, meta=meta, payload=payload, entries=entries, groups=groups)

    out.mkdir(parents=True, exist_ok=True)
    target = out / f"{meta['name']}-{version}.addon.mm"
    target.write_text(document, encoding="utf-8", newline="\n")

    print(f"lucide    : {meta['lucide']['commit'][:12]}  ({len(list((sources / 'icons').glob('*.svg')))} svgs)")
    print(f"icons     : {len(entries)} in {len(groups)} groups")
    for category, icons in groups.items():
        print(f"  {category:<20} {len(icons):>4}")
    for warning in warnings[:10]:
        print(f"warning: {warning}", file=sys.stderr)
    if len(warnings) > 10:
        print(f"warning: ... and {len(warnings) - 10} more", file=sys.stderr)
    print(f"payload   : {len(payload):,} bytes zipped, {len(document):,} bytes of .mm")
    print(f"add-on    : {target}  sha256={sha256_file(target)}")
    return target


# --------------------------------------------------------------------------- #
# self check - mirrors what installScriptAddOn.groovy insists on
# --------------------------------------------------------------------------- #
REQUIRED_CHILDREN = (
    "description",
    "license",
    "translations",
    "preferences.xml",
    "default.properties",
    "scripts",
    "zips",
    "deinstall",
)


def check(addon_path: Path) -> int:
    import xml.etree.ElementTree as ElementTree

    problems: list[str] = []

    def fail(message: str) -> None:
        problems.append(message)

    raw = addon_path.read_bytes()
    document = ElementTree.fromstring(raw)
    if document.tag != "map":
        fail(f"document element is <{document.tag}>, expected <map>")
        return report(problems)
    root_node = document.find("node")
    if root_node is None:
        fail("<map> holds no root <node>")
        return report(problems)

    attributes = {}
    for element in root_node.findall("attribute"):
        name = element.get("NAME", "")
        value = element.get("VALUE", "")
        if value:
            attributes[name] = value
    for required in ("name", "version", "author", "freeplaneVersionFrom"):
        if not attributes.get(required):
            fail(f"root is missing the mandatory attribute {required}")
    if not re.match(r"^v\d+\.\d+", attributes.get("version", "")):
        fail(f"version {attributes.get('version')!r} should look like v1.2.3")

    children: dict[str, list] = {}
    for child in root_node.findall("node"):
        children.setdefault(child.get("TEXT", ""), []).append(child)
    for name in REQUIRED_CHILDREN:
        if not children.get(name):
            fail(f"missing mandatory child node {name}")
        if len(children[name]) > 1:
            fail(f"child node {name} appears {len(children[name])} times")

    for name in ("description", "license"):
        node = (children.get(name) or [None])[0]
        if node is not None and len(node.findall("node")) != 1:
            fail(f"{name} must have exactly one child node")

    addon_name = attributes.get("name", "")
    for locale in (children.get("translations") or []):
        for locale_node in locale.findall("node"):
            keys = {element.get("NAME") for element in locale_node.findall("attribute")}
            if f"addons.${{name}}" not in keys:
                fail(f"translation {locale_node.get('TEXT')} lacks addons.${{name}}")

    zips = (children.get("zips") or [None])[0]
    payload = b""
    if zips is not None:
        zips_children = zips.findall("node")
        if len(zips_children) != 1:
            fail(f"zips must have exactly one child, found {len(zips_children)}")
        else:
            only = zips_children[0]
            inner = only.findall("node")
            if len(inner) != 1:
                fail(f"zips child {only.get('TEXT')!r} must hold exactly one binary node")
            else:
                text = (inner[0].get("TEXT") or "").strip()
                try:
                    payload = base64.b64decode(re.sub(r"\s+", "", text), validate=True)
                except Exception as error:
                    fail(f"zip payload is not valid base64: {error}")

    entries: list[str] = []
    if payload:
        try:
            with zipfile.ZipFile(io.BytesIO(payload)) as bundle:
                entries = [name for name in bundle.namelist() if not name.endswith("/")]
                for name in entries:
                    if not name.startswith("icons/lucide/"):
                        fail(f"{name}: unexpected install path")
                    if not name.endswith(".svg"):
                        fail(f"{name}: unexpected file type")
                    ElementTree.fromstring(bundle.read(name))
        except zipfile.BadZipFile as error:
            fail(f"zip payload does not open: {error}")
        except ElementTree.ParseError as error:
            fail(f"an icon is not valid XML: {error}")

    deinstall = (children.get("deinstall") or [None])[0]
    rules = []
    if deinstall is not None:
        rules = [
            element.get("VALUE", "")
            for element in deinstall.findall("attribute")
            if element.get("NAME") == "delete"
        ]
    expected = {f"${{installationbase}}/{name}" for name in entries}
    if set(rules) != expected:
        missing = expected - set(rules)
        extra = set(rules) - expected
        if missing:
            fail(f"{len(missing)} installed file(s) have no deinstall rule, e.g. {sorted(missing)[0]}")
        if extra:
            fail(f"{len(extra)} deinstall rule(s) point at files that are not shipped")

    categories = {name.split("/")[2] for name in entries}
    print(f"file      : {addon_path.name}  {len(raw):,} bytes  sha256={sha256_file(addon_path)[:16]}...")
    print(f"add-on    : {attributes.get('name')} {attributes.get('version')} "
          f"(from Freeplane {attributes.get('freeplaneVersionFrom')})")
    print(f"icons     : {len(entries)} svgs in {len(categories)} categories")
    print(f"deinstall : {len(rules)} rules")
    return report(problems)


def report(problems: list[str]) -> int:
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        print(f"{len(problems)} problem(s) found", file=sys.stderr)
        return 1
    print("OK: structure matches what installScriptAddOn.groovy parses")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", help="add-on version without the v prefix, e.g. 0.1.0")
    parser.add_argument("--out", default="dist", help="output folder (default: dist)")
    parser.add_argument("--cache", default=None, help=f"Lucide cache folder (default: {DEFAULT_CACHE})")
    parser.add_argument("--lucide-archive", default=None, help="use a local lucide source zip instead of downloading")
    parser.add_argument(
        "--categories",
        default=None,
        help="comma separated Lucide categories to keep (default: all), e.g. arrows,files,security",
    )
    parser.add_argument("--check-only", default=None, help="only validate an existing .addon.mm")
    options = parser.parse_args(argv[1:])

    if options.check_only:
        return check(Path(options.check_only))
    if not options.version:
        print("error: --version is required (or use --check-only)", file=sys.stderr)
        return 2

    root = Path(__file__).resolve().parent.parent
    out = Path(options.out)
    if out.resolve() == root:
        print("error: --out must not be the repository root", file=sys.stderr)
        return 2

    target = build_addon(
        root,
        out,
        options.version,
        cache_dir=Path(options.cache) if options.cache else None,
        local_archive=Path(options.lucide_archive) if options.lucide_archive else None,
        categories=options.categories.split(",") if options.categories else None,
    )
    return check(target)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
