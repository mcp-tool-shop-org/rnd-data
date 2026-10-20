import type { SiteConfig } from '@mcptoolshop/site-theme';

export const config: SiteConfig = {
  title: 'rnd-data',
  description:
    "The raw data behind the studio's research: every run's receipts and outputs, with a manifest per run that pins each file by SHA-256.",
  logoBadge: 'RD',
  brandName: 'rnd-data',
  repoUrl: 'https://github.com/mcp-tool-shop-org/rnd-data',
  footerText:
    'CC BY 4.0 (data) · MIT (scripts) — Built by <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a>',

  hero: {
    badge: 'Open research · raw data · no code',
    headline: 'The raw data.',
    headlineAccent: 'Every file pinned by SHA-256.',
    description:
      'Every run behind the studio’s research, with its receipts and outputs, and a manifest that pins each file by hash. It’s public because the research is open by default. The few files with a named reason to be private sit in a private companion, and no private file’s hash is ever published.',
    primaryCta: { href: '#check-a-file', label: 'Check a file' },
    secondaryCta: { href: 'handbook/', label: 'Read the Handbook' },
    previews: [
      { label: 'Clone', code: 'git clone https://github.com/mcp-tool-shop-org/rnd-data' },
      { label: 'Find a run', code: 'ls runs/   # one folder per run: manifest.json, files/' },
      { label: 'Check a file', code: 'sha256sum runs/<id>/files/outcome.json' },
    ],
  },

  sections: [
    {
      kind: 'features',
      id: 'whats-here',
      title: 'What’s here',
      subtitle: 'Manifests and small files in git; larger files once, by content.',
      features: [
        {
          title: 'A manifest per run',
          desc: 'runs/<id>/manifest.json (schema rnd-data-run/v1) lists each file’s path, SHA-256, size, tier, licence and visibility, and every copy.',
        },
        {
          title: 'Small files in git',
          desc: 'A run’s public files of 256 KB or less sit under runs/<id>/files/, stored byte-exact so every hash holds.',
        },
        {
          title: 'Larger files once',
          desc: 'Files over 256 KB are stored once, by content, at blobs/<sha256[:2]>/<sha256>, so a build several runs used is kept once. They go public as a Hugging Face dataset at the next phase.',
        },
        {
          title: 'A run id is its folder',
          desc: 'The source folder, with / written as --. A run is the nearest folder holding an outcome.json, so each retry is its own run; other files are grouped into a collection.',
        },
        {
          title: 'No code',
          desc: 'rnd writes it (rnd raw ingest) and reads it (rnd raw verify, rnd where, the index). The repo’s own scripts are verify.sh and two workflows; the .sh and .py files under runs/ are receipts of runs.',
        },
        {
          title: 'No machine paths',
          desc: 'store.json names the stores that hold bytes outside the repo. Each machine finds their roots through a gitignored file or an environment variable.',
        },
      ],
    },
    {
      kind: 'code-cards',
      id: 'check-a-file',
      title: 'Check a file without rnd',
      cards: [
        {
          title: 'One file, by hand',
          code: 'sha256sum runs/<id>/files/<path>\ngrep -A1 \'"path": "<path>"\' runs/<id>/manifest.json\n# the two hashes must match',
        },
        {
          title: 'Every git copy (with jq)',
          code: 'jq -r \'.copies[] | select(.store == "rnd-data")\n  | "\\(.sha256)  \\(.location)"\' runs/*/manifest.json \\\n  | sha256sum -c --quiet',
        },
        {
          title: 'With rnd',
          code: 'RND_DATA="$PWD" rnd raw verify --public-only\nbash verify.sh   # the same, as CI runs it',
        },
      ],
    },
    {
      kind: 'data-table',
      id: 'private-files',
      title: 'Private files',
      subtitle: 'Private only for a named reason. No private file’s hash is published.',
      columns: ['Why it’s private', 'What its run’s manifest says'],
      rows: [
        ['Sealed or held-out keys, blind files, item text, unapproved plans, private projects', 'Nothing by name: it’s left out, and counted by reason in private_files'],
        ['Only identity (the studio’s identity scan flagged it)', 'Its path and size, with "visibility": "private", "private_why": "identity" and "sha256": null'],
        ['Anything else', 'It’s public, with its hash and its copies'],
      ],
    },
    {
      kind: 'features',
      id: 'why-no-hash',
      title: 'Why no private hash is published',
      subtitle: 'A hash can give a short file away.',
      features: [
        {
          title: 'Hashes can be guessed',
          desc: 'A short label file has few possible contents. Publishing its SHA-256 would let anyone confirm a guess, so a private file’s hash never appears here.',
        },
        {
          title: 'The bytes live elsewhere',
          desc: 'A private file’s copy is in rnd-data-private, the private companion, or in the studio’s blob store. Nothing from either enters this repository.',
        },
        {
          title: 'Checked on every pull request',
          desc: 'CI fails on a private entry with a hash, the private tag, a private-looking file name, a machine path in a manifest, or a file under runs/ that no manifest names.',
        },
      ],
    },
    {
      kind: 'data-table',
      id: 'owners',
      title: 'Who owns what',
      columns: ['Who', 'What'],
      rows: [
        ['R&D', 'The layout and the tooling: rnd writes every manifest and checks every copy'],
        ['The Publisher', 'Its receipts, and a review of every ingest of them'],
        ['The Director', 'The rulings on what is public, and the go before anything is deleted from the studio rig'],
      ],
    },
  ],
};
