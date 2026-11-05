# Themes for Freeplane

[中文](README.md) · English

A small collection of mind-map themes (style templates) for [Freeplane](https://www.freeplane.org),
plus the bits needed to build and check your own.

A Freeplane theme is just an ordinary `.mm` map file — all the styling lives inside it, so no
code and no build step is involved. This repo ships a few ready-to-use themes, a structural
validator, and the gotchas collected while writing them.

![xmind-classic](previews/xmind-classic-demo.png)

## Install

**1. As a template** (recommended)

```
Tools → Open user directory
  └─ templates\              ← create it if missing, drop the .mm in
File → New map from template…
  └─ pick “User templates (*.mm)” in the file type dropdown
```

On Windows the installer's user directory is `%APPDATA%\Freeplane\<version>\templates`;
portable installs use `%USERPROFILE%\.freeplane\<version>\templates`. When in doubt, use the menu.

Or run the helper (Windows, finds the user directory itself):

```powershell
.\tools\install_themes.ps1
```

To make a theme the default for new maps: `Tools → Preferences → Environment → Standard template file`.

**2. Apply to an existing map**

```
Format → Manage Styles → Copy map styles from…      (merge styles)
Format → Manage Styles → Replace map styles by…     (replace everything)
```

**3. Just look at it**: open any file in `demos/` — sample maps that already use the theme.

> ⚠️ `AutomaticEdgeColor` only assigns colours **when a branch is created**. Applying a theme to an
> existing map will not recolour the edges that are already there — create a new branch or set the
> branch colour manually.

## Themes

| File | Look | Notes |
| --- | --- | --- |
| [`themes/xmind-classic.mm`](themes/xmind-classic.mm) | XMind classic | dark central pill, coloured level-1 cards (8-card palette), branch-coloured outlines |
| [`themes/xmind-zen.mm`](themes/xmind-zen.mm) | XMind modern | white canvas, no borders, text + thick coloured curves |
| [`themes/ember-night.mm`](themes/ember-night.mm) | dark | dark canvas, per-level colours, semantic styles (Callout/Todo/Done/Quote) |
| [`themes/ember-day.mm`](themes/ember-day.mm) | light | same family as night |

| xmind-classic | xmind-zen |
| --- | --- |
| ![classic](previews/xmind-classic-demo.png) | ![zen](previews/xmind-zen-demo.png) |

Screenshots are real Freeplane 1.13.4 windows, not mock-ups.

### The 8-card palette (xmind-classic)

Level-1 topics default to “white card + 2 px branch-colour outline”. Applying `色卡1`…`色卡8`
(`card 1`…`card 8`) turns them into solid coloured cards:

| Style | Fill | Text | Contrast on white text |
| --- | --- | --- | --- |
| `色卡1 蓝` | `#4C7FD1` | `#FFFFFF` | 3.99 |
| `色卡2 朱` | `#DF684C` | `#FFFFFF` | 3.38 |
| `色卡3 绿` | `#6FAE5A` | `#FFFFFF` | 2.67 |
| `色卡4 橙` | `#E8A33D` | `#FFFFFF` | 2.16 |
| `色卡5 紫` | `#6C5B9E` | `#FFFFFF` | 5.79 |
| `色卡6 青` | `#2A9D8F` | `#FFFFFF` | 3.32 |
| `色卡7 粉` | `#E06C9F` | `#FFFFFF` | 3.08 |
| `色卡8 灰蓝` | `#55707F` | `#FFFFFF` | 5.24 |

Usage: select a level-1 topic → the “style” dropdown in the toolbar → pick a card.

**Order is the colour.** `AutomaticEdgeColor` hands out branch colours in the order of
`edgeColorConfiguration`, so branch 1 gets `#4C7FD1`, branch 2 `#DF684C`, and so on. Apply the cards
in the same order and every card matches the colour of its own edge. The palette has 8 colours, so
branch 9 falls back to the first colour (`色卡1`), branch 10 to the second, and so on.

15 pt bold counts as WCAG “large text” (threshold 3:1). `色卡4 橙` and `色卡3 绿` are below that and
white text looks a little washed out. To fix it, darken those fills by one step (same hue):
`#E8A33D → #BC7916`, `#6FAE5A → #5D974A`, `#DF684C → #DD6245`, `#2A9D8F → #28988B`, `#E06C9F → #DC5B93`.

## Build your own

A theme is a `.mm` file whose `<hook NAME="MapStyle">` contains a `<map_styles>` tree. The full
attribute list, enum values and pitfalls are in **[docs/style-reference.md](docs/style-reference.md)**
(checked against the Freeplane sources and its bundled templates).

Check your work:

```powershell
python tools\validate_theme.py themes\xmind-classic.mm
```

It verifies the XML structure, the style tree, the three hooks, enum values and colour formats, plus
the two things that fail silently: `TEXT` vs `LOCALIZED_TEXT`, and `STYLE_REF` vs `LOCALIZED_STYLE_REF`.

Regenerate the demo maps:

```powershell
python tools\make_demo.py .
```

## Layout

```
themes/     theme templates (.mm)
demos/      sample maps (.mm) that already use a theme — just open them
previews/   real Freeplane screenshots (.png)
tools/      validate_theme.py, make_demo.py, install_themes.ps1
docs/       style-reference.md
```

## Known limitations

1. Freeplane cannot make a **node fill follow the branch colour** (only border colour / width / dash
   can follow the edge, via `BORDER_*_LIKE_EDGE`), so solid cards are applied by hand — that is the
   only extra step compared to XMind.
2. Edges are always the same width; there is no tapered line.
3. Themes cannot ship icons or stickers — only built-in `BUILTIN` icon names.
4. Themes only affect the mind map rendering, not the editor UI (that is the FlatLaf `.theme.json` layer).

## Compatibility

The `.mm` files use the `freeplane 1.9.8` format; Freeplane 1.11 / 1.12 / 1.13 all read them.
Older versions are untested.

## License

**GPL-2.0** (SPDX: `GPL-2.0-only`), see [LICENSE](LICENSE). Same license as the Freeplane repository,
so a pull request upstream needs no relicensing.

In short: use, modify and redistribute freely (commercial use included), but when you distribute a
modified version it must stay under GPL-2.0 with the source available. Using it privately without
distributing anything does not force you to publish.

Applying a theme to your own map does not change the license of that map — it is your content, the
theme is only the source of the styles it references.

The palette is inspired by XMind's default themes (colour values are not copyrightable); the
structure and attribute names come from Freeplane's open-source implementation.
