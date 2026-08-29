# 🛠️ TOOLBOX CLI — Modern Linux Utility Toolbox

**Toolbox (`tool`)**, Linux kullanıcılarının günlük dosya dönüştürme, medya işleme, veri biçimlendirme, şifreleme ve metin analiz gibi tüm işlerini tek bir komut altında toplamak amacıyla tasarlanmış **hızlı, modüler ve güçlü bir Linux CLI uygulamasıdır.**

Terminalde onlarca farklı araç kurmak veya karmaşık `ffmpeg` / `convert` parametreleri hatırlamak yerine, tüm işlemlerinizi tek bir `tool` komutu ile halledebilirsiniz.

---

## 🚀 Öne Çıkan Özellikler & Tüm Dosya Türleri Çözümleri

Toolbox CLI, her dosya ve veri türü için özel çözümler sunar:

### 📸 1. Görsel & Resim Dönüştürme (Image & GIF)
* **Desteklenen Formatlar:** PNG, JPG, JPEG, WEBP, BMP, TIFF, GIF.
* **Format Dönüştürme:** `tool image-convert input.png webp` (kalite ayarı `--quality` destekli).
* **Boyutlandırma (Resize):** `tool image-resize image.png 1920x1080`
* **Sıkıştırma (Compress):** `tool image-compress image.jpg`
* **Kırpma (Crop):** `tool image-crop image.png 800x600`
* **GIF Kare Çıkarma (GIF Frames):**
  * `tool gif-to-png animation.gif`
  * `tool gif-to-jpg animation.gif`
  * `tool gif-to-webp animation.gif`

---

### 🎥 2. Video & Ses Dönüştürme (Video & Audio via FFmpeg)
* **Genel Medya Dönüştürücü:** `tool media-convert video.mkv mp4`, `tool media-convert song.flac mp3` (Tüm video/ses formatları arası sınırsız dönüşüm).
* **MP3 → MP4 (Kapak Görselli Video):** `tool mp3-to-mp4 song.mp3 cover.jpg`
* **Ses Çıkarma:**
  * `tool mp4-to-mp3 video.mp4`
  * `tool mp4-to-wav video.mp4`
* **Video → GIF & WebM:**
  * `tool mp4-to-gif video.mp4` (Yüksek kaliteli 2-pass palet üretimi ile)
  * `tool mp4-to-webm video.mp4`
* **Video Düzenleme:**
  * **Trim (Kırpma):** `tool video-trim video.mp4 00:10 00:30`
  * **Resize (Yeniden Boyutlandırma):** `tool video-resize video.mp4 1280x720`
  * **Compress (Sıkıştırma):** `tool video-compress video.mp4`

---

### 📐 3. Genel Birim Dönüştürücü (Unit Converter)
* **Mesafe/Uzunluk:** km, m, cm, mm, miles, yd, ft, in
* **Ağırlık:** kg, g, mg, lb, oz, t
* **Sıcaklık:** Celsius (`c`), Fahrenheit (`f`), Kelvin (`k`)
* **Veri Depolama:** bytes (`b`), kb, mb, gb, tb, pb
* **Zaman:** ms, s, min, hours, days, weeks
* **Hız & Alan & Hacim:** kph, mph, m2, km2, acre, ha, liters, gal
* **Kullanım:** `tool convert 10 km miles`, `tool convert 100 c f`, `tool convert 5 gb mb`

---

### 📄 4. Veri & Kodlama & SQL Dönüştürme (Data, SQL & Encoding)
* **SQL → JSON Dönüştürücü:**
  * SQL script / Dump dosyası veya `.db`/`.sqlite` veritabanı dosyasından JSON üretimi:
    ```bash
    tool sql-to-json dump.sql
    tool sql-to-json database.db --table users
    cat dump.sql | tool sql-to-json
    ```
* **JSON → SQL Dönüştürücü:**
  * JSON nesne dizisinden SQL `CREATE TABLE` ve `INSERT INTO` cümleleri üretimi:
    ```bash
    tool json-to-sql users.json --table users
    ```
* **CSV ↔ JSON Dönüştürme:**
  * `tool csv-to-json data.csv`
  * `tool json-to-csv data.json`
* **XML → JSON Dönüştürücü:**
  * `tool xml-to-json document.xml`
* **JSON:**
  * Biçimlendirme (Pretty): `tool json pretty data.json`
  * Sıkıştırma (Minify): `tool json minify data.json`
  * Doğrulama (Validate): `tool json validate data.json`
  * **STDIN Desteği:** `cat data.json | tool json pretty`
* **Base64:** `tool base64 encode "Hello"`, `tool base64 decode "SGVsbG8="` (Metin veya Dosya desteği)
* **URL:** `tool url encode "hello world"`, `tool url decode "hello%20world"`

---

### 🔐 5. Hash & Kripto & Rastgele Üretim (Crypto & Random)
* **Streaming Hash (RAM dostu):** `tool hash sha256 file.txt` (MD5, SHA1, SHA256, SHA512, STDIN destekli)
* **UUID:** `tool uuid` (Cryptographically strong UUID v4)
* **Rastgele Üretici (`secrets` tabanlı):**
  * Sayı: `tool random number 1 100`
  * String: `tool random string 32`
  * Güvenli Parola: `tool random password 24`

---

### 📁 6. Dosya & Arşiv İşlemleri (File & Archive)
* **Dosya Bilgisi:** `tool file info image.png` (Ad, Yol, Tür, Boyut, Düzenleme Tarihi, İzinler)
* **Dizin Boyutu:** `tool file size ./project` (Recursive boyut hesaplama)
* **Arşivleme:**
  * `tool zip folder/ output.zip`
  * `tool unzip archive.zip output_dir/` (Zip Slip / Path traversal korumalı)

---

### 📝 7. Metin İşleme Araçları (Text Utilities)
* **Metin İstatistiği:** `tool text count file.txt` (Satır, Kelime, Karakter, Bayt)
* **Büyütme/Küçültme:** `tool text upper "hello"`, `tool text lower "HELLO"`
* **URL Slug Oluşturma:** `tool text slug "Ünlü Şarkıcı!"` -> `unlu-sarkici` (Türkçe karakter desteği ile)

---

## 🛠️ Kurulum (Installation)

### 1. Sistem Bağımlılıkları (FFmpeg)

Video ve ses dönüştürme özellikleri için sisteminizde `ffmpeg` yüklü olmalıdır:

* **Debian / Ubuntu:**
  ```bash
  sudo apt update && sudo apt install ffmpeg
  ```
* **Fedora / RHEL:**
  ```bash
  sudo dnf install ffmpeg
  ```
* **Arch Linux:**
  ```bash
  sudo pacman -S ffmpeg
  ```
* **openSUSE:**
  ```bash
  sudo zypper install ffmpeg
  ```

---

### 2. Toolbox CLI Kurulumu

Geliştirme modunda kurulum:
```bash
pip install -e .
```

Görsel işleme (Pillow) desteği ile kurulum:
```bash
pip install -e '.[images]'
```

Kullanıcı ortamına global olarak kurmak için (`pipx` önerilir):
```bash
pipx install .
```

Kurulum sonrası komutu test edin:
```bash
tool --help
tool --version
```

---

## 📖 Kullanım Örnekleri

```bash
# Yardım ve Komut Listesi
tool --help
tool help convert

# Birim Dönüştürme
tool convert 10 km miles
tool convert 100 c f
tool convert 5 gb mb

# JSON ve Base64
tool json pretty data.json
echo '{"status": "ok"}' | tool json pretty
tool base64 encode "Hello World"

# Hash & Şifre
tool hash sha256 archive.tar.gz
tool random password 32

# Medya & Video
tool image-convert photo.png webp
tool mp3-to-mp4 song.mp3 cover.jpg
tool media-convert video.mkv mp4
tool video-trim video.mp4 00:10 00:30

# Arşiv
tool zip ./my_folder archive.zip
tool unzip archive.zip ./extracted
```

---

## 🧪 Testleri Çalıştırma

Projeyi test etmek için `pytest` kullanabilirsiniz:

```bash
PYTHONPATH=src pytest
```

---

## 🏗️ Proje Mimarisi

```text
src/toolbox/
├── cli.py              # CLI Giriş Noktası & Kategorik Yardım Formatlayıcı
├── errors.py           # Merkezi Hata Tipleri (AppError, DependencyError)
├── commands/           # CLI Komut Katmanı (Media, Video, Convert, Data, Crypto, File, Text)
├── services/           # İş Mantığı (FFmpeg, Pillow, Converters)
└── utils/              # Yardımcı Fonksiyonlar (Files, Formatting, Output)
```

---

## 📜 Lisans

MIT License.
