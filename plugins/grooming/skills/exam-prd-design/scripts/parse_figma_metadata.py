#!/usr/bin/env python3
"""Ringkas output get_metadata Figma menjadi daftar modul, layar, anotasi, dan teks.

Pemakaian:
    python3 parse_figma_metadata.py <file_output_get_metadata> [opsi]

File input boleh berupa XML mentah atau JSON hasil simpanan tool
([{type: "text", text: "<xml...>"}]).

Opsi:
    --json            output terstruktur JSON (tanpa batas teks per baris)
    --summary         profil ringkas per modul (jumlah layar, kode US, platform)
    --section ID      proses satu section saja (detail penuh)
    --grep TEKS       hanya section/layar/label yang namanya mengandung TEKS
    --max-texts N     batas teks per layar pada output teks (default 8)
    --min-repeat N    teks tersembunyi yang muncul di >= N layar dianggap isi
                      bawaan komponen dan diringkas sekali (default 3; 0 = mati)

Dua struktur file dikenali:
  1. Mode section: canvas berisi <section> per modul — kode US sering ada di
     nama section ("... (US/BK/T3/26/07, 11)"), badge "Prioritas · P0 · US-xx"
     menempel di atas layar, caption "Label · ..." menerangkan layar di
     bawahnya. Papan anotasi (".Ringkasan modul", "Pertanyaan Terbuka untuk
     PO", "Riwayat Versi"), section "Arsip ·", dan sheet komponen dicatat
     terpisah, tidak dihitung sebagai layar.
  2. Mode legacy: canvas berisi frame layar + header "↳" (konvensi Digidoc).
     Header lebar = modul; header sempit di atas layar = label sub-alur/edge case.
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter

GENERIC_TEXT = {"Primary Text", "Label", "Label Menu", "Text", "Title", "*", "Digital", "Document"}

# Frasa spesifik yang menandai papan anotasi/info, bukan layar.
ANOTASI_PATTERNS = ("Pertanyaan Terbuka", "Riwayat Versi")
ARSIP_PREFIXES = ("Arsip ·", "Arsip —")
CAPTION_PREFIX = "Label ·"
# Sheet komponen/dokumentasi: selalu komponen, berapa pun ukurannya.
KOMPONEN_SHEET_RE = re.compile(
    r"^(Button|Icon|Badge|Chip|Input|Toggle|Avatar|Tab|Dokumentasi /)\s*·|^Dokumentasi /|sesuai IDDS"
)
# Prefiks yang bisa berupa komponen ATAU state layar (modal konfirmasi, toast sukses).
# Komponen hanya kalau ukurannya bukan ukuran layar.
STATE_RE = re.compile(r"^(Card|Alert|Toast|Modal|Dialog|Bottom ?Sheet|Popup|Snackbar)\s*·", re.I)
PRIORITAS_RE = re.compile(r"^Prioritas\s*·\s*(P\d+)\s*·\s*(.+)$")
US_PANJANG_RE = re.compile(r"US/[A-Z]{2}/[A-Z0-9]+/\d{2,4}/\d{1,3}")
KODE_RE = re.compile(r"(US|UC|FR|BR)-(\d+)")
PLATFORMS = ("Mobile App iOS", "Mobile App Android", "Mobile App", "Web", "Backoffice", "Desktop")
HEADER_PREFIX = "↳"

# Layar = node berukuran layar (desktop ~1440x1028, mobile 390x844, modal 1440x1024).
LAYAR_TAG = ("frame", "instance")
LAYAR_MIN_SISI = 280
LAYAR_MIN_SISI_TERPANJANG = 700
LEGACY_MIN_SISI = 200    # mode legacy: frame top-level sekecil ini masih dianggap layar
JARAK_BARIS = 300        # selisih y maksimum untuk dianggap satu baris
JARAK_TEMPEL = 140       # jarak maksimum caption/badge di atas layar


def load_xml(path):
    raw = open(path, encoding="utf-8").read()
    try:
        data = json.loads(raw)
        raw = "".join(x.get("text", "") for x in data if x.get("type") == "text")
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass
    start = raw.find("<")
    end = max(raw.rfind("</section>"), raw.rfind("</frame>"), raw.rfind("</canvas>"))
    closing = raw[end:].split(">", 1)[0] + ">" if end != -1 else ""
    xml = raw[start:end + len(closing)] if end != -1 else raw[start:]
    return ET.fromstring(xml)


def dims(node):
    def f(k):
        try:
            return float(node.get(k, 0))
        except ValueError:
            return 0.0
    return f("x"), f("y"), f("width"), f("height")


def bersih_header(nama):
    return nama.lstrip(HEADER_PREFIX + " ").strip()


def parse_kode(teks):
    """Kode US/UC/FR/BR dari sebuah nama. Token angka murni melanjutkan kode
    sebelumnya: 'US/BK/T3/26/07, 11' -> 07 dan 11; 'UC-09, 11, 12' -> 09, 11, 12."""
    hasil = []
    for grup in re.findall(r"\(([^()]*)\)", teks):
        basis = None
        for token in re.split(r"[·;,]", grup):
            token = token.strip()
            if not token:
                continue
            if US_PANJANG_RE.fullmatch(token):
                basis = token.rsplit("/", 1)[0] + "/"
                hasil.append(token)
                continue
            m = KODE_RE.fullmatch(token)
            if m:
                basis = m.group(1) + "-"
                hasil.append(token)
                continue
            if token.isdigit() and basis:
                hasil.append(basis + token)
    for m in US_PANJANG_RE.finditer(teks):
        if m.group(0) not in hasil:
            hasil.append(m.group(0))
    for m in KODE_RE.finditer(teks):
        kode = f"{m.group(1)}-{m.group(2)}"
        if kode not in hasil:
            hasil.append(kode)
    return hasil


def deteksi_platform(nama):
    for p in PLATFORMS:
        if p in nama:
            return p
    return "-"


def texts_of(node):
    """(teks terlihat, teks tersembunyi) dari seluruh subpohon node."""
    terlihat, sembunyi = [], []

    def walk(n, hidden):
        hidden = hidden or n.get("hidden") == "true"
        if n.tag == "text":
            nama = (n.get("name") or "").strip()
            if nama:
                (sembunyi if hidden else terlihat).append(nama)
        for c in n:
            walk(c, hidden)

    walk(node, False)
    terlihat = [t for t in dict.fromkeys(terlihat) if t not in GENERIC_TEXT]
    sembunyi = list(dict.fromkeys(sembunyi))
    return terlihat, sembunyi


def ukuran_layar(tag, w, h):
    if tag not in LAYAR_TAG:
        return False
    return min(w, h) >= LAYAR_MIN_SISI and max(w, h) >= LAYAR_MIN_SISI_TERPANJANG


def klasifikasi(node):
    """Bucket satu node anak: layar / caption / anotasi / arsip / komponen / sembunyi / kecil."""
    tag = node.tag
    nama = (node.get("name") or "").strip()
    if node.get("hidden") == "true":
        return "sembunyi"
    x, y, w, h = dims(node)
    seukuran_layar = ukuran_layar(tag, w, h)
    if tag in ("symbol", "component", "componentSet") or KOMPONEN_SHEET_RE.search(nama):
        return "komponen"
    if STATE_RE.search(nama) and not seukuran_layar:
        return "komponen"
    if nama.startswith(ARSIP_PREFIXES):
        return "arsip"
    if nama.startswith(".") or any(p in nama for p in ANOTASI_PATTERNS):
        return "anotasi"
    if nama.startswith(CAPTION_PREFIX) or PRIORITAS_RE.match(nama):
        return "caption"
    if seukuran_layar:
        return "layar"
    return "kecil"


def overlap_x(a, b):
    kiri = max(a["x"], b["x"])
    kanan = min(a["x"] + a["w"], b["x"] + b["w"])
    return max(0.0, kanan - kiri)


def buat_layar(node, platform="-"):
    nama = (node.get("name") or "").strip()
    x, y, w, h = dims(node)
    terlihat, sembunyi = texts_of(node)
    return {
        "id": node.get("id"), "name": nama, "x": x, "y": y, "w": w, "h": h,
        "generic": nama.lower().startswith("frame ") or nama == "Frame",
        "platform": platform, "groups": [],
        "us": [], "prioritas": None, "caption": "",
        "texts": terlihat, "hidden_texts": sembunyi, "hidden_bawaan": [],
    }


def node_kecil(node):
    x, y, w, h = dims(node)
    return {"id": node.get("id"), "name": (node.get("name") or "").strip(),
            "x": x, "y": y, "w": w, "h": h}


def tempel_caption(screens, kecil_nodes):
    """Tempelkan caption ('Label · ...') dan badge ('Prioritas · P0 · US-xx')
    ke layar tepat di bawahnya (x tumpang tindih, y berjarak dekat)."""
    for s in screens:
        kandidat = []
        for c in kecil_nodes:
            if not (c["y"] + c["h"] <= s["y"] + 2 <= c["y"] + c["h"] + JARAK_TEMPEL):
                continue
            if overlap_x(c, s) < 0.5 * min(c["w"], s["w"]):
                continue
            kandidat.append((s["y"] - (c["y"] + c["h"]), c))
        for _, c in sorted(kandidat, key=lambda k: k[0]):
            m = PRIORITAS_RE.match(c["name"])
            if m:
                if s["prioritas"] is None:
                    s["prioritas"] = m.group(1)
                    s["us"] = [u for u in s["us"] + parse_kode(m.group(2)) if u not in s["us"]]
            elif not s["caption"]:
                s["caption"] = c["name"]


def kelompokkan_baris(screens):
    screens.sort(key=lambda s: (s["y"], s["x"]))
    rows, last_y = [], None
    for s in screens:
        if last_y is None or abs(s["y"] - last_y) > JARAK_BARIS:
            rows.append([])
        rows[-1].append(s)
        last_y = s["y"]
    return rows


def proses_section(sec):
    nama = (sec.get("name") or "").strip()
    kategori = klasifikasi(sec)
    if kategori == "komponen" and STATE_RE.search(nama):
        kategori = "modul"  # section "Modal · ..." berisi layar, bukan sheet komponen
    if kategori in ("layar", "kecil", "caption"):
        kategori = "modul"
    data = {
        "id": sec.get("id"), "name": nama, "kategori": kategori,
        "platform": deteksi_platform(nama), "us": parse_kode(nama),
        "prioritas": [], "screens": [], "anotasi": [], "arsip": [],
        "komponen": [], "sembunyi": [], "rows": [], "subsections": [],
    }

    screens, kecil = [], []
    for c in sec:
        if c.tag == "section":
            data["subsections"].append(proses_section(c))
            continue
        bucket = klasifikasi(c)
        if bucket == "layar":
            screens.append(buat_layar(c, data["platform"]))
        elif bucket == "caption":
            kecil.append(node_kecil(c))
        elif bucket in ("anotasi", "arsip", "komponen", "sembunyi"):
            node = {"id": c.get("id"), "name": (c.get("name") or "").strip(), "kind": bucket}
            if bucket in ("anotasi", "arsip"):
                t, th = texts_of(c)
                node["texts"] = t
                node["n_hidden_texts"] = len(th)
            data[bucket].append(node)

    tempel_caption(screens, kecil)
    for s in screens:
        for u in data["us"]:
            if u not in s["us"]:
                s["us"].append(u)
        if s["prioritas"] and s["prioritas"] not in data["prioritas"]:
            data["prioritas"].append(s["prioritas"])
    data["screens"] = screens
    data["rows"] = kelompokkan_baris(screens)
    return data


def semua_layar_section(sections):
    for s in sections:
        yield from s["screens"]
        yield from semua_layar_section(s["subsections"])


def proses_legacy(root):
    """Konvensi Digidoc: frame layar + header '↳' rata di satu canvas."""
    headers, screens, captions = [], [], []
    lain = {"anotasi": [], "arsip": [], "komponen": [], "sembunyi": [], "lainnya": []}
    for c in root:
        bucket = klasifikasi(c)
        nama = (c.get("name") or "").strip()
        x, y, w, h = dims(c)
        if (bucket == "komponen" and STATE_RE.search(nama) and c.tag in LAYAR_TAG
                and min(w, h) >= LEGACY_MIN_SISI):
            bucket = "layar"  # modal/dialog lepas di canvas legacy = state layar
        if bucket in ("anotasi", "arsip", "komponen", "sembunyi"):
            node = {"id": c.get("id"), "name": nama, "kind": bucket, "x": x, "y": y, "w": w, "h": h}
            if bucket in ("anotasi", "arsip"):
                t, th = texts_of(c)
                node["texts"] = t
                node["n_hidden_texts"] = len(th)
            lain[bucket].append(node)
            continue
        if nama.startswith(HEADER_PREFIX):
            headers.append(dict(node_kecil(c), kind="header"))
        elif bucket == "caption":
            captions.append(node_kecil(c))
        elif h <= 80 and w >= 600:  # bar lebar tanpa "↳" tetap dianggap header
            headers.append(dict(node_kecil(c), kind="header"))
        elif bucket == "layar" or (c.tag in LAYAR_TAG and min(w, h) >= LEGACY_MIN_SISI):
            screens.append(buat_layar(c))
        else:  # panah, teks lepas, sticky note, dll.
            lain["lainnya"].append({"id": c.get("id"), "name": nama, "kind": c.tag})

    widest = max((hd["w"] for hd in headers), default=0)
    modules = [hd for hd in headers if hd["w"] >= max(3000, widest * 0.5)]
    labels = [hd for hd in headers if hd not in modules]

    def gap(hd, s):  # jarak horizontal layar ke rentang header (0 = tertutup)
        return max(0.0, hd["x"] - s["x"], s["x"] + s["w"] - (hd["x"] + hd["w"]))

    tempel_caption(screens, captions)
    for s in screens:
        above = [m for m in modules if m["y"] < s["y"]]
        if above:  # modul: header lebar terdekat secara horizontal
            m = min(above, key=lambda m: (gap(m, s), s["y"] - m["y"]))
            s["groups"].append(bersih_header(m["name"]))
        # label sub-alur/edge case: header sempit terdekat di atas layar
        lab = [hd for hd in labels if hd["y"] < s["y"] and gap(hd, s) <= 1]
        if lab:
            s["groups"].append(bersih_header(max(lab, key=lambda hd: hd["y"])["name"]))
    return {"headers": headers, "modules": modules, "labels": labels,
            "screens": kelompokkan_baris(screens), "lain": lain}


def pisahkan_teks_bawaan(screens, min_repeat):
    """Teks tersembunyi yang berulang di >= min_repeat layar = isi bawaan komponen
    (captcha, slot suffix, dll.). Dipindah ke hidden_bawaan; dikembalikan dengan hitungannya."""
    if min_repeat <= 0:
        return Counter()
    hitung = Counter(t for s in screens for t in set(s["hidden_texts"]))
    bawaan = Counter({t: n for t, n in hitung.items() if n >= min_repeat})
    for s in screens:
        s["hidden_bawaan"] = [t for t in s["hidden_texts"] if t in bawaan]
        s["hidden_texts"] = [t for t in s["hidden_texts"] if t not in bawaan]
    return bawaan


def potong(teks_list, maks, panjang_baris=160):
    if not teks_list:
        return "-"
    tampil = [t[:panjang_baris] for t in teks_list[:maks]]
    sisa = len(teks_list) - len(tampil)
    out = " | ".join(tampil)
    if sisa > 0:
        out += f" …+{sisa} lagi"
    return out


def cetak_bawaan(bawaan, min_repeat):
    if not bawaan:
        return
    daftar = [f"{t[:60]} ({n})" for t, n in bawaan.most_common(12)]
    sisa = len(bawaan) - len(daftar)
    print(f"teks tersembunyi bawaan komponen (muncul di ≥{min_repeat} layar, bukan temuan): "
          + " | ".join(daftar) + (f" …+{sisa} lagi" if sisa > 0 else ""))


def label_layar(s):
    parts = []
    if s["groups"]:
        parts.append("grup: " + " > ".join(s["groups"]))
    if s["caption"]:
        parts.append("caption: " + s["caption"][:120])
    return (" | " + " | ".join(parts)) if parts else ""


def cetak_ringkasan_legacy(root_name, legacy, bawaan, min_repeat):
    semua = [s for r in legacy["screens"] for s in r]
    print(f"# {root_name} — ringkasan (mode legacy)")
    print(f"canvas: modul={len(legacy['modules'])} label={len(legacy['labels'])} layar={len(semua)} "
          f"generik={sum(s['generic'] for s in semua)} "
          f"anotasi={len(legacy['lain']['anotasi'])} arsip={len(legacy['lain']['arsip'])} "
          f"komponen={len(legacy['lain']['komponen'])} lainnya={len(legacy['lain']['lainnya'])} "
          f"teks-sembunyi-unik={sum(len(s['hidden_texts']) for s in semua)}")
    cetak_bawaan(bawaan, min_repeat)
    per_modul = {}
    for s in semua:
        per_modul.setdefault(s["groups"][0] if legacy["modules"] and s["groups"] else "(tanpa modul)", []).append(s)
    print("\n## Modul (header ↳ lebar)")
    for m in sorted(legacy["modules"], key=lambda m: (m["y"], m["x"])):
        isi = per_modul.get(bersih_header(m["name"]), [])
        label = sorted({s["groups"][1] for s in isi if len(s["groups"]) > 1})
        print(f"- {m['id']} | {bersih_header(m['name'])} | layar={len(isi)} | "
              f"generik={sum(s['generic'] for s in isi)} | "
              f"teks-sembunyi-unik={sum(len(s['hidden_texts']) for s in isi)} | "
              f"label: {', '.join(label) or '-'}")
    if "(tanpa modul)" in per_modul:
        isi = per_modul["(tanpa modul)"]
        label = sorted({g for s in isi for g in s["groups"]})
        print(f"- (tanpa header modul) | layar={len(isi)} | label: {', '.join(label) or '-'}")


def cetak_ringkasan_section(root_name, sections, bawaan, min_repeat):
    semua = list(semua_layar_section(sections))
    print(f"# {root_name} — ringkasan (mode section)")
    print(f"canvas: section={len(sections)} layar={len(semua)} "
          f"generik={sum(x['generic'] for x in semua)} "
          f"teks-sembunyi-unik={sum(len(x['hidden_texts']) for x in semua)} "
          f"arsip={sum(1 for s in sections if s['kategori'] == 'arsip')}")
    cetak_bawaan(bawaan, min_repeat)

    def baris(s, level):
        layar = list(semua_layar_section([s]))
        pri = ",".join(s["prioritas"]) or "-"
        us = ", ".join(s["us"]) or "-"
        print(f"{'  ' * level}- {s['id']} | {s['kategori']} | {s['name']} | {s['platform']} | US={us} | "
              f"{pri} | layar={len(layar)} | teks-sembunyi-unik="
              f"{sum(len(x['hidden_texts']) for x in layar)}")
        for sub in s["subsections"]:
            baris(sub, level + 1)

    for s in sections:
        baris(s, 0)


def cetak_layar(x, max_texts, indent=""):
    flag = " [nama generik]" if x["generic"] else ""
    pri = f" {x['prioritas']}" if x["prioritas"] else ""
    print(f"{indent}- {x['id']} | {x['name']}{flag} | {x['w']:.0f}x{x['h']:.0f}{pri}{label_layar(x)}")
    print(f"{indent}    teks: {potong(x['texts'], max_texts)}")
    if x["hidden_texts"]:
        print(f"{indent}    teks-sembunyi ({len(x['hidden_texts'])}): {potong(x['hidden_texts'], 4)}")


def cetak_section(s, max_texts, level=0):
    indent = "  " * level
    print(f"\n{indent}## {s['name']} ({s['id']})")
    print(f"{indent}   kategori={s['kategori']} · platform={s['platform']} · "
          f"US={', '.join(s['us']) or '-'} · prioritas={','.join(s['prioritas']) or '-'} · "
          f"layar={len(s['screens'])}"
          + (f" (+{sum(1 for _ in semua_layar_section(s['subsections']))} di subsection)"
             if s["subsections"] else ""))
    if s["kategori"] == "arsip":
        print(f"{indent}   (arsip — dikecualikan dari review; hanya dihitung)")
        return
    for sub in s["subsections"]:
        cetak_section(sub, max_texts, level + 1)
    for i, row in enumerate(s["rows"], 1):
        print(f"{indent}### Baris {i} (y ≈ {row[0]['y']:.0f})")
        for x in row:
            cetak_layar(x, max_texts, indent)
    for node in s["anotasi"]:
        print(f"{indent}- [anotasi] {node['id']} | {node['name']}")
        print(f"{indent}    teks: {potong(node.get('texts', []), 20, 200)}")
    for node in s["arsip"]:
        print(f"{indent}- [arsip] {node['id']} | {node['name']} | teks: {potong(node.get('texts', []), 4)}")
    for node in s["komponen"]:
        print(f"{indent}- [komponen] {node['id']} | {node['name']}")


def cocok(pat, s):
    return pat in s["name"].lower() or any(pat in g.lower() for g in s["groups"]) \
        or pat in s["caption"].lower()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--section", help="id section yang mau ditampilkan detail")
    ap.add_argument("--grep", help="filter nama section/layar/label mengandung teks ini")
    ap.add_argument("--max-texts", type=int, default=8)
    ap.add_argument("--min-repeat", type=int, default=3)
    args = ap.parse_args()

    root = load_xml(args.file)
    sections = [proses_section(c) for c in root if c.tag == "section"]
    legacy = proses_legacy(root) if not sections else None
    root_name = (root.get("name") or "").strip()

    # Deteksi teks bawaan dihitung dari SELURUH file, sebelum filter --section/--grep,
    # supaya hasilnya sama di setiap batch.
    semua = [s for r in legacy["screens"] for s in r] if legacy else list(semua_layar_section(sections))
    bawaan = pisahkan_teks_bawaan(semua, args.min_repeat)

    if args.grep:
        pat = args.grep.lower()
        if legacy:
            legacy["screens"] = [r for r in ([s for s in row if cocok(pat, s)] for row in legacy["screens"]) if r]
        else:
            sections = [s for s in sections if pat in s["name"].lower()
                        or any(cocok(pat, x) for x in semua_layar_section([s]))]
    if args.section:
        sections = [s for s in sections if s["id"] == args.section]
        if not sections:
            sys.exit(f"section {args.section} tidak ditemukan")

    if args.json:
        meta = {"root": root_name, "teks_bawaan": dict(bawaan.most_common())}
        if legacy:
            print(json.dumps({**meta, "mode": "legacy", **legacy}, ensure_ascii=False, indent=1))
        else:
            print(json.dumps({**meta, "mode": "section", "sections": sections}, ensure_ascii=False, indent=1))
        return
    if args.summary:
        if legacy:
            cetak_ringkasan_legacy(root_name, legacy, bawaan, args.min_repeat)
        else:
            cetak_ringkasan_section(root_name, sections, bawaan, args.min_repeat)
        return

    if legacy:
        total = sum(len(r) for r in legacy["screens"])
        generic = sum(1 for r in legacy["screens"] for s in r if s["generic"])
        print(f"# {root_name} ({root.get('id')}) - {total} layar, {len(legacy['headers'])} header, "
              f"{generic} nama generik")
        cetak_bawaan(bawaan, args.min_repeat)
        print("\n## Header grup (↳)")
        for hd in sorted(legacy["headers"], key=lambda hd: (hd["y"], hd["x"])):
            jenis = "modul" if hd in legacy["modules"] else "label"
            print(f"- {hd['id']} | {jenis} | {hd['name'].strip()} | "
                  f"x {hd['x']:.0f}-{hd['x'] + hd['w']:.0f}, y {hd['y']:.0f}")
        for bucket, nodes in legacy["lain"].items():
            if bucket == "lainnya":
                if nodes:
                    print(f"- [lainnya] {len(nodes)} node non-layar diabaikan (panah, teks lepas, dll.)")
                continue
            for n in nodes:
                print(f"- [{bucket}] {n['id']} | {n['name']}")
        for r, row in enumerate(legacy["screens"], 1):
            print(f"\n## Baris {r} (y ≈ {row[0]['y']:.0f}), kiri ke kanan")
            for s in row:
                cetak_layar(s, args.max_texts)
        return

    total = sum(1 for _ in semua_layar_section(sections))
    generic = sum(1 for x in semua_layar_section(sections) if x["generic"])
    print(f"# {root_name} ({root.get('id')}) — mode section · section={len(sections)} · "
          f"layar={total} · generik={generic}")
    cetak_bawaan(bawaan, args.min_repeat)
    for s in sections:
        cetak_section(s, args.max_texts)


if __name__ == "__main__":
    main()
