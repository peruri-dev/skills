# Team Skills

Kumpulan skill AI agent untuk alur kerja tim: dari persiapan grooming sampai development.

Repo ini adalah plugin marketplace Claude Code. Kami mengelompokkan skill menjadi plugin per peran atau tahap kerja, jadi setiap orang cukup memasang plugin yang relevan untuknya.

## Katalog

| Plugin     | Untuk    | Skill               | Kegunaan                                                                               |
| ---------- | -------- | ------------------- | -------------------------------------------------------------------------------------- |
| `grooming` | Engineer | `exam-prd-design`   | Review kesesuaian antara PRD (Confluence) dan Figma sebelum grooming; bisa menulis komentar temuan (opsional) |
| `grooming` | Engineer | `boil-api-contract` | Draf kontrak API dan kartu technical grooming per story Jira, dicek ke OpenAPI backend |

Rencana plugin berikutnya ada di [CHANGELOG.md](CHANGELOG.md) bagian "Unreleased".

## Instalasi

### Prasyarat akses

Repo ini private. Claude Code memakai kredensial git di laptopmu sendiri (Claude Code tidak menyimpan token), jadi pastikan salah satu ini sudah beres:

- HTTPS: `gh auth login`, lalu `gh auth setup-git`.
- SSH: kunci SSH GitHub sudah dimuat di `ssh-agent` tanpa prompt passphrase. Kalau tidak punya kunci SSH GitHub, set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`.

### Claude Code (yang disarankan)

Di dalam sesi Claude Code:

```
/plugin marketplace add peruri-dev/skills
/plugin install grooming@peruri-dev
```

Kamu memanggil skill dengan awalan nama plugin, misalnya `/grooming:exam-prd-design`. Claude juga bisa memakainya otomatis berdasarkan deskripsi skill.

Untuk menyalakan auto-update: `/plugin` → **Marketplaces** → pilih `peruri-dev` → **Enable auto-update**. Tanpa ini, perbarui manual dengan `/plugin marketplace update peruri-dev`.

> Sudah pernah menyalin skill secara manual ke `~/.claude/skills/` atau `.claude/skills/`? Hapus salinan itu setelah memasang plugin, supaya skill yang sama tidak termuat dua kali.

### Daftarkan otomatis di repo project

Supaya Claude Code menawarkan plugin ini ke semua orang yang membuka sebuah repo project, jalankan sekali dari shell di root repo project tersebut:

```bash
claude plugin marketplace add peruri-dev/skills --scope project
```

Lalu tambahkan plugin yang ingin kamu aktifkan ke file `.claude/settings.json` yang baru dibuat, dan commit file itu:

```json
{
  "extraKnownMarketplaces": {
    "peruri-dev": {
      "source": { "source": "github", "repo": "peruri-dev/skills" }
    }
  },
  "enabledPlugins": {
    "grooming@peruri-dev": true
  }
}
```

### Agent lain seperti Cursor, Codex, atau Copilot

Format skill di repo ini mengikuti standar terbuka `SKILL.md`, jadi kamu bisa memasangnya dengan [skills CLI](https://skills.sh). Arahkan langsung ke folder skill-nya:

```bash
npx skills add https://github.com/peruri-dev/skills/tree/main/plugins/grooming/skills/exam-prd-design -a <agent>
```

Perbarui dengan `npx skills update`. Cara ini menyalin file, jadi tidak ikut auto-update seperti plugin. Untuk satu agent, pilih salah satu cara saja: plugin atau skills CLI, jangan keduanya.

Alternatif tanpa tool: salin folder skill ke direktori skill agent kamu (misalnya `~/.claude/skills/` untuk Claude Code atau `.agents/skills/` untuk Codex/Cursor).

### Admin Claude Team/Enterprise (opsional)

Kalau organisasi memakai Claude Team/Enterprise, admin bisa mewajibkan marketplace ini dan menyalakan auto-update untuk semua orang lewat managed settings (`extraKnownMarketplaces` dengan `"autoUpdate": true`, dan `enabledPlugins`). Lihat [Manage plugins for your organization](https://code.claude.com/docs/en/plugins/org).

## Prasyarat per skill

| Skill               | Butuh                                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------- |
| `exam-prd-design`   | MCP Atlassian dan Figma terhubung (cek dengan `/mcp`), `python3` (hanya library standar)                |
| `boil-api-contract` | MCP Atlassian dan Figma, `python3`, di repo project: `docs/api-konvensi.md` dan `docs/api/openapi.json` |

Fitur komentar opsional di `exam-prd-design` butuh akses menulis komentar di MCP Atlassian dan Figma.

## Struktur repo

```
.claude-plugin/marketplace.json   katalog plugin
plugins/<plugin>/
  .claude-plugin/plugin.json      nama, versi, deskripsi plugin
  skills/<skill>/SKILL.md         instruksi skill
  skills/<skill>/scripts/         script pendukung + tests/
```

## Kontribusi

Baca [CONTRIBUTING.md](CONTRIBUTING.md) sebelum menambah atau mengubah skill. Kirim semua perubahan lewat pull request, dan minta review dulu sebelum digabung.
