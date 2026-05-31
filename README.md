# 🤖 Roblox-Automation

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)]()

> **⚠️ Uyarı / Disclaimer:** Bu araç **sadece eğitim amaçlıdır**. Roblox otomasyonu, Roblox'un Kullanım Şartları'nı ihlal eder. Hesap yasaklamalarından ve diğer olası sorunlardan yazarlar sorumlu değildir. Kullanım tamamen kendi sorumluluğunuzdadır.

Web arayüzü, proxy desteği ve e-posta doğrulama içeren kapsamlı bir Roblox hesap otomasyon aracı. Hesap oluşturma, mevcut hesaplarla giriş yapma, gruplara katılma, oyunları beğenme, kullanıcı takip etme ve rastgele biografi ayarlama gibi işlemleri otomatikleştirir.

## ✨ Özellikler / Features

- 🚀 **Hesap Oluşturma** – Otomatik kayıt (rastgele veya özel kullanıcı adı)
- 🔐 **Mevcut Hesaplarla Giriş** – `accounts.txt` dosyasından okuma
- 📧 **E-posta Doğrulama** – Geçici e-posta adresi oluşturma ve otomatik doğrulama
- 🌐 **Proxy Desteği** – Decodo konut proxy entegrasyonu veya özel proxy listesi
- 🎮 **Otomatik Eylemler** – Gruplara katılma, oyun beğenme, kullanıcı takip etme
- 🎭 **Avatar Özelleştirme** – Gerçekçi görünüm için avatar değiştirme
- 🛡️ **Anti-Debug** – Çalışma zamanında hata ayıklayıcı ve analiz araçlarını tespit etme
- ⏱️ **Lisans Sistemi** – Çevrimiçi tarih doğrulama ile süre sınırlı lisans
- 🖥️ **Web Kontrol Paneli** – Gerçek zamanlı loglar, terminal komutları ve acil durdurma butonu
- 📡 **Discord Webhook** – Her hesap işleminden sonra detaylı rapor

## 📦 Gereksinimler / Requirements

- Python 3.9 veya üzeri
- Windows (tavsiye edilir) veya Linux
- Chrome veya Brave tarayıcı (otomatik algılanır)
- Lisans doğrulaması için internet bağlantısı

## 🚀 Hızlı Başlangıç / Quick Start

### 1. Depoyu klonlayın / Clone the repository
```bash
git clone https://github.com/Sasorii-sc/Roblox-Automation.git
cd Roblox-Automation
2. Gerekli kütüphaneleri yükleyin / Install dependencies
bash
pip install -r requirements.txt
3. lib/ klasörünü hazırlayın / Prepare the lib/ folder
Dosya yapısının şu şekilde olduğundan emin olun:

text
lib/
├── __init__.py
├── lib.py          # Main sınıfı ve Roblox işlemleri
└── NopeCHA/        # (opsiyonel) Captcha çözücü eklentisi
4. Uygulamayı çalıştırın / Run the application
bash
python main.py
Kontrol paneli otomatik olarak http://127.0.0.1:5000 adresinde açılacaktır.

5. Giriş yapın / Login
Varsayılan kullanıcı bilgileri (main.py içinde değiştirebilirsiniz):

Kullanıcı adı / Username: sasorii / Şifre / Password: Kayra1676

Kullanıcı adı / Username: froxyy / Şifre / Password: Furkan1234

⚙️ Yapılandırma / Configuration
Tüm ayarlar web arayüzü üzerinden yapılır:

Sekme / Tab	Seçenek / Option	Açıklama / Description
Genel / General	Mod	Yeni hesap oluştur veya mevcut hesaplarla giriş yap
İşlem sayısı	İşlenecek hesap sayısı
İsim öneki (opsiyonel)	Oluşturulan kullanıcı adları için önek
E-posta doğrulama	Geçici e-posta ve doğrulama işlemlerini aktifleştir
Avatar özelleştirme	Avatarı otomatik değiştir
Eylemler / Actions	Grup linki	Katılınacak Roblox grubunun URL'si
Oyun linki (beğen)	Beğenilecek oyunun URL'si
Kullanıcı takip et	Virgülle ayrılmış kullanıcı adları
Discord webhook	İşlem raporları için webhook adresi
Proxy ve Güvenlik	Decodo ağı	Yerleşik konut proxy'leri (tavsiye edilir)
Manuel proxy'ler	Özel proxy listesi (ip:port)
Gizli mod	Özel gezinti modu
NopeCHA anahtarı	(opsiyonel) Captcha çözücü
⌨️ Dahili Terminal Komutları / Built‑in Terminal Commands
Web kontrol paneli içinde aşağıdaki komutları yazabilirsiniz:

Komut / Command	İşlev / Action
/clear	Konsol loglarını temizler
/stop	Çalışan işlemi acilen durdurur
/read acc	accounts.txt dosyasının içeriğini gösterir
/clear acc	accounts.txt dosyasını siler
/list acc	Dosyadaki toplam hesap sayısını gösterir
/help	Tüm komutları listeler
🧪 Örnek accounts.txt (Giriş modu için)
text
Username: john_doe, Password: pass123, Email: john@example.com
Username: jane_doe, Password: abc456, Email: jane@example.com
📁 Proje Yapısı / Project Structure
text
Roblox-Automation/
├── main.py                # Ana uygulama
├── lib/
│   ├── lib.py             # Ana iş mantığı (Main sınıfı)
│   └── NopeCHA/           # (opsiyonel) Captcha eklentisi
├── accounts.txt           # Mevcut hesaplar (varsa)
├── requirements.txt       # Bağımlılıklar
├── .gitignore             # Gereksiz dosyalar
└── README.md              # Bu dosya
⚠️ Yasal Sorumluluk Reddi / Legal Disclaimer
Bu yazılım yalnızca eğitim ve araştırma amaçları için sağlanmıştır.
Roblox üzerinde otomasyon kullanmak, Roblox'un Kullanım Şartları'nı ihlal eder ve hesap askıya alınmasına veya kalıcı olarak yasaklanmasına neden olabilir.
Yazarlar, bu aracın yanlış veya izinsiz kullanımından doğacak herhangi bir hasar veya hesap kaybından sorumlu değildir.

📜 Lisans / License
Bu proje MIT Lisansı ile lisanslanmıştır – uygun atıf yapıldığı sürece kullanım, değiştirme ve dağıtım serbesttir.

👥 Yapımcılar / Authors
Froxyy/Sasorii

Sasori (Sasorii-sc)

Built with 🖤 for automation research / Otomasyon araştırmaları için 🖤 ile yapılmıştır.
