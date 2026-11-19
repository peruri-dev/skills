# Skill AI agent untuk tim

Kumpulan skill untuk alur kerja tim, dari persiapan grooming sampai pengembangan.

Repo ini adalah plugin marketplace Claude Code. Kami mengelompokkan skill ke dalam plugin berdasarkan peran atau tahap kerja, jadi setiap orang cukup memasang plugin yang relevan untuknya.

## Katalog

| Plugin     | Untuk    | Skill             | Kegunaan                                                                        |
| ---------- | -------- | ----------------- | ------------------------------------------------------------------------------- |
| `grooming` | Engineer | `exam-prd-design` | Review kesesuaian PRD (Confluence) dengan desain Figma sebelum backlog grooming |

Rencana plugin berikutnya ada di bagian `Unreleased` pada [CHANGELOG.md](CHANGELOG.md).

## Instalasi

### Prasyarat akses

Repo ini privat. Claude Code memakai kredensial git di laptopmu sendiri dan tidak menyimpan token, jadi pastikan salah satu cara ini sudah beres:

- HTTPS: jalankan `gh auth login`, lalu `gh auth setup-git`.
- SSH: kunci SSH GitHub sudah dimuat di `ssh-agent` tanpa meminta passphrase. Kalau tidak punya kunci SSH GitHub, set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`.

### Claude Code (disarankan)

Di dalam sesi Claude Code:

```
/plugin marketplace add peruri-dev/skills
/plugin install grooming@peruri-dev
```

Panggil skill plugin dengan prefiks nama pluginnya, misalnya `/grooming:exam-prd-design`. Claude juga tetap bisa memakainya otomatis berdasarkan deskripsi skill.

Nyalakan auto-update: `/plugin` → **Marketplaces** → `peruri-dev` → **Enable auto-update**. Tanpa ini, perbarui manual dengan `/plugin marketplace update peruri-dev`.

> Sudah pernah menyalin skill secara manual ke `~/.claude/skills/` atau `.claude/skills/`? Hapus salinan itu setelah memasang plugin, supaya skill yang sama tidak termuat dua kali.

### Daftarkan otomatis di repo proyek

Agar semua orang yang membuka repo proyek langsung ditawari plugin ini, jalankan perintah ini sekali dari shell di root repo proyek tersebut:

```bash
claude plugin marketplace add peruri-dev/skills --scope project
```

Lalu tambahkan plugin yang mau diaktifkan ke `.claude/settings.json` yang dihasilkan, dan commit file itu:

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

### Agent lain

Format skill di repo ini mengikuti standar terbuka `SKILL.md`, jadi bisa dipasang dengan [skills CLI](https://skills.sh) di agent seperti Cursor, Codex, atau Copilot. Arahkan perintahnya langsung ke folder skill:

```bash
npx skills add https://github.com/peruri-dev/skills/tree/main/plugins/grooming/skills/exam-prd-design -a <agent>
```

Perbarui dengan `npx skills update`. Cara ini menyalin file, jadi tidak otomatis diperbarui seperti plugin. Untuk satu agent, pilih salah satu cara — plugin atau skills CLI — jangan keduanya.

Alternatif tanpa tool: salin folder skill ke direktori skill agent-mu, misalnya `~/.claude/skills/` untuk Claude Code atau `.agents/skills/` untuk Codex atau Cursor.

### Untuk admin Claude Team atau Claude Enterprise (opsional)

Kalau organisasi memakai Claude Team atau Claude Enterprise, admin bisa mewajibkan marketplace ini dan menyalakan auto-update untuk semua orang lewat managed settings (`extraKnownMarketplaces` dengan `"autoUpdate": true` dan `enabledPlugins`). Lihat [panduan pengelolaan plugin untuk organisasi](https://code.claude.com/docs/en/plugins/org).

## Prasyarat per skill

| Skill             | Butuh                                                                                    |
| ----------------- | ---------------------------------------------------------------------------------------- |
| `exam-prd-design` | MCP Atlassian dan Figma terhubung (cek dengan `/mcp`), `python3` (hanya library standar) |

## Struktur repo

```
.claude-plugin/marketplace.json   katalog plugin
plugins/<plugin>/
  .claude-plugin/plugin.json      nama, versi, deskripsi plugin
  skills/<skill>/SKILL.md         instruksi skill
  skills/<skill>/scripts/         script pendukung + tests/
```

## Kontribusi

Baca [CONTRIBUTING.md](CONTRIBUTING.md) sebelum menambah atau mengubah skill. Semua perubahan lewat pull request dan wajib direview.
