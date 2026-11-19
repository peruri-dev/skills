# Panduan untuk AI agent yang bekerja di repo ini

Repo ini berisi skill untuk AI agent, dikemas sebagai plugin marketplace Claude Code. Kamu kemungkinan diminta menambah atau mengubah skill.

## Aturan

- Ikuti [CONTRIBUTING.md](CONTRIBUTING.md): struktur folder, konvensi `SKILL.md`, konvensi script, dan aturan versi.
- Setiap perubahan pada sebuah plugin wajib menaikkan `version` di `plugins/<plugin>/.claude-plugin/plugin.json` dan menambah entri di `CHANGELOG.md`. Jangan menulis `version` di `marketplace.json`.
- Jangan mengganti nama plugin atau skill yang sudah ada.
- Script hanya boleh memakai library standar, tanpa akses jaringan, tanpa menghapus file.
- Fixture di `scripts/tests/` harus data dummy. Jangan menyalin data dari Figma, Confluence, atau Jira asli ke repo ini.
- Kalau mengubah script parser, tambahkan atau perbarui cek di `scripts/tests/run_tests.py` untuk perilaku yang diubah.

## Sebelum menyatakan selesai

Jalankan dari root repo dan pastikan semuanya lulus:

```bash
claude plugin validate .
python3 plugins/grooming/skills/exam-prd-design/scripts/tests/run_tests.py
```
