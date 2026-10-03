# Laporan Internet / Network Layer (IoT Laptop Lab 2)

Laporan praktikum **Laptop Lab 2: Internet/Network Layer** pada mata kuliah IoT, Universitas Gadjah Mada.
Repositori ini berisi sumber laporan (LaTeX), hasil kompilasi, serta seluruh bukti eksperimen
(tangkapan layar, log terminal, dan kode) yang dirujuk di dalam laporan.

**Penulis:** Mohammad Wisam Wiraghina

## Ringkasan

Eksperimen dijalankan pada VM Ubuntu 24.04 LTS dengan tiga *network namespace* yang dihubungkan
pasangan *veth*, sehingga membentuk jaringan *dual-stack* (IPv4 + IPv6) yang terisolasi:

```text
iot-sensor ──(s0 ↔ r0)── iot-router ──(r1 ↔ c0)── iot-cloud
10.10.1.2/24            10.10.1.1/24 | 10.10.2.1/24            10.10.2.2/24
2001:db8:1::2/64        2001:db8:1::1 | 2001:db8:2::1          2001:db8:2::2/64
```

| No. | Eksperimen | Konsep yang diamati |
|-----|------------|---------------------|
| 1 | Topologi dan baseline | Alamat, tabel *route*, `ping` end-to-end |
| 2 | ARP dan Neighbor Discovery | Resolusi MAC *next-hop* di IPv4 dan IPv6 |
| 3 | TTL / hop limit, *route* balik, *forwarding* | Kegagalan karena *return route* hilang dan `ip_forward` mati |
| 4 | Path MTU | *Packet Too Big* (IPv6) dan *Fragmentation needed* (IPv4) pada MTU 1280 |
| 5 | HTTP melalui IPv6 | Komunikasi aplikasi *sensor* ke *cloud* |

## Struktur Repositori

```text
.
├── laporan_internet_layer.tex     # sumber laporan (LaTeX, kelas report)
├── laporan_internet_layer.pdf     # hasil kompilasi (PDF)
├── laporan_internet_layer.docx    # salinan Word (untuk Google Docs)
├── gambar/                        # tangkapan layar asli E0..E7, versi beranotasi (*_anotasi.png), logo-ugm.png
├── log/                           # salinan teks keluaran Terminal A dan B tiap eksperimen
├── code/
│   ├── network_lab.sh             # skrip pembentuk topologi (up | down)
│   └── http_client.py             # klien HTTP IPv6 untuk Eksperimen 5
└── scripts/
    └── anotasi.py                 # pembuat kotak dan nomor merah pada tangkapan layar tcpdump
```

Penamaan tangkapan layar mengikuti pola `E<eksperimen>-<urutan>_<deskripsi>.png`,
sedangkan log mengikuti `E<eksperimen>_<terminal>_<deskripsi>.txt`.

## Menjalankan Ulang Eksperimen

Jalankan di VM Ubuntu (atau Linux lain dengan `iproute2` dan `tcpdump`), dari folder `code/`:

```bash
sudo apt install -y iproute2 tcpdump python3
sudo bash network_lab.sh up      # membentuk iot-sensor, iot-router, iot-cloud
# ... lakukan eksperimen (lihat laporan) ...
sudo bash network_lab.sh down    # membersihkan; hentikan proses di namespace terlebih dahulu
```

Seluruh perintah dan keluaran tiap eksperimen dibahas pada laporan; salinan teks keluarannya ada di `log/`.

## Mengompilasi Laporan

Dibutuhkan distribusi TeX (MiKTeX atau TeX Live). Dari folder ini:

```bash
latexmk -pdf laporan_internet_layer.tex
# atau, jalankan dua kali agar daftar isi benar:
pdflatex laporan_internet_layer.tex
pdflatex laporan_internet_layer.tex
```

Paket LaTeX yang dipakai: `geometry`, `mathptmx`, `lm` (font `lmtt`), `graphicx`, `xcolor`, `listings`,
`upquote`, `enumitem`, `titlesec`, `titletoc`, `array`, `tabularx`, `amsmath`, `float`, `placeins`,
`caption`, `setspace`, `indentfirst`, `microtype`, `tikz`, `hyperref`.

## Membuat Ulang Gambar Beranotasi (opsional)

```bash
pip install pillow
sudo apt install -y tesseract-ocr    # atau pasang tesseract untuk OS masing-masing
python3 scripts/anotasi.py
```

Skrip membaca tangkapan layar tcpdump di `gambar/` dan menghasilkan berkas `*_anotasi.png`.
