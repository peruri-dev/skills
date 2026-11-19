# Konvensi API: <nama project>

Dipakai oleh skill `boil-api-contract`. Simpan di repo FE project pada `docs/api-konvensi.md`.

Status tiap butir:

- ✅ **Terkonfirmasi**: konsisten di OpenAPI backend atau kontrak yang sudah jadi.
- ⚠️ **Asumsi**: dari contoh terbatas. Konfirmasi ke BE sebelum dianggap baku.

## Sumber

- OpenAPI backend: `docs/api/openapi.json` (diekspor dari `<url>/openapi.json`)
- Contoh kontrak final: <daftar endpoint atau link board>

## Path dan method

- Prefiks dan versi:
- Penamaan segmen (kebab/camel, jamak/tunggal):
- Gaya REST vs aksi:
- Data milik user login (`me`):
- Method yang dipakai, cara update, cara hapus, aksi bulk:
- Path param dan tipe ID:

## Header dan autentikasi

- Endpoint user login:
- Endpoint token sekali pakai (link email):
- Endpoint publik:
- Format nama permission:

## Request

- Format dan casing field:
- Enum:
- Upload file:

## Query untuk list

- Paginasi:
- Urutan:
- Pencarian:
- Rentang tanggal dan formatnya:
- Filter multi-nilai:

## Response

- Envelope sukses:
- Envelope list (pagination, links):
- Timestamp dan boolean:
- Status sukses (200/201/202):

## Error

- Bentuk body error:
- Skema penomoran kode:
- Kode umum yang sering dipakai ulang:
- Cara menandai kode baru (usulan):

## Pola yang sudah ada

- <OTP, token email, rate limit, bulk, dll.>

## Catatan untuk BE

- [ ] <temuan yang perlu dibereskan>
