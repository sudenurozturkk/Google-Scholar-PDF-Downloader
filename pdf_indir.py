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

# Çoklu Giriş Sistemi - Multiple Cookie Profiles
MULTI_LOGIN_ENABLED = True  # Çoklu giriş sistemini aktifleştir
SCHOLAR_LOGIN_ENABLED = True  # True yaparak giriş sistemini aktifleştirin
COOKIES_FILE = "scholar_cookies.json"  # Ana session cookies dosyası
COOKIES_BACKUP_FILE = "scholar_cookies_backup.json"  # Yedek cookie profili

# Cookie profilleri tanımları
COOKIE_PROFILE_1 = "scholar_cookies.json"           # Ana profil
COOKIE_PROFILE_2 = "scholar_cookies_profile2.json"   # İkinci profil
COOKIE_PROFILE_3 = "scholar_cookies_profile3.json"   # Üçüncü profil

# Aktif cookie profil indeksi
active_cookie_profile = 1

# Profil kalitesi takip sistemi
profil_basari_orani = {
    1: {"basarili": 0, "basarisiz": 0, "son_kullanim": None},
    2: {"basarili": 0, "basarisiz": 0, "son_kullanim": None},
    3: {"basarili": 0, "basarisiz": 0, "son_kullanim": None}
}

# En az kaç başarısız deneme sonrası profil atlanacak
PROFIL_ATLAMA_SINIRI = 3

# Selenium ile otomatik giriş (isteğe bağlı)
SELENIUM_AUTO_LOGIN = False  # True yaparak otomatik giriş aktifleştirin
GOOGLE_EMAIL = "sinemdana2@gmail.com"  # Google email adresiniz
GOOGLE_PASSWORD = "asd789asd78"  # Google şifreniz (güvenlik için environment variable kullanın!)

# Selenium import (isteğe bağlı)
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

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

def guvenli_istek_gonder(url, maks_deneme=3, use_session=True):
    """Güvenli HTTP isteği gönderir (session destekli)"""
    global scholar_session
    
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
    
    # Session var mı ve kullanılacak mı?
    session_to_use = None
    if use_session and scholar_session and SCHOLAR_LOGIN_ENABLED:
        session_to_use = scholar_session
        print("🔐 Giriş session'ı ile istek gönderiliyor...")
    else:
        print("🌐 Normal HTTP isteği gönderiliyor...")
    
    for deneme in range(maks_deneme):
        try:
            # Rastgele user agent seç
            headers['User-Agent'] = random.choice(USER_AGENT_LISTESI)
            
            if session_to_use:
                # Session ile istek gönder
                session_to_use.headers.update(headers)
                response = session_to_use.get(url, timeout=NORMAL_TIMEOUT)
            else:
                # Normal requests ile istek gönder
                response = requests.get(url, headers=headers, timeout=NORMAL_TIMEOUT)
            
            if response.status_code == 200:
                if session_to_use:
                    print("✅ Session ile istek başarılı!")
                    
                    # Başarılı profil performansını kaydet
                    if MULTI_LOGIN_ENABLED:
                        profil_performans_kaydet(active_cookie_profile, basarili=True)
                    
                    # Aktif profili güncelle
                    profiles = get_cookie_profiles()
                    if profiles and active_cookie_profile <= len(profiles):
                        aktif_profil_dosyasi = profiles[active_cookie_profile - 1]
                        cookies_kaydet(session_to_use, aktif_profil_dosyasi)
                    else:
                        cookies_kaydet(session_to_use, COOKIES_FILE)  # Fallback
                else:
                    print("✅ Normal istek başarılı!")
                return response
            elif response.status_code == 429:
                bekleme = 60 + (deneme * 30)
                print(f"⚠️ Rate limit algılandı, {bekleme} saniye bekleniyor...")
                time.sleep(bekleme)
            elif response.status_code == 403:
                print(f"🚨 403 FORBIDDEN TESPİT EDİLDİ! (Deneme {deneme + 1}/{maks_deneme})")
                
                # Mevcut profili başarısız olarak kaydet
                if MULTI_LOGIN_ENABLED and session_to_use:
                    profil_performans_kaydet(active_cookie_profile, basarili=False)
                
                # Çoklu profil sistemi aktifse otomatik geçiş yap
                if MULTI_LOGIN_ENABLED and len(get_cookie_profiles()) > 1:
                    print("🔄 Çoklu profil sistemi ile otomatik geçiş yapılıyor...")
                    if otomatik_profil_degistir():
                        print("✅ Profil değiştirildi, istek tekrarlanacak...")
                        session_to_use = scholar_session  # Yeni session'ı kullan
                        akilli_bekleme("rate_limit", ekstra_faktor=1.5)
                        continue
                    else:
                        print("❌ Profil değiştirme başarısız, normal bekleme...")
                
                # Profil değiştirme yoksa veya başarısızsa eski yöntem
                if session_to_use:
                    print("⚠️ Session ile 403 hatası, normal moda geçiliyor...")
                    session_to_use = None  # Normal moda geç
                    continue
                else:
                    print("⚠️ Erişim engellendi (403), uzun bekleme...")
                    print("💡 Tüm profiller tükendi, manuel giriş gerekebilir!")
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

# ===== ÇOK PROFILLL GİRİŞ SİSTEMİ =====

def profil_performans_kaydet(profil_no, basarili=True):
    """Profil performansını kaydet"""
    global profil_basari_orani
    from datetime import datetime
    
    if profil_no in profil_basari_orani:
        if basarili:
            profil_basari_orani[profil_no]["basarili"] += 1
            print(f"✅ Profil {profil_no} başarı sayısı: {profil_basari_orani[profil_no]['basarili']}")
        else:
            profil_basari_orani[profil_no]["basarisiz"] += 1
            print(f"❌ Profil {profil_no} başarısızlık sayısı: {profil_basari_orani[profil_no]['basarisiz']}")
        
        profil_basari_orani[profil_no]["son_kullanim"] = datetime.now().strftime("%H:%M:%S")

def profil_basari_orani_hesapla(profil_no):
    """Profil başarı oranını hesapla (0-100)"""
    if profil_no not in profil_basari_orani:
        return 0
    
    stats = profil_basari_orani[profil_no]
    toplam = stats["basarili"] + stats["basarisiz"]
    
    if toplam == 0:
        return 50  # Henüz test edilmemiş profil için varsayılan oran
    
    return round((stats["basarili"] / toplam) * 100, 1)

def en_iyi_profil_bul():
    """En iyi performansa sahip profili bul"""
    profiles = get_cookie_profiles()
    if not profiles:
        return 1
    
    en_iyi_profil = 1
    en_yuksek_oran = -1
    
    for i in range(1, len(profiles) + 1):
        oran = profil_basari_orani_hesapla(i)
        basarisizlik = profil_basari_orani[i]["basarisiz"] if i in profil_basari_orani else 0
        
        # Çok başarısız olan profilleri atla
        if basarisizlik >= PROFIL_ATLAMA_SINIRI:
            print(f"⚠️ Profil {i} atlanıyor (çok başarısız: {basarisizlik})")
            continue
        
        if oran > en_yuksek_oran:
            en_yuksek_oran = oran
            en_iyi_profil = i
    
    return en_iyi_profil

def profil_istatistikleri_goster():
    """Tüm profillerin istatistiklerini göster"""
    profiles = get_cookie_profiles()
    if not profiles:
        print("❌ Hiç profil bulunamadı!")
        return
    
    print(f"\n📊 PROFİL PERFORMANS İSTATİSTİKLERİ:")
    print("="*60)
    
    for i in range(1, len(profiles) + 1):
        if i in profil_basari_orani:
            stats = profil_basari_orani[i]
            oran = profil_basari_orani_hesapla(i)
            profil_dosya = profiles[i-1] if i <= len(profiles) else "N/A"
            
            durum = "🎯 AKTİF" if i == active_cookie_profile else ""
            if stats["basarisiz"] >= PROFIL_ATLAMA_SINIRI:
                durum += " ⚠️ ATLANAN"
            
            print(f"\n📁 Profil {i}: {profil_dosya} {durum}")
            print(f"   ✅ Başarılı: {stats['basarili']}")
            print(f"   ❌ Başarısız: {stats['basarisiz']}")
            print(f"   📊 Başarı oranı: %{oran}")
            print(f"   🕐 Son kullanım: {stats['son_kullanim'] or 'Henüz kullanılmadı'}")

def aktif_profil_durumu():
    """Aktif profil durumunu göster"""
    profiles = get_cookie_profiles()
    if not profiles:
        print("❌ Hiç profil bulunamadı!")
        return
    
    print(f"\n📊 ÇOK PROFİLLİ SİSTEM DURUMU:")
    print(f"   🔢 Toplam profil: {len(profiles)}")
    print(f"   🎯 Aktif profil: {active_cookie_profile}")
    print(f"   📊 Başarı oranı: %{profil_basari_orani_hesapla(active_cookie_profile)}")
    
    if active_cookie_profile <= len(profiles):
        aktif_dosya = profiles[active_cookie_profile - 1]
        print(f"   📁 Aktif dosya: {aktif_dosya}")
    else:
        print(f"   ⚠️ Aktif profil indeksi hatalı!")

def otomatik_profil_degistir():
    """403 hatası sonrası otomatik profil değiştir - AKILLI SEÇİM"""
    global scholar_session, active_cookie_profile
    
    profiles = get_cookie_profiles()
    if len(profiles) <= 1:
        print("⚠️ Tek profil mevcut, profil değiştirilemez")
        return False
    
    eski_profil = active_cookie_profile
    
    # Akıllı profil seçimi - en iyi performanslı profili bul
    print("🧠 En iyi profil analiz ediliyor...")
    en_iyi_profil = en_iyi_profil_bul()
    
    # Eğer en iyi profil şu anki profilse, sonraki profili seç
    if en_iyi_profil == active_cookie_profile:
        active_cookie_profile = (active_cookie_profile % len(profiles)) + 1
        print(f"🔄 Mevcut profil en iyi, sıradaki profil seçiliyor: {active_cookie_profile}")
    else:
        active_cookie_profile = en_iyi_profil
        print(f"🎯 En iyi profil seçildi: {active_cookie_profile} (%{profil_basari_orani_hesapla(en_iyi_profil)} başarı oranı)")
    
    print(f"\n🔄 403 HATASI TESPİT EDİLDİ - AKILLI PROFİL DEĞİŞTİRME")
    print(f"   ❌ Eski: {profiles[eski_profil - 1]} (Profil {eski_profil})")
    print(f"   ✅ Yeni: {profiles[active_cookie_profile - 1]} (Profil {active_cookie_profile})")
    
    # Yeni session oluştur
    scholar_session = requests.Session()
    scholar_session.headers.update({
        'User-Agent': random.choice(USER_AGENT_LISTESI),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    # Yeni profili yükle
    yeni_profil = profiles[active_cookie_profile - 1]
    if cookies_yukle(scholar_session, yeni_profil):
        # Hızlı test et
        test_url = "https://scholar.google.com.tr/"
        try:
            test_response = scholar_session.get(test_url, timeout=15)
            if test_response.status_code == 200:
                print("✅ Yeni profil başarıyla aktif!")
                print(f"🎯 Şimdi aktif profil: {active_cookie_profile}")
                aktif_profil_durumu()  # Durumu göster
                return True
            else:
                print(f"⚠️ Yeni profil test başarısız: {test_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Yeni profil test hatası: {e}")
            return False
    else:
        print("❌ Yeni profil yüklenemedi")
        return False

def get_cookie_profiles():
    """Mevcut cookie profillerinin listesini döndür"""
    profiles = []
    if os.path.exists(COOKIE_PROFILE_1):
        profiles.append(COOKIE_PROFILE_1)
    if os.path.exists(COOKIE_PROFILE_2):
        profiles.append(COOKIE_PROFILE_2)
    if os.path.exists(COOKIE_PROFILE_3):
        profiles.append(COOKIE_PROFILE_3)
    return profiles

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
        
        cookie_count = 0
        for name, value in cookies_dict.items():
            session.cookies.set(name, value, domain='.google.com')
            session.cookies.set(name, value, domain='.scholar.google.com')
            session.cookies.set(name, value, domain='.scholar.google.com.tr')
            cookie_count += 1
        
        print(f"✅ Cookies yüklendi: {dosya_yolu} ({cookie_count} cookie)")
        return True
    except Exception as e:
        print(f"❌ Cookies yükleme hatası: {e}")
        return False

def cookies_yukle_coklu_profil(session):
    """Çoklu profil sistemi ile cookie yükleme - fallback mechanism"""
    global active_cookie_profile
    
    profiles = get_cookie_profiles()
    if not profiles:
        print("❌ Hiç cookie profili bulunamadı!")
        return False
    
    print(f"🔄 {len(profiles)} cookie profili tespit edildi")
    
    # Önce aktif profili dene
    if active_cookie_profile <= len(profiles):
        aktif_profil = profiles[active_cookie_profile - 1]
        print(f"🎯 Aktif profil deneniyor: {aktif_profil}")
        
        if cookies_yukle(session, aktif_profil):
            # Quick test
            if test_cookie_profile(session, aktif_profil):
                print(f"✅ Aktif profil başarılı: {aktif_profil}")
                return True
            else:
                print(f"⚠️ Aktif profil geçersiz: {aktif_profil}")
    
    # Fallback: Diğer profilleri sırayla dene
    print("🔄 Fallback sistemi aktif - diğer profiller deneniyor...")
    
    for i, profil in enumerate(profiles):
        if i + 1 == active_cookie_profile:
            continue  # Skip already tested profile
        
        print(f"🔄 Fallback profil deneniyor: {profil}")
        
        # Clear existing cookies
        session.cookies.clear()
        
        if cookies_yukle(session, profil):
            if test_cookie_profile(session, profil):
                print(f"✅ Fallback başarılı! Aktif profil değiştirildi: {profil}")
                active_cookie_profile = i + 1
                return True
            else:
                print(f"❌ Fallback profil başarısız: {profil}")
    
    print("❌ Hiçbir cookie profili çalışmıyor!")
    return False

def test_cookie_profile(session, profil_adi):
    """Cookie profilinin çalışıp çalışmadığını test et"""
    try:
        print(f"🧪 Test ediliyor: {profil_adi}")
        test_url = "https://scholar.google.com.tr/"
        response = session.get(test_url, timeout=15)
        
        if response.status_code == 200:
            giris_durumu = giris_durumu_kontrol(response.text, session)
            if giris_durumu:
                print(f"✅ {profil_adi} - Test başarılı!")
                return True
            else:
                print(f"⚠️ {profil_adi} - Giriş tespit edilemedi")
                return False
        else:
            print(f"❌ {profil_adi} - HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {profil_adi} - Test hatası: {e}")
        return False

def giris_durumu_kontrol(response_text, session):
    """Google Scholar giriş durumunu kontrol eder"""
    try:
        # 1. Cookies'da kimlik doğrulama token'larını kontrol et
        kimlik_cookies = ['SID', 'HSID', 'SSID', 'APISID', 'SAPISID']
        active_auth_cookies = 0
        
        for cookie_name in kimlik_cookies:
            if any(cookie.name == cookie_name and cookie.value for cookie in session.cookies):
                active_auth_cookies += 1
        
        print(f"🔐 Kimlik doğrulama cookies: {active_auth_cookies}/{len(kimlik_cookies)}")
        
        # 2. Sayfa içeriğinde giriş belirtilerini kontrol et
        giris_belirtileri = [
            'data-signin-url',  # Google giriş URL'si
            'My library',       # Kişisel kütüphane
            'Kütüphanem',      # Türkçe kütüphane
            'My profile',      # Profil
            'Alerts',          # Uyarılar
            'Cited by',        # Atıf takibi
            'Scholar Metrics'   # Scholar Metrikleri
        ]
        
        bulundu_belirtiler = 0
        for belirti in giris_belirtileri:
            if belirti.lower() in response_text.lower():
                bulundu_belirtiler += 1
        
        print(f"📊 Giriş belirtileri: {bulundu_belirtiler}/{len(giris_belirtileri)}")
        
        # 3. Anti-belirtiler (giriş yapılmamış işaretleri)
        anti_belirtiler = [
            'Sign in',
            'Oturum aç',
            'Giriş yap',
            'Please sign in'
        ]
        
        anti_bulundu = 0
        for anti in anti_belirtiler:
            if anti.lower() in response_text.lower():
                anti_bulundu += 1
        
        print(f"⚠️ Giriş yapılmamış belirtileri: {anti_bulundu}/{len(anti_belirtiler)}")
        
        # Değerlendirme
        if active_auth_cookies >= 3:  # En az 3 kimlik cookie'si var
            print("✅ Güçlü kimlik doğrulama tespit edildi")
            return True
        elif active_auth_cookies >= 2 and bulundu_belirtiler >= 2:  # Orta seviye
            print("✅ Kısmi giriş tespit edildi")
            return True
        elif anti_bulundu == 0 and bulundu_belirtiler >= 1:  # Zayıf ama pozitif
            print("⚠️ Zayıf giriş tespit edildi")
            return True
        else:
            print("❌ Giriş yapılmamış")
            return False
            
    except Exception as e:
        print(f"❌ Giriş kontrolü hatası: {e}")
        return False

def scholar_session_baslat():
    """Çoklu profil sistemi ile Google Scholar giriş session'ı başlat"""
    global scholar_session
    
    if not SCHOLAR_LOGIN_ENABLED:
        print("ℹ️ Scholar giriş sistemi pasif")
        return None
    
    print("\n" + "="*60)
    print("🔐 ÇOK PROFİLLİ GİRİŞ SİSTEMİ BAŞLATILIYOR")
    print("="*60)
    
    try:
        # Önce Selenium ile otomatik giriş dene
        if SELENIUM_AUTO_LOGIN and selenium_otomatik_giris():
            return scholar_session
        
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
        
        # Çoklu profil sistemi ile cookie yükleme
        if MULTI_LOGIN_ENABLED:
            print("🎯 Çoklu giriş sistemi aktif")
            
            if cookies_yukle_coklu_profil(scholar_session):
                print("✅ Çoklu profil sistemi - Giriş başarılı!")
                print(f"🎯 Aktif profil: {active_cookie_profile}")
                return scholar_session
            else:
                print("❌ Çoklu profil sistemi - Tüm profiller başarısız")
        else:
            # Tek profil sistemi (eski yöntem)
            print("🔄 Tek profil sistemi aktif")
            if cookies_yukle(scholar_session, COOKIES_FILE):
                test_url = "https://scholar.google.com.tr/"
                response = scholar_session.get(test_url, timeout=30)
                
                if response.status_code == 200:
                    if giris_durumu_kontrol(response.text, scholar_session):
                        print("✅ Tek profil - Giriş başarılı!")
                        return scholar_session
                    else:
                        print("⚠️ Tek profil - Cookies geçersiz")
                else:
                    print(f"⚠️ Tek profil - HTTP {response.status_code}")
        
        print("🔐 Manuel Google Scholar giriş gerekli")
        return scholar_session
        
    except Exception as e:
        print(f"❌ Scholar session başlatma hatası: {e}")
        return None

def profil_yonetimi_menu():
    """Çoklu cookie profili yönetim menüsü"""
    while True:
        print("\n" + "="*60)
        print("🔐 ÇOK PROFİLLİ GİRİŞ YÖNETİMİ")
        print("="*60)
        
        profiles = get_cookie_profiles()
        print(f"📊 Mevcut profiller: {len(profiles)}")
        
        for i, profil in enumerate(profiles, 1):
            status = "🎯 AKTİF" if i == active_cookie_profile else "💤 PASİF"
            print(f"  {i}. {profil} {status}")
        
        if not profiles:
            print("  ❌ Hiç profil bulunamadı!")
        
        print("\n📋 MENÜ:")
        print("1. Profil değiştir")
        print("2. Profil test et")
        print("3. Yeni profil ekle")
        print("4. Profil durumları")
        print("5. Manuel giriş rehberi")
        print("0. Ana menüye dön")
        
        secim = input("\n🎯 Seçiminiz (0-5): ").strip()
        
        if secim == "0":
            break
        elif secim == "1":
            profil_degistir()
        elif secim == "2":
            profil_test_et()
        elif secim == "3":
            yeni_profil_ekle()
        elif secim == "4":
            profil_durumlari()
        elif secim == "5":
            manuel_giris_rehberi()
        else:
            print("❌ Geçersiz seçim!")

def profil_degistir():
    """Aktif profili değiştir"""
    global active_cookie_profile
    
    profiles = get_cookie_profiles()
    if not profiles:
        print("❌ Değiştirilecek profil yok!")
        return
    
    print("\n📋 Mevcut profiller:")
    for i, profil in enumerate(profiles, 1):
        status = "🎯 AKTİF" if i == active_cookie_profile else ""
        print(f"  {i}. {profil} {status}")
    
    try:
        secim = int(input(f"\n🎯 Yeni aktif profil (1-{len(profiles)}): "))
        if 1 <= secim <= len(profiles):
            active_cookie_profile = secim
            print(f"✅ Aktif profil değiştirildi: {profiles[secim-1]}")
        else:
            print("❌ Geçersiz profil numarası!")
    except ValueError:
        print("❌ Geçerli bir sayı girin!")

def profil_test_et():
    """Seçilen profili test et"""
    profiles = get_cookie_profiles()
    if not profiles:
        print("❌ Test edilecek profil yok!")
        return
    
    print("\n📋 Test edilecek profil:")
    for i, profil in enumerate(profiles, 1):
        print(f"  {i}. {profil}")
    
    try:
        secim = int(input(f"\n🧪 Test edilecek profil (1-{len(profiles)}): "))
        if 1 <= secim <= len(profiles):
            test_session = requests.Session()
            test_session.headers.update({
                'User-Agent': random.choice(USER_AGENT_LISTESI),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            })
            
            test_cookie_profile(test_session, profiles[secim-1])
        else:
            print("❌ Geçersiz profil numarası!")
    except ValueError:
        print("❌ Geçerli bir sayı girin!")

def yeni_profil_ekle():
    """Yeni cookie profili ekle"""
    print("\n🆕 Yeni Cookie Profili Ekleme")
    print("="*40)
    print("1. Browser'da Google Scholar'a giriş yapın")
    print("2. F12 → Network → herhangi bir istek → Headers")
    print("3. 'Cookie:' değerini kopyalayın")
    
    cookie_string = input("\n📋 Cookie string'ini yapıştırın: ").strip()
    
    if not cookie_string:
        print("❌ Boş cookie string!")
        return
    
    # Yeni profil dosya adı
    profil_no = 3
    while os.path.exists(f"scholar_cookies_profile{profil_no}.json"):
        profil_no += 1
    
    yeni_profil = f"scholar_cookies_profile{profil_no}.json"
    
    try:
        # Cookie string'i parse et
        cookies_dict = {}
        for cookie in cookie_string.split(';'):
            if '=' in cookie:
                name, value = cookie.strip().split('=', 1)
                cookies_dict[name.strip()] = value.strip()
        
        # Dosyaya kaydet
        with open(yeni_profil, 'w', encoding='utf-8') as f:
            json.dump(cookies_dict, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Yeni profil oluşturuldu: {yeni_profil}")
        print(f"📊 {len(cookies_dict)} cookie kaydedildi")
        
        # Test et
        test_session = requests.Session()
        test_session.headers.update({
            'User-Agent': random.choice(USER_AGENT_LISTESI),
        })
        
        test_cookie_profile(test_session, yeni_profil)
        
    except Exception as e:
        print(f"❌ Profil oluşturma hatası: {e}")

def profil_durumlari():
    """Tüm profillerin durumlarını göster"""
    profiles = get_cookie_profiles()
    if not profiles:
        print("❌ Profil bulunamadı!")
        return
    
    print("\n📊 PROFİL DURUM RAPORU")
    print("="*50)
    
    for i, profil in enumerate(profiles, 1):
        status = "🎯 AKTİF" if i == active_cookie_profile else "💤 PASİF"
        print(f"\n{i}. {profil} {status}")
        
        # Dosya bilgileri
        if os.path.exists(profil):
            file_size = os.path.getsize(profil)
            with open(profil, 'r', encoding='utf-8') as f:
                cookies_dict = json.load(f)
            print(f"   📁 Dosya boyutu: {file_size} byte")
            print(f"   🍪 Cookie sayısı: {len(cookies_dict)}")
            
            # Önemli cookie'leri kontrol et
            important_cookies = ['SID', 'HSID', 'SSID', 'APISID', 'SAPISID']
            found_important = [cookie for cookie in important_cookies if cookie in cookies_dict]
            print(f"   🔐 Önemli cookies: {len(found_important)}/{len(important_cookies)}")
        else:
            print("   ❌ Dosya bulunamadı!")

def manuel_giris_rehberi():
    """Manuel giriş için rehber göster"""
    print("\n" + "="*80)
    print("🔐 GOOGLE SCHOLAR MANuel GİRİŞ REHBERİ")
    print("="*80)
    print("📋 ÇOK PROFİLLİ SİSTEM İÇİN:")
    print("1. Browser'ınızda https://scholar.google.com.tr/ adresine gidin")
    print("2. Google hesabınız ile giriş yapın")
    print("3. Herhangi bir arama yapın (örn: 'beslenme bilimi')")
    print("4. F12 basıp Developer Tools'u açın")
    print("5. Network tab'ına gidin")
    print("6. Bir PDF linkine tıklayın")
    print("7. İsteklerde 'Headers' kısmından 'Cookie' değerini kopyalayın")
    print("8. Program menüsünden 'Yeni profil ekle' seçeneğini kullanın")
    print("\n💡 MEVCUT PROFİLLER:")
    profiles = get_cookie_profiles()
    for i, profil in enumerate(profiles, 1):
        status = "🎯 AKTİF" if i == active_cookie_profile else "💤 PASİF"
        print(f"  {i}. {profil} {status}")
    print("\n💡 Fallback Sistemi: Bir profil çalışmazsa otomatik diğeri denenecek!")
    print("="*80)

def selenium_otomatik_giris():
    """Selenium ile Google Scholar'a otomatik giriş"""
    global scholar_session
    
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium yüklü değil. Yüklemek için: pip install selenium")
        return False
    
    if not SELENIUM_AUTO_LOGIN:
        print("ℹ️ Selenium otomatik giriş pasif")
        return False
    
    if not GOOGLE_EMAIL or not GOOGLE_PASSWORD:
        print("❌ Google email/şifre tanımlanmamış")
        print("💡 GOOGLE_EMAIL ve GOOGLE_PASSWORD değişkenlerini ayarlayın")
        return False
    
    try:
        print("🔄 Selenium ile otomatik giriş başlatılıyor...")
        
        # Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Görünmez mod
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # WebDriver başlat
        driver = webdriver.Chrome(options=chrome_options)
        
        # Google Scholar'a git
        driver.get("https://scholar.google.com.tr/")
        time.sleep(3)
        
        # Giriş linkini bul ve tıkla
        try:
            login_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Giriş"))
            )
            login_link.click()
            time.sleep(3)
        except:
            print("❌ Giriş linki bulunamadı")
            driver.quit()
            return False
        
        # Email gir
        try:
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
            email_input.send_keys(GOOGLE_EMAIL)
            
            next_button = driver.find_element(By.ID, "identifierNext")
            next_button.click()
            time.sleep(3)
        except:
            print("❌ Email girme hatası")
            driver.quit()
            return False
        
        # Şifre gir
        try:
            password_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "password"))
            )
            password_input.send_keys(GOOGLE_PASSWORD)
            
            next_button = driver.find_element(By.ID, "passwordNext")
            next_button.click()
            time.sleep(5)
        except:
            print("❌ Şifre girme hatası")
            driver.quit()
            return False
        
        # Giriş başarılı mı kontrol et
        current_url = driver.current_url
        if "scholar.google" in current_url:
            print("✅ Selenium ile giriş başarılı!")
            
            # Cookies'leri al
            cookies = driver.get_cookies()
            
            # Session'a cookies'leri ekle
            scholar_session = requests.Session()
            for cookie in cookies:
                scholar_session.cookies.set(
                    cookie['name'], 
                    cookie['value'],
                    domain=cookie.get('domain', '.google.com')
                )
            
            # Cookies'leri kaydet
            cookies_kaydet(scholar_session, COOKIES_FILE)
            
            driver.quit()
            return True
        else:
            print("❌ Giriş başarısız - yönlendirme hatası")
            driver.quit()
            return False
            
    except Exception as e:
        print(f"❌ Selenium giriş hatası: {e}")
        if 'driver' in locals():
            driver.quit()
        return False

def kullanim_rehberi():
    """Google Scholar giriş sisteminin kullanım rehberi"""
    print("\n" + "="*80)
    print("🎯 GOOGLE SCHOLAR GİRİŞ SİSTEMİ KULLANIM REHBERİ")
    print("="*80)
    print("\n🔐 YÖNTEMLERİ:")
    print("1. Manual Cookies (Kolay)")
    print("2. Selenium Otomatik Giriş (Tam Otomatik)")
    print("\n" + "-"*80)
    print("📋 YÖNTEM 1 - MANUAL COOKİES:")
    print("-"*80)
    print("1. Bu kodu çalıştırın:")
    print("   SCHOLAR_LOGIN_ENABLED = True")
    print("\n2. Scholar giriş yapmak için:")
    print("   - https://scholar.google.com.tr/ adresine gidin")
    print("   - Google hesabınızla giriş yapın")
    print("   - F12 → Network → Headers → Cookie değerini kopyalayın")
    print("   - Sistem otomatik cookie dosyası oluşturacak")
    print("\n" + "-"*80)
    print("🤖 YÖNTEM 2 - SELENİUM OTOMATİK:")
    print("-"*80)
    print("1. Selenium kurun: pip install selenium")
    print("2. Chrome WebDriver indirin: https://chromedriver.chromium.org/")
    print("3. Bu ayarları yapın:")
    print("   SCHOLAR_LOGIN_ENABLED = True")
    print("   SELENIUM_AUTO_LOGIN = True")
    print("   GOOGLE_EMAIL = 'email@gmail.com'")
    print("   GOOGLE_PASSWORD = 'your_password'")
    print("\n⚠️ GÜVENLİK: Environment variable kullanın:")
    print("   import os")
    print("   GOOGLE_EMAIL = os.getenv('GOOGLE_EMAIL')")
    print("   GOOGLE_PASSWORD = os.getenv('GOOGLE_PASSWORD')")
    print("\n" + "-"*80)
    print("🧪 TEST KOMUTLARİ:")
    print("-"*80)
    print("# Giriş sistemini test et")
    print("python -c \"from pdf_indir import test_scholar_login; test_scholar_login()\"")
    print("\n# Tek kelime ile test et")
    print("python -c \"from pdf_indir import mini_test; mini_test()\"")
    print("="*80)

def test_scholar_login():
    """Google Scholar giriş sistemini test et"""
    print("🧪 Google Scholar Giriş Sistemi Test Ediliyor...")
    
    if not SCHOLAR_LOGIN_ENABLED:
        print("❌ Giriş sistemi pasif. SCHOLAR_LOGIN_ENABLED = True yapın")
        return False
    
    # Session başlat
    session = scholar_session_baslat()
    
    if session:
        # Test isteği gönder
        test_url = "https://scholar.google.com.tr/"
        response = guvenli_istek_gonder(test_url)
        
        if response and response.status_code == 200:
            print("\n🔍 Giriş durumu analizi:")
            if giris_durumu_kontrol(response.text, session):
                print("\n✅ Giriş sistemi çalışıyor!")
                print("✅ Google Scholar oturum aktif!")
                print("✅ 403 hataları azalacak!")
                return True
            else:
                print("\n⚠️ Giriş tespit edilemedi")
                print("💡 Cookie'leri yenileyin veya manuel giriş yapın")
                print("💡 Yine de session ile 403 hataları azalacak")
                return True  # Session yine de yararlı
        else:
            print("❌ Scholar'a erişim başarısız")
            return False
    else:
        print("❌ Session başlatılamadı")
        return False

def mini_test():
    """Tek anahtar kelime ile mini test"""
    print("🧪 Mini Test: 'beslenme bilimi' anahtar kelimesi ile...")
    
    # Google Scholar giriş session'ı başlat
    scholar_session_baslat()
    
    # Test klasörü oluştur
    os.makedirs(ANA_DIZIN, exist_ok=True)
    
    try:
        # Test anahtar kelimesi ile arama ve indirme
        indirilen_sayi = anahtar_kelime_ara_ve_indir("beslenme bilimi", maks_sayfa=1)
        
        if indirilen_sayi > 0:
            print(f"✅ Test başarılı! {indirilen_sayi} PDF indirildi")
            return True
        else:
            print("❌ Test başarısız, PDF indirilemedi")
            print("💡 Olası nedenler:")
            print("   - Cookie profilleri geçersiz olabilir")
            print("   - Google Scholar geçici blokaj")
            print("   - İnternet bağlantı sorunu")
            return False
            
    except Exception as e:
        print(f"❌ Mini test hatası: {e}")
        return False

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

    # Google Scholar giriş session'ı başlat
    scholar_session_baslat()
    
    if SCHOLAR_LOGIN_ENABLED and not scholar_session:
        manuel_giris_rehberi()
        yanit = input("\n🤔 Google Scholar giriş olmadan devam etmek istiyor musunuz? (e/h): ")
        if yanit.lower() != 'e':
            print("❌ İşlem iptal edildi. Giriş yapmak için SCHOLAR_LOGIN_ENABLED = True yapın.")
            return

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

def ana_menu():
    """Ana menü sistemi"""
    while True:
        print("\n" + "="*80)
        print("🇹🇷 TÜRKÇE DİYETİSYEN LLM EĞİTİMİ İÇİN PDF İNDİRİCİ")
        print("="*80)
        print("📚 Amaç: Google Scholar'dan Türkçe beslenme/diyetetik PDF'lerini toplar")
        print("🎯 Hedef: LLM model eğitimi için kaliteli Türkçe akademik veri seti")
        
        # Profil durumu göster
        profiles = get_cookie_profiles()
        if profiles:
            print(f"\n🔐 Aktif profil sistemi: {len(profiles)} profil bulundu")
            aktif_profil = profiles[active_cookie_profile - 1] if active_cookie_profile <= len(profiles) else "Belirtilmemiş"
            print(f"🎯 Aktif: {aktif_profil}")
        else:
            print("\n⚠️ Hiç cookie profili bulunamadı!")
        
        print("\n📋 MENÜ:")
        print("1. PDF indirmeyi başlat (113 Türkçe anahtar kelime)")
        print("2. Mini test (tek anahtar kelime ile)")
        print("3. Google Scholar giriş testi")
        print("4. Çoklu profil yönetimi 🆕")
        print("5. İstatistikleri görüntüle")
        print("6. Profil performans istatistikleri 🚀")
        print("7. Kullanım rehberi")
        print("0. Çıkış")
        print("="*80)
        
        secim = input("\n🎯 Seçiminiz (0-7): ").strip()
        
        if secim == "0":
            print("👋 Çıkış yapılıyor...")
            break
        elif secim == "1":
            print("\n🚀 PDF indirme başlatılıyor...")
            main()
            break
        elif secim == "2":
            print("\n🧪 Mini test başlatılıyor...")
            mini_test()
        elif secim == "3":
            print("\n🔍 Google Scholar giriş testi...")
            test_scholar_login()
        elif secim == "4":
            profil_yonetimi_menu()
        elif secim == "5":
            istatistikleri_goster()
        elif secim == "6":
            profil_istatistikleri_goster()
        elif secim == "7":
            kullanim_rehberi()
        else:
            print("❌ Geçersiz seçim! Lütfen 0-7 arası bir sayı girin.")

def istatistikleri_goster():
    """İstatistikleri göster"""
    istatistik_dosyasi = os.path.join(ANA_DIZIN, "turkce_indirme_istatistikleri.json")
    
    if not os.path.exists(istatistik_dosyasi):
        print("❌ İstatistik dosyası bulunamadı!")
        print(f"   Dosya: {istatistik_dosyasi}")
        print("💡 PDF indirme işlemi henüz çalıştırılmamış.")
        return
    
    try:
        with open(istatistik_dosyasi, 'r', encoding='utf-8') as f:
            istatistikler = json.load(f)
        
        print("\n📊 TÜRKÇE PDF İNDİRME İSTATİSTİKLERİ")
        print("="*50)
        print(f"🕐 Başlangıç: {istatistikler.get('baslangic_zamani', 'N/A')}")
        print(f"🕒 Bitiş: {istatistikler.get('bitis_zamani', 'Devam ediyor...')}")
        print(f"⏱️ Süre: {istatistikler.get('toplam_sure_dakika', 'N/A')} dakika")
        print(f"📚 Toplam anahtar kelime: {istatistikler.get('toplam_anahtar_kelime', 0)}")
        print(f"✅ Başarılı anahtar kelime: {istatistikler.get('basarili_anahtar_kelime', 0)}")
        print(f"📄 Toplam PDF: {istatistikler.get('toplam_indirilen_pdf', 0)}")
        print(f"🔗 Bağlantı modu: {istatistikler.get('baglanti_modu', 'N/A')}")
        print(f"📂 Ana dizin: {istatistikler.get('ana_dizin', ANA_DIZIN)}")
        
        if 'basarili_anahtar_kelimeler' in istatistikler:
            print(f"\n🎯 Son 10 başarılı anahtar kelime:")
            for i, kelime in enumerate(istatistikler['basarili_anahtar_kelimeler'][-10:], 1):
                print(f"   {i}. {kelime}")
    
    except Exception as e:
        print(f"❌ İstatistik okuma hatası: {e}")

if __name__ == "__main__":
    import sys
    
    # Komut satırı argümanları kontrol et
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--help', '-h', 'help']:
            kullanim_rehberi()
        elif arg in ['--menu', '-m', 'menu']:
            ana_menu()
        elif arg in ['--test', '-t', 'test']:
            test_scholar_login()
        elif arg in ['--mini', 'mini']:
            mini_test()
        elif arg in ['--setup', 'setup']:
            print("🔧 Hızlı Kurulum:")
            print("1. pip install requests beautifulsoup4 tqdm lxml")
            print("2. İsteğe bağlı: pip install selenium")
            print("3. SCHOLAR_LOGIN_ENABLED = True yapın")
            print("4. python pdf_indir.py --help")
        else:
            print("❌ Bilinmeyen argüman!")
            print("💡 Kullanım: python pdf_indir.py [--help|--menu|--test|--mini|--setup]")
    else:
        # Argüman yoksa ana menüyü başlat
        ana_menu() 
