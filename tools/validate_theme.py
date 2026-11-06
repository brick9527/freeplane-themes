#!/usr/bin/env python
"""Structural validator for Freeplane mind-map theme templates (.mm).

Checks a theme against the format that Freeplane's own bundled templates use
(freeplane/src/external/resources/templates/*.mm) and the enums/attribute names
that the Freeplane sources define. It does not render the map; it only makes
sure Freeplane can load the file and that style values are legal.

Usage:
    python tools/validate_theme.py themes/ember-night.mm [themes/ember-day.mm ...]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.etree import ElementTree

NODE_SHAPES = {
    "fork", "bubble", "oval", "rectangle",
    "wide_hexagon", "narrow_hexagon", "as_parent", "combined",
}
# values that only exist in old maps; Freeplane ignores them on load
LEGACY_NODE_SHAPES = {"circle", "invisible"}
# org.freeplane.features.edge.EdgeStyle
EDGE_STYLES = {
    "bezier", "hide_edge", "horizontal", "linear",
    "sharp_bezier", "sharp_linear", "summary",
}
# org.freeplane.api.Dash
DASHES = {"SOLID", "CLOSE_DOTS", "DASHES", "DISTANT_DOTS", "DOTS_AND_DASHES"}
# org.freeplane.features.cloud.CloudShape
CLOUD_SHAPES = {"ARC", "STAR", "RECT", "ROUND_RECT"}
TEXT_ALIGN = {"LEFT", "CENTER", "RIGHT", "DEFAULT"}
# org.freeplane.view.swing.map.IconLocation - map property "show_icons"
ICON_LOCATIONS = {"BESIDE_NODES", "ABOVE_NODES", "HIDE"}

REQUIRED_PREDEFINED = [
    "default",
    "defaultstyle.details",
    "defaultstyle.attributes",
    "defaultstyle.note",
    "defaultstyle.selection",
    "defaultstyle.floating",
]

COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")

STYLENODE_ATTRS = {
    "LOCALIZED_TEXT", "LOCALIZED_STYLE_REF", "TEXT", "ID", "STYLE", "COLOR",
    "BACKGROUND_COLOR", "TEXT_ALIGN", "BORDER_WIDTH", "BORDER_COLOR",
    "BORDER_COLOR_LIKE_EDGE", "BORDER_WIDTH_LIKE_EDGE", "BORDER_DASH",
    "BORDER_DASH_LIKE_EDGE", "SHAPE_HORIZONTAL_MARGIN", "SHAPE_VERTICAL_MARGIN",
    "MIN_WIDTH", "MAX_WIDTH", "ICON_SIZE", "UNIFORM_SHAPE", "VGAP_QUANTITY",
    "COMMON_HGAP_QUANTITY", "VSHIFT_QUANTITY", "POSITION", "FORMAT",
    "FORMAT_AS_HYPERLINK", "NUMBERED", "TEXT_SHORTENED", "FOLDED", "CREATED",
    "MODIFIED", "LINK", "TAGS", "PLAINTEXT",
}

# LocationBuilder only registers these for <node>, not for <stylenode>;
# a style silently ignores them (COMMON_HGAP_QUANTITY is the style variant)
NODE_ONLY_ATTRS = {"HGAP_QUANTITY", "HGAP"}


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def check_color(errors: list[str], where: str, name: str, value: str) -> None:
    if not COLOR_RE.match(value):
        fail(errors, f"{where}: {name}={value!r} is not #RRGGBB or #RRGGBBAA")


def validate(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        tree = ElementTree.parse(path)
    except ElementTree.ParseError as exc:
        return [f"XML is not well formed: {exc}"], warnings

    root = tree.getroot()
    if root.tag != "map":
        fail(errors, f"root element is <{root.tag}>, expected <map>")
    if not root.get("version"):
        fail(errors, "<map> has no version attribute")
    elif not root.get("version", "").startswith("freeplane"):
        warnings.append(f"<map version={root.get('version')!r}> is not a freeplane version string")

    nodes = root.findall("node")
    if len(nodes) != 1:
        fail(errors, f"expected exactly one root <node>, found {len(nodes)}")
        return errors, warnings
    root_node = nodes[0]

    hooks = {h.get("NAME"): h for h in root_node.findall("hook")}

    # --- map level hooks -------------------------------------------------
    map_style = hooks.get("MapStyle")
    if map_style is None:
        fail(errors, "root node has no <hook NAME=\"MapStyle\">; there is no theme to apply")
        return errors, warnings

    if map_style.get("background") is None:
        warnings.append("MapStyle hook has no background colour")
    else:
        check_color(errors, "MapStyle", "background", map_style.get("background"))
    if (alpha := map_style.get("background_alpha")) is not None:
        if not alpha.isdigit():
            fail(errors, f"MapStyle: background_alpha={alpha!r} is not an integer")

    if "AutomaticEdgeColor" not in hooks:
        warnings.append("root node has no AutomaticEdgeColor hook: edges get no automatic colours")
    if "accessories/plugins/AutomaticLayout.properties" not in hooks:
        warnings.append(
            "root node has no AutomaticLayout hook: AutomaticLayout.level,* styles "
            "will not be applied automatically"
        )
    else:
        value = hooks["accessories/plugins/AutomaticLayout.properties"].get("VALUE")
        if value not in (None, "ALL", "HEADINGS"):
            fail(errors, f"AutomaticLayout VALUE={value!r}, expected ALL or HEADINGS")

    if root_node.get("LOCALIZED_STYLE_REF") != "AutomaticLayout.level.root":
        warnings.append(
            "root node has LOCALIZED_STYLE_REF="
            f"{root_node.get('LOCALIZED_STYLE_REF')!r}; themes normally set "
            "'AutomaticLayout.level.root'"
        )

    # --- <properties> ----------------------------------------------------
    props = map_style.find("properties")
    if props is None:
        warnings.append("MapStyle hook has no <properties> element")
    else:
        conf = props.get("edgeColorConfiguration")
        if conf is None:
            warnings.append("properties has no edgeColorConfiguration: default edge palette is used")
        else:
            colours = [c for c in conf.split(",") if c]
            if len(colours) < 2:
                fail(errors, "edgeColorConfiguration needs at least 2 colours")
            for c in colours:
                check_color(errors, "edgeColorConfiguration", "colour", c)
                if len(c) != 9:
                    warnings.append(
                        f"edgeColorConfiguration entry {c!r} has no alpha channel; "
                        "Freeplane writes #RRGGBBAA"
                    )

        # map property show_icons: BESIDE_NODES keeps icons on the text baseline,
        # ABOVE_NODES stacks them on top of the label - easy to mistake for a bug.
        show_icons = props.get("show_icons")
        if show_icons is None:
            warnings.append(
                "properties has no show_icons: Freeplane falls back to BESIDE_NODES, "
                "but a map that carries its own ABOVE_NODES keeps icons above the label"
            )
        elif show_icons not in ICON_LOCATIONS:
            fail(
                errors,
                f"show_icons={show_icons!r}, expected one of {', '.join(sorted(ICON_LOCATIONS))}",
            )

    # --- <map_styles> ----------------------------------------------------
    map_styles = map_style.find("map_styles")
    if map_styles is None:
        fail(errors, "MapStyle hook has no <map_styles> element")
        return errors, warnings

    style_root = map_styles.find("stylenode")
    if style_root is None or style_root.get("LOCALIZED_TEXT") != "styles.root_node":
        fail(errors, "map_styles does not start with <stylenode LOCALIZED_TEXT=\"styles.root_node\">")
        return errors, warnings

    groups = {
        s.get("LOCALIZED_TEXT"): s
        for s in style_root.findall("stylenode")
        if s.get("LOCALIZED_TEXT")
    }
    for group in ("styles.predefined", "styles.user-defined", "styles.AutomaticLayout"):
        if group not in groups:
            fail(errors, f"map_styles is missing the {group} branch")

    predefined = groups.get("styles.predefined")
    if predefined is not None:
        present = {s.get("LOCALIZED_TEXT") for s in predefined.findall("stylenode")}
        for key in REQUIRED_PREDEFINED:
            if key not in present:
                warnings.append(f"predefined style {key!r} is missing (Freeplane falls back to defaults)")

    levels = groups.get("styles.AutomaticLayout")
    if levels is not None:
        present = {s.get("LOCALIZED_TEXT") for s in levels.findall("stylenode")}
        if "AutomaticLayout.level.root" not in present:
            fail(errors, "AutomaticLayout branch has no 'AutomaticLayout.level.root' style")
        for depth in range(1, 5):
            if f"AutomaticLayout.level,{depth}" not in present:
                warnings.append(f"AutomaticLayout.level,{depth} is missing")

    # --- style node values ----------------------------------------------
    for style in map_styles.iter("stylenode"):
        key = style.get("LOCALIZED_TEXT") or style.get("TEXT") or "<unnamed>"
        where = f"style {key}"

        for attr in sorted(set(style.attrib) & NODE_ONLY_ATTRS):
            warnings.append(
                f"{where}: {attr} is only read for <node>, a style ignores it; "
                "use COMMON_HGAP_QUANTITY"
            )

        # LOCALIZED_TEXT is looked up in the translation table; unknown keys are
        # rendered as "[key]". Custom names therefore have to use TEXT.
        localized = style.get("LOCALIZED_TEXT")
        if localized is not None and not localized.startswith(
            ("styles.", "default", "AutomaticLayout.")
        ):
            warnings.append(
                f"{where}: LOCALIZED_TEXT goes through the translation table "
                f"(unknown keys render as \"[{localized}]\"), use TEXT= for custom style names"
            )

        unknown = set(style.attrib) - STYLENODE_ATTRS
        for attr in sorted(unknown):
            warnings.append(f"{where}: unknown attribute {attr!r}")

        shape = style.get("STYLE")
        if shape is not None:
            if shape.lower() in LEGACY_NODE_SHAPES:
                warnings.append(
                    f"{where}: STYLE={shape!r} is a legacy value that Freeplane ignores; "
                    f"use one of {sorted(NODE_SHAPES)}"
                )
            elif shape.lower() not in NODE_SHAPES:
                fail(errors, f"{where}: STYLE={shape!r} is not one of {sorted(NODE_SHAPES)}")

        align = style.get("TEXT_ALIGN")
        if align is not None and align.upper() not in TEXT_ALIGN:
            fail(errors, f"{where}: TEXT_ALIGN={align!r} is not one of {sorted(TEXT_ALIGN)}")

        for colour_attr in ("COLOR", "BACKGROUND_COLOR", "BORDER_COLOR"):
            if (value := style.get(colour_attr)) is not None:
                check_color(errors, where, colour_attr, value)

        if (dash := style.get("BORDER_DASH")) is not None and dash not in DASHES:
            fail(errors, f"{where}: BORDER_DASH={dash!r} is not one of {sorted(DASHES)}")

        font = style.find("font")
        if font is not None:
            size = font.get("SIZE")
            if size is not None:
                try:
                    int(size)
                except ValueError:
                    fail(errors, f"{where}: font SIZE={size!r} is not an integer point size")

        edge = style.find("edge")
        if edge is not None:
            if (style_name := edge.get("STYLE")) is not None and style_name not in EDGE_STYLES:
                fail(errors, f"{where}: edge STYLE={style_name!r} is not one of {sorted(EDGE_STYLES)}")
            if (dash := edge.get("DASH")) is not None and dash not in DASHES:
                fail(errors, f"{where}: edge DASH={dash!r} is not one of {sorted(DASHES)}")
            if (colour := edge.get("COLOR")) is not None:
                check_color(errors, where, "edge COLOR", colour)

        cloud = style.find("cloud")
        if cloud is not None:
            if (shape := cloud.get("SHAPE")) is not None and shape not in CLOUD_SHAPES:
                fail(errors, f"{where}: cloud SHAPE={shape!r} is not one of {sorted(CLOUD_SHAPES)}")
            if (colour := cloud.get("COLOR")) is not None:
                check_color(errors, where, "cloud COLOR", colour)

        for arrow in style.findall("arrowlink"):
            if (colour := arrow.get("COLOR")) is not None:
                check_color(errors, where, "arrowlink COLOR", colour)
            destination = arrow.get("DESTINATION")
            if destination is not None and not any(
                s.get("ID") == destination for s in map_styles.iter("stylenode")
            ):
                fail(errors, f"{where}: arrowlink DESTINATION={destination!r} does not match any style ID")

    # --- how nodes reference styles -------------------------------------
    # LOCALIZED_STYLE_REF builds a StyleTranslatedObject and STYLE_REF a
    # StyleString; a node can only pick up a style built the same way.
    translated_keys = {s.get("LOCALIZED_TEXT") for s in map_styles.iter("stylenode")} - {None}
    literal_names = {s.get("TEXT") for s in map_styles.iter("stylenode")} - {None}

    for node in root.iter("node"):
        title = node.get("TEXT") or node.get("LOCALIZED_TEXT") or "<untitled>"
        localized_ref = node.get("LOCALIZED_STYLE_REF")
        literal_ref = node.get("STYLE_REF")

        if localized_ref is not None:
            if localized_ref in literal_names and localized_ref not in translated_keys:
                fail(
                    errors,
                    f"node {title!r}: LOCALIZED_STYLE_REF={localized_ref!r} points at a "
                    f"style that is defined with TEXT=; use STYLE_REF instead "
                    f"(the reference silently resolves to nothing otherwise)",
                )
            elif localized_ref not in translated_keys:
                warnings.append(
                    f"node {title!r}: style {localized_ref!r} is not defined in this map "
                    f"(it must be a built-in translated key or defined via LOCALIZED_TEXT)"
                )

        if literal_ref is not None and literal_ref not in literal_names:
            warnings.append(
                f"node {title!r}: STYLE_REF={literal_ref!r} is not defined with TEXT= in "
                f"this map; the node falls back to the default style"
            )

    return errors, warnings


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv[1:]]
    if not paths:
        print(__doc__)
        return 2

    failed = False
    for path in paths:
        errors, warnings = validate(path)
        status = "FAIL" if errors else "OK  "
        print(f"\n[{status}] {path}")
        for message in errors:
            print(f"  error   : {message}")
        for message in warnings:
            print(f"  warning : {message}")
        if not errors:
            print("  theme structure and style values look valid")
        failed |= bool(errors)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
