# 图标 / Icons

一句话：**节点图标放 `<用户目录>/icons/` 就能用；主题 `.mm` 里带不了图标文件；本仓库另做一个
add-on 把 [Lucide](https://lucide.dev) 全套图标装进那个目录。**

## 三种图标，各归各的

| 你看到的图标 | 实际在哪 | 能不能换 | 怎么换 |
| --- | --- | --- | --- |
| 节点图标（节点左侧那一排） | `<用户目录>/icons/` 里的文件；内置的一组打在 Freeplane 的 jar 里 | 能 | 往目录里放 `.svg`/`.png`，或者装 add-on |
| 主题里的图标 | `.mm` 里只存图标的**名字**，没有图 | 能（换名字） | `<icon BUILTIN="…"/>` |
| 编辑器界面图标（工具栏、菜单） | Freeplane 的 jar 内，属 FlatLaf 皮肤 | 不能 | 得另做 UI 主题 add-on |

这也是为什么「换个主题图标跟着换」做不到：主题是纯数据，包里没有图片。

## 用户图标目录怎么工作

读 `IconStoreFactory` 的源码确认，规则很朴素：

| 规则 | 说明 |
| --- | --- |
| 目录 | `工具 → 打开用户目录` 下的 `icons/`。Windows 安装版是 `%APPDATA%\Freeplane\<版本>\icons` |
| 认什么格式 | 只看 `.svg` 和 `.png`（大小写不敏感），其他文件忽略 |
| 子目录 | **递归扫描**，一个子目录就是一个图标分组；分组图标取组里第一个图标 |
| 图标名 | 相对路径去掉扩展名：`icons/lucide/notifications/check.svg` → 名字 `lucide/notifications/check` |
| 覆盖内置 | 只有**完全同名**才顶掉内置图标（2021 年起用户图标不再整体替换内置那一套） |
| 何时生效 | Freeplane 启动时扫描，加/删文件后要重启 |
| 会不会进导图 | 不会。图标是文件不是数据，发给别人只有名字，图没跟着走 |

引用就是写文件名：

```xml
<node TEXT="发布完成">
  <icon BUILTIN="lucide/notifications/circle-check"/>
</node>
```

## 本仓库的 Lucide 图标包

`addons/lucide-icons/` 是它的源集，Release 里叫 `lucide-icons-<版本>.addon.mm`。

| 项 | 值 |
| --- | --- |
| 图标数 | 2029 个 SVG |
| 分组 | 42 个，即 Lucide 的分类（`files`、`notifications`、`arrows`、`text`…） |
| 装到哪 | `<用户目录>/icons/lucide/<分类>/<名>.svg` |
| 图标名 | `lucide/<分类>/<名>`，如 `lucide/files/folder` |
| Lucide 版本 | 固定提交 `b826f0c5`（2026-11-05） |
| 需要 | Freeplane ≥ 1.11（`freeplaneVersionFrom`） |
| 许可 | Lucide 的 ISC；其中源自 Feather 的图标是 MIT。全文**整篇写进包里**（安装时那个许可确认框显示的就是全文），仓库里另有一份 `addons/lucide-icons/LICENSE-lucide.txt` |

安装：

```
1. 文件 → 打开导图…          (File → Open map…)        选中 lucide-icons-<版本>.addon.mm
2. 工具 → 插件 → 插件安装器   (Tools → Plugins → Add-on installer)
      → 安装 → 确认重启 Freeplane
3. 图标面板 → lucide 分组 → notifications / files / arrows …
```

> **必须先把这个 `.addon.mm` 当成普通导图打开**：安装器读的是「当前这张导图」根节点上的
> `name` / `version` / `author` / `freeplaneVersionFrom`，不会自己弹文件选择框。菜单名按界面
> 语言略有不同（中文「插件安装器」，英文「Add-on installer」，有些版本里挂成「附加组件」），
> 都在「工具」菜单下。

卸载就在附加组件列表里点 Uninstall：包里写了 2029 条 `delete` 规则，逐个删 `icons/lucide/` 下的文件。

## 常用图标在哪

图标名不由我们改，直接沿用 Lucide；分组取的是该图标在 Lucide 元数据里的第一个分类，
所以位置有点随缘 —— 下面这张表是实测的（版本同上）：

| 用途 | 图标名 | 引用值 |
| --- | --- | --- |
| 完成 | `check` | `lucide/notifications/check` |
| 完成（圆） | `circle-check` | `lucide/notifications/circle-check` |
| 警告 | `triangle-exclamation-point` | `lucide/notifications/triangle-exclamation-point` |
| 出错 / 取消 | `x` | `lucide/notifications/x` |
| 待办 | `list-todo` | `lucide/text/list-todo` |
| 清单 | `list-checks` | `lucide/text/list-checks` |
| 文件夹 | `folder` | `lucide/files/folder` |
| 文档 | `file-text` | `lucide/text/file-text` |
| 人 | `user` | `lucide/account/user` |
| 团队 | `users` | `lucide/account/users` |
| 时间 | `clock` | `lucide/time/clock` |
| 日期 | `calendar` | `lucide/time/calendar` |
| 地点 | `map-pin` | `lucide/navigation/map-pin` |
| 重点 | `star` | `lucide/social/star` |
| 想法 | `lightbulb` | `lucide/photography/lightbulb` |
| 说明 | `info` | `lucide/accessibility/info` |
| 搜索 | `search` | `lucide/text/search` |
| 设置 | `settings` | `lucide/account/settings` |
| 权限 | `lock` | `lucide/security/lock` |
| 链接 | `link` | `lucide/text/link` |
| 缺陷 | `bug` | `lucide/development/bug` |
| 删除 | `trash` | `lucide/files/trash` |

找不到某个图标时去 [lucide.dev](https://lucide.dev/icons) 搜名字，图标详情页上的分类就是它在
`lucide/` 下的子目录。注意 Lucide 会改名（老版本的 `alert-triangle` 现在叫
`triangle-exclamation-point`），换 Lucide 版本后名字以新版为准。

## 自己改 / 重建

```powershell
# 下载（或复用 .cache/lucide/<commit>/ 里的缓存）并打包 + 自检
python tools\build_icon_addon.py --version 0.1.0 --out dist

# 只打几个分类
python tools\build_icon_addon.py --version 0.1.0 --out dist --categories notifications,files,arrows

# 离线：用已经下好的源码包
python tools\build_icon_addon.py --version 0.1.0 --out dist --lucide-archive lucide.zip

# 只检查一个现成的 .addon.mm
python tools\build_icon_addon.py --check-only dist\lucide-icons-0.1.0.addon.mm
```

- 图标源、分组、描述文案来自 `addons/lucide-icons/addon.json`，许可文案来自同目录的
  `LICENSE-lucide.txt`（打包时整篇写进 `license` 节点）；脚本 `tools/build_icon_addon.py` 只管打包。
- 换 Lucide 版本：改 `addon.json` 里的 `lucide.commit`（`archive` 里的 `{commit}` 会自动替换），重跑一遍。
  分类跟着 Lucide 走，图标增减也是自动的。
- 打包脚本会做一遍**模拟安装器的自检**：根属性齐全、8 个必备子节点各一份、`description`/`license`
  各只有一个子节点、`translations` 带 `addons.${name}`、base64 zip 能解开、路径都在 `icons/lucide/`、
  每个文件都有对应的卸载规则、SVG 是合法 XML。过不了就非零退出。
- 只是想往自己机器上加几个图标，不用碰这个包：把 svg 丢进 `<用户目录>/icons/<组>/` 重启即可。

## add-on 的格式要求

要自己另写一个 add-on 时，这些是 `installScriptAddOn.groovy`（Freeplane 安装脚本）硬性要求的：

| 位置 | 要求 |
| --- | --- |
| 根节点属性 | `name`、`version`、`author`、`freeplaneVersionFrom` 必填，`freeplaneVersionTo` 可空 |
| 根节点子节点 | `description`、`license`、`translations`、`preferences.xml`、`default.properties`、`scripts`、`zips`、`deinstall` 这 8 个必须有；`images`、`lib`、`changes` 可选 |
| `description` / `license` | 各自**恰好一个**子节点，用它的文本 |
| `translations` | 每个语言节点里要有 `addons.${name}` 属性（`${name}` 保持字面） |
| `zips` | 每个子节点**只能有一个**子节点，其文本是 base64 编码的 zip；解包目标是用户目录，所以包内路径要自带 `icons/…` |
| `deinstall` | 只认 `delete` 属性，`${installationbase}` 会展开成用户目录 |
| base64 | 允许换行，安装器会先去掉所有空白 |

`version` 写成 `v0.1.0` 这种带 `v` 的形式，和 Release 的 tag 对得上。

## 分享与团队

- 别人没装这个 add-on：节点上的图标**会缺**，节点本身还在。
- 想让别人也看到：把 `lucide-icons-<版本>.addon.mm` 发给对方装一次，或者把 `icons/lucide/` 目录拷过去。
- 换主题不会动图标目录，两者互不影响。
