# Freeplane 脑图主题

中文 · [English](README.en.md)

[![release](https://github.com/brick9527/freeplane-themes/actions/workflows/release.yml/badge.svg)](https://github.com/brick9527/freeplane-themes/actions/workflows/release.yml)
[![latest release](https://img.shields.io/github/v/release/brick9527/freeplane-themes?display_name=tag&sort=semver)](https://github.com/brick9527/freeplane-themes/releases/latest)
[![themes: CC BY 4.0](https://img.shields.io/badge/themes-CC%20BY%204.0-lightgrey)](LICENSE-CC-BY-4.0.txt)

A small collection of mind-map themes (style templates) for [Freeplane](https://www.freeplane.org),
plus the bits needed to build and check your own.

Freeplane 的主题就是一个普通的 `.mm` 模板文件 —— 样式全在里面，不需要写代码、不需要编译。
这个仓库提供几套可直接用的主题、一个结构校验脚本，以及踩坑记录。

![xmind-classic](previews/xmind-classic-demo.png)

## 下载

不用 clone，直接去 [Releases](https://github.com/brick9527/freeplane-themes/releases/latest) 拿包：

| 拿什么 | 用在哪 |
| --- | --- |
| 单个 `*.mm` | 只想要某一套主题，下载后放进 `templates\` |
| `lucide-icons-<版本>.addon.mm` | Lucide 图标包（2029 个图标），装完图标面板多出 `lucide` 分组 |
| `freeplane-themes-<版本>-themes.zip` | 全部主题 + `NOTICE.txt` + 许可，扁平结构，解压后 `.mm` 直接落进 `templates\` |
| `freeplane-themes-<版本>-full.zip` | 整个工程：主题 / 演示图 / 截图 / 文档 / 工具 / 许可 |
| `freeplane-themes-<版本>-source.zip`、`-source.tar.gz` | 该 tag 的源码快照（含 CI 配置） |
| `SHA256SUMS.txt` | 上面每个文件的 SHA-256，`sha256sum -c SHA256SUMS.txt` 校验 |

每个包都带许可全文和署名说明：主题、演示图、截图、文档是 **CC BY 4.0**，脚本是 **GPL-2.0**。

## 安装 / 加载

**1. 装成模板**（推荐）

```
工具 → 打开用户目录            (Tools → Open user directory)
  └─ templates\              ← 没有就新建，把 .mm 放进去
文件 → 从模板新建导图…        (File → New map from template…)
  └─ 文件类型选「用户模板 (*.mm)」
```

Windows 安装版用户目录是 `%APPDATA%\Freeplane\<版本>\templates`，
免安装版是 `%USERPROFILE%\.freeplane\<版本>\templates`。记不住就用菜单打开。

也可以一条命令（自动定位用户目录，Windows）：

```powershell
.\tools\install_themes.ps1
```

想让某套主题成为默认：`工具 → 首选项 → 环境 → 默认模板文件`。

**2. 套到已有的图上**

```
格式 → 管理样式 → 从…中复制导图样式…   (Copy map styles from…)
格式 → 管理样式 → 替换导图样式为…       (Replace map styles by…)
```

**3. 只看效果**：双击 `demos/*.mm`，就是带示例内容的演示图。

> ⚠️ `AutomaticEdgeColor` 只在**新建分支**时上色。用方式 2 套主题时，已有连线不会自动变色，
> 需要新建一个分支或手动给分支设色。

## 主题

| 文件 | 风格 | 说明 |
| --- | --- | --- |
| [`themes/xmind-classic.mm`](themes/xmind-classic.mm) | XMind 经典 | 中央深色胶囊 + 一级彩色卡片（8 色卡）+ 分支色描边 |
| [`themes/xmind-zen.mm`](themes/xmind-zen.mm) | XMind 现代 | 纯白底、无边框，文字 + 粗彩色曲线 |
| [`themes/ember-night.mm`](themes/ember-night.mm) | 深色 | 深底 + 层级配色 + 语义样式（Callout/Todo/Done/Quote） |
| [`themes/ember-day.mm`](themes/ember-day.mm) | 浅色 | 与 night 同色系 |

| xmind-classic | xmind-zen |
| --- | --- |
| ![classic](previews/xmind-classic-demo.png) | ![zen](previews/xmind-zen-demo.png) |
| **ember-night** | **ember-day** |
| ![ember-night](previews/ember-night-demo.png) | ![ember-day](previews/ember-day-demo.png) |

四张都是 Freeplane 1.13.4 实际渲染的窗口截图，对应的源文件在 `demos/` 下，双击即可打开。

### 8 个顺序色卡（xmind-classic）

一级主题默认是「白底 + 2 px 分支色描边」。套上 `色卡1`…`色卡8` 就变成实心彩卡：

| 样式名 | 底色 | 文字 | 白字对比度 |
| --- | --- | --- | --- |
| `色卡1 蓝` | `#4C7FD1` | `#FFFFFF` | 3.99 |
| `色卡2 朱` | `#DF684C` | `#FFFFFF` | 3.38 |
| `色卡3 绿` | `#6FAE5A` | `#FFFFFF` | 2.67 |
| `色卡4 橙` | `#E8A33D` | `#FFFFFF` | 2.16 |
| `色卡5 紫` | `#6C5B9E` | `#FFFFFF` | 5.79 |
| `色卡6 青` | `#2A9D8F` | `#FFFFFF` | 3.32 |
| `色卡7 粉` | `#E06C9F` | `#FFFFFF` | 3.08 |
| `色卡8 灰蓝` | `#55707F` | `#FFFFFF` | 5.24 |

用法：选中一级主题 → 工具栏「样式」下拉 → 选 `色卡N`。

**顺序即颜色**：`AutomaticEdgeColor` 按 `edgeColorConfiguration` 的顺序给新分支上色，
第 1 支拿 `#4C7FD1`、第 2 支 `#DF684C`…… 所以按顺序套色卡，卡片底色和它的连线永远同色。
调色板只有 8 色，第 9 个分支回到第 1 色（`色卡1`），第 10 个 `色卡2`，以此类推。

15pt 粗体属于 WCAG 的「大字号」（门槛 3:1），`色卡4 橙` 和 `色卡3 绿` 低于门槛，白字会略糊。
想达标就把底色压暗一档（同色相）：
`#E8A33D → #BC7916`、`#6FAE5A → #5D974A`、`#DF684C → #DD6245`、`#2A9D8F → #28988B`、`#E06C9F → #DC5B93`。

## 图标

主题本身带不了图标（`.mm` 里只存图标名字）。除了 Freeplane 内置那一套，还可以装本仓库的
**Lucide 图标包**：2029 个 SVG，按 Lucide 的 42 个分类放进 `<用户目录>/icons/lucide/`。

图标全部来自 **[Lucide](https://lucide.dev)**，不是我们画的。上游仓库：
**[lucide-icons/lucide](https://github.com/lucide-icons/lucide)**；构建时 pin 到一个固定提交
（当前 `b826f0c527e1498f5e46f41ca0277ccab144bf31`），只取 `icons/` 下的 svg 和分类 json。

| 项 | 说明 |
| --- | --- |
| 上游项目 | Lucide · https://lucide.dev · https://github.com/lucide-icons/lucide |
| 许可 | ISC（Copyright © Lucide Icons and Contributors）；其中 115 个源自 Feather 的图标为 MIT |
| 我们的改动 | 仅改写法以便 Freeplane 的 kitfox 渲染器能画出来：路径全分隔、样式内联并写死颜色，图形本身未改 |
| 许可全文 | `addons/lucide-icons/LICENSE-lucide.txt`，安装时的许可确认框显示的就是它 |

```
文件 → 打开导图…          选中 lucide-icons-<版本>.addon.mm
工具 → 插件 → 插件安装器   (Tools → Plugins → Add-on installer) → 安装 → 重启 Freeplane
```

装完在图标面板的 `lucide` 分组里挑，引用写 `BUILTIN="lucide/notifications/circle-check"`。
规则、常用图标的路径、怎么自己加图标、怎么重建这个包，都在
**[docs/icons.md](docs/icons.md)**。

> 图标只在本机生效：把带 Lucide 图标的导图发给没装这个包的人，那边图标会缺。

**图标跑到 label 左上角？** 四套主题都在 `<properties>` 里写死了 `show_icons="BESIDE_NODES"`，
图标和文字在同一行。真遇到图标贴在节点左上角，按顺序查三件事：① 用文本编辑器打开那张 `.mm` 搜
`show_icons`，写着 `ABOVE_NODES` 才是这个属性作怪（旧模板/别的主题留下的，文件里已写死的值不会被默认值覆盖），
用 `格式 → 管理样式 → 复制导图样式…` 从主题再套一次即可，Freeplane 复制样式时会一并搬地图级属性；② 写着
`BESIDE_NODES` 的话，问题多半是「字号明显大于 `ICON_SIZE`」—— `BESIDE_NODES` 是顶端对齐而不是垂直居中，
根节点 22 pt 配 14 pt 图标就会显高；③ 再考虑带 `STYLE="bubble"` 的形状节点叠加 `SHAPE_VERTICAL_MARGIN` 的观感。
取值含义和排查过程见 [docs/style-reference.md](docs/style-reference.md#图标摆在文字旁还是上方)。

## 自己做一个

主题 = 一张 `.mm`，里面 `<hook NAME="MapStyle">` 下有 `<map_styles>` 样式树。
完整的属性、枚举值、易错点见 **[docs/style-reference.md](docs/style-reference.md)**（从 Freeplane
源码和官方模板里核对出来的）。

改完用脚本自检：

```powershell
python tools\validate_theme.py themes\xmind-classic.mm
```

它会检查 XML 结构、样式树是否完整、三个 hook 是否齐全、枚举值与颜色格式，
以及最容易静默失效的两处：`TEXT`/`LOCALIZED_TEXT` 与 `STYLE_REF`/`LOCALIZED_STYLE_REF` 的配对。

重新生成演示图：

```powershell
python tools\make_demo.py .
```

## 目录

```
themes/     主题模板（.mm）
demos/      带示例内容的演示图（.mm），双击即可看效果
previews/   演示图的 Freeplane 真实截图（.png）
addons/     图标 add-on 的源集（lucide-icons：元数据 + Lucide 许可全文）
tools/      validate_theme.py 校验 / make_demo.py 生成演示 / build_release.py 打包 / build_icon_addon.py 打图标包 / install_themes.ps1 安装
docs/       style-reference.md 格式速查、icons.md 图标、releasing.md 发版说明
.github/    CI：validate.yml 每次提交校验、release.yml 打 tag 自动发版
```

## 发版

```bash
git tag -a v1.0.0 -m "v1.0.0"
git push origin v1.0.0
```

推上去就完了：CI 先校验每套主题、确认 `demos/` 与 `themes/` 同步，再打包成
各主题独立 `.mm`、`lucide-icons-<版本>.addon.mm`、`-themes.zip`、`-full.zip`、`-source.zip` /
`-source.tar.gz` 和 `SHA256SUMS.txt`，最后创建 Release 并写好发布正文。
同一个 tag 重跑是刷新附件而不是报错。
细节（触发条件、附件清单、回滚）见 [docs/releasing.md](docs/releasing.md)。

## 已知限制

1. Freeplane 的**节点填充色不能跟随分支色**（只有边框的颜色/宽度/线型能跟随 `BORDER_*_LIKE_EDGE`），
   所以实心彩卡需要手动套样式 —— 这是比 XMind 多出来的唯一一步。
2. 连线只有等宽曲线，没有 XMind 那种锥形渐细（tapered line）。
3. 主题不携带图标/贴纸，只能用 `BUILTIN` 图标名；想要更多图标就装 [Lucide 图标包](docs/icons.md)
   （用户图标是文件、存在本机，别人没装就看不到）。
4. 主题只影响 mind map 渲染，不影响编辑器 UI（那是 FlatLaf `.theme.json` 那层）。

## 兼容性

`.mm` 用的是 `freeplane 1.9.8` 格式，Freeplane 1.11 / 1.12 / 1.13 都能读。
更老的版本未测试。

## License

代码和内容分开授权：

| 内容 | 许可 | 全文 |
| --- | --- | --- |
| `tools/`、`.github/` | GPL-2.0（SPDX：`GPL-2.0-only`） | [LICENSE](LICENSE) |
| `themes/`、`demos/`、`previews/`、`docs/` | **CC BY 4.0**（也可按 GPL-2.0 使用，二选一） | [LICENSE-CC-BY-4.0.txt](LICENSE-CC-BY-4.0.txt) |
| `addons/lucide-icons/`（图标本体） | **ISC**（部分源自 Feather 的图标为 MIT），版权归 Lucide | [LICENSE-lucide.txt](addons/lucide-icons/LICENSE-lucide.txt) |

**为什么这样分**：主题是数据文件，不是程序。用 GPL 授权数据文件，会让不少人担心"套了主题我的导图是不是也被
传染了"，而 GPL 本来也不是为这类内容设计的。所以主题、示例图、截图、文档默认走 **CC BY 4.0** —— 署名即可使用，
商用、改色、放进闭源模板都没问题；如果你更习惯 GPL，同一份文件也可以选择按 GPL-2.0 使用。

代码（校验脚本、演示图生成脚本、CI）保持 GPL-2.0，和 Freeplane 主仓库一致，方便回提 PR。

**CC BY 4.0 的唯一硬性要求是署名**：再分发时请保留出处（本仓库链接）和
`Copyright (c) 2026 brick9527`，并注明是否做过修改。

把主题套到你自己的导图上，不会改变导图内容的授权 —— 那是你的作品。

配色参考了 XMind 的默认主题（色值本身不构成版权内容），结构和属性名来自 Freeplane 的开源实现。
