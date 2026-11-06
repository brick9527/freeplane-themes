# lucide-icons

Lucide 图标的 Freeplane add-on 源集。这个目录里**没有图标文件**——图标在打包时从 Lucide 源码
下载并塞进 `.addon.mm`，那样的产物是几 MB 的二进制，不适合进仓库。

| 文件 | 作用 |
| --- | --- |
| `addon.json` | add-on 元数据：技术名（`lucide-icons`）、界面标题（`Lucide Icons` / `Lucide 图标`）、版本下限、描述与许可文案模板，以及 pin 住的 Lucide 提交 |
| `LICENSE-lucide.txt` | Lucide 的许可全文（ISC + 源自 Feather 的 MIT 部分），原样拷贝，随包分发 |

## 打包

```powershell
python tools\build_icon_addon.py --version 0.1.0 --out dist
```

产物 `dist\lucide-icons-0.1.0.addon.mm`，结构是：

```
根节点（属性 name / version / author / freeplaneVersionFrom）
├── description     一个子节点，文本是 addon.json 里 description 模板展开后的说明
├── changes         v<version> 的变更条目
├── license         一个子节点，许可说明
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
- **改描述/许可文案**：直接改 `addon.json`，`{icon_count}`、`{category_count}`、`{lucide_commit}`
  会在打包时替换成真实数字。

细节和踩过的坑见仓库的 [docs/icons.md](../../docs/icons.md)。
