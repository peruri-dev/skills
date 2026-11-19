# Changelog

Semua perubahan penting dicatat di sini, per plugin. Format mengikuti [Keep a Changelog](https://keepachangelog.com/id-ID/1.1.0/), versi mengikuti [semver](https://semver.org/lang/id/).

## Unreleased

Rencana, belum dirilis:

- Plugin `product` untuk PO: kandidat `prd-master`, `prd-compliance-review`, `idds-acceptance-criteria`.
- Plugin `dev`: loop AI-to-AI dengan kriteria CodeReviewer DevSecOps sebelum push.

## grooming 0.2.0

### Ditambahkan

- Skill `boil-api-contract`: draf kontrak API dan kartu technical grooming (Backend API + Frontend) per story Jira, dengan gating dari temuan `exam-prd-design`, cek reuse ke OpenAPI backend, dan push opsional ke FigJam.
- Script `openapi_index.py` (indeks endpoint, katalog kode error, statistik konvensi, `--exclude` untuk uji) beserta fixture dummy dan test regresi. Parameter di level path digabung dengan level operasi, body multipart di-resolve dari `$ref` dan menghormati `required`, `$ref` ke semua komponen lokal (`#/components/parameters/`, dll.) ikut di-resolve, dan file yang tidak ada memberi pesan jelas tanpa traceback.
- Template konvensi API per project (`references/konvensi-template.md`).

## grooming 0.1.0

### Ditambahkan

- Skill `exam-prd-design`: review kesesuaian PRD ↔ desain Figma sebelum backlog grooming, dengan laporan di `docs/exam-prd-design-result.md`.
- Parser metadata Figma (`scripts/parse_figma_metadata.py`) untuk mode section dan mode legacy (`↳`), beserta fixture dummy dan test regresi.
