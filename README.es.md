<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.md">English</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
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

Los datos sin procesar que respaldan la investigación del estudio: los registros y resultados de cada ejecución, con un manifiesto que identifica cada archivo mediante SHA-256. **Es público, porque la investigación del estudio es abierta por defecto.** Los pocos archivos que tienen una razón específica para ser privados se almacenan en el repositorio complementario privado, rnd-data-private, y el hash de ningún archivo privado se publica aquí.

El repositorio contiene datos, además de su paquete MIT de solo lectura bajo `src/` (`rnd-data`: `ls`, `show`, `where`, `schema`). rnd lo escribe y verifica (`rnd raw ingest`, `rnd raw verify`, `rnd where`). El índice de rnd lee sus manifiestos cuando este clon se encuentra junto a la biblioteca rnd, o se identifica mediante `$RND_DATA`. Los scripts del repositorio son `verify.sh` y sus dos flujos de trabajo; los archivos `.sh` y `.py` bajo `runs/` son registros de ejecuciones, que se conservan como datos.

El [manual](https://mcp-tool-shop-org.github.io/rnd-data/handbook/) contiene el manifiesto, campo por campo, las reglas para archivos privados y las verificaciones.

## Qué hay aquí

| Ruta | Qué |
|---|---|
| `runs/<id>/manifest.json` | Los archivos de una ejecución (esquema `rnd-data-run/v1`): la ruta de cada archivo, SHA-256, tamaño, nivel, licencia y visibilidad, y cada copia. |
| `runs/<id>/files/…` | Los archivos públicos pequeños de esa ejecución (256 KB o menos), en git. |
| `store.json` | Los almacenes que contienen bytes fuera de este repositorio, y cómo una máquina encuentra cada uno. |
| `src/rnd_data/` | El paquete Python MIT de solo lectura (`rnd-data`: `ls`, `show`, `where`, `schema`) y los esquemas JSON del manifiesto. |

- **Los archivos de más de 256 KB** se almacenan una sola vez, por contenido, en `blobs/<sha256[:2]>/<sha256>`. Cada ejecución que tiene uno lo identifica mediante su hash, por lo que una compilación utilizada en varias ventanas se almacena una sola vez.
- **Se publican como un conjunto de datos de Hugging Face** en la siguiente fase. Hasta entonces, se encuentran en la unidad de respaldo del estudio.

## Un ID de ejecución

Un ID de ejecución es su carpeta de origen, con `/` escrito como `--`. Por ejemplo, `receipts--colab--window14b-…-20261019` es el `receipts/colab/window14b-…-20261019` del Publicador.
- **Sus archivos.** Los archivos de una ejecución son aquellos que se encuentran en la carpeta más cercana que contiene un `outcome.json`, por lo que cada reintento (`try1/`) es su propia ejecución.
- **Los archivos fuera de una carpeta de ejecución** se agrupan en su carpeta de ventana (para Colab) o en su carpeta principal.

Un `runs[].raw_manifest_id` de un experimento en [rnd](https://github.com/mcp-tool-shop-org/rnd) identifica uno de estos ID.

## Archivos privados

Un archivo es privado solo por una razón específica: claves selladas o excluidas, archivos confidenciales, texto de elementos, planes no aprobados, proyectos privados o contenido que el escáner de identidad del estudio marca. Su copia se encuentra en rnd-data-private, y el manifiesto de su ejecución indica lo siguiente al respecto:
- **Privado por su contenido:** se omite y se cuenta por razón en el `private_files` del manifiesto.
- **Privado solo por identidad:** se enumera por ruta y tamaño, con `"visibility": "private"`, `"private_why": "identity"` y `"sha256": null`.

El hash de ningún archivo privado se publica, ya que el hash de un archivo de etiqueta corto podría coincidir mediante conjeturas. Todo lo demás es público.

## Copias y verificación

Las copias de un archivo se enumeran en el `copies` de su manifiesto. La raíz de cada almacén se encuentra por máquina, a través de `store.local.json` (ignorada en git) o `$RND_DATA_STORE_<NAME>`, por lo que no se guarda ninguna ruta de máquina.

El SHA-256 de cada archivo público se encuentra en el manifiesto de su ejecución, por lo que se puede verificar una copia descargada sin rnd, o con `rnd raw verify`. Manualmente, desde la raíz del repositorio (cualquier plataforma con `sha256sum`; `jq` para la segunda):

```bash
sha256sum runs/<id>/files/<path>      # compare with that file's "sha256" in runs/<id>/manifest.json
jq -r '.copies[] | select(.store == "rnd-data") | "\(.sha256)  \(.location)"' runs/*/manifest.json \
  | sha256sum -c --quiet              # every git copy at once; silent when all match
```

Con rnd instalado, `bash verify.sh` ejecuta `rnd raw verify --public-only`, como lo hace CI en cada solicitud de extracción: vuelve a calcular el hash de cada copia de git, omite los almacenes que no tiene un clon público y falla en un archivo rastreado bajo `runs/` que no está nombrado en ningún manifiesto, una entrada privada con un hash, la etiqueta privada, un nombre de archivo de aspecto privado o una ruta de máquina en un manifiesto. En el equipo, donde se configura el almacén de blobs, `bash verify.sh --full` ejecuta el `rnd raw verify` completo.

Nada se elimina del equipo del estudio hasta que existen dos copias verificadas, se ha superado una prueba de restauración y el Director ha dado su aprobación.

## Propietarios

- **I+D** es propietario del diseño y las herramientas.
- **El Publicador** es propietario de sus registros y revisa cada incorporación de ellos.

## Seguridad y confianza

- **Qué contiene:** manifiestos de ejecución, los archivos públicos pequeños de las ejecuciones, `store.json`, el paquete MIT de solo lectura bajo `src/`, `tests/`, `verify.sh`, dos flujos de trabajo y el sitio.
- **Qué nunca contiene:** credenciales; los bytes de un archivo privado o su hash; rutas de máquina.
- **Qué lo toca:** la incorporación de rnd (`rnd raw ingest`) escribe cada manifiesto y cada archivo bajo `runs/`, con la revisión del Publicador de cada incorporación de sus registros. CI verifica cada solicitud de extracción con permisos de solo lectura.
- **No se recopilan ni se envían datos de telemetría; el sitio es estático.**

Para informar sobre un archivo privado que llegó a este repositorio, un hash publicado de un archivo privado o identidad en un archivo público, consulte [SECURITY.md](SECURITY.md).

## Licencia

rnd-data tiene la misma licencia que rnd:
- **Los datos** tienen licencia [CC BY 4.0](LICENSE).
- **El paquete y los scripts** (`src/`, `tests/`, `*.sh`, `*.py`) tienen licencia [MIT](LICENSE-MIT).
- **Un archivo de terceros** conserva la licencia que indica su manifiesto. La compilación de llama.cpp tiene licencia MIT (commit 620d2225).

El campo `licence` del manifiesto de un archivo es la última palabra para ese archivo. El manifiesto de cada archivo público indica su licencia; las entradas privadas contienen `"licence": null`, porque no se publican.

## Estado

Se mantiene y crece con cada incorporación. No hay versiones: cada ejecución se identifica por su manifiesto, y el repositorio por su commit. [CHANGELOG.md](CHANGELOG.md) enumera los cambios por fecha.
