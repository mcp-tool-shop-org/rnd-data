<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.md">English</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/rnd-data/readme.png" alt="rnd-data" width="400">
</p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/rnd-data/actions/workflows/ci.yml"><img src="https://github.com/mcp-tool-shop-org/rnd-data/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-CC_BY_4.0-blue.svg" alt="CC BY 4.0 License"></a>
  <a href="https://mcp-tool-shop-org.github.io/rnd-data/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page"></a>
</p>

# rnd-data

工作室研究背后的原始数据：每次运行的记录和输出，以及一个清单文件，它通过 SHA-256 来固定每个文件。**它是公开的，因为工作室的研究默认是开放的。** 少数几个有明确理由需要私有的文件，存储在私有仓库 rnd-data-private 中，并且没有私有文件的哈希值会在此处发布。

该仓库包含数据，以及其 MIT 只读包，位于 `src/` (`rnd-data`: `ls`, `show`, `where`, `schema`)。rnd 会写入和检查这些数据（`rnd raw ingest`, `rnd raw verify`, `rnd where`）。当此检出与 rnd 库并排放置时，或者通过 `$RND_DATA` 命名时，rnd 的索引会读取其清单。该仓库自身的脚本是 `verify.sh`，以及两个工作流程；位于 `runs/` 下的 `.sh` 和 `.py` 文件是运行的记录，作为数据保存。

[手册](https://mcp-tool-shop-org.github.io/rnd-data/handbook/) 包含按字段排列的清单，以及私有文件规则和检查。

## 这里有什么

| 路径 | 内容 |
|---|---|
| `runs/<id>/manifest.json` | 一次运行的文件（模式 `rnd-data-run/v1`）：每个文件的路径、SHA-256、大小、层级、许可证和可见性，以及每个副本。 |
| `runs/<id>/files/…` | 该次运行的小型公共文件（256 KB 或更小），位于 git 中。 |
| `store.json` | 存储在此仓库之外的字节，以及机器如何找到每个字节。 |
| `src/rnd_data/` | MIT 只读 Python 包（`rnd-data`：`ls`、`show`、`where`、`schema`）和清单 JSON 模式。 |

- **大于 256 KB 的文件**，按内容存储一次，位于 `blobs/<sha256[:2]>/<sha256>`。每次运行都通过哈希值来命名它，因此在多个窗口期间构建的文件只存储一次。
- **它们将在下一个阶段作为 Hugging Face 数据集公开发布。** 在此之前，它们存储在工作室的备份驱动器上。

## 运行 ID

运行 ID 是其源文件夹，其中 `/` 写入为 `--`。例如，`receipts--colab--window14b-…-20261019` 是发布者的 `receipts/colab/window14b-…-20261019`。
- **其文件。** 运行的文件是位于最近的包含 `outcome.json` 的文件夹下的文件，因此每次重试（`try1/`）都是其自身的运行。
- **位于运行文件夹之外的文件**，会分组到其窗口文件夹（用于 Colab）或其顶级文件夹下。

实验的 `runs[].raw_manifest_id`，位于 [rnd](https://github.com/mcp-tool-shop-org/rnd) 中，命名了这些 ID 中的一个。

## 私有文件

文件只有在有明确理由的情况下才是私有的：密封或保留的密钥、盲文件、项目文本、未经批准的计划、私有项目，或者工作室的身份扫描标记的内容。其副本位于 rnd-data-private 中，并且其运行的清单仅对此进行说明：
- **因其内容而私有：** 它被排除在外，并且在清单的 `private_files` 中按理由进行计数。
- **仅因身份而私有：** 它按路径和大小列出，并带有 `"visibility": "private"`、`"private_why": "identity"` 和 `"sha256": null`。

没有私有文件的哈希值会被发布，因为简短的标签文件的哈希值可以通过猜测来匹配。其他所有内容都是公开的。

## 副本和验证

文件的副本列在其清单的 `copies` 中。每个存储的根目录都通过 `store.local.json`（git 忽略）或 `$RND_DATA_STORE_<NAME>` 来查找，因此不会提交任何机器路径。

每个公共文件的 SHA-256 位于其运行的清单中，因此可以下载副本并在没有 rnd 的情况下进行检查，或者使用 `rnd raw verify` 进行检查。手动操作，从仓库的根目录开始（任何具有 `sha256sum` 的平台；第二个平台为 `jq`）：

```bash
sha256sum runs/<id>/files/<path>      # compare with that file's "sha256" in runs/<id>/manifest.json
jq -r '.copies[] | select(.store == "rnd-data") | "\(.sha256)  \(.location)"' runs/*/manifest.json \
  | sha256sum -c --quiet              # every git copy at once; silent when all match
```

安装 rnd 后，`bash verify.sh` 运行 `rnd raw verify --public-only`，就像 CI 在每次推送请求中执行的操作一样：它会重新计算每个 git 副本的哈希值，跳过公共克隆中没有的存储，并且如果发现位于 `runs/` 下的已跟踪文件没有在清单中命名，或者存在具有哈希值的私有条目、私有标签、看起来像私有文件的文件名或清单中的机器路径，则会失败。在配置了 blob 存储的机器上，`bash verify.sh --full` 运行完整的 `rnd raw verify`。

在工作室机器上，在存在两个已验证的副本、已通过恢复测试并且主管已批准后，不会删除任何内容。

## 所有者

- **研发部门** 拥有布局和工具。
- **发布者** 拥有其记录，并审核其所有记录的导入。

## 安全性和信任

- **它包含的内容：** 运行清单、运行的小型公共文件、`store.json`、位于 `src/`、`tests/`、`verify.sh` 的 MIT 只读包、两个工作流程和站点。
- **它绝不包含的内容：** 凭据；私有文件的字节或其哈希值；机器路径。
- **访问它的是：** rnd 的导入（`rnd raw ingest`）会写入每个清单和位于 `runs/` 下的每个文件，并且发布者会审核其所有记录的导入。CI 使用只读权限检查每个推送请求。
- **不收集或发送任何遥测数据；该站点是静态的。**

要报告到达此仓库的私有文件、已发布的私有文件的哈希值或公共文件中的身份信息，请参阅 [SECURITY.md](SECURITY.md)。

## 许可证

rnd-data 的许可证与 rnd 相同：
- **数据** 采用 [CC BY 4.0](LICENSE)。
- **包和脚本**（`src/`、`tests/`、`*.sh`、`*.py`）采用 [MIT](LICENSE-MIT)。
- **第三方文件** 采用其清单中指定的许可证。llama.cpp 的构建采用 MIT 许可证（提交 620d2225）。

文件的清单 `licence` 字段是该文件的最终说明。每个公共文件的清单都指定其许可证；私有条目带有 `"licence": null`，因为它们不会被发布。

## 状态

正在维护中，并且随着每次导入而不断发展。没有发布版本：每次运行都通过其清单进行固定，并且仓库通过其提交进行固定。[CHANGELOG.md](CHANGELOG.md) 按日期列出更改。
