"""
Google Scholar'dan akademik makalelerin PDF'lerini toplu olarak indiren script.
10 farklı aramayı sırayla işler ve her arama için ayrı klasör oluşturur.
Kullanım: python pdf_indir.py
"""
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import time

# Google Scholar arama URL'leri
SCHOLAR_URLS = [
    {
        "url": "https://scholar.google.com.tr/scholar?hl=tr&as_sdt=0,5&as_vis=1&q=beslenme+kilo+verme+obezite",
        "klasor_adi": "beslenme_kilo_verme"
    },
    {
        "url": "https://scholar.google.com.tr/scholar?hl=tr&as_sdt=0,5&as_vis=1&q=spor+egzersiz+fitness",
        "klasor_adi": "spor_egzersiz"
    },
    {
        "url": "https://scholar.google.com.tr/scholar?hl=tr&as_sdt=0,5&as_vis=1&q=psikoloji+motivasyon",
        "klasor_adi": "psikoloji_motivasyon"
    },
    {
        "url": "https://scholar.google.com.tr/scholar?hl=tr&as_sdt=0,5&as_vis=1&q=sağlık+beslenme+diyet",
        "klasor_adi": "saglik_beslenme"
    },
    {
        "url": "https://scholar.google.com.tr/scholar?hl=tr&as_sdt=0,5&as_vis=1&q=teknoloji+sağlık+uygulama",
        "klasor_adi": "teknoloji_saglik"
    },
    {
        "url": "https://scholar.google.com.tr/scholar?hl=tr&as_sdt=0,5&as_vis=1&q=ilaç+tedavi+medikal",
        "klasor_adi": "ilac_tedavi"
    },
    {
        "url": "https://scholar.google.com.tr/scholar?hl=tr&as_sdt=0,5&as_vis=1&q=cerrahi+ameliyat",
        "klasor_adi": "cerrahi_ameliyat"
    },
    {
        "url": "https://scholar.google.com.tr/scholar?hl=tr&as_sdt=0,5&as_vis=1&q=pediatri+çocuk+sağlığı",
        "klasor_adi": "pediatri_cocuk"
    },
    {
        "url": "https://scholar.google.com.tr/scholar?hl=tr&as_sdt=0,5&as_vis=1&q=kardiyoloji+kalp+sağlığı",
        "klasor_adi": "kardiyoloji_kalp"
    },
    {
        "url": "https://scholar.google.com.tr/scholar?hl=tr&as_sdt=0,5&as_vis=1&q=nöroloji+beyin+sinir",
        "klasor_adi": "noroloji_beyin"
    }
]

# Ayarlar
BASE_DOWNLOAD_FOLDER = r"C:\Users\Administrator\Desktop\TEKNOFEST\akademikmakaleler"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
MAX_PDFS_PER_SEARCH = 20
DELAY_BETWEEN_DOWNLOADS = 1
DELAY_BETWEEN_SEARCHES = 3

def pdf_indir_tek_arama(scholar_url, klasor_adi):
    """Tek bir Google Scholar aramasından PDF indirir"""
    download_folder = os.path.join(BASE_DOWNLOAD_FOLDER, klasor_adi)
    os.makedirs(download_folder, exist_ok=True)
    
    print(f"\n🔍 Arama: {klasor_adi}")
    print(f"📁 Klasör: {download_folder}")
    
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
            return 0
        
        basarili_indirilen = 0
        for i, pdf_url in enumerate(tqdm(pdf_linkleri, desc=f"İndiriliyor ({klasor_adi})")):
            try:
                dosya_adi = os.path.join(download_folder, f"makale_{i + 1}.pdf")
                
                r = requests.get(pdf_url, headers=headers, stream=True, timeout=30)
                r.raise_for_status()
                
                content_type = r.headers.get('content-type', '').lower()
                if 'pdf' not in content_type and not pdf_url.lower().endswith('.pdf'):
                    continue
                    
                with open(dosya_adi, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                basarili_indirilen += 1
                time.sleep(DELAY_BETWEEN_DOWNLOADS)
                
            except Exception as e:
                print(f"❌ Hata: {pdf_url} -> {e}")
        
        print(f"✅ {klasor_adi}: {basarili_indirilen}/{len(pdf_linkleri)} PDF başarıyla indirildi.")
        return basarili_indirilen
        
    except Exception as e:
        print(f"❌ Arama hatası ({klasor_adi}): {e}")
        return 0

def main():
    """Ana fonksiyon - tüm aramaları sırayla işler"""
    print("🚀 PDF İndirici Başlatılıyor...")
    print(f"📂 Ana dizin: {BASE_DOWNLOAD_FOLDER}")
    print(f"🔍 Toplam {len(SCHOLAR_URLS)} arama işlenecek")
    print("=" * 50)
    
    os.makedirs(BASE_DOWNLOAD_FOLDER, exist_ok=True)
    
    toplam_indirilen = 0
    basarili_aramalar = 0
    
    for i, arama in enumerate(SCHOLAR_URLS, 1):
        print(f"\n{'='*20} ARAMA {i}/{len(SCHOLAR_URLS)} {'='*20}")
        
        try:
            indirilen_sayi = pdf_indir_tek_arama(arama["url"], arama["klasor_adi"])
            toplam_indirilen += indirilen_sayi
            
            if indirilen_sayi > 0:
                basarili_aramalar += 1
            
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
    print(f"📄 Toplam indirilen PDF: {toplam_indirilen}")
    print(f"📂 İndirme dizini: {BASE_DOWNLOAD_FOLDER}")
    print("🎉 İşlem tamamlandı!")

if __name__ == "__main__":
    main() 