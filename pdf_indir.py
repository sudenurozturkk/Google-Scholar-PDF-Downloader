"""
Google Scholar'dan akademik makalelerin PDF'lerini toplu olarak indiren script.
Kullanım: python pdf_indir.py
"""
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import time
import hashlib
import json

# Google Scholar arama URL'leri - Buraya kendi URL'lerinizi ekleyin
SCHOLAR_URLS = [
    # Örnek: "https://scholar.google.com.tr/scholar?hl=tr&as_sdt=0,5&as_vis=1&q=ARAMA_KELIMELERI"
    # Buraya kendi URL'lerinizi ekleyin
    "https://scholar.google.com.tr/scholar?start=0&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",        
    "https://scholar.google.com.tr/scholar?start=10&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=20&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=30&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=40&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=50&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=60&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=70&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=80&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=90&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=100&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=110&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=120&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=130&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=140&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=150&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=160&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=170&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=180&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=190&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=200&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=210&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=220&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=230&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=240&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=250&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=260&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=270&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=280&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=290&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1",
    "https://scholar.google.com.tr/scholar?start=300&q=beslenme+kilo+verme+obezite&hl=tr&as_sdt=0,5&as_vis=1"
]

# Ayarlar
DOWNLOAD_FOLDER = r"C:\Users\Administrator\Desktop\TEKNOFEST\akademikmakaleler"
HASH_FILE = os.path.join(DOWNLOAD_FOLDER, "indirilen_pdfler.json")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
MAX_PDFS_PER_SEARCH = 10  # Her aramada maksimum 10 PDF indir
DELAY_BETWEEN_DOWNLOADS = 2  # PDF'ler arası bekleme (saniye)
DELAY_BETWEEN_SEARCHES = 20  # Aramalar arası bekleme (saniye)

def dosya_hash_hesapla(dosya_yolu):
    """Dosyanın MD5 hash'ini hesaplar"""
    hash_md5 = hashlib.md5()
    try:
        with open(dosya_yolu, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None

def indirilen_pdfler_yukle():
    """Önceden indirilen PDF'lerin hash'lerini yükler"""
    if os.path.exists(HASH_FILE):
        try:
            with open(HASH_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def indirilen_pdfler_kaydet(indirilen_pdfler):
    """İndirilen PDF'lerin hash'lerini kaydeder"""
    try:
        with open(HASH_FILE, 'w', encoding='utf-8') as f:
            json.dump(indirilen_pdfler, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Hash dosyası kaydedilemedi: {e}")

def pdf_zaten_indirilmis_mi(pdf_content, indirilen_pdfler):
    """PDF içeriğinin daha önce indirilip indirilmediğini kontrol eder"""
    hash_md5 = hashlib.md5(pdf_content).hexdigest()
    return hash_md5 in indirilen_pdfler

def pdf_indir_tek_arama(scholar_url, arama_no, indirilen_pdfler):
    """Tek bir Google Scholar aramasından PDF indirir"""
    print(f"\n🔍 Arama {arama_no}")
    
    headers = {'User-Agent': USER_AGENT}
    
    try:
        print("Google Scholar taranıyor...")
        response = requests.get(scholar_url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        pdf_linkleri = set()
        
        # PDF linklerini bul
        for link in soup.find_all("a", href=True):
            href = link["href"]
            link_text = link.get_text().strip()
            
            if "[PDF]" in link_text or "PDF" in link_text:
                if href.startswith("/"):
                    pdf_url = urljoin("https://scholar.google.com", href)
                    pdf_linkleri.add(pdf_url)
                elif href.startswith("http"):
                    if href.lower().endswith(".pdf") or "pdf" in href.lower():
                        pdf_linkleri.add(href)
        
        # Div içindeki PDF linklerini de ara
        for div in soup.find_all("div", class_="gs_or_ggsm"):
            for link in div.find_all("a", href=True):
                href = link["href"]
                if href.startswith("/"):
                    pdf_url = urljoin("https://scholar.google.com", href)
                    pdf_linkleri.add(pdf_url)
                elif href.startswith("http") and ("pdf" in href.lower() or href.lower().endswith(".pdf")):
                    pdf_linkleri.add(href)
        
        pdf_linkleri = list(pdf_linkleri)[:MAX_PDFS_PER_SEARCH]
        
        print(f"📄 {len(pdf_linkleri)} adet PDF linki bulundu. İndiriliyor...")
        
        if len(pdf_linkleri) == 0:
            print("❌ PDF linki bulunamadı.")
            return 0, indirilen_pdfler
        
        basarili_indirilen = 0
        atlanan_pdfler = 0
        
        for i, pdf_url in enumerate(tqdm(pdf_linkleri, desc=f"İndiriliyor (Arama {arama_no})")):
            try:
                # PDF içeriğini al
                r = requests.get(pdf_url, headers=headers, stream=True, timeout=30)
                r.raise_for_status()
                
                content_type = r.headers.get('content-type', '').lower()
                if 'pdf' not in content_type and not pdf_url.lower().endswith('.pdf'):
                    continue
                
                # PDF içeriğini oku
                pdf_content = r.content
                
                # PDF daha önce indirilmiş mi kontrol et
                if pdf_zaten_indirilmis_mi(pdf_content, indirilen_pdfler):
                    atlanan_pdfler += 1
                    continue
                
                # Yeni PDF ise indir
                dosya_adi = os.path.join(DOWNLOAD_FOLDER, f"makale_{len(indirilen_pdfler) + 1}.pdf")
                
                with open(dosya_adi, "wb") as f:
                    f.write(pdf_content)
                
                # Hash'i kaydet
                hash_md5 = hashlib.md5(pdf_content).hexdigest()
                indirilen_pdfler[hash_md5] = {
                    "dosya_adi": os.path.basename(dosya_adi),
                    "url": pdf_url,
                    "tarih": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                basarili_indirilen += 1
                time.sleep(DELAY_BETWEEN_DOWNLOADS)
                
            except Exception as e:
                print(f"❌ Hata: {pdf_url} -> {e}")
        
        print(f"✅ Arama {arama_no}: {basarili_indirilen} yeni PDF indirildi, {atlanan_pdfler} PDF atlandı.")
        return basarili_indirilen, indirilen_pdfler
        
    except Exception as e:
        print(f"❌ Arama hatası ({arama_no}): {e}")
        return 0, indirilen_pdfler

def main():
    """Ana fonksiyon - tüm aramaları sırayla işler"""
    if not SCHOLAR_URLS:
        print("❌ Hata: SCHOLAR_URLS listesi boş!")
        print("Lütfen pdf_indir.py dosyasındaki SCHOLAR_URLS listesine URL'lerinizi ekleyin.")
        return
    
    print("🚀 PDF İndirici Başlatılıyor...")
    print(f"📂 İndirme dizini: {DOWNLOAD_FOLDER}")
    print(f"🔍 Toplam {len(SCHOLAR_URLS)} arama işlenecek")
    print("🔄 Önceden indirilen PDF'ler kontrol edilecek")
    print("=" * 50)
    
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    
    # Önceden indirilen PDF'leri yükle
    indirilen_pdfler = indirilen_pdfler_yukle()
    print(f"📋 Önceden {len(indirilen_pdfler)} PDF indirilmiş.")
    
    toplam_indirilen = 0
    basarili_aramalar = 0
    
    for i, scholar_url in enumerate(SCHOLAR_URLS, 1):
        print(f"\n{'='*20} ARAMA {i}/{len(SCHOLAR_URLS)} {'='*20}")
        
        try:
            indirilen_sayi, indirilen_pdfler = pdf_indir_tek_arama(scholar_url, i, indirilen_pdfler)
            toplam_indirilen += indirilen_sayi
            
            if indirilen_sayi > 0:
                basarili_aramalar += 1
            
            # Her aramadan sonra hash'leri kaydet
            indirilen_pdfler_kaydet(indirilen_pdfler)
            
            if i < len(SCHOLAR_URLS):
                print(f"⏳ {DELAY_BETWEEN_SEARCHES} saniye bekleniyor...")
                time.sleep(DELAY_BETWEEN_SEARCHES)
                
        except KeyboardInterrupt:
            print("\n⚠️ Kullanıcı tarafından durduruldu.")
            break
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}")
            continue
    
    print(f"\n{'='*50}")
    print("📊 İNDİRME ÖZETİ")
    print(f"{'='*50}")
    print(f"✅ Başarılı aramalar: {basarili_aramalar}/{len(SCHOLAR_URLS)}")
    print(f"📄 Yeni indirilen PDF: {toplam_indirilen}")
    print(f"📂 Toplam PDF sayısı: {len(indirilen_pdfler)}")
    print(f"📂 İndirme dizini: {DOWNLOAD_FOLDER}")
    print("🎉 İşlem tamamlandı!")

if __name__ == "__main__":
    main() 