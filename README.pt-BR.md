<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.md">English</a>
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

Os dados brutos que sustentam a pesquisa do estúdio: os registros e resultados de cada execução, com um manifesto que identifica cada arquivo por
SHA-256. **É público, porque a pesquisa do estúdio é aberta por padrão.** Os poucos arquivos com uma razão específica para
serem privados são armazenados no repositório complementar privado, rnd-data-private, e o hash de nenhum arquivo privado é publicado aqui.

O repositório contém dados, além de seu pacote MIT somente leitura em `src/` (`rnd-data`: `ls`, `show`, `where`, `schema`).
rnd escreve e verifica (`rnd raw ingest`, `rnd raw verify`, `rnd where`). O índice de rnd lê seus manifestos quando este
repositório está ao lado da biblioteca rnd, ou é nomeado por `$RND_DATA`. Os próprios scripts do repositório são `verify.sh` e seus
dois fluxos de trabalho; os arquivos `.sh` e `.py` em `runs/` são registros de execuções, armazenados como dados.

O [manual](https://mcp-tool-shop-org.github.io/rnd-data/handbook/) contém o manifesto, campo a campo, as
regras para arquivos privados e as verificações.

## O que está aqui

| Caminho | O que |
|---|---|
| `runs/<id>/manifest.json` | Os arquivos de uma execução (esquema `rnd-data-run/v1`): o caminho de cada arquivo, SHA-256, tamanho, nível, licença e visibilidade, e cada cópia |
| `runs/<id>/files/…` | Os arquivos públicos pequenos dessa execução (256 KB ou menos), no git |
| `store.json` | Os armazenamentos que contêm bytes fora deste repositório e como uma máquina encontra cada um |
| `src/rnd_data/` | O pacote Python MIT somente leitura (`rnd-data`: `ls`, `show`, `where`, `schema`) e os esquemas JSON do manifesto |

- **Arquivos com mais de 256 KB** são armazenados uma vez, por conteúdo, em `blobs/<sha256[:2]>/<sha256>`. Cada execução que tem um o nomeia
por hash, para que uma construção usada em várias janelas seja armazenada uma vez.
- **Eles se tornam públicos como um conjunto de dados do Hugging Face** na próxima fase. Até então, eles estão no disco de backup do estúdio.

## Um ID de execução

Um ID de execução é sua pasta de origem, com `/` escrito como `--`. Por exemplo, `receipts--colab--window14b-…-20261019` é o
`receipts/colab/window14b-…-20261019` do Publicador.
- **Seus arquivos.** Os arquivos de uma execução são aqueles na pasta mais próxima que contém um `outcome.json`, para que cada nova tentativa
(`try1/`) seja sua própria execução.
- **Arquivos fora de uma pasta de execução** são agrupados em sua pasta de janela (para o Colab) ou em sua pasta principal.

Um `runs[].raw_manifest_id` de um experimento em [rnd](https://github.com/mcp-tool-shop-org/rnd) nomeia um desses IDs.

## Arquivos privados

Um arquivo é privado apenas por uma razão específica: chaves seladas ou retidas, arquivos confidenciais, texto do item, planos não aprovados,
projetos privados ou conteúdo que o scanner de identidade do estúdio sinaliza. Sua cópia está em rnd-data-private, e o manifesto de sua execução diz apenas o seguinte sobre ele:
- **Privado por seu conteúdo:** ele é omitido e contado por razão no `private_files` do manifesto.
- **Privado apenas por identidade:** ele é listado por caminho e tamanho, com `"visibility": "private"`, `"private_why": "identity"` e `"sha256": null`.

O hash de nenhum arquivo privado é publicado, já que o hash de um arquivo de rótulo curto pode ser descoberto por tentativa e erro. Tudo o mais
é público.

## Cópias e verificação

As cópias de um arquivo são listadas no `copies` do manifesto. A raiz de cada armazenamento é encontrada por máquina, por meio de
`store.local.json` (ignorados pelo git) ou `$RND_DATA_STORE_<NAME>`, para que nenhum caminho de máquina seja registrado.

O SHA-256 de cada arquivo público está no manifesto de sua execução, para que uma cópia baixada possa ser verificada sem o rnd ou com
`rnd raw verify`. Manualmente, a partir da raiz do repositório (qualquer plataforma com `sha256sum`; `jq` para o segundo):

```bash
sha256sum runs/<id>/files/<path>      # compare with that file's "sha256" in runs/<id>/manifest.json
jq -r '.copies[] | select(.store == "rnd-data") | "\(.sha256)  \(.location)"' runs/*/manifest.json \
  | sha256sum -c --quiet              # every git copy at once; silent when all match
```

Com o rnd instalado, `bash verify.sh` executa `rnd raw verify --public-only`, como o CI faz em cada solicitação de pull: ele
recalcula o hash de cada cópia do git, ignora os armazenamentos que um clone público não tem e falha em um arquivo rastreado em `runs/`
que nenhum manifesto nomeia, uma entrada privada com um hash, a tag privada, um nome de arquivo de aparência privada ou um caminho de máquina
em um manifesto. No equipamento, onde o armazenamento de blobs está configurado, `bash verify.sh --full` executa o `rnd raw verify` completo.

Nada é excluído do equipamento do estúdio até que existam duas cópias verificadas, um teste de restauração tenha sido aprovado e o Diretor
tenha dado o sinal verde.

## Proprietários

- **P&D** é proprietário do layout e das ferramentas.
- **O Publicador** é proprietário de seus registros e revisa cada ingestão deles.

## Segurança e confiança

- **O que ele contém:** manifestos de execução, os arquivos públicos pequenos das execuções, `store.json`, o pacote MIT somente leitura em
`src/`, `tests/`, `verify.sh`, dois fluxos de trabalho e o site.
- **O que ele nunca contém:** credenciais; os bytes de um arquivo privado ou seu hash; caminhos de máquina.
- **O que o acessa:** a ingestão de rnd (`rnd raw ingest`) grava cada manifesto e cada arquivo em `runs/`, com a
revisão do Publicador de cada ingestão de seus registros. O CI verifica cada solicitação de pull com permissões somente leitura.
- **Nenhuma telemetria** é coletada ou enviada; o site é estático.

Para relatar um arquivo privado que chegou a este repositório, um hash publicado de um arquivo privado ou identidade em um arquivo público, consulte [SECURITY.md](SECURITY.md).

## Licença

rnd-data é licenciado como rnd:
- **Os dados** são [CC BY 4.0](LICENSE).
- **O pacote e os scripts** (`src/`, `tests/`, `*.sh`, `*.py`) são [MIT](LICENSE-MIT).
- **Um arquivo de terceiros** mantém a licença que seu manifesto nomeia. A construção llama.cpp é MIT (commit 620d2225).

O campo `licence` do manifesto de um arquivo é a palavra final para esse arquivo. O manifesto de cada arquivo público nomeia sua licença;
entradas privadas contêm `"licence": null`, porque não são publicadas.

## Status

Mantido e crescendo com cada ingestão. Não há lançamentos: cada execução é identificada por seu manifesto, e o repositório por seu commit. [CHANGELOG.md](CHANGELOG.md) lista as alterações por data.
