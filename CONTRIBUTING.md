# Kontribusi

Panduan menambah dan mengubah skill di repo ini. Skill di sini dijalankan di laptop rekan kerja, termasuk script-nya, jadi perlakukan setiap perubahan seperti kode produksi.

## Alur kerja

1. Buat branch dari `main`.
2. Ubah atau tambah skill (lihat konvensi di bawah).
3. Uji di laptop sendiri (lihat [Menguji](#menguji)).
4. Naikkan `version` di `plugin.json` plugin yang berubah, dan catat di [CHANGELOG.md](CHANGELOG.md).
5. Buka pull request. Minimal 1 approval dari rekan lain dan CI `Validate skills` lulus sebelum merge (diatur lewat branch protection `main`).

## Menambah skill

1. Tentukan plugin tujuan berdasarkan **siapa yang memakai** dan **di tahap mana**:
   - `grooming`: engineer, persiapan backlog dan technical grooming.
   - Plugin baru (misalnya `product` untuk PO, `dev` untuk development): buat folder `plugins/<nama>/` beserta `.claude-plugin/plugin.json`, lalu daftarkan di `.claude-plugin/marketplace.json`.
2. Buat folder `plugins/<plugin>/skills/<nama-skill>/` berisi `SKILL.md`.
3. Tambahkan baris skill ke tabel Katalog di [README.md](README.md).

### Konvensi `SKILL.md`

- **Nama**: kebab-case, sama dengan nama folder. Nama skill tidak boleh berubah setelah dirilis, karena orang memanggilnya dengan nama itu.
- **Description**: satu kalimat yang menjelaskan **kapan** skill dipakai, bukan sekadar apa isinya. Claude memilih skill dari kalimat ini.
- **Jenis pemanggilan**: tentukan sejak awal (mengikuti pola [mattpocock/skills](https://github.com/mattpocock/skills)):
  - _Dipanggil pengguna_: alur kerja yang dijalankan dengan sengaja, misalnya `/grooming:exam-prd-design`. Boleh memanggil skill lain.
  - _Dipanggil model_: praktik yang bisa dipakai Claude kapan pun relevan, misalnya cara menulis acceptance criteria.
- **Batasan eksplisit**: tulis apa yang tidak boleh dilakukan skill (misalnya read-only terhadap Confluence/Figma).
- **Output**: sebutkan file apa yang ditulis dan di mana.
- **Bahasa**: Bahasa Indonesia, istilah teknis boleh tetap dalam bahasa Inggris.

### Konvensi script

- **Hanya library standar** bahasa yang dipakai. Tidak ada `pip install` / `npm install`.
- **Tidak ada akses jaringan**, tidak menghapus file, tidak menjalankan perintah lain. Script membaca input dan mencetak hasil.
- Rujuk script dari `SKILL.md` relatif terhadap folder skill.
- Sertakan `scripts/tests/` berisi fixture dan test runner yang bisa dijalankan tanpa akses ke sistem asli.

### Data dan kerahasiaan

- **Fixture wajib dummy.** Jangan menyalin potongan metadata Figma, isi PRD, nama klien, atau kode US asli. Kalau fixture dibuat dari file asli, ganti semua nama dan teks sebelum commit.
- **Jangan pernah** menaruh token, cookie, URL berisi kredensial, atau data pribadi di skill mana pun.
- Contoh output (laporan, screenshot) tidak di-commit ke repo ini.

## Versi dan rilis

- Versi hanya ditulis di `plugins/<plugin>/.claude-plugin/plugin.json`, **bukan** di entri `marketplace.json`.
- Rekan kerja hanya menerima pembaruan kalau `version` berubah. Commit tanpa kenaikan versi tidak akan sampai ke mereka.
- Pakai semver:
  - **patch** (`0.1.1`): perbaikan bug, perbaikan kata-kata instruksi.
  - **minor** (`0.2.0`): skill baru, opsi atau bagian laporan baru.
  - **major** (`1.0.0`): perubahan yang memaksa orang mengubah cara pakai, misalnya rename skill atau format output berubah total.
- **Jangan mengganti `name` plugin** setelah dirilis. Untuk mengubah label yang tampil, pakai `displayName` di `plugin.json`. Kalau rename memang harus, tambahkan peta `renames` di `marketplace.json`.

## Menguji

Dari root repo:

```bash
# 1. Validasi struktur marketplace dan plugin
claude plugin validate .

# 2. Test regresi script (ulangi untuk setiap skill yang punya tests/)
python3 plugins/grooming/skills/exam-prd-design/scripts/tests/run_tests.py

# 3. Pasang dari salinan lokal, lalu coba skill-nya di sesi Claude Code
claude plugin marketplace add ./
claude plugin install grooming@peruri-dev
```

Dengan marketplace lokal, perubahan file langsung terbaca di sesi berikutnya atau setelah `/reload-plugins`, tanpa menaikkan versi. Setelah selesai menguji, hapus dengan `claude plugin marketplace remove peruri-dev` lalu pasang ulang dari GitHub.

## Checklist pull request

- [ ] `claude plugin validate .` lulus
- [ ] Test script lulus
- [ ] Sudah dicoba di sesi Claude Code pada kasus nyata
- [ ] `version` di `plugin.json` naik dan CHANGELOG diperbarui
- [ ] Fixture dan contoh bebas data internal
- [ ] Katalog di README diperbarui (kalau ada skill baru)
