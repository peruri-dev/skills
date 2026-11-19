#!/usr/bin/env python3
"""Uji regresi openapi_index.py terhadap fixture dummy di folder ini.

Pemakaian (dari folder skill):
    python3 scripts/tests/run_tests.py
"""
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE.parent / "openapi_index.py"
FIX = HERE / "openapi-sample.json"
gagal = []


def run(*opsi):
    return subprocess.run([sys.executable, "-I", str(SCRIPT), str(FIX), *opsi],
                          capture_output=True, text=True, check=True).stdout


def cek(nama, kondisi):
    print(("  ok    " if kondisi else "  GAGAL ") + nama)
    if not kondisi:
        gagal.append(nama)


print("openapi-sample.json")
semua = json.loads(run("--json"))
ids = {e["operationId"] for e in semua}
cek("6 endpoint terbaca", len(semua) == 6)
cek("--exclude menyembunyikan endpoint", "check-item-token" not in {e["operationId"] for e in json.loads(run("--json", "--exclude", "check-item-token"))})

d = {e["operationId"]: e for e in json.loads(run("--endpoint", "get-item-list,create-item,get-item-detail,check-item-token", "--json"))}
cek("auth Authorization terdeteksi", d["get-item-list"]["auth"] == "Authorization")
cek("auth X-API-Key terdeteksi", d["check-item-token"]["auth"] == "X-API-Key")
cek("permission dengan kutip", d["get-item-list"]["permission"] == ["ITEM.LIST"])
cek("permission tanpa kutip", d["create-item"]["permission"] == ["ITEM.CREATE"])
cek("query param terbaca", [q["name"] for q in d["get-item-list"]["queryParams"]] == ["page", "pageSize", "search", "status"])
body = {f["name"]: f for f in d["create-item"]["body"]["fields"]}
cek("$schema dibuang dari body", "$schema" not in body)
cek("enum terbaca", body["kind"]["type"] == "enum(BASIC,PREMIUM)")
cek("array nullable terbaca", body["tagIds"]["type"] == "integer(int64)[]")
cek("field wajib terbaca", body["name"]["required"] and not body["tagIds"]["required"])
cek("body Generic* dianggap tanpa body", d["get-item-detail"]["body"] is None)
cek("path param int64", d["get-item-detail"]["pathParams"] == [{"name": "id", "type": "integer(int64)"}])
cek("status 201 terbaca", d["create-item"]["successStatus"] == ["201"])
cek("schema response kosong terdeteksi", d["get-item-list"]["responseSchemaDocumented"] is False)
cek("kode di deskripsi terbaca", d["check-item-token"]["errorCodes"] == ["100901", "100902"])

kode = {k["code"]: k for k in json.loads(run("--codes", "--json"))}
cek("katalog kode lengkap", set(kode) == {"000001", "000003", "100003", "100901", "100902", "200001", "200404"})
cek("jenis sukses/error", kode["000003"]["kind"] == "sukses" and kode["200404"]["kind"] == "error")
cek("HTTP kode terbaca", kode["200404"]["http"] == 404)
cek("--codes --grep menyaring", "100901" in run("--codes", "--grep", "token") and "200404" not in run("--codes", "--grep", "token"))

u = json.loads(run("--endpoint", "upload-item-photo", "--json"))[0]
cek("parameter level path ikut terbaca (auth)", u["auth"] == "Authorization")
cek("path param dari level path", u["pathParams"] == [{"name": "id", "type": "integer(int64)"}])
mp = {f["name"]: f for f in u["body"]["fields"]}
cek("multipart $ref di-resolve, $schema dibuang", set(mp) == {"photo", "caption", "extras"})
cek("multipart field file", mp["photo"]["type"] == "file" and mp["extras"]["type"] == "file[]")
cek("multipart required dihormati", mp["photo"]["required"] and not mp["caption"]["required"])

gagal_run = subprocess.run([sys.executable, "-I", str(SCRIPT), str(HERE / "tidak-ada.json")],
                           capture_output=True, text=True)
cek("file tidak ada: pesan ramah, tanpa traceback",
    gagal_run.returncode != 0 and "tidak ditemukan" in gagal_run.stderr and "Traceback" not in gagal_run.stderr)

ar = json.loads(run("--endpoint", "get-archived-items", "--json"))[0]
cek("$ref ke components/parameters di-resolve", [q["name"] for q in ar["queryParams"]] == ["pageSize"]
    and ar["queryParams"][0]["type"] == "integer(int64)")

k = json.loads(run("--conventions", "--json"))
cek("statistik method", dict(map(tuple, k["method"])) == {"GET": 4, "POST": 1, "PUT": 1})

print()
if gagal:
    print(f"{len(gagal)} cek gagal")
    sys.exit(1)
print("semua cek lulus")
