# PDF İndirici

Google Scholar'dan akademik makalelerin PDF'lerini toplu olarak indiren Python scripti.

## Özellikler

- 10 farklı Google Scholar aramasını sırayla işler
- Her arama için ayrı klasör oluşturur
- Otomatik PDF arama ve indirme
- İlerleme çubuğu ile görsel geri bildirim

## Kurulum

1. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Scripti çalıştırın:
```bash
python pdf_indir.py
```

## Kullanım

Script çalıştırıldığında:
- 10 farklı sağlık konusunda Google Scholar araması yapar
- Her arama için ayrı klasör oluşturur
- PDF'leri otomatik olarak indirir ve numaralandırır

## İndirme Dizini

PDF'ler şu dizine indirilir:
```
C:\Users\Administrator\Desktop\TEKNOFEST\akademikmakaleler\
├── beslenme_kilo_verme/
├── spor_egzersiz/
├── psikoloji_motivasyon/
├── saglik_beslenme/
├── teknoloji_saglik/
├── ilac_tedavi/
├── cerrahi_ameliyat/
├── pediatri_cocuk/
├── kardiyoloji_kalp/
└── noroloji_beyin/
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
