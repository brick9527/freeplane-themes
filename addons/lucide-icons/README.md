# lucide-icons

Lucide 图标的 Freeplane add-on 源集。这个目录里**没有图标文件**——图标在打包时从 Lucide 源码
下载并塞进 `.addon.mm`，那样的产物是几 MB 的二进制，不适合进仓库。

| 文件 | 作用 |
| --- | --- |
| `addon.json` | add-on 元数据：技术名（`lucide-icons`）、界面标题（`Lucide Icons` / `Lucide 图标`）、版本下限、描述模板，以及 pin 住的 Lucide 提交 |
| `LICENSE-lucide.txt` | Lucide 的许可全文（ISC + 源自 Feather 的 MIT 部分），原样拷贝；打包时**整篇**写进产物的 `license` 节点，所以只下载 `.addon.mm` 的人也拿得到全文 |

## 打包

```powershell
python tools\build_icon_addon.py --version 0.1.0 --out dist
```

产物 `dist\lucide-icons-0.1.0.addon.mm`，结构是：

```
根节点（属性 name / version / author / freeplaneVersionFrom）
├── description     一个子节点，文本是 addon.json 里 description 模板展开后的说明
├── changes         v<version> 的变更条目
├── license         一个子节点，Lucide 许可全文（原样取自 LICENSE-lucide.txt）
├── preferences.xml 空
├── default.properties 空
├── translations    en / zh_CN，各带 addons.${name}
├── scripts         空
├── zips/icons      一个子节点，文本是 base64 的 zip：icons/lucide/<分类>/<名>.svg
└── deinstall       每个文件一条 delete 规则
```

脚本跑完会自己解析一遍（模拟 `installScriptAddOn.groovy` 的检查），任何一项不过就非零退出。

## 改什么

- **换图标集版本**：改 `addon.json` 里的 `lucide.commit`。`archive` 里的 `{commit}` 会自动替换，
  分类、图标数、许可都跟着新版本走。
- **只打一部分图标**：构建时加 `--categories notifications,files,arrows`。
- **改描述文案**：直接改 `addon.json`，`{icon_count}`、`{category_count}`、`{lucide_commit}`
  会在打包时替换成真实数字。许可文案不在 `addon.json` 里，改 `LICENSE-lucide.txt`。

### 打包时会改写 svg 的两个地方（都是必须的）

Freeplane 的 kitfox 渲染器（svgSalamander 1.1.4）有两个限制，不改就画不出来：

1. **路径不能紧凑写**：`a2 2 0 012 2v1` 把 arc 的两个 flag 粘在数字里，kitfox 抛
   `Unexpected element while parsing cmd 'a'`，启动建菜单时崩。→ 重写成
   `a 2 2 0 0 1 2 2`，全分隔，几何不变。
2. **样式不能只写在根节点**：Lucide 的 `fill="none"` / `stroke="currentColor"` /
   `stroke-width="2"` 都在根 `<svg>` 上，kitfox 不继承，还把 `currentColor` 当文件路径去
   加载 —— 结果**一个像素都不画**，图标看起来是透明的。→ 把这几条属性内联到每个
   `path` / `circle` 上，颜色写死成 `--color`（默认 `#000000`）。

自检会检查这两条：路径必须是规整形式、文件里不能有 `currentColor`、每个 shape 必须自带
`stroke`。改完这两处后，2029 个图标用 Freeplane 自带的 svgSalamander 逐个渲染验证过，
空白 0、报错 0。

细节和踩过的坑见仓库的 [docs/icons.md](../../docs/icons.md)。
