# ⚡ CONV CLI

**`conv`**, Linux kullanıcılarının günlük dosya dönüştürme, medya işleme, veri biçimlendirme, şifreleme ve metin analiz işlemlerini tek bir komut altında hızlıca yapmasını sağlayan minimalist ve güçlü bir CLI aracıdır.

---

## 📦 Kurulum

```bash
# Proje dizininde kuruluma başlayın
pip install -e .

# Opsiyonel: Görsel işleme (Pillow) desteği ile kurulum
pip install -e '.[images]'
```

Kurulum tamamlandıktan sonra komutun çalıştığını doğrulayın:

```bash
conv --version
```

> **Not:** Video ve ses dönüştürme işlemleri için sisteminizde **FFmpeg** yüklü olmalıdır (`sudo apt install ffmpeg` veya `sudo dnf install ffmpeg`).

---

## 🚀 Hızlı Kullanım Rehberi

### 1. 🎥 Medya, Video ve Ses Dönüştürme
```bash
# Her türlü video / ses formatını birbirine dönüştürme (MKV, MP4, FLAC, MP3, WAV vb.)
conv media-convert video.mkv mp4
conv media-convert song.flac mp3

# MP3'ten kapak görselli MP4 video oluşturma
conv mp3-to-mp4 song.mp3 cover.jpg

# Ses çıkarma ve video kırpma
conv mp4-to-mp3 video.mp4
conv video-trim video.mp4 00:10 00:30
```

### 2. 🖼️ Görsel ve GIF İşlemleri
```bash
# Format dönüştürme, boyutlandırma ve sıkıştırma
conv image-convert photo.png webp
conv image-resize photo.png 1920x1080
conv image-compress photo.jpg

# GIF karelerini resim olarak dışa aktarma
conv gif-to-png animation.gif
```

### 3. 📄 Veri, SQL & Kodlama Dönüştürme
```bash
# SQL Script / SQLite (.db) dosyasından JSON üretme
conv sql-to-json dump.sql
conv sql-to-json database.db --table users

# JSON → SQL & CSV ↔ JSON
conv json-to-sql users.json --table users
conv csv-to-json data.csv
conv json-to-csv data.json

# JSON Pretty & Base64 / URL Encode
conv json pretty data.json
conv base64 encode "Hello World"
conv url encode "hello world"
```

### 4. 📐 Birim Dönüştürücü (Unit Converter)
```bash
conv convert 10 km miles
conv convert 100 c f
conv convert 5 gb mb
```

### 5. 🔐 Hash, UUID & Şifre Üretici
```bash
conv hash sha256 file.txt
conv uuid
conv random password 24
```

### 6. 📁 Dosya & Metin Araçları
```bash
conv file info image.png
conv file size ./project
conv zip folder/ output.zip
conv text slug "Ünlü Şarkıcı!"
```

---

## 🧪 Testleri Çalıştırma

```bash
PYTHONPATH=src pytest
```

---

## 📜 Lisans
MIT License
# FileCoverter
