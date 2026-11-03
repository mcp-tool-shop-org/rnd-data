<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.md">English</a> | <a href="README.pt-BR.md">Português (BR)</a>
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

I dati grezzi alla base della ricerca dello studio: le ricevute e i risultati di ogni esecuzione, con un file manifest che identifica ogni file tramite SHA-256. **È pubblico, perché la ricerca dello studio è aperta per impostazione predefinita.** I pochi file che hanno una ragione specifica per essere privati sono conservati nel repository complementare privato, rnd-data-private, e l'hash di nessun file privato viene pubblicato qui.

Il repository contiene i dati, oltre al pacchetto MIT in sola lettura sotto `src/` (`rnd-data`: `ls`, `show`, `where`, `schema`). rnd li scrive e li verifica (`rnd raw ingest`, `rnd raw verify`, `rnd where`). L'indice di rnd legge i suoi file manifest quando questa copia è affiancata alla libreria rnd, oppure quando è identificata da `$RND_DATA`. Gli script del repository sono `verify.sh` e i suoi due workflow; i file `.sh` e `.py` sotto `runs/` sono le ricevute delle esecuzioni, conservate come dati.

Il [manuale](https://mcp-tool-shop-org.github.io/rnd-data/handbook/) contiene il file manifest, campo per campo, le regole per i file privati e le verifiche.

## Cosa c'è qui

| Percorso | Cosa |
|---|---|
| `runs/<id>/manifest.json` | I file di una singola esecuzione (schema `rnd-data-run/v1`): il percorso di ogni file, SHA-256, dimensione, livello, licenza e visibilità, e ogni copia. |
| `runs/<id>/files/…` | I piccoli file pubblici di quella esecuzione (256 KB o meno), in git. |
| `store.json` | Gli archivi che contengono i byte al di fuori di questo repository e il modo in cui una macchina li trova. |
| `src/rnd_data/` | Il pacchetto Python MIT in sola lettura (`rnd-data`: `ls`, `show`, `where`, `schema`) e gli schemi JSON del file manifest. |

- **I file di dimensioni superiori a 256 KB** vengono archiviati una sola volta, in base al contenuto, all'indirizzo `blobs/<sha256[:2]>/<sha256>`. Ogni esecuzione che ne ha uno lo identifica tramite hash, in modo che una build utilizzata in più finestre venga archiviata una sola volta.
- **Vengono resi pubblici come set di dati di Hugging Face** nella fase successiva. Fino ad allora, si trovano sull'unità di backup dello studio.

## Un ID di esecuzione

Un ID di esecuzione è la sua cartella di origine, con `/` scritto come `--`. Ad esempio, `receipts--colab--window14b-…-20261019` è il `receipts/colab/window14b-…-20261019` dell'editore.
- **I suoi file.** I file di un'esecuzione sono quelli contenuti nella cartella più vicina che contiene un `outcome.json`, quindi ogni tentativo (`try1/`) è una sua esecuzione.
- **I file al di fuori di una cartella di esecuzione** sono raggruppati nella loro cartella di finestra (per Colab) o nella loro cartella principale.

Un `runs[].raw_manifest_id` di un esperimento in [rnd](https://github.com/mcp-tool-shop-org/rnd) identifica uno di questi ID.

## File privati

Un file è privato solo per una ragione specifica: chiavi sigillate o escluse, file anonimi, testo degli elementi, piani non approvati, progetti privati o contenuti contrassegnati dalla scansione dell'identità dello studio. La sua copia si trova in rnd-data-private e il file manifest della sua esecuzione indica solo questo:
- **Privato per il suo contenuto:** viene escluso e conteggiato in base alla ragione nel `private_files` del file manifest.
- **Privato solo per l'identità:** viene elencato per percorso e dimensione, con `"visibility": "private"`, `"private_why": "identity"` e `"sha256": null`.

L'hash di nessun file privato viene pubblicato, poiché l'hash di un file di etichetta breve potrebbe essere individuato tramite tentativi. Tutto il resto è pubblico.

## Copie e verifica

Le copie di un file sono elencate nel `copies` del suo file manifest. La radice di ogni archivio viene individuata per macchina tramite `store.local.json` (ignorato da git) o `$RND_DATA_STORE_<NAME>`, in modo che nessun percorso di macchina venga registrato.

L'SHA-256 di ogni file pubblico è presente nel file manifest della sua esecuzione, in modo che una copia scaricata possa essere verificata senza rnd o con `rnd raw verify`. Manualmente, dalla radice del repository (qualsiasi piattaforma con `sha256sum`; `jq` per la seconda):

```bash
sha256sum runs/<id>/files/<path>      # compare with that file's "sha256" in runs/<id>/manifest.json
jq -r '.copies[] | select(.store == "rnd-data") | "\(.sha256)  \(.location)"' runs/*/manifest.json \
  | sha256sum -c --quiet              # every git copy at once; silent when all match
```

Con rnd installato, `bash verify.sh` esegue `rnd raw verify --public-only`, come fa CI per ogni richiesta di pull: ricalcola l'hash di ogni copia git, salta gli archivi che una copia pubblica non ha e fallisce per un file tracciato sotto `runs/` che nessun file manifest identifica, una voce privata con un hash, il tag privato, un nome di file dall'aspetto privato o un percorso di macchina in un file manifest. Sulla macchina di test, dove l'archivio di blob è configurato, `bash verify.sh --full` esegue l'intero `rnd raw verify`.

Niente viene eliminato dalla macchina di test dello studio finché non esistono due copie verificate, è stato superato un test di ripristino e il direttore ha dato il via libera.

## Proprietari

- **R&D** è proprietaria del layout e degli strumenti.
- **L'editore** è proprietario delle sue ricevute e controlla ogni importazione di esse.

## Sicurezza e affidabilità

- **Cosa contiene:** file manifest delle esecuzioni, i piccoli file pubblici delle esecuzioni, `store.json`, il pacchetto MIT in sola lettura sotto `src/`, `tests/`, `verify.sh`, due workflow e il sito.
- **Cosa non contiene mai:** credenziali; i byte di un file privato o il suo hash; percorsi di macchina.
- **Cosa lo tocca:** l'importazione di rnd (`rnd raw ingest`) scrive ogni file manifest e ogni file sotto `runs/`, con la revisione dell'editore di ogni importazione delle sue ricevute. CI controlla ogni richiesta di pull con autorizzazioni in sola lettura.
- **Non vengono raccolti o inviati dati di telemetria; il sito è statico.**

Per segnalare un file privato che ha raggiunto questo repository, un hash pubblicato di un file privato o un'identità in un file pubblico, vedere [SECURITY.md](SECURITY.md).

## Licenza

rnd-data è concesso in licenza come rnd:
- **I dati** sono [CC BY 4.0](LICENSE).
- **Il pacchetto e gli script** (`src/`, `tests/`, `*.sh`, `*.py`) sono [MIT](LICENSE-MIT).
- **Un file di terze parti** mantiene la licenza indicata nel suo file manifest. La build di llama.cpp è MIT (commit 620d2225).

Il campo `licence` del file manifest di un file è la parola finale per quel file. Il file manifest di ogni file pubblico indica la sua licenza; le voci private contengono `"licence": null`, perché non vengono pubblicate.

## Stato

Mantenuto e in continua crescita con ogni importazione. Non ci sono versioni: ogni esecuzione è identificata dal suo file manifest e il repository dal suo commit. [CHANGELOG.md](CHANGELOG.md) elenca le modifiche per data.
