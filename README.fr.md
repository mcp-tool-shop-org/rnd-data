<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.md">English</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
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

Les données brutes qui sous-tendent la recherche du studio : les enregistrements et les résultats de chaque exécution, avec un manifeste qui identifie chaque fichier par SHA-256. **C’est public, car la recherche du studio est ouverte par défaut.** Les quelques fichiers qui ont une raison spécifique d’être privés sont conservés dans le référentiel compagnon privé, rnd-data-private, et aucun hachage de fichier privé n’est publié ici.

Le référentiel contient les données, ainsi que son paquetage MIT en lecture seule sous `src/` (`rnd-data` : `ls`, `show`, `where`, `schema`). rnd les écrit et les vérifie (`rnd raw ingest`, `rnd raw verify`, `rnd where`). L’index de rnd lit ses manifestes lorsque ce clone est placé à côté de la bibliothèque rnd, ou est nommé par `$RND_DATA`. Les scripts du référentiel sont `verify.sh` et ses deux flux de travail ; les fichiers `.sh` et `.py` sous `runs/` sont les enregistrements des exécutions, conservés en tant que données.

Le [manuel](https://mcp-tool-shop-org.github.io/rnd-data/handbook/) contient le manifeste, champ par champ, les règles pour les fichiers privés et les vérifications.

## Ce qui s’y trouve

| Chemin | Quoi |
|---|---|
| `runs/<id>/manifest.json` | Les fichiers d’une exécution (schéma `rnd-data-run/v1`) : le chemin de chaque fichier, SHA-256, sa taille, sa catégorie, sa licence et sa visibilité, ainsi que chaque copie. |
| `runs/<id>/files/…` | Les petits fichiers publics de cette exécution (256 Ko ou moins), dans git. |
| `store.json` | Les emplacements qui contiennent les octets en dehors de ce référentiel, et la manière dont une machine trouve chacun d’eux. |
| `src/rnd_data/` | Le paquetage Python MIT en lecture seule (`rnd-data` : `ls`, `show`, `where`, `schema`) et les schémas JSON du manifeste. |

- Les **fichiers de plus de 256 Ko** sont stockés une seule fois, par contenu, à l’adresse `blobs/<sha256[:2]>/<sha256>`. Chaque exécution qui en contient un l’identifie par son hachage, de sorte qu’une version utilisée sur plusieurs fenêtres est stockée une seule fois.
- **Ils deviennent publics sous la forme d’un ensemble de données Hugging Face** lors de la phase suivante. Jusqu’alors, ils se trouvent sur le disque de sauvegarde du studio.

## Un ID d’exécution

Un ID d’exécution est son dossier source, avec `/` écrit comme `--`. Par exemple, `receipts--colab--window14b-…-20261019` est le `receipts/colab/window14b-…-20261019` de l’éditeur.
- **Ses fichiers.** Les fichiers d’une exécution sont ceux qui se trouvent dans le dossier le plus proche contenant un `outcome.json`, de sorte que chaque nouvelle tentative (`try1/`) est sa propre exécution.
- **Les fichiers en dehors d’un dossier d’exécution** sont regroupés sous leur dossier de fenêtre (pour Colab) ou sous leur dossier principal.

Un `runs[].raw_manifest_id` d’une expérience dans [rnd](https://github.com/mcp-tool-shop-org/rnd) nomme l’un de ces ID.

## Fichiers privés

Un fichier est privé uniquement pour une raison spécifique : clés scellées ou mises de côté, fichiers masqués, texte d’élément, plans non approuvés, projets privés ou contenu que l’analyse d’identité du studio signale. Sa copie se trouve dans rnd-data-private, et le manifeste de son exécution indique seulement ce qui suit à ce sujet :
- **Privé pour son contenu :** il est exclu et comptabilisé par raison dans le `private_files` du manifeste.
- **Privé uniquement pour l’identité :** il est répertorié par chemin et par taille, avec `"visibility": "private"`, `"private_why": "identity"` et `"sha256": null`.

Aucun hachage de fichier privé n’est publié, car le hachage d’un fichier d’étiquette court pourrait être trouvé par tâtonnement. Tout le reste est public.

## Copies et vérification

Les copies d’un fichier sont répertoriées dans le `copies` de son manifeste. La racine de chaque stockage est trouvée par machine, via `store.local.json` (ignoré par git) ou `$RND_DATA_STORE_<NAME>`, de sorte qu’aucun chemin de machine n’est enregistré.

Le SHA-256 de chaque fichier public se trouve dans le manifeste de son exécution, de sorte qu’une copie téléchargée puisse être vérifiée sans rnd, ou avec `rnd raw verify`. Manuellement, à partir de la racine du référentiel (toute plateforme avec `sha256sum` ; `jq` pour la seconde) :

```bash
sha256sum runs/<id>/files/<path>      # compare with that file's "sha256" in runs/<id>/manifest.json
jq -r '.copies[] | select(.store == "rnd-data") | "\(.sha256)  \(.location)"' runs/*/manifest.json \
  | sha256sum -c --quiet              # every git copy at once; silent when all match
```

Avec rnd installé, `bash verify.sh` exécute `rnd raw verify --public-only`, comme le fait CI pour chaque demande d’extraction : il recalcule le hachage de chaque copie git, ignore les stockages qu’un clone public n’a pas, et échoue sur un fichier suivi sous `runs/` qui n’est pas nommé dans un manifeste, une entrée privée avec un hachage, la balise privée, un nom de fichier d’apparence privée ou un chemin de machine dans un manifeste. Sur le banc d’essai, où le stockage de blobs est configuré, `bash verify.sh --full` exécute le `rnd raw verify` complet.

Rien n’est supprimé du banc d’essai du studio tant que deux copies vérifiées n’existent pas, qu’un test de restauration a réussi et que le directeur a donné son accord.

## Propriétaires

- Le département de **recherche et développement** est propriétaire de la mise en page et des outils.
- **L’éditeur** est propriétaire de ses enregistrements et examine chaque importation de ces derniers.

## Sécurité et confiance

- **Ce qu’il contient :** les manifestes d’exécution, les petits fichiers publics des exécutions, `store.json`, le paquetage MIT en lecture seule sous `src/`, `tests/`, `verify.sh`, deux flux de travail et le site.
- **Ce qu’il ne contient jamais :** les informations d’identification ; les octets d’un fichier privé ou son hachage ; les chemins de machine.
- **Ce qui y a accès :** l’importation de rnd (`rnd raw ingest`) écrit chaque manifeste et chaque fichier sous `runs/`, avec l’examen par l’éditeur de chaque importation de ses enregistrements. CI vérifie chaque demande d’extraction avec des autorisations en lecture seule.
- **Aucune télémétrie** n’est collectée ou envoyée ; le site est statique.

Pour signaler un fichier privé qui a atteint ce référentiel, un hachage publié d’un fichier privé ou une identité dans un fichier public, consultez [SECURITY.md](SECURITY.md).

## Licence

rnd-data est sous licence comme rnd :
- **Les données** sont sous [CC BY 4.0](LICENSE).
- **Le paquetage et les scripts** (`src/`, `tests/`, `*.sh`, `*.py`) sont sous [MIT](LICENSE-MIT).
- **Un fichier tiers** conserve la licence que son manifeste nomme. La version llama.cpp est sous licence MIT (commit 620d2225).

Le champ `licence` du manifeste d’un fichier est le dernier mot à ce sujet. Le manifeste de chaque fichier public indique sa licence ; les entrées privées contiennent `"licence": null`, car elles ne sont pas publiées.

## État

Maintenu et en constante évolution avec chaque importation. Il n’y a pas de versions : chaque exécution est identifiée par son manifeste, et le référentiel par son commit. [CHANGELOG.md](CHANGELOG.md) répertorie les modifications par date.
