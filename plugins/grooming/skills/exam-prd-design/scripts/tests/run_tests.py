#!/usr/bin/env python3
"""Uji regresi parser terhadap fixture tersamarkan di folder ini.

Pemakaian (dari folder skill):
    python3 scripts/tests/run_tests.py

Hanya library standar. Keluar dengan kode 1 kalau ada yang gagal.
"""
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
PARSER = HERE.parent / "parse_figma_metadata.py"
gagal = []


def jalankan(fixture, *opsi):
    hasil = subprocess.run(
        [sys.executable, "-I", str(PARSER), str(HERE / fixture), *opsi],
        capture_output=True, text=True, check=True,
    )
    return hasil.stdout


def cek(nama, kondisi):
    print(("  ok    " if kondisi else "  GAGAL ") + nama)
    if not kondisi:
        gagal.append(nama)


def layar_legacy(data):
    return {s["id"]: s for row in data["screens"] for s in row}


def layar_section(data):
    out = {}

    def jalan(secs):
        for s in secs:
            for x in s["screens"]:
                out[x["id"]] = x
            jalan(s["subsections"])

    jalan(data["sections"])
    return out


print("legacy-sample.xml")
d = json.loads(jalankan("legacy-sample.xml", "--json"))
L = layar_legacy(d)
cek("mode legacy terdeteksi", d["mode"] == "legacy")
cek("6 layar (panah & teks lepas tidak dihitung)", len(L) == 6)
cek("label edge case: Registrasi > OTP salah", L["a:3"]["groups"] == ["Registrasi", "OTP salah"])
cek("caption 'Label ·' menempel ke layarnya", L["a:5"]["caption"] == "Label · Nomor sudah dipakai")
cek("modal lepas 480x320 dianggap layar", "a:6" in L)
cek("captcha berulang jadi isi bawaan", d["teks_bawaan"].get("I'm not a robot") == 3)
cek("teks tersembunyi unik tetap terlihat", L["a:3"]["hidden_texts"] == ["Syarat survei (modul lain)"])
cek("output teks mencetak grup label", "grup: Registrasi > OTP salah" in jalankan("legacy-sample.xml"))
cek("--grep cocok ke caption", "a:5" in jalankan("legacy-sample.xml", "--grep", "sudah dipakai"))

print("section-sample.xml")
d = json.loads(jalankan("section-sample.xml", "--json"))
S = layar_section(d)
cek("mode section terdeteksi", d["mode"] == "section")
cek("Modal 1440x1024 dianggap layar", "2:2" in S)
cek("Toast kecil tetap komponen", "2:3" not in S)
cek("sheet 'sesuai IDDS' tetap komponen walau besar", "2:4" not in S)
cek("badge prioritas P0 menempel", S["2:1"]["prioritas"] == "P0")
cek("kode US panjang terurai (07 dan 11)",
    {"US/BK/T3/26/07", "US/BK/T3/26/11"} <= set(S["2:1"]["us"]))
cek("layar subsection mobile ikut terhitung", "4:1" in S)
cek("section 'Modal · …' tetap modul", any(s["id"] == "1:3" and s["kategori"] == "modul"
                                            for s in d["sections"]))
cek("section Arsip ditandai arsip", any(s["id"] == "1:2" and s["kategori"] == "arsip"
                                        for s in d["sections"]))

print()
if gagal:
    print(f"{len(gagal)} cek gagal")
    sys.exit(1)
print("semua cek lulus")
