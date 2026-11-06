# Freeplane 脑图主题格式速查

本文所有结论来自 freeplane/freeplane 仓库（分支 `1.13.x`）的源码与随包模板，不是猜测。

- 主题文件：`freeplane/src/external/resources/templates/*.mm`（官方自带的就是主题）
- 样式模型：`freeplane/src/main/java/org/freeplane/features/styles/`
- 枚举：`org.freeplane.features.edge.EdgeStyle`、`org.freeplane.api.Dash`、
  `org.freeplane.features.cloud.CloudShape`、`org.freeplane.api.NodeShape`

---

## 1. 文件骨架

一个主题就是一个普通 `.mm` 思维导图，只是它承载样式定义。最小可用结构：

```xml
<map version="freeplane 1.9.8">
<node LOCALIZED_TEXT="new_mindmap" LOCALIZED_STYLE_REF="AutomaticLayout.level.root"
      FOLDED="false" ID="ID_1" CREATED="1730000000000" MODIFIED="1730000000000">
  <!-- 让 AutomaticLayout.level,* 自动生效；VALUE=ALL 含叶子节点，HEADINGS 只作用于有子节点的节点 -->
  <hook NAME="accessories/plugins/AutomaticLayout.properties" VALUE="ALL"/>
  <font BOLD="true"/>

  <hook NAME="MapStyle" background="#0f1115">
    <properties auto_compact_layout="true" show_note_icons="true"
                edgeColorConfiguration="#8ab4f8ff,#9be3a0ff,..."/>
    <map_styles>
      <stylenode LOCALIZED_TEXT="styles.root_node" STYLE="fork">
        <font SIZE="24"/>
        <stylenode LOCALIZED_TEXT="styles.predefined" POSITION="right">…</stylenode>
        <stylenode LOCALIZED_TEXT="styles.user-defined" POSITION="right">…</stylenode>
        <stylenode LOCALIZED_TEXT="styles.AutomaticLayout" POSITION="right">…</stylenode>
      </stylenode>
    </map_styles>
  </hook>

  <hook NAME="AutomaticEdgeColor" COUNTER="0" RULE="ON_BRANCH_CREATION"/>
</node>
</map>
```

三个 `<hook>` 各管一件事：

| hook | 作用 | 不加会怎样 |
| --- | --- | --- |
| `MapStyle` | 画布背景、`<properties>`、整棵样式树 | 没有主题 |
| `accessories/plugins/AutomaticLayout.properties` | 层级样式自动生效 | `AutomaticLayout.level,*` 只存在于样式编辑器里，不会自动套用 |
| `AutomaticEdgeColor` | 按分支自动分配边色 | 所有边同色（默认边色） |

`AutomaticEdgeColor` 的 `RULE="ON_BRANCH_CREATION"` 只在**新建分支那一刻**上色：
打开旧文件、或用「替换导图样式」套主题，已有连线不会重新上色。
所以主题里依赖边色的效果（`BORDER_COLOR_LIKE_EDGE`、分支配色）在旧图上要等新分支出现才显现，
或者手动给分支设一次颜色。

---

## 2. 样式树：三个分支

```
styles.root_node
├── styles.predefined        系统预定义样式，LOCALIZED_TEXT 用固定 key
├── styles.user-defined      自定义样式，自定义名字必须用 TEXT="名字"
└── styles.AutomaticLayout   层级样式 AutomaticLayout.level.root /
                             AutomaticLayout.level,1 … level,11
```

### `styles.predefined` 里值得改的 key

| key | 用途 |
| --- | --- |
| `default` | 基础层，所有节点先套它 |
| `defaultstyle.details` | 节点详情文字 |
| `defaultstyle.attributes` | 属性表格文字 |
| `defaultstyle.note` | 便签（可设底色，让它像一张便利贴） |
| `defaultstyle.selection` | 选中节点的高亮 |
| `defaultstyle.floating` | 浮动节点（常用 `hide_edge` + `cloud`） |
| `defaultstyle.tags` | 标签文字 |

### `styles.user-defined` 的命名规则（易错点）

- **预定义样式**用 `LOCALIZED_TEXT="styles.important"`：
  这样才会覆盖 Freeplane 自带的 Important（工具栏里那个星标样式）。
  其它内置 key：`styles.topic`、`styles.subtopic`、`styles.subsubtopic`、
  `styles.flower`、`styles.connection`。
- **自定义样式必须用 `TEXT="Callout"`**：
  `LOCALIZED_TEXT` 会去翻译表里查 key（`ResourceBundles.getResourceString`），
  查不到会返回 `"[Callout]"` 并在日志里报 missing key。
  `TEXT` 走 `StyleFactory.create(String)` → `StyleString`，是字面量，显示什么就是什么。

验证过的源码位置：`features/text/NodeTextBuilder.java` 第 143-160 行。

### 引用样式：`STYLE_REF` 与 `LOCALIZED_STYLE_REF` 不能混用

节点上用哪个属性，取决于目标样式当初是用什么定义的 —— 两边必须"同一种对象"才匹配得上：

| 样式的定义 | 节点上的引用 | 读取后是 |
| --- | --- | --- |
| `LOCALIZED_TEXT="styles.important"`（翻译 key） | `LOCALIZED_STYLE_REF="styles.important"` | `StyleTranslatedObject` |
| `TEXT="Tag"`（自定义字面量） | `STYLE_REF="Tag"` | `StyleString` |

写错不会报错，只是**静默失效**、节点退回默认样式：

```xml
<!-- 有效：Tag 是用 TEXT="Tag" 定义的自定义样式 -->
<node TEXT="技术方案" STYLE_REF="Tag"/>

<!-- 无效：LOCALIZED_STYLE_REF 会构造 StyleTranslatedObject，和 StyleString 不相等 -->
<node TEXT="技术方案" LOCALIZED_STYLE_REF="Tag"/>
```

源码：`features/styles/LogicalStyleController.java` 第 201-212 行（读取）、
第 226-233 行（写出时按对象类型自动选 `LOCALIZED_STYLE_REF` 或 `STYLE_REF`）。
`tools/validate_theme.py` 会检查这个错配。

### 层级样式

`AutomaticLayoutController` 按节点深度取 `AutomaticLayout.level,<depth>`，
深度 0 取 `AutomaticLayout.level.root`；**只有样式节点存在时才生效**，
所以 `level,1` 到 `level,10` 都写出来最稳。

---

## 3. `<stylenode>` 属性

通用格式：`长度 = "12 pt" / "3 px" / "6 cm"`，颜色 `#RRGGBB`（背景可 `#RRGGBBAA`）。

| 属性 | 含义 | 取值 |
| --- | --- | --- |
| `TEXT` / `LOCALIZED_TEXT` | 样式名 | 见上文规则 |
| `STYLE` | 节点形状 | `fork` `bubble` `oval` `rectangle` `wide_hexagon` `narrow_hexagon` `as_parent` `combined` |
| `COLOR` | 文字颜色 | `#RRGGBB` |
| `BACKGROUND_COLOR` | 节点填充 | `#RRGGBB` |
| `TEXT_ALIGN` | 文字对齐 | `LEFT` `CENTER` `RIGHT` |
| `BORDER_WIDTH` | 边框宽度 | `1 px`、`1.9 px`… |
| `BORDER_COLOR` | 边框颜色 | `#RRGGBB` |
| `BORDER_DASH` | 边框线型 | 同 Dash 枚举 |
| `BORDER_*_LIKE_EDGE` | 边框宽度/颜色/线型跟随连线 | `true` / `false` |
| `SHAPE_HORIZONTAL_MARGIN` / `SHAPE_VERTICAL_MARGIN` | 形状内边距 | `8 pt` |
| `MIN_WIDTH` / `MAX_WIDTH` | 形状最小/最大宽度 | `3 cm`、`120 pt` |
| `UNIFORM_SHAPE` | 同级节点同宽 | `true` / `false` |
| `VGAP_QUANTITY` / `HGAP_QUANTITY` | 子节点垂直/水平间距 | `3 pt` |
| `ICON_SIZE` | 图标大小 | `12 pt` |
| `POSITION` | 分支位置 | `right` `left` `bottom_or_right` |
| `FORMAT_AS_HYPERLINK`、`NUMBERED`、`TEXT_SHORTENED`、`FORMAT` | 各种开关 | `true` / `false` |

子元素：

| 元素 | 属性 |
| --- | --- |
| `<font>` | `NAME` `SIZE` `BOLD` `ITALIC` `STRIKETHROUGH` |
| `<edge>` | `STYLE` `COLOR` `WIDTH` `DASH` |
| `<cloud>` | `COLOR` `SHAPE` |
| `<icon>` | `BUILTIN="yes|help|idea|clock2|button_ok|messagebox_warning|password…"` |
| `<arrowlink>` | 连接线模板：`SHAPE` `COLOR` `WIDTH` `TRANSPARENCY` `DASH` `DESTINATION`（= 本样式自己的 ID） |
| `<richcontent>` | `TYPE="NOTE"` or `"DETAILS"`、`CONTENT-TYPE="plain/auto"` |

---

## 4. 枚举值

| 枚举 | 值 |
| --- | --- |
| 节点形状 `STYLE` | `fork` `bubble` `oval` `rectangle` `wide_hexagon` `narrow_hexagon` `as_parent` `combined` |
| 连线 `<edge STYLE>` | `bezier` `linear` `sharp_bezier` `sharp_linear` `horizontal` `hide_edge` `summary` |
| 虚线 `DASH` | `SOLID` `CLOSE_DOTS` `DASHES` `DISTANT_DOTS` `DOTS_AND_DASHES` |
| 云 `<cloud SHAPE>` | `ARC` `STAR` `RECT` `ROUND_RECT` |
| 箭头 `<arrowlink SHAPE>` | `LINEAR_PATH` `CUBIC_CURVE` |

旧图里的 `circle`、`invisible` 是历史值，Freeplane 读取时**静默忽略**（不会报错，但也不会生效）。

### 只对 `<node>` 生效、写在 `<stylenode>` 上会被忽略的属性

`LocationBuilder` 给 `stylenode` 只注册了 `VGAP` / `VGAP_QUANTITY` / `COMMON_HGAP_QUANTITY`：

| 想设置 | `stylenode` 上要写 | 无效写法 |
| --- | --- | --- |
| 子节点水平间距 | `COMMON_HGAP_QUANTITY` | `HGAP_QUANTITY` / `HGAP` |
| 子节点垂直间距 | `VGAP_QUANTITY` | — |

官方模板里出现的 `HGAP_QUANTITY` 都在 `<node>` 上，照抄到 `<stylenode>` 里不会有任何效果。

---

## 5. `<hook NAME="MapStyle">` 与 `<properties>`

`MapStyle` 自身可以带：`background`、`background_alpha`、`zoom`、`max_node_width`、`layout`。

`<properties>` 里是地图级属性，写主题时常用的：

| 属性 | 作用 |
| --- | --- |
| `edgeColorConfiguration` | 自动边色调色板，逗号分隔，**每项 `#RRGGBBAA`**，官方模板给 12 色 |
| `auto_compact_layout` | 自动紧凑布局 |
| `show_note_icons` / `show_icon_for_attributes` | 便签/属性图标 |
| `show_icons` | 图标摆放：`BESIDE_NODES`（和文字同一行）`ABOVE_NODES`（堆在文字上方）`HIDE`。详见下面「图标摆在文字旁还是上方」 |
| `fit_to_viewport` | 打开时自适应 |
| `show_tags` / `showTagCategories` | 标签显示 |

### 图标摆在文字旁还是上方

`show_icons` 是**地图级属性**，不是样式属性 —— 写进 `<stylenode>` 里没有任何效果，只认 `<properties>`。

它由 `MapStyle.iconLocation(map)` 读取（`org.freeplane.view.swing.map.IconLocation`，只有三个枚举值），
底层是 `MapStyleModel.getEnumProperty("show_icons", BESIDE_NODES)`：**文件里没写时回落到 `BESIDE_NODES`**。

| 值 | 渲染 | 典型现象 |
| --- | --- | --- |
| `BESIDE_NODES` | 图标在文字左侧；`MainView.setVerticalTextPosition(TOP)`，**图标顶端对齐文字行顶端** | 图标和文字在同一行，XMind 那种排法；字号远大于图标时图标会显得偏高 |
| `ABOVE_NODES` | `MainView.setVerticalTextPosition(BOTTOM)`，**文字底端对齐图标底端**，图标整体抬到文字上方 | 图标贴在节点/label 的**左上角**，文字被压到下一行 |
| `HIDE` | 不画图标（数据还在，只是不显示） | 画布上完全看不到图标 |

「加了图标却偏到 label 左上角」按下面三步查，不要一上来就怪 `show_icons`：

1. **看这张图自己的 `<properties>`**：用文本编辑器打开 `.mm` 搜 `show_icons`。写着 `ABOVE_NODES` 就是它，
   换成 `BESIDE_NODES`（或直接重新套一次主题）即可；写着 `BESIDE_NODES` 则不是这个原因，继续往下。
2. **看字号和图标尺寸**：`BESIDE_NODES` 是「顶端对齐」，不是垂直居中。某个层级的字号明显大于
   样式里的 `ICON_SIZE` 时（例如根节点 22 pt 配 14 pt 图标），图标会被顶到文字行顶部，看起来就像
   「跑到左上角」。给该层级单独写一个更大的 `ICON_SIZE`，或把字号调小，就能压回视觉中线。
3. **看是不是带形状（`STYLE="bubble"`）的节点**：形状节点有 `SHAPE_VERTICAL_MARGIN`，文字在色块里居中，
   图标仍按标签行顶对齐，叠加起来更容易显得"浮"在左上角。对这类节点，要么调 `ICON_SIZE`，
   要么把这一层换成不带 `STYLE="bubble"` 的样式。

文件里没写 `show_icons` 时 Freeplane 用默认 `BESIDE_NODES`（`MyXmlReader` 还会按首选项里的布尔 `show_icons`
写死成 `BESIDE_NODES` 或 `HIDE`，**从不写 `ABOVE_NODES`**），所以只有从别处（别的主题、官方模板、早期版本）
沿用了这个值，图里才会出现 `ABOVE_NODES`；**已经写进去的值不会被"默认值"覆盖**。

本仓库四套主题都在 `<properties>` 里显式写了 `show_icons="BESIDE_NODES"`，免得渲染结果取决于
用户所用模板的残留值。要让一张已有导图也跟着变，用 `格式 → 管理样式 → 复制导图样式…`：
Freeplane 的 `StyleExchange` 会把源导图的**非样式属性**搬过来（只保留目标图自己的
`edgeColorConfiguration`），`show_icons` 就在其中。改完 `tools/validate_theme.py` 会检查取值合法性，
没写这个属性时给一条 warning。

---

## 6. 条件样式（进阶）

`<conditional_styles>` 与 `<map_styles>` 同级，条件用的是过滤器那套条件节点：

```xml
<conditional_styles>
  <conditional_style ACTIVE="true" LOCALIZED_STYLE_REF="styles.important">
    <node_level_condition VALUE="2" IGNORE_CASE="true" COMPARATION_RESULT="0" SUCCEED="true"/>
  </conditional_style>
  <conditional_style ACTIVE="true" TEXT="Quote">
    <node_periodic_level_condition PERIOD="2" REMAINDER="1"/>
  </conditional_style>
</conditional_styles>
```

可用的条件元素取决于过滤器条件控制器（层级、周期层级、文本包含、属性、标签、图标…）。
官方 `conceptMap.mm` 就是这种写法。

---

## 7. 样式叠加顺序

Freeplane 的样式是分层叠加的，后面覆盖前面（官方文档 *Styles* 一节）：

1. 字符/词级格式
2. 节点单独设置的格式
3. 显式指定的样式
4. 节点条件样式
5. 地图条件样式
6. 自动边色（分支/层级/列）
7. 自动层级样式（`AutomaticLayout.level,*`）
8. `default` 样式

写主题时记住：只想改"默认观感"就改 `default`；想按深度区分就改 level 样式；
想按语义区分（重要、待办、结论）就定义 user-defined 样式。

---

## 8. 主题的分发

1. **直接放模板目录**（最简单，零成本）
   - 用户模板：`<用户目录>/templates/`（菜单 Tools → Open user directory）
   - 系统模板：`<安装目录>/resources/templates/`
   - 两者都由 `TemplateManager` 扫描，`File → New map from template…` 可见
2. **设为默认模板**：Tools → Preferences → Environment → *Standard template file*
3. **打包成 add-on**：`AddOnType` 只有 `SCRIPT` / `PLUGIN`，主题通过
   `installScriptAddOn.groovy` 落盘（该类注释写明 "themes and script collections"），
   可带 `deinstall` 规则；适合对外发布，不适合本地迭代。
4. **贡献回上游**：把 `.mm`（+ 同名 `.svg` 预览）放进
   `freeplane/src/external/resources/templates/` 提 PR。

---

## 9. 应用外观（另一层，可选）

界面本身的配色不走 `.mm`，走 FlatLaf 的 IntelliJ 主题：

- 资源：`freeplane/src/editor/resources/laf/*.theme.json`（自带 Atom One Dark Contrast、SolarizedLight）
- 加载：`org.freeplane.core.ui.flatlaf.CustomThemeLaf extends IntelliJTheme.ThemeLaf`
- 偏好：`lookandfeel` 默认 `com.formdev.flatlaf.FlatIntelliJLaf`

所以一套"完整主题"= 深色 `.mm`（脑图配色）+ 同名 `.theme.json`（界面配色），
两者可以分开交付。
