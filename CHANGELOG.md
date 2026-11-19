# Changelog

Semua perubahan penting dicatat di sini, per plugin. Format mengikuti [Keep a Changelog](https://keepachangelog.com/id-ID/1.1.0/), versi mengikuti [semver](https://semver.org/lang/id/).

## Unreleased

Rencana, belum dirilis:

- `grooming`: pindahkan `api-contract-generator` (draf API contract FE–BE dari PRD + Figma).
- Plugin `product` untuk PO: kandidat `prd-master`, `prd-compliance-review`, `idds-acceptance-criteria`.
- Plugin `dev`: loop AI-to-AI dengan kriteria CodeReviewer DevSecOps sebelum push.

## grooming 0.1.0

### Ditambahkan

- Skill `exam-prd-design`: review kesesuaian PRD ↔ desain Figma sebelum backlog grooming, dengan laporan di `docs/exam-prd-design-result.md`.
- Parser metadata Figma (`scripts/parse_figma_metadata.py`) untuk mode section dan mode legacy (`↳`), beserta fixture dummy dan test regresi.
