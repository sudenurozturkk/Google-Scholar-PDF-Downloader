"""
Bir web sayfasındaki tüm PDF dosyalarını toplu olarak indiren script.
Kullanım: python pdf_indir.py
PDF'ler, scriptin bulunduğu dizinde 'indirilen_pdfler' klasörüne kaydedilir.
Zaten indirilmiş PDF'leri atlar.
"""
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import re

# Hedef site
URL = "https://hsgm.saglik.gov.tr/tr/dokumanlar-6.html"
KLASOR = "indirilen_pdfler"

# Ek PDF linkleri
EK_LINKLER = [
    "https://tkd.org.tr/TKDData/Uploads/files/hipertansiyonda-beslenme.pdf?hl=tr-TR",
    "https://temd.org.tr/Assets/docs/DiyabetveSaglikliBeslenmeKitapcigi.pdf?hl=tr-TR",
    "https://dergipark.org.tr/en/download/article-file/988815?hl=tr-TR",
    "https://www.sporhekimligi.com/Metablik_sendrom_ve_egzersiz.pdf?hl=tr-TR",
    "https://dergipark.org.tr/tr/download/article-file/382638?hl=tr-TR",
    "https://dergipark.org.tr/en/download/article-file/1038020?hl=tr-TR",
    "https://dergipark.org.tr/en/download/article-file/3288900?hl=tr-TR",
    "https://www.medipol.edu.tr/sites/default/files/2022-06/web.RAMAZAN%20REHBER-f4e69932-d956-4a5d-a8cf-36a762e3e76a.pdf",
    "https://openknowledge.fao.org/server/api/core/bitstreams/bf234a5b-2b30-4afa-94d7-e14997c06b68/content",
    "https://tekinakpolat.com/wp-content/uploads/2017/12/turkiye-beslenme-rehberi.pdf",
    "https://meslek.meb.gov.tr/upload/dersmateryali/pdf/YIH2024DYH111209.pdf",
    "https://www.beykoz.edu.tr/content/editor/5e67287487405_beykozuniversitesi-vucuttipi-002.pdf",
    "https://pedider.org.tr/pdf/1.pdf"
]

def dosya_adi_temizle(url):
    """URL'den güvenli dosya adı oluştur"""
    parsed = urlparse(url)
    dosya_adi = os.path.basename(parsed.path)
    
    # Eğer dosya adı yoksa veya .pdf ile bitmiyorsa, URL'den benzersiz bir ad oluştur
    if not dosya_adi or not dosya_adi.lower().endswith('.pdf'):
        # URL'den hash benzeri bir ad oluştur
        url_hash = str(abs(hash(url)))[:8]
        dosya_adi = f"dokuman_{url_hash}.pdf"
    
    # Dosya adındaki zararlı karakterleri temizle
    dosya_adi = re.sub(r'[<>:"/\\|?*]', '_', dosya_adi)
    return dosya_adi

def pdf_indir(url, dosya_yolu):
    """Tek PDF dosyasını indir"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        r = requests.get(url, stream=True, timeout=30, headers=headers)
        r.raise_for_status()
        
        with open(dosya_yolu, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"Hata: {url} -> {e}")
        return False

# Klasör oluştur
os.makedirs(KLASOR, exist_ok=True)

# Zaten indirilmiş dosyaları kontrol et
mevcut_dosyalar = set(os.listdir(KLASOR))
print(f"Klasörde {len(mevcut_dosyalar)} dosya mevcut.")

# Siteyi çek
print("Site taranıyor...")
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    # PDF linklerini bul
    pdf_linkleri = set()
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.lower().endswith(".pdf"):
            tam_link = urljoin(URL, href)
            pdf_linkleri.add(tam_link)

    print(f"Siteden {len(pdf_linkleri)} adet PDF bulundu.")
    
except Exception as e:
    print(f"Site tarama hatası: {e}")
    pdf_linkleri = set()

# Ek linkleri ekle
pdf_linkleri.update(EK_LINKLER)
print(f"Toplam {len(pdf_linkleri)} adet PDF indirilecek.")

# PDF'leri indir
indirilen_sayi = 0
atlanan_sayi = 0

for pdf_url in tqdm(pdf_linkleri, desc="PDF'ler indiriliyor"):
    dosya_adi = dosya_adi_temizle(pdf_url)
    dosya_yolu = os.path.join(KLASOR, dosya_adi)
    
    # Dosya zaten mevcutsa atla
    if dosya_adi in mevcut_dosyalar:
        print(f"Atlandı (zaten mevcut): {dosya_adi}")
        atlanan_sayi += 1
        continue
    
    # PDF'yi indir
    if pdf_indir(pdf_url, dosya_yolu):
        indirilen_sayi += 1
        mevcut_dosyalar.add(dosya_adi)  # Listede güncelle
    else:
        # Başarısız indirme durumunda dosyayı sil
        if os.path.exists(dosya_yolu):
            os.remove(dosya_yolu)

print(f"\nİşlem tamamlandı!")
print(f"Yeni indirilen: {indirilen_sayi}")
print(f"Atlanan (mevcut): {atlanan_sayi}")
print(f"Toplam dosya: {len(mevcut_dosyalar)}")
