# 发版 / Releasing

一句话：**打一个 semver tag 推上去，CI 打包并发布 Release。**

```bash
git tag -a v1.2.3 -m "v1.2.3"
git push origin v1.2.3
```

工作流在 [`.github/workflows/release.yml`](../.github/workflows/release.yml)，
打包逻辑在同仓库的 [`tools/build_release.py`](../tools/build_release.py)。

## 触发方式

| 方式 | 行为 |
| --- | --- |
| push 一个 semver tag（`v1.2.3`、`1.2.3`、`v1.2.3-rc.1`） | 校验 → 打包 → 创建 / 刷新 Release |
| push 一个非 semver tag（如 `backup-0925`） | 跑一遍、置绿、**不产生 Release**，在日志里留一条 notice |
| Actions → release → Run workflow（填已有 tag，`publish` 打开） | 重新发布该 tag（附件覆盖，正文重写） |
| Actions → release → Run workflow（`publish` 关闭） | 只打包，产物留在本次运行的 `release-assets` artifact 里 |

`v` 前缀可省，`v1.2.3` 与 `1.2.3` 等价，产物里的版本号统一写成 `1.2.3`。
版本号带 `-` 后缀（`1.2.3-rc.1`）会发成 **pre-release**，不会盖掉 latest。

## 发布前自动挡的三道关

1. tag 必须是 semver——不是就直接不发布（不是报错刷红）；
2. `tools/validate_theme.py` 对 `themes/*.mm` 和 `demos/*.mm` 全通过；
3. `demos/` 与 `themes/` 同步——`python tools/make_demo.py .` 之后 `git diff` 必须为空；
4. 图标 add-on 打包后自检通过（模拟 `installScriptAddOn.groovy` 的解析，见下面的说明）。

任何一道不过，Release 不会创建。

## 附件清单

| 附件 | 内容 | 给谁 |
| --- | --- | --- |
| `<theme>.mm` | 每套主题一个独立文件 | 只想要某一套的人，下载即用 |
| `lucide-icons-<ver>.addon.mm` | Lucide 图标包（2029 个图标装进 `icons/lucide/`） | 想在导图里用更多图标的人 |
| `freeplane-themes-<ver>-themes.zip` | 全部 `.mm` + `NOTICE.txt` + `LICENSE` + `LICENSE-CC-BY-4.0.txt` + `README.md`，扁平结构 | 想一次装进 `templates\` 的人 |
| `freeplane-themes-<ver>-full.zip` | 完整工程：主题 / 演示图 / 预览图 / 文档 / 工具 / 许可，统一在 `freeplane-themes-<ver>/` 下 | 想读源码、自己改的人 |
| `freeplane-themes-<ver>-source.zip` | `git archive` 导出的该 tag 快照（含 `.github/`） | 归档、发行版打包 |
| `freeplane-themes-<ver>-source.tar.gz` | 同上，tar 格式 | Linux / 脚本消费 |
| `SHA256SUMS.txt` | 上面每个文件的 SHA-256，GNU `sha256sum` 格式 | 校验 |
| `Source code (zip/tar.gz)` | GitHub 对每个 Release 自动附带的源码快照 | 顺手的存档 |

发布正文 `release-notes.md` 由脚本生成：下载表、主题表、安装步骤、自上个 tag 起的提交列表、
许可说明，结尾附英文摘要。它不会作为附件上传。

## 幂等与重跑

同一个 tag 再跑一次不会失败：已存在 Release 时改为 `gh release upload --clobber` + `gh release edit`
重写正文，附件始终与 tag 一致。第二次跑不会产生重复的附件。

包内写的是固定时间戳（`git archive` 用提交时间），所以同一个 tag 重跑字节一致，
`SHA256SUMS.txt` 也不会变。

## 本地复现

```bash
python tools/build_release.py --tag v1.2.3 --out dist
```

- 产物落 `dist/`（已 gitignore），发布正文落 `release-notes.md`（同样 gitignore）；
- 只想知道 tag 能不能发：`python tools/build_release.py --tag v1.2.3 --parse-only`；
- 只重打图标包：`python tools/build_icon_addon.py --version 1.2.3 --out dist`
  （默认从 `addons/lucide-icons/addon.json` 里 pin 的 Lucide 提交下载，缓存在 `.cache/lucide/`；
  离线时加 `--lucide-archive <lucide.zip>`）；
- 重新打包会先清掉 `dist/` 里上一版留下的 `*.mm` / `*.zip` / `*.tar.gz` / `SHA256SUMS.txt`，
  避免把旧版本混进附件。

## 需要知道的几件事

- **附件名不要加空格**：GitHub 会把空格改成点号，正文里写的名字就对不上了。
- **删 tag 不会删 Release**：`git push origin :refs/tags/v1.2.3` 之后 Release 还在，
  需要去 Releases 页面删，或 `gh release delete v1.2.3`。
- **`latest` 标记**：GitHub 默认把最新发布的非 pre-release 设为 latest，不需要额外配置。
- **图标 add-on 是打包时现做的**：源头是 `addons/lucide-icons/addon.json` 和
  `tools/build_icon_addon.py`，Lucide 版本 pin 在 `addon.json` 的 `lucide.commit` 里。
  CI 用 `actions/cache` 缓存 `.cache/lucide/<commit>/`，缓存没命中会从 codeload 下约 7 MB 的源码包。
  「图标名带分类、文件名带 Lucide 版本」这两件事全自动，不用手工维护清单。
- **换 Lucide 版本要单独提交**：改 `addon.json` 里的 commit 再打 tag，这样两个 tag 之间图标集是稳定的。
- **新增主题时**：在 `tools/build_release.py` 的 `THEME_DESCRIPTIONS` 里补一行，
  否则发布正文里那套主题只显示「自定义主题」（脚本会在日志里 warning，不阻断发布）。
- **token 权限**：publish 任务单独申请 `contents: write`，build 任务只有 `contents: read`；
  用的是仓库自带的 `GITHUB_TOKEN`，不需要额外 secret。
- **fork 上不发布**：在别人的 fork 里打 tag 也会尝试建 Release（用 fork 自己的 token），
  不想发就别推送 tag。

## 回滚

```bash
gh release delete v1.2.3 --yes     # 删 Release（tag 还在）
git push origin :refs/tags/v1.2.3  # 删远端 tag
```

顺序反过来更安全：先删 Release，确认没人下载了再删 tag。
