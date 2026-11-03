<p align="center">
  <a href="README.md">English</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
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

スタジオの研究の基となる生データ：各実行のレシートと出力、および各ファイルを SHA-256 で特定するマニフェスト。**これは公開されており、スタジオの研究はデフォルトでオープンになっているためです。** 何らかの理由で非公開にする必要がある少数のファイルは、プライベートなコンパニオンである rnd-data-private に保存され、非公開ファイルのハッシュはここでは公開されません。

このリポジトリには、データと、`src/` の MIT 読み取り専用パッケージ（`rnd-data`：`ls`、`show`、`where`、`schema`）が含まれています。rnd が書き込みとチェックを行います（`rnd raw ingest`、`rnd raw verify`、`rnd where`）。rnd のインデックスは、このチェックアウトが rnd ライブラリの隣に配置されている場合、または `$RND_DATA` で名前が指定されている場合に、そのマニフェストを読み取ります。リポジトリ自体のスクリプトは `verify.sh` で、2 つのワークフローがあります。`runs/` の下の `.sh` と `.py` のファイルは、実行のレシートであり、データとして保存されます。

[ハンドブック](https://mcp-tool-shop-org.github.io/rnd-data/handbook/) には、マニフェストの各フィールド、非公開ファイルのルール、およびチェックが記載されています。

## ここに何があるか

| パス | 内容 |
|---|---|
| `runs/<id>/manifest.json` | 一回の実行のファイル（スキーマ `rnd-data-run/v1`）：各ファイルのパス、SHA-256、サイズ、ティア、ライセンス、および可視性、およびすべてのコピー |
| `runs/<id>/files/…` | その実行の小さな公開ファイル（256 KB 以下）、git に保存 |
| `store.json` | このリポジトリの外にバイトを保存するストレージ、および各ストレージをマシンがどのように見つけるか |
| `src/rnd_data/` | MIT 読み取り専用の Python パッケージ（`rnd-data`：`ls`、`show`、`where`、`schema`）と、マニフェスト JSON スキーマ |

- **256 KB を超えるファイル**は、コンテンツに基づいて `blobs/<sha256[:2]>/<sha256>` に 1 回だけ保存されます。1 つ以上のファイルを含むすべての実行は、ハッシュで名前が付けられるため、複数のウィンドウで使用されるビルドは 1 回だけ保存されます。
- **次の段階で、Hugging Face データセットとして公開されます。** それまでは、スタジオのバックアップドライブに保存されます。

## 実行 ID

実行 ID は、そのソースフォルダーであり、`/` が `--` として記述されます。たとえば、`receipts--colab--window14b-…-20261019` はパブリッシャーの `receipts/colab/window14b-…-20261019` です。
- **そのファイル。** 実行のファイルは、最も近い `outcome.json` を含むフォルダーの下にあるファイルであり、各再試行（`try1/`）はそれぞれ独自の実行です。
- **実行フォルダー外のファイル**は、Colab の場合はウィンドウフォルダーに、それ以外の場合は最上位フォルダーにグループ化されます。

[rnd](https://github.com/mcp-tool-shop-org/rnd) の実験の `runs[].raw_manifest_id` は、これらの ID の 1 つに名前を付けます。

## 非公開ファイル

ファイルが非公開になるのは、名前付きの理由がある場合のみです。たとえば、シールされたキー、保留中のキー、ブラインドファイル、アイテムテキスト、未承認の計画、非公開プロジェクト、またはスタジオの ID スキャンでフラグが立てられたコンテンツなどです。そのコピーは rnd-data-private にあり、その実行のマニフェストには、それについて次のように記述されています。
- **コンテンツが非公開の場合：** 除外され、マニフェストの `private_files` で理由別にカウントされます。
- **ID のみが非公開の場合：** パスとサイズが `"visibility": "private"`、`"private_why": "identity"`、および `"sha256": null` でリストされます。

非公開ファイルのハッシュは公開されません。短いラベルファイルのハッシュは推測によって一致する可能性があるためです。それ以外はすべて公開されます。

## コピーと検証

ファイルのコピーは、そのマニフェストの `copies` にリストされます。各ストレージのルートは、マシンごとに `store.local.json`（gitignore される）または `$RND_DATA_STORE_<NAME>` を介して見つけることができるため、マシンパスはコミットされません。

すべての公開ファイルの SHA-256 は、その実行のマニフェストに記載されているため、ダウンロードしたコピーは rnd なし、または `rnd raw verify` を使用して検証できます。手動で、リポジトリのルートから（`sha256sum` を備えた任意のプラットフォーム、2 番目のプラットフォームの場合は `jq`）：

```bash
sha256sum runs/<id>/files/<path>      # compare with that file's "sha256" in runs/<id>/manifest.json
jq -r '.copies[] | select(.store == "rnd-data") | "\(.sha256)  \(.location)"' runs/*/manifest.json \
  | sha256sum -c --quiet              # every git copy at once; silent when all match
```

rnd がインストールされている場合、`bash verify.sh` は `rnd raw verify --public-only` を実行します。これは、すべてのプルリクエストで CI が実行する処理です。すべての git コピーを再ハッシュし、公開クローンにないストレージをスキップし、追跡されているファイルが `runs/` の下にあり、マニフェストに名前が付けられていない場合、ハッシュを持つ非公開エントリ、非公開タグ、非公開に見えるファイル名、またはマニフェスト内のマシンパスがある場合に失敗します。リグでは、blob ストレージが構成されている場合、`bash verify.sh --full` は完全な `rnd raw verify` を実行します。

2 つの検証済みのコピーが存在し、復元テストに合格し、ディレクターが承認するまで、スタジオリグから何も削除されません。

## 所有者

- **R&D** は、レイアウトとツールを所有します。
- **パブリッシャー**は、そのレシートを所有し、それらのすべての取り込みを確認します。

## セキュリティと信頼

- **含まれるもの：** 実行マニフェスト、実行の小さな公開ファイル、`store.json`、`src/`、`tests/`、`verify.sh` の MIT 読み取り専用パッケージ、2 つのワークフロー、およびサイト。
- **含まれないもの：** 認証情報、非公開ファイルのバイトまたはそのハッシュ、マシンパス。
- **アクセスするもの：** rnd の取り込み（`rnd raw ingest`）は、すべてのマニフェストと `runs/` の下のすべてのファイルを書き込み、パブリッシャーがそのレシートのすべての取り込みを確認します。CI は、読み取り専用の権限で、すべてのプルリクエストをチェックします。
- **テレメトリは収集または送信されません。** サイトは静的です。

このリポジトリに到達した非公開ファイル、公開された非公開ファイルのハッシュ、または公開ファイル内の ID について報告するには、[SECURITY.md](SECURITY.md) を参照してください。

## ライセンス

rnd-data は、rnd と同様のライセンスで提供されます。
- **データ**は [CC BY 4.0](LICENSE) です。
- **パッケージとスクリプト**（`src/`、`tests/`、`*.sh`、`*.py`）は [MIT](LICENSE-MIT) です。
- **サードパーティのファイル**は、そのマニフェストに記載されているライセンスを保持します。llama.cpp のビルドは MIT です（コミット 620d2225）。

ファイルのマニフェスト `licence` フィールドは、そのファイルに関する最終的な情報です。すべての公開ファイルのマニフェストには、そのライセンスが記載されています。非公開のエントリには `"licence": null` が含まれています。これは、公開されないためです。

## ステータス

維持されており、各取り込みで拡張されています。リリースはありません。各実行は、そのマニフェストで特定され、リポジトリはコミットで特定されます。[CHANGELOG.md](CHANGELOG.md) には、日付ごとに変更がリストされています。
