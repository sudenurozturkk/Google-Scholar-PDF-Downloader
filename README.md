# PDF İndirici

Google Scholar'dan akademik makalelerin PDF'lerini toplu olarak indiren Python scripti.

## Özellikler

- Google Scholar URL'lerini sırayla işler
- Tüm PDF'leri tek klasöre indirir
- Otomatik PDF arama ve indirme
- İlerleme çubuğu ile görsel geri bildirim

## Kurulum

1. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

2. `pdf_indir.py` dosyasındaki `SCHOLAR_URLS` listesine URL'lerinizi ekleyin:
```python
SCHOLAR_URLS = [
    "https://scholar.google.com.tr/scholar?hl=tr&as_sdt=0,5&as_vis=1&q=ARAMA_KELIMELERI",
    "https://scholar.google.com.tr/scholar?hl=tr&as_sdt=0,5&as_vis=1&q=DIGER_ARAMA",
    # Daha fazla URL ekleyebilirsiniz...
]
```

3. Scripti çalıştırın:
```bash
python pdf_indir.py
```

## Kullanım

Script çalıştırıldığında:
- Eklediğiniz URL'leri sırayla işler
- Tüm PDF'leri tek klasöre indirir
- PDF'leri sırayla numaralandırır

## İndirme Dizini

PDF'ler şu dizine indirilir:
```
C:\Users\KLASÖRÜNÜZ
├── makale_1.pdf
├── makale_2.pdf
├── makale_3.pdf
└── ...
```

## Gereksinimler

- Python 3.7+
- requests
- beautifulsoup4
- tqdm
- lxml

## Not

- Google Scholar'ın kullanım şartlarına uygun kullanın
- Sadece açık erişimli PDF'leri indirin
- Telif hakkı kurallarına dikkat edin 
