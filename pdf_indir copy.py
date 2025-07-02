"""
TÜRKÇE DİYETİSYEN LLM EĞİTİMİ İÇİN GELİŞMİŞ PDF İNDİRİCİ

🎯 Google Scholar'dan Türkçe beslenme/diyetetik alanında akademik PDF'leri otomatik indirir.
🇹🇷 113 Türkçe anahtar kelime ile kapsamlı akademik literatür toplama.
📚 Türkçe LLM model eğitimi için optimize edilmiş veri seti oluşturur.
⚡ Güvenli bekleme mekanizmaları ile Google Scholar engellemelerine karşı korumalı.

Kullanım: python pdf_indir.py
"""

import requests
import random
import time
import json
import urllib.parse
import os
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urljoin, urlparse
from datetime import datetime

# Türkçe Diyetisyen/Beslenme alanı anahtar kelimeleri
TURKCE_ANAHTAR_KELIMELER = [
    # Temel Beslenme Terimleri
    "beslenme bilimi", "diyetetik", "beslenme tedavisi", "klinik beslenme",
    "gıda bilimi", "beslenme danışmanlığı", "diyet tedavisi", "beslenme değerlendirmesi",
    "beslenme eğitimi", "nutrisyon", "diyet planlaması", "beslenme analizi",
    
    # Hastalık Spesifik Beslenme
    "diyabetik beslenme", "diyabet diyeti", "kardiyovasküler beslenme", "kalp hastalığı diyeti",
    "obezite beslenme", "zayıflama diyeti", "kanser beslenme", "onkoloji diyeti",
    "böbrek hastalığı beslenme", "renal diyet", "karaciğer hastalığı beslenme", "hepatik diyet",
    "yeme bozuklukları", "anoreksia nervoza", "bulimia nervoza", "malnütrisyon",
    "beslenme yetersizliği", "protein enerji malnütrisyonu", "mikro besin eksikliği",
    
    # Yaş Gruplarına Göre Beslenme
    "çocuk beslenme", "pediatrik beslenme", "bebek beslenme", "infant beslenme",
    "adölesan beslenme", "ergen beslenme", "yaşlı beslenme", "geriatrik beslenme",
    "okul öncesi beslenme", "okul çağı beslenme", "yetişkin beslenme",
    
    # Özel Durumlar
    "gebelik beslenme", "hamilelik diyeti", "emzirme beslenme", "laktasyon diyeti",
    "sporcu beslenme", "spor diyeti", "atletik beslenme", "egzersiz beslenme",
    "vejetaryen beslenme", "vegan beslenme", "bitkisel beslenme", "helal beslenme",
    
    # Besin Öğeleri
    "makro besin öğeleri", "mikro besin öğeleri", "vitaminler", "mineraller",
    "protein", "karbonhidrat", "yağ", "lif", "su", "enerji",
    "omega yağ asitleri", "antioksidanlar", "probiyotikler", "prebiyotikler",
    "fonksiyonel gıdalar", "besin takviyeleri", "vitamin mineral desteği",
    
    # Beslenme Değerlendirmesi
    "beslenme taraması", "diyet analizi", "antropometrik ölçümler", "vücut kompozisyonu",
    "beslenme biomarkerleri", "diyet hatırlama", "gıda frekansı", "porsiyon kontrolü",
    "kalori hesaplama", "besin değeri", "glisemik indeks", "metabolik sendrom",
    
    # Türk Mutfağı ve Kültürel Beslenme
    "türk mutfağı beslenme", "geleneksel türk yemekleri", "akdeniz diyeti türkiye",
    "türkiye beslenme durumu", "türk halkı beslenme", "kültürel beslenme",
    "anadolu mutfağı", "türk gıda kültürü", "geleneksel gıdalar",
    
    # Gıda Güvenliği ve Teknolojisi
    "gıda güvenliği", "gıda hijyeni", "gıda teknolojisi", "gıda muhafaza",
    "gıda zehirlenmesi", "gıda alerjileri", "gıda intoleransı", "çölyak hastalığı",
    "laktoz intoleransı", "gıda etiketleme", "organik gıdalar",
    
    # Toplum Sağlığı ve Beslenme Politikaları
    "toplum beslenme", "halk sağlığı beslenme", "beslenme politikaları", "okul beslenme programları",
    "beslenme eğitimi programları", "beslenme rehberleri türkiye", "beslenme kılavuzu",
    "türkiye beslenme ve sağlık araştırması", "tüber", "hacettepe beslenme"
]

# Türkçe Beslenme alanında önemli akademik dergiler ve kurumlar
TURKCE_BESLENME_KAYNAKLARI = [
    "Beslenme ve Diyet Dergisi",
    "Türk Diyetisyenler Derneği", 
    "Hacettepe Üniversitesi Beslenme",
    "Ankara Üniversitesi Beslenme",
    "İstanbul Üniversitesi Beslenme",
    "Ege Üniversitesi Beslenme",
    "Başkent Üniversitesi Beslenme",
    "Türkiye Endokrinoloji ve Metabolizma Derneği",
    "Türk Pediatri Derneği Beslenme"
]

# Ana indirme dizini
ANA_DIZIN = "Turkce_Beslenme_PDFleri"

# User-Agent listesi (Google Scholar için)
USER_AGENT_LISTESI = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
]

# Güvenli indirme ayarları
HER_ARAMA_MAKS_PDF = 25  # Her anahtar kelime için maksimum PDF
HER_ARAMA_MAKS_SAYFA = 3  # Her arama için maksimum sayfa
INDIRMELER_ARASI_BEKLEME = 8  # İndirmeler arası bekleme (saniye)
ARAMALAR_ARASI_BEKLEME = 20  # Google Scholar için güvenli bekleme
SAYFALAR_ARASI_BEKLEME = 12  # Sayfa arası bekleme
NORMAL_TIMEOUT = 30  # HTTP timeout süresi

# Google Scholar Giriş Ayarları
SCHOLAR_LOGIN_ENABLED = False  # True yaparak giriş sistemini aktifleştirin
COOKIES_FILE = "scholar_cookies.json"  # Session cookies dosyası

# Giriş session'ı için global requests session
scholar_session = None

def turkce_scholar_url_olustur(anahtar_kelime, sayfa_no=0, yil_baslangic=2010):
    """Türkçe Google Scholar arama URL'si oluşturur"""
    base_url = "https://scholar.google.com.tr/scholar"
    params = {
        'q': anahtar_kelime,
        'hl': 'tr',  # Türkçe arayüz
        'lr': 'lang_tr',  # Türkçe dil tercihi
        'as_sdt': '0,5',
        'as_vis': '1',
        'as_ylo': str(yil_baslangic),
        'start': str(sayfa_no * 10)
    }
    
    url = base_url + "?"
    for key, value in params.items():
        url += f"{key}={urllib.parse.quote(str(value))}&"
    
    return url.rstrip('&')

def makale_bilgilerini_cikar(sonuc_div):
    """Türkçe makale bilgilerini çıkarır"""
    try:
        # Başlık
        baslik_elem = sonuc_div.find('h3', class_='gs_rt')
        baslik = baslik_elem.get_text().strip() if baslik_elem else "Bilinmeyen Başlık"
        
        # Yazarlar ve yayın bilgisi
        yazar_elem = sonuc_div.find('div', class_='gs_a')
        yazar_bilgisi = yazar_elem.get_text().strip() if yazar_elem else "Bilinmeyen Yazarlar"
        
        # Özet
        ozet_elem = sonuc_div.find('div', class_='gs_rs')
        ozet = ozet_elem.get_text().strip() if ozet_elem else ""
        
        # Atıf sayısı
        atif_elem = sonuc_div.find('a', string=lambda text: text and ('atıf' in text.lower() or 'cited by' in text.lower()))
        if not atif_elem:
            atif_elem = sonuc_div.find('a', href=lambda href: href and 'cites' in href)
        atiflar = atif_elem.get_text().strip() if atif_elem else "0 atıf"
        
        return {
            'baslik': baslik,
            'yazarlar': yazar_bilgisi,
            'ozet': ozet,
            'atiflar': atiflar
        }
    except Exception as e:
        return {
            'baslik': "Bilinmeyen Başlık",
            'yazarlar': "Bilinmeyen Yazarlar", 
            'ozet': "",
            'atiflar': "0 atıf"
        }

def turkce_beslenme_kontrolu(makale_bilgisi):
    """Makalenin Türkçe beslenme alanıyla ilgili olup olmadığını kontrol eder"""
    kontrol_metni = (makale_bilgisi['baslik'] + " " + makale_bilgisi['ozet']).lower()
    
    turkce_beslenme_terimleri = [
        'beslenme', 'diyet', 'gıda', 'besin', 'vitamin', 'mineral',
        'obezite', 'diyabet', 'kalp', 'kardiyovasküler', 'metabolik',
        'yeme', 'yemek', 'kalori', 'protein', 'karbonhidrat', 'yağ',
        'lif', 'antioksidan', 'diyetisyen', 'nutrisyon', 'sağlık',
        'çocuk', 'yaşlı', 'gebelik', 'sporcu', 'hastalık', 'tedavi'
    ]
    
    return any(terim in kontrol_metni for terim in turkce_beslenme_terimleri)

def pdf_indir_ve_kaydet(pdf_url, dosya_adi, makale_bilgisi):
    """PDF indirir ve Türkçe meta verileri kaydeder"""
    try:
        print(f"📥 PDF indiriliyor: {pdf_url}")
        
        # Güvenli istek gönder
        response = guvenli_istek_gonder(pdf_url)
        
        if not response:
            print(f"❌ PDF indirme başarısız: {pdf_url}")
            return False
        
        # Content-Type kontrolü
        content_type = response.headers.get('content-type', '').lower()
        if 'pdf' not in content_type and not pdf_url.lower().endswith('.pdf'):
            print("❌ İçerik PDF değil")
            return False
        
        # PDF boyut kontrolü (çok küçük dosyaları reddet)
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) < 1024:  # 1KB'dan küçük
            print("❌ Dosya çok küçük, muhtemelen PDF değil")
            return False
        
        # PDF indir
        with open(dosya_adi, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # PDF dosya boyutunu kontrol et
        if os.path.getsize(dosya_adi) < 1024:
            print("❌ İndirilen dosya çok küçük, siliniyor")
            os.remove(dosya_adi)
            return False
        
        # Türkçe meta veri dosyası oluştur
        meta_dosya_adi = dosya_adi.replace('.pdf', '_bilgiler.json')
        meta_veri = {
            'dosya_adi': os.path.basename(dosya_adi),
            'indirilme_tarihi': datetime.now().isoformat(),
            'kaynak_url': pdf_url,
            'dosya_boyutu': os.path.getsize(dosya_adi),
            'makale_bilgileri': makale_bilgisi
        }
        
        with open(meta_dosya_adi, 'w', encoding='utf-8') as f:
            json.dump(meta_veri, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        print(f"❌ İndirme hatası: {e}")
        return False

def akilli_bekleme(bekleme_turu="normal", ekstra_faktor=1.0):
    """Akıllı ve rastgele bekleme sistemi"""
    if bekleme_turu == "arama":
        temel_bekleme = ARAMALAR_ARASI_BEKLEME
    elif bekleme_turu == "sayfa":
        temel_bekleme = SAYFALAR_ARASI_BEKLEME
    elif bekleme_turu == "indirme":
        temel_bekleme = INDIRMELER_ARASI_BEKLEME
    else:
        temel_bekleme = 5
    
    # Rastgele varyasyon ekle (%50-150 arası)
    rastgele_faktor = random.uniform(0.5, 1.5)
    toplam_bekleme = temel_bekleme * rastgele_faktor * ekstra_faktor
    
    if toplam_bekleme > 3:
        print(f"⏰ {toplam_bekleme:.1f} saniye bekleniyor...")
    
    time.sleep(toplam_bekleme)

def anahtar_kelime_ara_ve_indir(anahtar_kelime, maks_sayfa=HER_ARAMA_MAKS_SAYFA):
    """Bir Türkçe anahtar kelime için arama yapar ve PDF'leri indirir"""
    print(f"\n🔍 Anahtar kelime: '{anahtar_kelime}'")
    
    # Türkçe klasör oluştur
    guvenli_kelime = re.sub(r'[^\w\s-]', '', anahtar_kelime).strip()
    guvenli_kelime = re.sub(r'[-\s]+', '_', guvenli_kelime)
    kelime_klasoru = os.path.join(ANA_DIZIN, guvenli_kelime)
    os.makedirs(kelime_klasoru, exist_ok=True)
    
    toplam_indirilen = 0
    
    for sayfa in range(maks_sayfa):
        # Her sayfa arası güvenli bekleme
        if sayfa > 1:
            akilli_bekleme("sayfa")
        
        # Google Scholar sayfasını al
        scholar_url = turkce_scholar_url_olustur(anahtar_kelime, sayfa_no=sayfa)
        print(f"🌐 URL: {scholar_url}")
        
        response = guvenli_istek_gonder(scholar_url)
        
        if not response:
            print(f"❌ Sayfa {sayfa + 1} yüklenemedi")
            continue
                
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Sonuç divlerini bul
        sonuclar = soup.find_all("div", class_="gs_r gs_or gs_scl")
        if not sonuclar:
            sonuclar = soup.find_all("div", class_="gs_ri")
        
        if not sonuclar:
            print(f"❌ Sayfa {sayfa + 1}'de sonuç bulunamadı")
            # Captcha kontrolü
            if "captcha" in response.text.lower() or "robot" in response.text.lower():
                print("🤖 Captcha algılandı! Uzun bekleme yapılıyor...")
                time.sleep(300)  # 5 dakika bekle
            break
        
        sayfa_indirilen = 0
        
        for i, sonuc_div in enumerate(sonuclar):
            if sayfa_indirilen >= HER_ARAMA_MAKS_PDF:
                break
                
            # Makale bilgilerini çıkar
            makale_bilgisi = makale_bilgilerini_cikar(sonuc_div)
            
            # Türkçe beslenme alanıyla ilgili mi kontrol et
            if not turkce_beslenme_kontrolu(makale_bilgisi):
                print(f"⏭️ Geçiliyor: {makale_bilgisi['baslik'][:40]}... (ilgisiz)")
                continue
            
            print(f"📖 İşleniyor: {makale_bilgisi['baslik'][:50]}...")
            
            # PDF linklerini bul
            pdf_linkleri = []
            for link in sonuc_div.find_all("a", href=True):
                href = link["href"]
                link_metni = link.get_text().strip()
                
                if "[PDF]" in link_metni or "PDF" in link_metni.upper():
                    if href.startswith("/"):
                        pdf_url = urljoin("https://scholar.google.com.tr", href)
                    else:
                        pdf_url = href
                    pdf_linkleri.append(pdf_url)
            
            # PDF'leri indir
            for j, pdf_url in enumerate(pdf_linkleri):
                if sayfa_indirilen >= HER_ARAMA_MAKS_PDF:
                    break
                    
                dosya_adi = os.path.join(kelime_klasoru, f"{guvenli_kelime}_s{sayfa+1}_{i+1}_{j+1}.pdf")
                
                if pdf_indir_ve_kaydet(pdf_url, dosya_adi, makale_bilgisi):
                    sayfa_indirilen += 1
                    toplam_indirilen += 1
                    print(f"✅ İndirildi: {makale_bilgisi['baslik'][:50]}...")
                
                # İndirme sonrası bekleme
                akilli_bekleme(bekleme_turu="indirme")
        
        print(f"📊 Sayfa {sayfa + 1}: {sayfa_indirilen} PDF indirildi")
        
        if sayfa < maks_sayfa - 1:
            akilli_bekleme(bekleme_turu="sayfa")
            
    print(f"✅ '{anahtar_kelime}' için toplam {toplam_indirilen} PDF indirildi")
    return toplam_indirilen

def guvenli_istek_gonder(url, maks_deneme=3):
    """Güvenli HTTP isteği gönderir"""
    
    headers = {
        'User-Agent': random.choice(USER_AGENT_LISTESI),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    print("🌐 HTTP isteği gönderiliyor...")
    for deneme in range(maks_deneme):
        try:
            # Rastgele user agent seç
            headers['User-Agent'] = random.choice(USER_AGENT_LISTESI)
            
            response = requests.get(url, headers=headers, timeout=NORMAL_TIMEOUT)
            
            if response.status_code == 200:
                print("✅ İstek başarılı!")
                return response
            elif response.status_code == 429:
                bekleme = 60 + (deneme * 30)
                print(f"⚠️ Rate limit algılandı, {bekleme} saniye bekleniyor...")
                time.sleep(bekleme)
            elif response.status_code == 403:
                print("⚠️ Erişim engellendi (403), daha uzun bekleme yapılacak...")
                time.sleep(120)  # 2 dakika bekle
            else:
                print(f"⚠️ HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Zaman aşımı (deneme {deneme + 1})")
            if deneme < maks_deneme - 1:
                time.sleep(15)
        except Exception as e:
            print(f"❌ İstek deneme {deneme + 1} başarısız: {e}")
            if deneme < maks_deneme - 1:
                bekleme = 15 + (deneme * 10)
                time.sleep(bekleme)
    
    print("❌ Tüm bağlantı denemeleri başarısız!")
    return None

def cookies_kaydet(session, dosya_yolu):
    """Session cookies'lerini dosyaya kaydet"""
    try:
        cookies_dict = {}
        for cookie in session.cookies:
            cookies_dict[cookie.name] = cookie.value
        
        with open(dosya_yolu, 'w', encoding='utf-8') as f:
            json.dump(cookies_dict, f, ensure_ascii=False, indent=2)
        print(f"✅ Cookies kaydedildi: {dosya_yolu}")
        return True
    except Exception as e:
        print(f"❌ Cookies kaydetme hatası: {e}")
        return False

def cookies_yukle(session, dosya_yolu):
    """Dosyadan cookies'leri yükle"""
    try:
        if not os.path.exists(dosya_yolu):
            print(f"⚠️ Cookies dosyası bulunamadı: {dosya_yolu}")
            return False
            
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            cookies_dict = json.load(f)
        
        for name, value in cookies_dict.items():
            session.cookies.set(name, value, domain='.google.com')
            session.cookies.set(name, value, domain='.scholar.google.com')
            session.cookies.set(name, value, domain='.scholar.google.com.tr')
        
        print(f"✅ Cookies yüklendi: {dosya_yolu}")
        return True
    except Exception as e:
        print(f"❌ Cookies yükleme hatası: {e}")
        return False

def scholar_session_baslat():
    """Google Scholar için giriş session'ı başlat"""
    global scholar_session
    
    if not SCHOLAR_LOGIN_ENABLED:
        print("ℹ️ Scholar giriş sistemi pasif")
        return None
    
    try:
        scholar_session = requests.Session()
        
        # Temel headers
        scholar_session.headers.update({
            'User-Agent': random.choice(USER_AGENT_LISTESI),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Kaydedilmiş cookies'leri yükle
        if cookies_yukle(scholar_session, COOKIES_FILE):
            # Session'ı test et
            test_url = "https://scholar.google.com.tr/"
            response = scholar_session.get(test_url, timeout=30)
            
            if response.status_code == 200:
                # Giriş yapılmış mı kontrol et
                if "Giriş" not in response.text and ("Çıkış" in response.text or "hesap" in response.text.lower()):
                    print("✅ Google Scholar giriş session'ı aktif!")
                    return scholar_session
                else:
                    print("⚠️ Cookies eski, yeniden giriş gerekli")
            else:
                print(f"⚠️ Session test başarısız: {response.status_code}")
        
        print("🔐 Manuel Google Scholar giriş gerekli")
        return scholar_session
        
    except Exception as e:
        print(f"❌ Scholar session başlatma hatası: {e}")
        return None

def manuel_giris_rehberi():
    """Manuel giriş için rehber göster"""
    print("\n" + "="*80)
    print("🔐 GOOGLE SCHOLAR MANuel GİRİŞ REHBERİ")
    print("="*80)
    print("1. Browser'ınızda https://scholar.google.com.tr/ adresine gidin")
    print("2. Google hesabınız ile giriş yapın")
    print("3. Herhangi bir arama yapın (örn: 'beslenme bilimi')")
    print("4. F12 basıp Developer Tools'u açın")
    print("5. Network tab'ına gidin")
    print("6. Bir PDF linkine tıklayın")
    print("7. İsteklerde 'Headers' kısmından 'Cookie' değerini kopyalayın")
    print("8. Aşağıdaki kodu çalıştırın:")
    print("\n```python")
    print("# Kopyaladığınız cookie string'ini buraya yapıştırın")
    print('cookie_string = "NID=xxx; GSP=xxx; ..."')
    print("import requests, json")
    print("session = requests.Session()")
    print("for cookie in cookie_string.split(';'):")
    print("    if '=' in cookie:")
    print("        name, value = cookie.strip().split('=', 1)")
    print("        session.cookies.set(name, value)")
    print("# Session'ı test et")
    print("response = session.get('https://scholar.google.com.tr/')")
    print("print('Giriş başarılı!' if response.status_code == 200 else 'Hata!')")
    print("```")
    print("="*80)
    print("\n💡 Daha kolay yöntem için Selenium kullanabilirsiniz:")
    print("   pip install selenium")
    print("   (Otomatik giriş kodu eklenecek)")
    print("="*80)

def main():
    """Ana çalışma fonksiyonu"""
    print("🚀 Türkçe Diyetisyen LLM Eğitimi için PDF İndirici Başlatılıyor...")
    print(f"📂 Ana dizin: {ANA_DIZIN}")
    print(f"🔍 Toplam {len(TURKCE_ANAHTAR_KELIMELER)} Türkçe anahtar kelime işlenecek")
    print("================================================================================")
    print("📊 GÜVENLİ BEKLEME SÜRELERİ AKTİF")
    print("📊 Her indirme arası: 8 saniye")
    print("🔍 Her arama arası: 20 saniye") 
    print("📄 Her sayfa arası: 12 saniye")
    print("⏰ HTTP timeout: 30 saniye")
    print("================================================================================")

    os.makedirs(ANA_DIZIN, exist_ok=True)
    
    toplam_indirilen = 0
    basarili_kelimeler = 0
    
    # Türkçe istatistik dosyası oluştur
    istatistik_dosyasi = os.path.join(ANA_DIZIN, "turkce_indirme_istatistikleri.json")
    baslangic_zamani = datetime.now()
    istatistikler = {
        "baslangic_zamani": baslangic_zamani.strftime("%Y-%m-%d %H:%M:%S"),
        "bitis_zamani": None,
        "toplam_sure_dakika": None,
        "toplam_anahtar_kelime": len(TURKCE_ANAHTAR_KELIMELER),
        "basarili_anahtar_kelime": 0,
        "toplam_indirilen_pdf": 0,
        "baglanti_modu": "Normal HTTP Bağlantısı",
        "ana_dizin": ANA_DIZIN,
        "basarili_anahtar_kelimeler": []
    }
    
    for i, anahtar_kelime in enumerate(TURKCE_ANAHTAR_KELIMELER, 1):
        print(f"\n{'='*30} ANAHTAR KELİME {i}/{len(TURKCE_ANAHTAR_KELIMELER)} {'='*30}")
        
        # Her anahtar kelime arası güvenli bekleme
        if i > 1:
            akilli_bekleme("arama")
        
        try:
            indirilen_sayi = anahtar_kelime_ara_ve_indir(anahtar_kelime)
            toplam_indirilen += indirilen_sayi
            
            if indirilen_sayi > 0:
                basarili_kelimeler += 1
            
            # İstatistikleri güncelle
            istatistikler['basarili_anahtar_kelime'] = basarili_kelimeler
            istatistikler['toplam_indirilen_pdf'] = toplam_indirilen
            istatistikler['basarili_anahtar_kelimeler'].append(anahtar_kelime)
            
            # İstatistikleri kaydet
            with open(istatistik_dosyasi, 'w', encoding='utf-8') as f:
                json.dump(istatistikler, f, ensure_ascii=False, indent=2)
            
            if i < len(TURKCE_ANAHTAR_KELIMELER):
                akilli_bekleme(bekleme_turu="arama")
                
        except KeyboardInterrupt:
            print("\n⚠️ Kullanıcı tarafından durduruldu.")
            break
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}")
            continue
    
    # Son istatistikler
    bitis_zamani = datetime.now()
    sure_dakika = round((bitis_zamani - baslangic_zamani).total_seconds() / 60, 2)
    istatistikler['bitis_zamani'] = bitis_zamani.strftime("%Y-%m-%d %H:%M:%S")
    istatistikler['toplam_sure_dakika'] = sure_dakika
    with open(istatistik_dosyasi, 'w', encoding='utf-8') as f:
        json.dump(istatistikler, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print("📊 TÜRKÇE DİYETİSYEN LLM PDF İNDİRME ÖZETİ")
    print("================================================================================")
    print(f"✅ Başarılı anahtar kelimeler: {basarili_kelimeler}/{len(TURKCE_ANAHTAR_KELIMELER)}")
    print(f"📄 Toplam indirilen PDF: {toplam_indirilen}")
    print(f"🌐 Bağlantı modu: Normal HTTP")
    print(f"📂 Ana dizin: {ANA_DIZIN}")
    print(f"📊 İstatistik dosyası: {istatistik_dosyasi}")
    
    print("\n💡 DAHA HIZLI İNDİRME ÖNERİLERİ:")
    print("   - VPN kullanarak IP değiştirin")
    print("   - Gece saatlerinde çalıştırın (23:00-07:00)")
    print("   - Farklı kategorileri farklı günlerde işleyin")
    print("   - Günde 100-200 PDF ile sınırlandırın")
    
    print("🎉 Türkçe Diyetisyen LLM eğitim veri seti hazır!")

if __name__ == "__main__":
    main() 
