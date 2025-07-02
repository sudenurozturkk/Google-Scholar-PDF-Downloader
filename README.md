# 🇹🇷 Türkçe Diyetisyen LLM için Google Scholar PDF İndirici

Türkçe beslenme ve diyetetik alanında akademik makaleler indiren **gelişmiş ve akıllı sistem**. Google Scholar giriş desteği, çoklu profil sistemi ve akıllı profil yönetimi ile 403 engellerini aşar.

## 🌟 Yeni Özellikler (2024)

- ✅ **Çoklu Google Scholar Profil Sistemi** (3 farklı hesap desteği)
- 🧠 **Akıllı Profil Performans Takibi** (otomatik optimizasyon)
- 🔄 **Otomatik 403 Hata Çözümü** (profil değiştirme)
- 🔐 **Google Scholar Giriş Sistemi** (cookie tabanlı)
- 📊 **Gerçek Zamanlı Performans İstatistikleri**
- 🎯 **113 Türkçe Beslenme Anahtar Kelimesi**
- 🌐 **Selenium Otomatik Giriş Desteği** (isteğe bağlı)

## 📦 Hızlı Kurulum

```bash
# 1. Gerekli paketleri yükle
pip install requests beautifulsoup4 tqdm lxml

# 2. İsteğe bağlı: Selenium desteği
pip install selenium

# 3. Projeyi çalıştır
python pdf_indir.py
```

## 🚀 Kullanım Rehberi

### 1. Temel Çalıştırma
```bash
python pdf_indir.py          # Ana menü açılır
python pdf_indir.py --menu   # Ana menü
python pdf_indir.py --test   # Scholar giriş testi
python pdf_indir.py --mini   # Mini test (tek kelime)
```

### 2. Ana Menü Seçenekleri
```
1. PDF indirmeyi başlat (113 Türkçe anahtar kelime)
2. Mini test (tek anahtar kelime ile)
3. Google Scholar giriş testi
4. Çoklu profil yönetimi 🆕
5. İstatistikleri görüntüle
6. Profil performans istatistikleri 🚀
7. Kullanım rehberi
0. Çıkış
```

## 🔐 Google Scholar Cookie Alma Rehberi

### Adım 1: Google Scholar'a Giriş Yapın
1. **Chrome/Firefox** tarayıcıyı açın
2. **https://scholar.google.com.tr** adresine gidin
3. **Google hesabınızla giriş yapın**
4. Giriş yaptığınızdan emin olun (sağ üstte profil fotoğrafı görmelisiniz)

### Adım 2: Cookie'leri Çıkarın

#### Chrome için:
```
1. F12 tuşuna basın (Developer Tools açılır)
2. "Application" sekmesine gidin
3. Sol menüden "Storage" > "Cookies" > "https://scholar.google.com" seçin
4. Tüm cookie'leri seçin (Ctrl+A)
5. Sağ tık > "Copy" yapın
```

#### Firefox için:
```
1. F12 tuşuna basın
2. "Storage" sekmesine gidin  
3. "Cookies" > "https://scholar.google.com" seçin
4. Tüm cookie'leri kopyalayın
```

### Adım 3: Cookie Dosyası Oluşturun

**Yöntem 1: Otomatik Dönüştürme (Önerilen)**
```bash
python pdf_indir.py
# Menüden "4. Çoklu profil yönetimi" seçin
# "3. Yeni profil ekle" seçin
# Cookie'leri yapıştırın, sistem otomatik dönüştürür
```

**Yöntem 2: Manuel JSON Oluşturma**
```json
{
  "GSP": "cookie_değeri_buraya",
  "HSID": "cookie_değeri_buraya", 
  "SSID": "cookie_değeri_buraya",
  "APISID": "cookie_değeri_buraya",
  "SAPISID": "cookie_değeri_buraya",
  "SID": "cookie_değeri_buraya",
  "NID": "cookie_değeri_buraya"
}
```

### Adım 4: Profil Dosyalarını Kaydedin
- **Ana profil**: `scholar_cookies.json`
- **2. profil**: `scholar_cookies_profile2.json`  
- **3. profil**: `scholar_cookies_profile3.json`

## 🛠️ Gelişmiş Yapılandırma

### Profil Sistemi Ayarları
```python
# pdf_indir.py dosyasında
MULTI_LOGIN_ENABLED = True        # Çoklu profil aktif
SCHOLAR_LOGIN_ENABLED = True      # Google Scholar giriş aktif
PROFIL_ATLAMA_SINIRI = 3         # Kaç başarısızlık sonrası profil atlanır
```

### Bekleme Süreleri
```python
INDIRME_BEKLEME = (6, 12)        # İndirme arası bekleme (sn)
SAYFA_BEKLEME = (10, 15)         # Sayfa arası bekleme (sn)  
ARAMA_BEKLEME = (18, 25)         # Arama arası bekleme (sn)
```

### Arama Parametreleri
```python
HER_ARAMA_MAKS_SAYFA = 3         # Sayfa/arama
HER_SAYFA_MAKS_PDF = 25          # PDF/sayfa
YIL_BASLANGIC = 2010             # Minimum yayın yılı
```

## 📊 Akıllı Profil Sistemi

### Profil Performans Takibi
- ✅ **Başarı Oranı**: Her profil için %0-100 arasında hesaplanır
- 📈 **Otomatik Optimizasyon**: Sistem en iyi profili seçer
- ⚠️ **Kötü Profil Atlama**: 3+ başarısızlık sonrası profil atlanır
- 🕐 **Son Kullanım**: Her profilin son kullanım zamanı

### Akıllı Profil Değiştirme
```
403 Hatası Geldiğinde:
1. Mevcut profil "başarısız" olarak işaretlenir
2. En iyi performanslı profil seçilir
3. Otomatik geçiş yapılır
4. İndirme devam eder
```

### Profil Durumu Kontrolü
```bash
python pdf_indir.py
# Menü > "4. Çoklu profil yönetimi"
# > "4. Profil durumları" seçin
```

## 🔍 Anahtar Kelime Kategorileri

### 113 Türkçe Anahtar Kelime:

**Temel Beslenme (25 kelime)**
```
beslenme bilimi, besin öğeleri, kalori, protein, karbonhidrat, 
yağ, vitamin, mineral, lif, su, metabolizma, enerji, 
makro besin öğeleri, mikro besin öğeleri, amino asit, 
yağ asitleri, antioksidan, probiyotik, prebiyotik, 
fonksiyonel gıda, organik gıda, doğal gıda, sağlıklı beslenme, 
dengeli beslenme, beslenme alışkanlıkları
```

**Hastalık-Spesifik Beslenme (35 kelime)**
```
diyabet beslenmesi, obezite, kalp hastalığı beslenmesi, 
hipertansiyon diyet, kolesterol düşürücü diyet, kanser önleyici beslenme,
böbrek hastalığı diyet, karaciğer hastalığı beslenme, ...
```

**Yaş Grubu Beslenmesi (20 kelime)**
```
bebek beslenmesi, çocuk beslenmesi, adölesan beslenme,
yaşlı beslenmesi, hamilelik beslenmesi, emzirme dönemi beslenme, ...
```

**Türk Mutfağı ve Kültürel Beslenme (15 kelime)**
```
Türk mutfağı, geleneksel Türk yemekleri, Anadolu mutfağı,
Osmanlı mutfağı, yerel gıdalar, ...
```

**Gıda Güvenliği ve Politikalar (18 kelime)**
```
gıda güvenliği, gıda hijyeni, gıda zehirlenmesi,
halk sağlığı beslenme, beslenme politikaları, ...
```

## 📁 Çıktı Yapısı

```
Turkce_Beslenme_PDFleri/
├── beslenme_bilimi/
│   ├── beslenme_bilimi_s1_1_1.pdf
│   ├── beslenme_bilimi_s1_1_1_bilgiler.json
│   ├── beslenme_bilimi_s1_2_1.pdf
│   └── beslenme_bilimi_s1_2_1_bilgiler.json
├── diyabet_beslenmesi/
│   ├── diyabet_beslenmesi_s1_1_1.pdf
│   └── diyabet_beslenmesi_s1_1_1_bilgiler.json
├── turkce_indirme_istatistikleri.json
└── scholar_cookies.json (profil dosyaları)
```

### JSON Metadata Örneği
```json
{
  "baslik": "Diyabet Hastalarında Beslenme Tedavisi",
  "yazarlar": ["Dr. Ahmet Yılmaz", "Prof. Dr. Ayşe Kaya"],
  "yayin_yili": "2023",
  "dergi": "Türk Diyabet Dergisi",
  "pdf_url": "https://example.com/paper.pdf",
  "google_scholar_url": "https://scholar.google.com/...",
  "ozet": "Bu çalışmada diyabet hastalarında...",
  "anahtar_kelimeler": ["diyabet", "beslenme", "diyet"],
  "turkce_icerik_skoru": 85,
  "indirme_zamani": "2024-01-15 14:30:25"
}
```

## 🚨 Sorun Giderme

### 403 Forbidden Hatası
```
✅ Sistem otomatik çözüm sağlar:
1. Profil performansı izlenir
2. Kötü profil otomatik değiştirilir  
3. En iyi profil seçilir
4. İndirme devam eder

❌ Manuel çözüm gerekirse:
1. Yeni cookie profili ekleyin
2. Bekleme sürelerini artırın
3. VPN kullanın
```

### Cookie Profil Sorunları
```bash
# Profil testi
python pdf_indir.py
# Menü > "3. Google Scholar giriş testi"

# Kötü profilleri temizle
# Menü > "4. Çoklu profil yönetimi" > "4. Profil durumları"
```

### Rate Limiting
```
⚠️ Çok hızlı istek gönderiyorsanız:
1. INDIRME_BEKLEME süresini artırın
2. Gece saatlerinde çalıştırın
3. Günlük indirme limitini azaltın
```

### İndirme Sorunları
```
❌ PDF indirilmiyorsa:
1. İnternet bağlantısını kontrol edin
2. Google Scholar erişimini test edin
3. Klasör izinlerini kontrol edin
4. Profil cookie'lerini yenileyin
```

## 📈 Performans İstatistikleri

### Sistem İstatistikleri
```bash
python pdf_indir.py
# Menü > "5. İstatistikleri görüntüle"
```

### Profil Performans Raporu  
```bash
python pdf_indir.py
# Menü > "6. Profil performans istatistikleri"
```

**Örnek Çıktı:**
```
📊 PROFİL PERFORMANS İSTATİSTİKLERİ:
============================================================

📁 Profil 1: scholar_cookies.json 🎯 AKTİF
   ✅ Başarılı: 45
   ❌ Başarısız: 3  
   📊 Başarı oranı: %93.8
   🕐 Son kullanım: 14:25:30

📁 Profil 2: scholar_cookies_profile2.json ⚠️ ATLANAN
   ✅ Başarılı: 5
   ❌ Başarısız: 8
   📊 Başarı oranı: %38.5
   🕐 Son kullanım: 14:20:15
```

## 💡 Optimizasyon Önerileri

### Daha Hızlı İndirme
- **Çoklu Profil**: 3 farklı Google hesabı kullanın
- **VPN Kullanımı**: IP değiştirerek rate limit'i aşın
- **Gece Çalıştırma**: 23:00-07:00 arası daha az kısıtlama
- **Kategorik İndirme**: Günde 1 kategori (100-200 PDF)

### Profil Kalitesi Artırma
```
✅ İyi Profil Özellikleri:
- Yeni oluşturulmuş Google Scholar hesabı
- Aktif araştırma geçmişi
- Düzenli Scholar kullanımı
- İnstitüsyonel email adresi

❌ Kötü Profil Özellikleri:
- Eski, uzun süredir kullanılmayan hesap
- Kötü geçmiş (spam, bot kullanımı)
- Ücretsiz email adresleri
- Çok fazla otomatik istek geçmişi
```

### Günlük Hedefler
- **Başlangıç**: 50-100 PDF/gün
- **Deneyimli**: 200-300 PDF/gün  
- **Maksimum**: 500 PDF/gün (3 profil ile)

## 🔧 Selenium Kurulumu (İsteğe Bağlı)

### ChromeDriver Kurulumu
```bash
# Windows
# ChromeDriver'ı indirip PATH'e ekleyin

# Linux/Mac  
sudo apt-get install chromium-chromedriver  # Ubuntu
brew install chromedriver                   # macOS
```

### Selenium Otomatik Giriş
```python
# pdf_indir.py içinde
SELENIUM_ENABLED = True

# Otomatik giriş kullanımı
python pdf_indir.py
# Menü > "4. Çoklu profil yönetimi" > "2. Selenium ile otomatik giriş"
```

## 🤝 Katkıda Bulunma

1. **Fork** yapın
2. **Feature branch** oluşturun (`git checkout -b feature/amazing-feature`)
3. **Commit** yapın (`git commit -m 'Add amazing feature'`)
4. **Push** edin (`git push origin feature/amazing-feature`)
5. **Pull Request** oluşturun

### Geliştirme Alanları
- [ ] GUI arayüz ekleme
- [ ] Veritabanı entegrasyonu  
- [ ] PDF içerik analizi
- [ ] Makine öğrenmesi ile kalite filtreleme
- [ ] Çoklu dil desteği

## 📋 Sistem Gereksinimleri

### Minimum Gereksinimler
- **Python**: 3.7+
- **RAM**: 2GB
- **Disk**: 10GB+ (PDF'ler için)
- **İnternet**: Stabil bağlantı

### Önerilen Gereksinimler  
- **Python**: 3.9+
- **RAM**: 8GB
- **Disk**: 100GB+ (büyük koleksiyon için)
- **İnternet**: Yüksek hızlı bağlantı

## 📄 Lisans

**MIT License** - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Teşekkürler

Bu proje **Türkçe diyetetik LLM modellerinin geliştirilmesi** için akademik araştırma amaçlı geliştirilmiştir.

### Özel Teşekkürler
- **Google Scholar**: Akademik veritabanı erişimi
- **Python Community**: Açık kaynak kütüphaneler
- **Turkish Research Community**: Türkçe akademik içerik

## 🆘 Destek

**Sorun mu yaşıyorsunuz?**

1. **GitHub Issues**: Hata raporları ve öneriler
2. **Dokümantasyon**: Bu README'yi tekrar inceleyin
3. **Test Araçları**: `python pdf_indir.py --test` çalıştırın

### Sık Sorulan Sorular

**S: Cookie'ler neden geçersiz oluyor?**
A: Google Scholar oturumları 1-2 haftada sona erer. Yeni cookie alın.

**S: 403 hatası almaya devam ediyorum?**  
A: Profil kalitesi düşük olabilir. Yeni Google hesabı oluşturun.

**S: PDF'ler indirilmiyor?**
A: URL'ler doğrudan indirme linki olmayabilir. Bu normal bir durumdur.

**S: Sistem çok yavaş çalışıyor?**
A: Bekleme sürelerini azaltın, ancak 403 hatası riski artar.

---

**🎯 Hedef**: Türkçe diyetetik alanında en kapsamlı akademik veri seti oluşturmak!

**📊 İstatistik**: 113 anahtar kelime × 3 sayfa × 25 PDF = ~8,475 PDF hedefi!
