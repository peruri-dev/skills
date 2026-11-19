---
name: exam-prd-design
description: Mereview kesesuaian PRD (Confluence atau .md) dengan desain Figma sebelum backlog grooming — dari satu user story sampai PRD modul besar (puluhan US, multi-platform). Menghasilkan laporan di docs/exam-prd-design-result.md berisi matriks keterlacakan, temuan berbukti, dan pertanyaan untuk PO/desainer.
---

# Exam PRD ↔ Desain

Skill ini membantu engineer menyiapkan backlog grooming: membandingkan PRD dengan desain Figma, lalu menghasilkan **laporan temuan berbukti** dan **pertanyaan siap bawa** untuk PO dan desainer.

Prinsip utama ada dua: **pisahkan membaca dari membandingkan** dan **kerjakan per batch**. Inventaris PRD dan desain disusun dulu sebagai hasil antara yang bisa dicek, baru setelah itu dibandingkan. PRD besar (banyak US) tidak pernah direview sekaligus — satu run menangani maksimal 3–5 US, laporan ditambah per batch.

## Batasan (wajib dipatuhi)

- **Read-only terhadap sumber.** Jangan menulis komentar ke Confluence/Figma dan jangan mengubah apa pun di sana. Satu-satunya file yang ditulis skill ini adalah laporan hasil (lihat "Output").
- **Setiap temuan wajib berbukti dari dua sisi**: ID/kutipan PRD dan nama frame + node-id Figma. Untuk temuan "tidak ada di desain", buktinya adalah daftar layar yang sudah diperiksa. Tanpa bukti, bukan temuan.
- **Jangan menilai estetika visual** (warna, spacing, ilustrasi). Itu domain desainer. Fokus pada perilaku, konten/copy, aturan, alur, dan state.
- **Jangan mengarang requirement.** Kalau PRD diam soal sesuatu, kategorinya "Ambigu" atau "Tidak ada di PRD", bukan "Konflik".

## Input

1. **PRD**: link Confluence (dibaca lewat Atlassian MCP) atau file `.md`.
2. **Figma**: link file/page/section. Link tanpa `node-id` tidak masalah — Tahap 0.5 akan mengusulkan node yang tepat. Jangan menebak sendiri dan jangan langsung minta node-id buta.
3. *Opsional*: daftar US yang mau direview.
4. *Opsional*: mode, `cepat` (default) atau `teliti`.

## Tahap 0: Catat versi dua sisi

Satu angka tidak cukup. Catat pasangan versi di header laporan:

- **Sisi PRD**: label versi dokumen (mis. "v2.0 FINAL") **dan** nomor revisi halaman Confluence (`metadata.version.number`) beserta tanggalnya.
- **Sisi desain**: klaim versi yang tertulis di file — nama page (mis. "✏️ v1.0"), atau section/anotasi yang menyebut versi PRD acuannya (mis. board "Riwayat Versi · PRD ↔ desain": "Acuan: PRD v1.0 FINAL (rev 35, 9 Nov)").

Pasangan ini dipakai di Tahap 3. Kalau desain mengaku mengacu versi PRD yang sudah lewat, itu **temuan wajib** — Major, atau Blocker kalau perubahan PRD menyentuh US yang sedang direview.

## Tahap 0.5: Rekonsa dan scoping

Wajib kalau node-id tidak diberikan, PRD berisi lebih dari ~5 US, atau pengguna tidak menyebut scope.

1. `get_metadata` **tanpa nodeId** → daftar page.
2. Kandidat page = yang berkonten dev (nama seperti "Ready for Dev", "In Progress", "✅ v1.0"). **Cek konten, jangan percaya nama**: panggil `get_metadata` per kandidat. Page kosong (canvas tanpa anak) bisa saja bernama "Ready for Dev" sedangkan konten asli ada di "In Progress".
3. Kalau output tersimpan ke file (bisa >1 MB), profil dulu dengan parser: `python3 <base_dir_skill>/scripts/parse_figma_metadata.py <file> --summary`. Hasilnya: daftar modul/section dengan jumlah layar, kode US, platform (Web/iOS/Android/Backoffice), prioritas (badge `Prioritas · P0 · US-xx`), dan jumlah teks tersembunyi.
4. Usulkan ke pengguna, **tunggu konfirmasi sebelum lanjut**: page yang direview, dan batch US pertama — **≤3–5 US per run**, mulai dari prioritas tertinggi (badge di desain atau section "Prioritisasi & Scope" di PRD). US lain dicatat sebagai sisa scope di laporan.

Lewati tahap ini hanya kalau pengguna sudah memberi node-id spesifik **dan** daftar US.

## Tahap 1: Inventaris PRD

Baca penuh dengan `getConfluenceContent` (`detail: "full"`, `content_format: "markdown"`). PRD besar (>~8 ribu kata) tetap dibaca utuh sekali, tapi:

- **Inventaris detail hanya untuk US dalam batch aktif.** US lain cukup didaftarkan (kode + judul) untuk cek duplikasi dan cakupan.
- Cek konsistensi internal lintas US — elemen yang sama disebut berbeda di bagian berbeda, angka tidak sama, aturan bertentangan — tetap jalan sekali di awal. Laporkan dengan kategori "Inkonsistensi PRD".

**Penomoran ID.** Pakai kode yang ada di PRD apa adanya (`US/BK/T3/26/07`, `FR-13`, `UC-09`) — jangan menggantinya dengan US1/US2 kalau kode resmi ada. Kalau tidak ada kode eksplisit, buat dari strukturnya:
- `US1`, `US2`, … per user story / halaman (urut kemunculan)
- `US1/UJ-7`: langkah ke-7 User Journey
- `US1/UA-4.2`: butir ke-4 User Acceptance, sub-butir ke-2
- `BR-9`: butir ke-9 Aturan Bisnis

Untuk setiap item, catat **implikasi UI**: layar, field, label/placeholder, tombol, pesan/copy, aturan validasi, angka (batas, durasi, jumlah), role, state, dan **platform yang diminta** (web/mobile).

## Tahap 2: Inventaris desain

1. Kalau tool `create_session` tersedia, panggil dengan fileKey dan deskripsi tugas, lalu pakai sessionId-nya di semua panggilan berikutnya.
2. `get_metadata` pada page/section terpilih. Output besar otomatis tersimpan ke file — **jangan dibaca utuh**, proses dengan parser dari folder skill ini:
   - `--summary` — profil per modul: jumlah layar, kode US, platform, prioritas, teks tersembunyi. Untuk kalibrasi dan pemilihan batch.
   - `--section <id>` atau `--grep <teks>` — detail satu modul/batch saja. Output bisa ratusan baris; jangan proses semua section sekaligus.
   - `--json` kalau perlu olah terstruktur; `--max-texts N` untuk memperbesar/memperkecil cuplikan teks per layar; `--min-repeat N` untuk ambang teks tersembunyi bawaan komponen (default 3, `0` = mati).
   - Di mode legacy, setiap layar tampil dengan `grup: <modul> > <label>` (label = header `↳` sempit di atasnya) dan `caption:` bila ada. Itulah penanda edge case. Jangan abaikan.
3. **Kalibrasi konvensi (hipotesis, bukan aturan).** Dari output `--summary`, tentukan struktur file dan tulis asumsinya di laporan (bagian "Asumsi struktur file"):
   - *Mode section*: satu `<section>` per modul; kode US + platform di nama section; badge `Prioritas · P0 · US-xx` menempel tepat di atas layarnya; caption `Label · …` menerangkan layar di bawahnya.
   - *Mode legacy*: frame `↳` = penanda — header lebar = modul, header sempit di atas satu layar = label sub-alur/edge case; baris teratas = happy path kiri ke kanan; baris di bawahnya = edge case untuk langkah di atasnya.
   Kalau polanya tidak cocok keduanya, catat sebagai asumsi dan jadikan pertanyaan untuk desainer.
4. **Klasifikasi non-layar** (parser sudah memisahkannya): papan anotasi (`.Ringkasan modul`, `Pertanyaan Terbuka untuk PO`, `Riwayat Versi · PRD ↔ desain`), section `Arsip ·` (alur lama), sheet komponen (`Button · …`, "sesuai IDDS"). Arsip dikecualikan dari review tapi dicatat — jangan dihitung sebagai layar.
   Frame bernama `Modal · …`, `Dialog · …`, `Toast · …`, `Alert · …`, `Card · …` dianggap **layar/state** kalau ukurannya ukuran layar (atau, di mode legacy, frame lepas ≥200 px), dan baru dianggap komponen kalau kecil. Modal konfirmasi dan toast sukses adalah bahan review, bukan sheet komponen.
   **Harvest dua board ini** — sering berisi materi review yang sudah jadi:
   - `Pertanyaan Terbuka untuk PO` → salin ke bagian "Pertanyaan dari file desain" di laporan, tandai yang sudah terjawab oleh temuan batch ini. Jangan ditagih ulang sebagai temuan baru.
   - `Riwayat Versi · PRD ↔ desain` → bukti untuk cek staleness versi (Tahap 0/3).
5. **Bukti copy berjenjang** (hemat screenshot di file besar):
   - **Teks layer dari parser = bukti awal (penyaring), bukan bukti akhir.** Metadata memberi **nama layer**, bukan isi teks. Nama layer teks memang mengikuti isinya secara default, tapi **tidak ikut berubah kalau layer pernah di-rename**, jadi bisa basi. Pakai teks layer untuk menemukan kandidat temuan dan memverifikasi copy yang *cocok* dengan PRD tanpa screenshot.
   - **Aturan bukti copy (wajib):**
     - Temuan copy yang hanya berbukti nama layer: **confidence maksimal Sedang**, tulis "bukti: nama layer" di temuan.
     - Temuan **Konflik copy** (severity apa pun) dan temuan **"Tidak ada di desain"** yang didasarkan pada tidak ditemukannya teks di layer: **wajib diverifikasi dengan screenshot** layar terkait sebelum ditulis. Kalau screenshot tidak mendukung, buang temuannya.
     - Konflik copy **Blocker/Major**: tambahan `get_design_context` pada satu frame itu untuk mengonfirmasi teks persisnya.
   - **Screenshot** (`get_screenshot`, `maxDimension: 800`; 900–1200 untuk layar panjang; `enableBase64Response: true` kalau URL tidak bisa diunduh) untuk verifikasi di atas, dan untuk apa yang tidak terbaca dari metadata: state visual, urutan, visibilitas, layout. **Batas 40 layar per run** — lebih dari itu, pecah batch.
   - `get_design_context` jangan dipakai untuk semua layar.
   - Kalau mayoritas teks generik (terlihat dari `--summary`), kembali ke cara lama: screenshot semua layar dalam batch.
6. **Teks tersembunyi** — hati-hati, rawan false positive:
   - Parser sudah memisahkan teks tersembunyi yang muncul di ≥3 layar sebagai **isi bawaan komponen** (captcha, slot "Suffix", "(Opsional)", penghitung "0/140", tautan "Belum punya akun?"). Itu dicetak sekali di atas output dan **bukan temuan**.
   - Teks tersembunyi unik per layar baru jadi temuan kalau isinya **copy fitur/modul lain** atau **sisa versi lama** dari konten yang sama (contoh: template email menyimpan sapaan dan footer versi lama di layer tersembunyi). Slot bawaan komponen yang kebetulan unik tetap bukan temuan.
   - Severity default **Minor** (tidak tampil ke pengguna), confidence **Sedang**. Naikkan ke Major hanya kalau ada indikasi kuat akan ikut terimplementasi, misalnya layer tersembunyi berada di template email/notifikasi yang akan disalin utuh oleh developer.
7. `get_comments` dengan `pageId` page tersebut. Simpan thread yang `position.nodeId`-nya ada di dalam node yang direview. Tandai thread yang **belum resolved** — sering berisi keputusan yang belum masuk PRD atau desain.
8. Susun **tabel inventaris layar per batch**: node-id | nama asli | nama inferensi (`Modul / Layar / State`) | platform | prioritas | ringkasan isi | confidence. Layar responsive (mobile) dari satu flow yang sama jangan dihitung state terpisah — catat sebagai cakupan platform layar desktop-nya.

**Pilih mode.** Sarankan `teliti` kalau ≥30% layar bernama generik, struktur tidak terbaca, atau pemetaan harus ditebak. Kalau scope batch >40 layar, sarankan **pecah per US** — bukan sekali jalan walau mode teliti.

## Tahap 3: Pemetaan

Per batch, buat **matriks keterlacakan** dua tingkat:
- US ↔ kelompok layar
- UJ/UA/FR/UC/BR ↔ layar spesifik (satu item bisa ke beberapa layar; catat **cakupan per platform**, mis. ✅ Web ❌ Mobile, kalau US-nya multi-platform)

Langkah User Journey dicocokkan dengan urutan layar di baris happy path. Langkah tanpa layar menjadi kandidat temuan.

Dua cek lintas batch:
- **Staleness versi**: bandingkan versi PRD aktif (Tahap 0) dengan klaim versi di desain. Desain mengaku rev lama → temuan wajib.
- **Cakupan antar-platform**: US punya layar Web tapi tidak mobile (atau sebaliknya) tanpa alasan di PRD → kandidat temuan "Tidak ada di desain".

**Mode teliti:** berhenti di sini. Tampilkan tabel inventaris + matriks batch ini, minta pengguna mengoreksi, lalu lanjut ke Tahap 4. **Mode cepat:** lanjut, tandai pemetaan dengan confidence rendah. Selesai satu batch, ulangi Tahap 2 langkah 2 (`--section` berikutnya) untuk batch berikutnya — jangan mengubah hasil batch lama.

## Tahap 4: Pengecekan

Jalankan per batch. Untuk setiap pasangan yang terpetakan, cek kesesuaian copy, angka, aturan, urutan alur, dan perilaku. Untuk setiap layar dan alur, jalankan checklist berikut. Item checklist hanya menjadi temuan kalau **PRD mensyaratkannya** atau **jelas dibutuhkan untuk membangun fitur**.

### Checklist kelengkapan

**Form dan input**
- Field wajib kosong: ada pesan "wajib diisi"? Atau tombol disabled? Cocok dengan cara validasi di PRD (saat submit vs real-time)?
- Format tidak valid: ada pesan, dan copy-nya sama dengan PRD?
- Hint/aturan input (panjang, komposisi karakter) lengkap sesuai PRD, tidak kurang dan tidak lebih
- Batas maksimal karakter/file didefinisikan?
- Placeholder dan label sama dengan PRD?
- Show/hide untuk field kata sandi

**Aksi dan proses**
- State loading/submitting dan pencegahan submit ganda
- Error server, error jaringan, error layanan pihak ketiga (email, SMS, OTP, unggah file)
- Feedback sukses (toast/halaman) dan redirect sesudahnya
- Aksi batal/kembali dan efeknya (draft dihapus?)
- Konfirmasi untuk aksi tak terbalikkan (submit sekali, kirim survei, hapus)

**Keamanan dan pembatasan**
- Rate limit / lockout / freeze: ada layar atau pesannya? Pesannya patuh aturan privasi PRD (misalnya tidak mengungkap email terdaftar)?
- Tautan/token: valid, kedaluwarsa, tidak valid, **sudah dipakai**. Masing-masing punya layar dan jalur lanjutan (minta ulang, ke login) sesuai PRD?
- Akses per role: state "tidak berwenang", perbedaan tampilan antar role, dan pemicunya terdokumentasi?

**Konten**
- Template email/notifikasi: tidak ada sisa copy dari template lain, placeholder (`{{...}}`, `[name]`) wajar, versi bahasa konsisten
- Label aksi yang sama ditulis sama di semua layar (contoh: "Halaman Login" vs "Halaman Masuk")
- Toggle bahasa ada di desain: apakah PRD mendefinisikan copy bahasa kedua?

**Data dan tampilan** (untuk fitur list/detail)
- Empty state, loading/skeleton, pagination, teks panjang/overflow, perbedaan tampilan per role

### Kategori temuan

| Kategori | Arti |
|---|---|
| Tidak ada di desain | PRD mensyaratkan, tidak ada layar/state-nya |
| Tidak ada di PRD | Ada di desain, PRD tidak menyebut (scope creep atau keputusan yang tidak terdokumentasi) |
| Konflik | Keduanya menyebut, isinya berbeda |
| Inkonsistensi PRD | PRD bertentangan dengan dirinya sendiri |
| Ambigu | PRD atau desain tidak cukup jelas untuk dibangun atau diverifikasi |

### Severity

- **Blocker**: tidak bisa diestimasi atau dibangun tanpa keputusan
- **Major**: kalau dibiarkan, akan jadi rework atau bug (logika, alur, konten salah ke pengguna)
- **Minor**: copy, label, konsistensi istilah

Setiap temuan juga diberi **confidence** (Tinggi/Sedang/Rendah). Confidence rendah ditandai "perlu cek manual".

## Output

Setelah Tahap 4 batch aktif selesai:

1. Tulis laporan ke **`docs/exam-prd-design-result.md`**, relatif terhadap root project (direktori kerja saat ini). Buat folder `docs/` kalau belum ada.
2. Kalau file itu **sudah ada**, tanya pengguna **sekali**: timpa, simpan dengan akhiran nama fitur (contoh `exam-prd-design-result-reset-password.md`), atau **lanjut (append)**. Pilihan "lanjut" untuk batch berikutnya dari review yang sama: tambahkan bagian baru di bawah bagian yang ada, perbarui Ringkasan global dan daftar sisa scope di bagian atas, jangan sentuh bagian batch lama. Dalam satu sesi, keputusan ini tidak ditanya ulang tiap batch.
3. Di chat, cukup tampilkan: path file, jumlah temuan per severity batch ini, daftar temuan Blocker/Major (satu baris per temuan), dan sisa scope (US belum direview). Jangan tempel ulang seluruh laporan.

Pada **mode teliti**, checkpoint Tahap 3 tetap dilakukan di chat. File baru ditulis setelah pengecekan selesai.

## Format laporan

Ikuti template ini persis, termasuk baris kosong dan perataan tabel. Bagian bertanda _(opsional)_ hanya ditulis kalau ada isinya.

````markdown
# Review PRD ↔ Desain: <fitur/modul>

- **Product Requirement Document (PRD)**: <judul> v<label> (rev halaman <n>, <tgl>)
  - Link: <URL Confluence lengkap, atau path relatif file .md>
- **Desain Figma**: <page/section> (<node-id>), file <nama file Figma>
  - Link: <URL Figma lengkap dengan node-id>
- **Direview**: <YYYY-MM-DD>
- **Mode**: <cepat/teliti>

## Ringkasan

Terdapat **<N> Temuan**:

- 🔴 **<n> Blocker**
  - <n> Konflik, <n> Inkonsistensi PRD, <n> Tidak ada di desain, <n> Tidak ada di PRD, <n> Ambigu
- 🟠 **<n> Major**
  - <rincian kategori, format sama>
- 🟡 **<n> Minor**
  - <rincian kategori, format sama>

<_(opsional, hanya kalau review di-batch)_ Progres: batch <n> dari <M> · US direview: <kode> · Sisa: <kode>>

Inti masalahnya <dua/tiga/…>:

1. <masalah inti pertama>;
2. <masalah inti kedua>;
3. <masalah inti ketiga>.

## Versi & staleness

<PRD rev <n> (<tgl>) vs klaim desain "<versi>" → status: segar / basi, plus implikasinya>

## Inventaris layar

<Kalimat pengantar cakupan, satu gagasan per paragraf.>

<Paragraf terpisah untuk catatan node non-layar: header, connector, anotasi.>

| Node       | Nama asli      | Nama inferensi                        | Grup       | Confidence |
| ---------- | -------------- | ------------------------------------- | ---------- | ---------- |
| 5264:39228 | Login / Defaut | Login / Default (kosong, tanpa error) | Happy path | Tinggi     |

Catatan inventaris:

- <catatan>

## Matriks keterlacakan

<Paragraf pengantar, misalnya US yang berbagi layar yang sama.>

| ID PRD   | Ringkasan             | Layar | Status |
| -------- | --------------------- | ----- | ------ |
| US1/UJ-1 | Membuka halaman login | 39228 | ✅     |

## Temuan

### F-01 · <Kategori> · <Severity> · Confidence <..>

- **PRD**: <ID> "<kutipan pendek>"
- **Figma**: <nama inferensi> (<node-id>): <apa yang terlihat>
- **Masalah**: <1–2 kalimat>
- **Pertanyaan untuk <PO/Desainer>**: <pertanyaan konkret yang bisa dijawab di grooming>

## Pertanyaan dari file desain _(opsional)_

- <salinan board "Pertanyaan Terbuka untuk PO"; tandai yang sudah terjawab oleh temuan di atas>

## Pertanyaan terkumpul

**Untuk PO**

1. F-xx: <pertanyaan singkat>

**Untuk Desainer**

1. F-xx: <pertanyaan singkat>

## Thread komentar Figma yang belum selesai

- <node> · <ringkasan diskusi> · <relevansi dengan temuan, jika ada>

## Tidak bisa dicek dari desain

- <ID PRD>: <alasan, misalnya perilaku backend, kebijakan token, interaksi prototype>

## Asumsi struktur file _(opsional)_

<konvensi yang terdeteksi: mode section / mode legacy / lainnya, dan bagian yang tidak standar>

## Keterbatasan review

- <keterbatasan yang memengaruhi confidence temuan>
````

Kolom Status matriks: ✅ sesuai · ⚠️ temuan (sebut nomor F-xx) · ❌ tidak ada. Kalau satu bagian tidak berisi apa pun, tulis satu kalimat (contoh: "Tidak ada — page `↳ Login` tidak memiliki komentar."), jangan dihapus.

### Aturan format Markdown (kompatibel Prettier)

- **Baris kosong** sebelum dan sesudah setiap heading, list, tabel, dan blok kode, termasuk antara `### F-xx` dan bullet pertamanya, dan antara `**Untuk PO**` dan list di bawahnya.
- **Header laporan** berupa list bertingkat seperti template, bukan satu baris panjang dengan pemisah `·`. Isi `Link:` dengan URL lengkap dari input pengguna. Jangan dikosongkan dan jangan dikarang.
- **Ringkasan**: jumlah per severity sebagai list dengan emoji (🔴 Blocker, 🟠 Major, 🟡 Minor). Di bawah tiap severity ada satu sub-bullet rincian kategori, contoh `  - 2 Konflik, 2 Inkonsistensi PRD, 2 Tidak ada di PRD, 1 Ambigu`. Urutan kategori selalu: Konflik, Inkonsistensi PRD, Tidak ada di desain, Tidak ada di PRD, Ambigu. Kategori bernilai 0 tidak ditulis, dan severity bernilai 0 tidak diberi sub-bullet. Jumlah rincian wajib sama dengan angka severity-nya, jadi hitung ulang sebelum menulis. Setelah itu tulis inti masalah sebagai list bernomor (maksimal 5 butir; tiap butir diakhiri `;`, butir terakhir `.`). Emoji hanya dipakai di Ringkasan. Heading temuan tetap teks biasa.
- **Paragraf pendek**: satu gagasan per paragraf. Jangan menggabungkan kalimat dengan topik berbeda dalam satu paragraf.
- **Tabel rata kolom**: setiap sel diberi padding spasi sampai selebar isi terpanjang di kolom itu, garis pemisah `---` juga selebar kolom, dan satu spasi di tepi kiri-kanan setiap sel.
- **Penekanan**: bold `**…**`, italic `_…_` (bukan `*…*`). List tak berurut pakai `-`, sub-item indentasi 2 spasi. List berurut pakai `1.`, `2.`, `3.`.
- **Rapikan otomatis kalau bisa**: setelah file ditulis, kalau `node_modules/.bin/prettier` ada di project, jalankan `node_modules/.bin/prettier --write <path laporan>`. Jangan meng-install Prettier dan jangan pakai `npx` yang mengunduh paket. Kalau Prettier tidak ada, terapkan aturan di atas secara manual.

Nomor temuan menyambung antar batch kalau append ke laporan yang sama (batch 1 berakhir di F-16 → batch 2 mulai F-17). Urutkan temuan: Blocker → Major → Minor, lalu menurut urutan alur.

## Script parser

Script ada di `scripts/parse_figma_metadata.py` di folder skill ini (lihat "Base directory for this skill" saat skill dimuat). Butuh `python3` di mesin lokal (hanya library standar). Opsi: `--summary` (profil per modul; di mode legacy berisi daftar modul `↳` beserta jumlah layar dan labelnya), `--section <id>`, `--grep <teks>` (mencocokkan nama layar, grup, dan caption), `--json`, `--max-texts N`, `--min-repeat N`.

Uji tanpa file asli: fixture di `scripts/tests/` berisi data dummy (bukan potongan file Figma asli).
- `python3 scripts/tests/run_tests.py` menjalankan semua cek regresi parser.
- `python3 scripts/parse_figma_metadata.py scripts/tests/legacy-sample.xml` (mode legacy: header `↳`, label edge case, caption, modal lepas, teks tersembunyi, panah)
- `python3 scripts/parse_figma_metadata.py scripts/tests/section-sample.xml` (mode section: kode US, badge prioritas, caption, subsection, arsip, sheet komponen)

## Keterbatasan yang perlu disampaikan di laporan

- Interaksi prototype, animasi, dan perilaku hover tidak terbaca.
- Parser mengandalkan nama layer/section. File dengan penamaan generik total jatuh kembali ke screenshot (lihat "Bukti copy berjenjang"). Nama layer teks bisa basi kalau pernah di-rename, jadi copy dari nama layer saja bukan bukti akhir.
- Deteksi isi bawaan komponen berbasis frekuensi (≥3 layar). Di file yang sangat kecil (<3 layar), teks bawaan tidak tersaring otomatis, jadi nilai manual.
- Section `Arsip ·` dianggap alur usang dan dikecualikan; konfirmasi ke desainer kalau ternyata masih hidup.
- Konversi `getConfluenceContent` bisa lossy terhadap gambar/diagram PRD — catat bagian PRD yang tidak terbaca dan turunkan confidence temuan yang bergantung padanya.
- Perilaku backend (token, penyimpanan, rate limit di server) hanya bisa dicek dari sisi apakah desain menyediakan layar/pesan untuknya.
