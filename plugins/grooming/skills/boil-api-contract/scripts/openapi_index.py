#!/usr/bin/env python3
"""Indeks OpenAPI (JSON) backend untuk menyusun draf kontrak API.

Pemakaian:
    python3 openapi_index.py <openapi.json> [opsi]

Opsi:
    (tanpa opsi)        daftar semua endpoint per tag
    --grep TEKS         saring endpoint yang path/operationId/summary/deskripsinya mengandung TEKS
    --endpoint ID[,ID]  detail endpoint per operationId: header auth, permission, path/query
                        param, field request body, status sukses, kode error yang disebut
    --codes             katalog kode sukses/error dari info.description (bisa digabung --grep)
    --conventions       statistik pola: method, header auth, nama query param, format ID, enum
    --exclude ID[,ID]   anggap operationId ini belum ada (untuk uji: "tutup" endpoint asli)
    --json              keluaran JSON

Hanya library standar. File harus JSON (Huma: /openapi.json), bukan YAML.
"""

import argparse
import collections
import json
import re
import sys

METHODS = ("get", "post", "put", "patch", "delete")
KODE_RE = re.compile(r"\b([0-3]\d{5})\b")
PERM_RE = re.compile(r"Requires\s+[`']?([A-Z][A-Z_]*(?:[.:][A-Z_]+)+)[`']?")
TABEL_KODE_RE = re.compile(r"^\|\s*(\d{6})\s*\|\s*(\d{3})\s*\|\s*(.*?)\s*\|\s*$")


def muat(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit(f"File tidak ditemukan: {path}. Ekspor OpenAPI backend ke docs/api/openapi.json.")
    except IsADirectoryError:
        sys.exit(f"{path} adalah folder, bukan file OpenAPI JSON.")
    except json.JSONDecodeError:
        sys.exit("File bukan JSON yang valid. Ekspor OpenAPI dalam format JSON (Huma: /openapi.json).")


def resolve(spec, schema, depth=0):
    if not isinstance(schema, dict) or depth > 8:
        return schema or {}
    ref = schema.get("$ref")
    if ref and ref.startswith("#/components/"):
        # Semua komponen lokal: schemas, parameters, requestBodies, responses, dll.
        _, _, jenis, nama = (ref.split("/", 3) + ["", ""])[:4]
        target = spec.get("components", {}).get(jenis, {}).get(nama.replace("~1", "/").replace("~0", "~"))
        if target is None:
            return {}
        hasil = dict(resolve(spec, target, depth + 1))
        if jenis == "schemas":
            hasil["_nama"] = nama
        return hasil
    return schema


def tipe(spec, s, depth=0):
    s = resolve(spec, s, depth)
    t = s.get("type")
    if isinstance(t, list):
        t = "|".join(x for x in t if x != "null") + ("?" if "null" in t else "")
    if t and "array" in t:
        return f"{tipe(spec, s.get('items', {}), depth + 1)}[]"
    if s.get("enum"):
        return "enum(" + ",".join(map(str, s["enum"])) + ")"
    if s.get("_nama") and (s.get("properties") or t == "object"):
        return s["_nama"]
    fmt = s.get("format")
    return f"{t}({fmt})" if t and fmt else (t or "any")


def field_body(spec, schema):
    s = resolve(spec, schema)
    nama = s.get("_nama", "")
    if nama.startswith("Generic") or not s.get("properties"):
        return []
    wajib = set(s.get("required") or [])
    out = []
    for k, v in s["properties"].items():
        if k == "$schema":
            continue
        v2 = resolve(spec, v)
        out.append({"name": k, "type": tipe(spec, v), "required": k in wajib,
                    "desc": (v2.get("description") or "").strip()})
    return out


def gabung_param(spec, level_path, level_op):
    """Parameter level path + level operasi. Operasi menimpa path untuk (name, in) yang sama."""
    hasil = {}
    for p in (level_path or []) + (level_op or []):
        p = resolve(spec, p)
        if p.get("name") and p.get("in"):
            hasil[(p["name"], p["in"])] = p
    return list(hasil.values())


def operasi(spec, exclude):
    for path, item in spec.get("paths", {}).items():
        for m, op in item.items():
            if m not in METHODS or not isinstance(op, dict):
                continue
            if op.get("operationId") in exclude:
                continue
            op = dict(op, parameters=gabung_param(spec, item.get("parameters"), op.get("parameters")))
            yield path, m.upper(), op


def field_multipart(spec, schema):
    s = resolve(spec, schema)
    wajib = set(s.get("required") or [])
    out = []
    for k, v in (s.get("properties") or {}).items():
        if k == "$schema":
            continue
        v2 = resolve(spec, v)
        jenis = "file" if v2.get("format") == "binary" or v2.get("contentMediaType") else tipe(spec, v)
        if jenis.endswith("[]") and resolve(spec, v2.get("items", {})).get("format") == "binary":
            jenis = "file[]"
        out.append({"name": k, "type": jenis, "required": k in wajib,
                    "desc": (v2.get("description") or "").strip()})
    return out


def ringkas(spec, path, method, op):
    params = op.get("parameters") or []
    header = [p["name"] for p in params if p.get("in") == "header"]
    auth = ("Authorization" if "Authorization" in header
            else "X-API-Key" if "X-API-Key" in header else "publik")
    desc = op.get("description") or ""
    perm = sorted(set(PERM_RE.findall(desc)))
    body = None
    rb = (op.get("requestBody") or {}).get("content", {})
    for ct, c in rb.items():
        skema = c.get("schema", {})
        fields = field_multipart(spec, skema) if ct.startswith("multipart") else field_body(spec, skema)
        body = {"contentType": ct, "fields": fields}
        break
    sukses = sorted(c for c in (op.get("responses") or {}) if c.startswith("2"))
    kosong = all(((op["responses"][c].get("content") or {}).get("application/json") or {}).get("schema") in ({}, None)
                 for c in sukses) if sukses else True
    return {
        "method": method, "path": path, "operationId": op.get("operationId"),
        "summary": op.get("summary", ""), "tags": op.get("tags", []), "auth": auth,
        "permission": perm,
        "pathParams": [{"name": p["name"], "type": tipe(spec, p.get("schema", {}))}
                       for p in params if p.get("in") == "path"],
        "queryParams": [{"name": p["name"], "type": tipe(spec, p.get("schema", {})),
                         "desc": (p.get("description") or "").strip()}
                        for p in params if p.get("in") == "query"],
        "body": body if body and body["fields"] else None,
        "successStatus": sukses, "responseSchemaDocumented": not kosong,
        "errorCodes": sorted(set(KODE_RE.findall(desc))),
        "description": desc.strip(),
    }


def katalog_kode(spec):
    teks = (spec.get("info") or {}).get("description") or ""
    modul, jenis, out = "", "", []
    for baris in teks.splitlines():
        b = baris.strip()
        if b.startswith("## "):
            modul = b[3:].strip()
        elif b.startswith("### "):
            jenis = "sukses" if "Success" in b else "error"
        else:
            m = TABEL_KODE_RE.match(b)
            if m:
                out.append({"code": m.group(1), "http": int(m.group(2)), "message": m.group(3),
                            "module": modul, "kind": jenis})
    return out


def konvensi(daftar):
    c = collections.Counter
    method, auth, query, idfmt, segmen = c(), c(), c(), c(), c()
    for e in daftar:
        method[e["method"]] += 1
        auth[e["auth"]] += 1
        for q in e["queryParams"]:
            query[q["name"]] += 1
        for p in e["pathParams"]:
            idfmt[p["type"]] += 1
        parts = [s for s in e["path"].split("/") if s and not s.startswith("{")][2:]
        for s in parts:
            segmen["kebab" if "-" in s else "satu-kata"] += 1
    status = c(s for e in daftar for s in e["successStatus"])
    return {"method": method.most_common(), "auth": auth.most_common(),
            "queryParam": query.most_common(), "pathParamType": idfmt.most_common(),
            "successStatus": status.most_common(), "segmenPath": segmen.most_common(),
            "responseTerdokumentasi": sum(e["responseSchemaDocumented"] for e in daftar),
            "totalEndpoint": len(daftar)}


def cetak_daftar(daftar):
    per_tag = collections.defaultdict(list)
    for e in daftar:
        per_tag[(e["tags"] or ["(tanpa tag)"])[0]].append(e)
    for tag in sorted(per_tag):
        print(f"\n## {tag} ({len(per_tag[tag])})")
        for e in sorted(per_tag[tag], key=lambda e: (e["path"], e["method"])):
            perm = f" | perm: {','.join(e['permission'])}" if e["permission"] else ""
            print(f"- {e['method']:6} {e['path']} | {e['operationId']} | {e['summary']} | auth: {e['auth']}{perm}")


def cetak_detail(e, katalog):
    idx = {k["code"]: k for k in katalog}
    print(f"\n## {e['method']} {e['path']}  ({e['operationId']})")
    print(f"- summary: {e['summary']}")
    print(f"- auth header: {e['auth']}")
    if e["permission"]:
        print(f"- permission: {', '.join(e['permission'])}")
    for p in e["pathParams"]:
        print(f"- path param: {p['name']}: {p['type']}")
    for q in e["queryParams"]:
        d = f" — {q['desc'][:120]}" if q["desc"] else ""
        print(f"- query: {q['name']}: {q['type']}{d}")
    if e["body"]:
        print(f"- body ({e['body']['contentType']}):")
        for f in e["body"]["fields"]:
            w = "wajib" if f["required"] else "opsional"
            d = f" — {f['desc'][:120]}" if f["desc"] else ""
            print(f"    - {f['name']}: {f['type']} ({w}){d}")
    else:
        print("- body: tidak ada")
    print(f"- status sukses: {', '.join(e['successStatus']) or '-'}"
          + ("" if e["responseSchemaDocumented"] else " (schema response TIDAK terdokumentasi)"))
    if e["errorCodes"]:
        print("- kode yang disebut di deskripsi:")
        for k in e["errorCodes"]:
            info = idx.get(k)
            print(f"    - {k}" + (f" ({info['http']}) {info['message']}" if info else " (tidak ada di katalog)"))
    if e["description"]:
        baris = [b for b in e["description"].splitlines() if b.strip()][:12]
        print("- deskripsi (cuplikan):")
        for b in baris:
            print(f"    {b[:160]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--grep")
    ap.add_argument("--endpoint")
    ap.add_argument("--codes", action="store_true")
    ap.add_argument("--conventions", action="store_true")
    ap.add_argument("--exclude", default="")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    spec = muat(a.file)
    exclude = {x.strip() for x in a.exclude.split(",") if x.strip()}
    daftar = [ringkas(spec, p, m, o) for p, m, o in operasi(spec, exclude)]
    katalog = katalog_kode(spec)
    info = spec.get("info") or {}

    if a.grep:
        g = a.grep.lower()
        if a.codes:
            katalog = [k for k in katalog if g in k["message"].lower() or g in k["code"]]
        else:
            daftar = [e for e in daftar if g in (e["path"] + e["operationId"] + e["summary"]
                                                  + e["description"]).lower()]

    if a.codes:
        if a.json:
            print(json.dumps(katalog, ensure_ascii=False, indent=1))
            return
        print("| Kode | HTTP | Modul | Jenis | Pesan |")
        print("| --- | --- | --- | --- | --- |")
        for k in katalog:
            print(f"| {k['code']} | {k['http']} | {k['module']} | {k['kind']} | {k['message']} |")
        return

    if a.conventions:
        hasil = konvensi(daftar)
        if a.json:
            print(json.dumps(hasil, ensure_ascii=False, indent=1))
            return
        print(f"# Statistik konvensi: {info.get('title')} {info.get('version')}")
        for k, v in hasil.items():
            print(f"- {k}: {v}")
        return

    if a.endpoint:
        ids = [x.strip() for x in a.endpoint.split(",") if x.strip()]
        pilih = [e for e in daftar if e["operationId"] in ids]
        hilang = set(ids) - {e["operationId"] for e in pilih}
        if a.json:
            print(json.dumps(pilih, ensure_ascii=False, indent=1))
            return
        for e in pilih:
            cetak_detail(e, katalog)
        if hilang:
            print(f"\n(tidak ditemukan: {', '.join(sorted(hilang))})")
        return

    if a.json:
        print(json.dumps([{k: v for k, v in e.items() if k != "description"} for e in daftar],
                         ensure_ascii=False, indent=1))
        return
    print(f"# {info.get('title')} {info.get('version')} — {len(daftar)} endpoint"
          + (f" (exclude: {', '.join(sorted(exclude))})" if exclude else ""))
    cetak_daftar(daftar)


if __name__ == "__main__":
    main()
