---
name: boil-api-contract
description: Menyusun draf kontrak API dan kartu technical grooming (Backend API + Frontend) per story Jira dari PRD, desain Figma, dan hasil exam-prd-design, mengikuti konvensi API project serta mengecek endpoint yang sudah ada di OpenAPI backend.
---

# Boil API Contract

Skill ini menyiapkan bahan technical grooming dari sisi FE: kebutuhan data tiap layar diubah menjadi **draf kontrak API** dan **kartu grooming per story** dengan format yang sama seperti board FigJam tim. Hasilnya adalah pembuka diskusi dengan BE, bukan keputusan final.

Prinsip utama sama dengan `exam-prd-design`: **pisahkan membaca dari mengusulkan.** Kebutuhan data disusun dulu, dicek terhadap endpoint yang sudah ada, baru diusulkan endpoint baru.

## Batasan (wajib dipatuhi)

- **Bukan desain internal BE.** Jangan merancang tabel, migration, struktur service, atau query. Bagian itu ditulis `[diisi BE]`.
- **Konvensi project menang.** Ikuti `docs/api-konvensi.md`. Kalau butir konvensi berstatus ⚠️ asumsi, tetap pakai tapi catat di bagian Asumsi.
- **Pakai ulang sebelum membuat baru.** Setiap kebutuhan dicek dulu ke OpenAPI. Endpoint, kode error, dan pola yang sudah ada tidak boleh diusulkan ulang dengan nama lain.
- **Jangan mengarang nomor kode error atau nama permission.** Kode baru ditulis `TBD` dan permission baru ditandai _usulan_.
- **Read-only terhadap Confluence, Figma, dan Jira.** File yang ditulis hanya laporan lokal (lihat "Output"). Menambah kartu ke FigJam hanya setelah pengguna setuju (lihat "Push ke FigJam").

## Input

1. **Story Jira** (key atau link, maksimal 3 story per run). Baca dengan `getJiraIssue` (`view: "evidence"`): summary, epic induk, subtask yang sudah ada, deskripsi. Kalau parameter `view` ditolak oleh versi MCP Atlassian yang terpasang, panggil ulang tanpa `view`. Kalau subtask tidak ikut, cari dengan `searchJiraIssuesUsingJql` (`parent = <KEY>`).
2. **Laporan `exam-prd-design`** (`docs/exam-prd-design-result*.md`) untuk story tersebut. Kalau belum ada, sarankan menjalankan `exam-prd-design` dulu. Lanjut tanpa laporan hanya kalau pengguna setuju, dan catat di header bahwa PRD ↔ desain belum direview.
3. **Konvensi project**: `docs/api-konvensi.md` di root project. Kalau tidak ada, **berhenti**. Tawarkan menyusunnya dari `references/konvensi-template.md` di folder skill ini plus hasil `openapi_index.py --conventions`, lalu minta pengguna mengonfirmasi butir-butirnya.
4. **OpenAPI backend**: `docs/api/openapi.json` (format JSON). Kalau tidak ada, minta pengguna mengekspornya. Kalau memang tidak tersedia, lanjut, tapi tandai semua endpoint "reuse belum dicek".
5. **PRD dan Figma**: hanya kalau tidak ada laporan exam, atau untuk detail yang tidak ada di laporan.

## Tahap 0: Persiapan

1. Baca `docs/api-konvensi.md` sampai habis.
2. Catat versi di header laporan: key story, versi PRD (dari laporan exam atau Confluence), tanggal laporan exam, dan `info.version` OpenAPI beserta tanggal file-nya. Kalau file OpenAPI lebih tua dari 14 hari, ingatkan pengguna untuk mengekspor ulang.
3. Kalau satu run berisi beberapa story, kerjakan story per story (Tahap 1–6), lalu tulis semuanya dalam satu laporan.

## Tahap 1: Gating dari hasil exam

Petakan story ke US di laporan exam (cocokkan summary story dengan judul US/halaman PRD), lalu ambil temuan yang menyentuh US itu:

- **Blocker terbuka**: endpoint yang bergantung padanya ditulis **TERTUNDA (F-xx)**, berisi kerangka saja (method + tujuan), tanpa detail request/response.
- **Major terbuka**: tetap disusun, tapi keputusan yang diambil dicatat sebagai asumsi dengan rujukan F-xx.
- Temuan yang sudah dijawab (ada catatan keputusan di laporan atau di Jira) diperlakukan sebagai requirement.

## Tahap 2: Kebutuhan data per layar

Dari inventaris layar laporan exam (atau Figma kalau tidak ada laporan), susun tabel kebutuhan:

| Layar (node) | Data ditampilkan | Aksi pengguna | State/edge case | Role |

Kolom **Role** dibawa sampai ke laporan, karena menjadi dasar usulan permission di kartu: satu kombinasi role + aksi yang berbeda biasanya berarti satu permission `DOMAIN.AKSI`. Tulis `publik` untuk layar tanpa login dan `semua user login` kalau tidak ada pembedaan role.

Aturan menebak tipe dari UI:

- Tanggal/jam → string ISO 8601 (field `*At`).
- Badge status, chip, tab, dropdown dengan opsi tetap → enum UPPER_SNAKE (nilai diambil dari copy UI, tandai asumsi).
- Angka dengan satuan uang → number, catat mata uang.
- Avatar/gambar → URL string.
- Toggle/centang → boolean.
- Tabel → list dengan paginasi; kolom yang bisa diurutkan → nilai `sortBy`; kolom filter → query filter.
- Layar edge case (kosong, error, kedaluwarsa, terkunci) → kandidat respons error atau state FE.

## Tahap 3: Cek reuse ke OpenAPI

Jalankan script dari folder skill ini (lihat "Script"):

1. `--grep <kata kunci domain>` untuk mencari endpoint kandidat. Coba beberapa kata kunci (nama resource dalam bahasa Inggris, nama aksi).
2. `--endpoint <operationId>` untuk detail kandidat: auth, permission, query, field body, kode error yang disebut.
3. `--codes --grep <kata kunci>` untuk mencari kode error yang bisa dipakai ulang.

Klasifikasikan setiap kebutuhan:

- **PAKAI ULANG**: endpoint yang ada sudah cukup. Tulis operationId-nya. Jangan buat kartu Backend untuknya, cukup sebut di bagian Frontend.
- **UBAH**: endpoint ada, tapi butuh field, query param, atau perilaku tambahan. Tulis sebagai "perubahan endpoint existing" beserta selisihnya.
- **BARU**: tidak ada endpoint yang cocok.

Karena schema response di OpenAPI bisa kosong (`schema: {}`), untuk PAKAI ULANG yang datanya dibutuhkan layar, tulis field response yang **diharapkan FE** sebagai pertanyaan konfirmasi ke BE.

## Tahap 4: Draf kontrak per endpoint BARU dan UBAH

Ikuti konvensi project untuk setiap butir:

- Method dan URL (pola path, `me`, aksi sebagai segmen, cara hapus/bulk sesuai konvensi).
- Header auth yang tepat (login, token dari email, atau publik).
- Path/query param (paginasi, urutan, pencarian, filter multi-nilai sesuai konvensi).
- Request body dengan tipe dan aturan validasi dari PRD (panjang, format, wajib/opsional).
- Daftar HTTP status code yang mungkin.
- Response body sukses dengan placeholder tipe (`"string"`, `0`, `boolean`, `[enum A / B]`), memakai envelope project.
- Error reference: `Kode | HTTP | Konteks | Pesan`. Pakai ulang kode dari katalog. Kode baru ditulis `TBD`.
- Business process: validasi token → validasi permission → validasi request (aturan dari PRD) → aturan bisnis (rate limit, status, kepemilikan data) → aksi.
- Keterlacakan: ID PRD (US/UJ/UA/BR) dan node layar yang membutuhkannya.

## Tahap 5: Kartu technical grooming

Satu kartu per story, format persis seperti board FigJam tim (teks biasa, dipakai di code block bahasa BASH):

```text
<KEY> <Summary story>

- Backend:
  1. [diisi BE] Migration / perubahan tabel (kalau perlu)
  2. Permission (usulan): <DOMAIN.AKSI>
  3. Buat API untuk <tujuan>
    a. Request method: <METHOD>
    b. URL: <path>
    c. Header: <Authorization / X-API-Key>
    d. Query params: (hapus kalau tidak ada)
        - <nama>: <keterangan>
    e. Request body: (hapus kalau tidak ada)
      { ... }
    f. HTTP status code:
      - 200 OK
      - ...
    g. Response body:
      { ... }
    h. Error reference:
      - <kode> (<HTTP>) <konteks>: <pesan>
    i. Business process:
      1. Validasi token
      2. Validasi permission
      3. ...
    j. Unit test (handler, service, repository, util)
    k. API docs (termasuk schema response di Huma)
  4. <API berikutnya, format sama>
- Frontend:
  1. UI
    - <komponen per layar, state kosong/loading, catatan "(tidak ada di PRD)" bila perlu>
  2. Data fetching / Form behaviour
    a. API: <METHOD path> (<BARU / UBAH / PAKAI ULANG operationId>)
    b. State: loading, error, data
    c. Setelah sukses: <redirect / tutup form / fetch ulang>
  3. Error handling
    - <kode atau status> → <layar/toast yang ditampilkan>
```

Endpoint TERTUNDA ditulis `3. [TERTUNDA F-xx] <tujuan>` tanpa sub-butir. Endpoint PAKAI ULANG tidak punya butir di Backend.

Sertakan juga **usulan subtask Jira** dengan prefiks tim: `[BE] Membuat API <tujuan>`, `[FE] <fitur>`, `[FE] Template Email` (kalau ada email), dan seterusnya. Bandingkan dengan subtask yang sudah ada di story. Yang sudah ada jangan diusulkan ulang.

## Tahap 6: Self-check sebelum menulis

Perbaiki dulu kalau ada yang gagal:

- [ ] Setiap data yang tampil di layar punya sumber di response sebuah endpoint (baru, ubah, atau pakai ulang).
- [ ] Setiap aksi pengguna punya endpoint.
- [ ] Setiap layar edge case punya kode error atau state FE yang memicunya.
- [ ] Setiap aturan validasi di PRD muncul di business process atau di validasi FE.
- [ ] Tidak ada endpoint baru yang sebenarnya sudah ada di OpenAPI.
- [ ] Method, casing, header auth, envelope, dan query list sesuai konvensi.
- [ ] Semua tebakan (tipe, enum, nama field) tercatat di Asumsi.

## Output

1. Tulis laporan ke **`docs/boil-api-contract-<KEY>.md`** (beberapa story: `<KEY1>_<KEY2>`), relatif terhadap root project. Buat folder `docs/` kalau belum ada.
2. Kalau file sudah ada, tanya pengguna: timpa, atau simpan dengan akhiran tanggal.
3. Di chat, tampilkan: path file, jumlah endpoint BARU/UBAH/PAKAI ULANG/TERTUNDA, dan daftar pertanyaan paling penting untuk BE (maksimal 5). Jangan tempel ulang seluruh laporan.
4. Tawarkan push ke FigJam.

### Format laporan

````markdown
# Boil API Contract: <KEY> <Summary>

- **Story Jira**: <KEY> <Summary> (epic <KEY epic>)
  - Link: <URL Jira>
- **Review PRD ↔ desain**: <path laporan exam, tanggal> atau "belum direview"
- **OpenAPI**: <info.title> <info.version> (file <tanggal>)
- **Konvensi**: `docs/api-konvensi.md`
- **Disusun**: <YYYY-MM-DD>

## Ringkasan

Terdapat **<N> kebutuhan endpoint**:

- 🆕 **<n> Baru**
- ✏️ **<n> Ubah endpoint existing**
- ♻️ **<n> Pakai ulang**
- ⏸️ **<n> Tertunda** (menunggu keputusan temuan exam)

<1–3 kalimat inti: hal yang paling perlu didiskusikan dengan BE.>

## Kartu technical grooming

Salin ke code block FigJam (bahasa BASH).

```text
<isi kartu Tahap 5>
```

## Kebutuhan data per layar

| Layar (node) | Data ditampilkan | Aksi | State/edge case | Role | Endpoint |
| ------------ | ---------------- | ---- | --------------- | ---- | -------- |

## Cek reuse

| Kebutuhan | Keputusan | Endpoint | Catatan |
| --------- | --------- | -------- | ------- |

## Usulan subtask Jira

- [BE] ...
- [FE] ...

## Asumsi

- <tebakan tipe/enum/nama, butir konvensi ⚠️ yang dipakai, keputusan Major F-xx>

## Pertanyaan

**Untuk BE**

1. <pertanyaan>

**Untuk PO**

1. <pertanyaan>

## Keterbatasan

- <misalnya schema response OpenAPI kosong, laporan exam tidak ada>
````

Aturan format Markdown sama dengan `exam-prd-design`: baris kosong di sekitar heading, list, tabel, dan blok kode; tabel rata kolom; italic `_…_`; emoji hanya di Ringkasan. Kalau `node_modules/.bin/prettier` ada di project, jalankan pada file laporan setelah ditulis. Jangan install Prettier dan jangan pakai `npx`.

## Push ke FigJam (opsional)

Hanya setelah pengguna setuju dan memberi link board (boleh dengan `node-id` area tujuan).

1. Muat skill Figma `figma-use` dan `figma-use-figjam` sebelum memanggil `use_figma` (kalau skill plugin tidak tersedia, baca resource `skill://figma/figma-use/SKILL.md` dan `skill://figma/figma-use-figjam/SKILL.md`).
2. `create_session` dengan fileKey board.
3. Buat **satu section baru** bernama `boil-api-contract · <KEY> · <YYYY-MM-DD>` di area kosong di sebelah kanan konten yang ada (atau di area yang ditunjuk pengguna).
4. Di dalamnya, buat satu **code block** per kartu, bahasa BASH, isi persis teks kartu.
5. **Jangan mengubah, memindah, atau menghapus node yang sudah ada.**
6. Laporkan link node section yang dibuat.

Kalau tool Figma untuk menulis tidak tersedia atau gagal, katakan dan minta pengguna menyalin kartu dari laporan.

## Script

`scripts/openapi_index.py` di folder skill ini (lihat "Base directory for this skill" saat skill dimuat). Butuh `python3`, hanya library standar, input harus JSON.

- (tanpa opsi): daftar semua endpoint per tag, dengan auth dan permission.
- `--grep <teks>`: saring endpoint.
- `--endpoint <id>[,<id>]`: detail endpoint.
- `--codes [--grep <teks>]`: katalog kode sukses/error.
- `--conventions`: statistik pola (method, auth, query, tipe ID, status) untuk menyusun atau memeriksa konvensi.
- `--exclude <id>[,<id>]`: anggap endpoint belum ada. Dipakai untuk menguji skill terhadap fitur yang kontraknya sudah final.
- `--json`: keluaran terstruktur.

Uji script: `python3 scripts/tests/run_tests.py`.

## Keterbatasan yang perlu disampaikan di laporan

- Schema response di OpenAPI bisa kosong. Bentuk response di kartu adalah usulan FE yang perlu dikonfirmasi BE.
- Tipe dan nilai enum ditebak dari UI. Semuanya tercatat di Asumsi.
- Perilaku backend (rate limit, masa berlaku token, transaksi) hanya diambil dari PRD dan deskripsi OpenAPI.
