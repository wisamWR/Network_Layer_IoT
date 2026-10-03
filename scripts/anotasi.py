"""Memberi kotak dan nomor pada baris paket penting di tangkapan layar tcpdump.

Baris paket dikenali dari timestamp di awal baris (OCR tesseract); satu paket
mencakup baris timestamp sampai sebelum timestamp berikutnya.
Jalankan dari folder laporan:  python3 scripts/anotasi.py
"""
import difflib, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

MERAH = (229, 50, 45)
TS = re.compile(r"(\d\d:\d\d:\d\d\.\d{6})")

# berkas -> daftar (timestamp awal, timestamp akhir, nomor)
TARGET = {
    "E2-01_tcpdump-arp.png": [("12:41:45.823824", "12:41:45.823824", "1")],
    "E2-02_tcpdump-ndp.png": [
        ("12:41:55.432071", "12:41:55.432071", "1"),
        ("12:41:55.432086", "12:41:55.432086", "2"),
        ("12:41:55.432312", "12:41:55.432312", "3"),
        ("12:41:55.432324", "12:41:55.432324", "4"),
    ],
    "E3-03_tcpdump-c0-tanpa-route.png": [
        ("13:03:20.826638", "13:03:22.856563", "1"),
        ("13:03:29.998877", "13:03:32.072638", "2"),
        ("13:03:59.514828", "13:04:01.576483", "3"),
    ],
    "E4-03_tcpdump-packet-too-big.png": [
        ("13:14:55.940237", "13:14:55.940237", "1"),
        ("13:14:55.940264", "13:14:55.940264", "2"),
    ],
}

def baris_teks(img):
    """Pita vertikal (atas, bawah) tiap baris teks, dari proyeksi horizontal."""
    g = img.convert("L")
    w, h = g.size
    px = g.load()
    isi = [sum(1 for x in range(0, w, 2) if px[x, y] > 90) > 2 for y in range(h)]
    pita, mulai = [], None
    for y, ada in enumerate(isi + [False]):
        if ada and mulai is None:
            mulai = y
        elif not ada and mulai is not None:
            pita.append((mulai, y - 1)); mulai = None
    return pita

def timestamp_ocr(img):
    """Posisi y tiap timestamp di kolom kiri."""
    besar = ImageOps.invert(img.convert("L")).resize((img.width * 3, img.height * 3))
    besar.save("/tmp/_ocr.png")
    out = subprocess.run(["tesseract", "/tmp/_ocr.png", "-", "--psm", "6", "tsv"],
                         capture_output=True, text=True).stdout
    hasil = {}
    for ln in out.splitlines()[1:]:
        k = ln.split("\t")
        if len(k) < 12:
            continue
        kata = k[11].replace("O", "0").replace("l", "1").lstrip("^C")
        # OCR kadang salah satu-dua karakter, jadi semua kata mirip timestamp disimpan
        if int(k[6]) < 400 * 3 and len(re.findall(r"\d", kata)) >= 10 and len(kata) <= 17:
            hasil.setdefault(kata, (int(k[7]) + int(k[9]) // 2) // 3)
    return hasil

def cari(ts, target):
    """Kata OCR yang paling mirip dengan timestamp target."""
    if target in ts:
        return target
    mirip = difflib.get_close_matches(target, list(ts), n=1, cutoff=0.8)
    return mirip[0] if mirip else None

def main():
    for nama, daftar in TARGET.items():
        img = Image.open(f"gambar/{nama}").convert("RGB")
        pita = baris_teks(img)
        ts = timestamp_ocr(img)
        def idx(y):
            return min(range(len(pita)), key=lambda i: abs((pita[i][0] + pita[i][1]) / 2 - y))
        awal_paket = sorted(idx(y) for y in ts.values())
        # kanvas dilebarkan ke kanan supaya nomor tidak menutupi teks
        lebar_asli = img.width
        kanvas = Image.new("RGB", (lebar_asli + 32, img.height), img.getpixel((2, 2)))
        kanvas.paste(img, (0, 0))
        img = kanvas
        d = ImageDraw.Draw(img)
        try:
            f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        except OSError:
            f = ImageFont.load_default()
        for t0, t1, no in daftar:
            k0, k1 = cari(ts, t0), cari(ts, t1)
            if k0 is None or k1 is None:
                sys.exit(f"{nama}: timestamp {t0}/{t1} tidak terbaca OCR; terbaca: {sorted(ts)}")
            if (k0, k1) != (t0, t1):
                print(f"  catatan: {t0}..{t1} dicocokkan dengan bacaan OCR {k0}..{k1}")
            a, b = idx(ts[k0]), idx(ts[k1])
            sesudah = [i for i in awal_paket if i > b]
            batas = (sesudah[0] - 1) if sesudah else len(pita) - 1
            # paket terakhir: ikutkan baris lanjutannya, berhenti di baris kosong
            akhir = b
            while akhir < batas and pita[akhir + 1][0] - pita[akhir][1] <= 14:
                akhir += 1
            y0, y1 = pita[a][0] - 3, pita[akhir][1] + 3
            d.rectangle([1, y0, lebar_asli - 1, y1], outline=MERAH, width=3)
            d.rectangle([lebar_asli + 4, y0, lebar_asli + 28, y0 + 22], fill=MERAH)
            d.text((lebar_asli + 11, y0 + 2), no, fill="white", font=f)
        keluar = nama.replace(".png", "_anotasi.png")
        img.save(f"gambar/{keluar}")
        print(nama, "->", keluar, "| timestamp terbaca:", len(ts))

main()
