# YTD (Year-to-Date) Performans Hesaplama Düzeltmesi

## 🔴 SORUN

**Kullanıcı Şikayeti:** "HER ŞEY DOĞRU GÜZEL GÖZÜKÜYOR AMA BEN YILBASINDAN BERİ 43 BİN TL ZARARDA MIYIM ? DEĞİLİM"

YTD performansı **₺-43,620 (-14.08%)** gösteriyordu, ancak bu **YANLIŞ** bir hesaplamaydı.

## 🔍 SORUNUN KÖK NEDENİ

### Ne Oluyordu?

YTD (Year-to-Date) hesaplaması, **"bu yılın ilk kaydından bugüne"** performansı hesaplıyordu. 

**Problem:**
- Eğer tarihsel veri kayıtları **Kasım ayında** başladıysa
- YTD hesaplaması **1 Ocak'tan değil, Kasım'dan** itibaren performansı gösteriyordu
- Bu, **"yılbaşından beri"** değil, sadece **"kayıt başlangıcından beri"** performanstı

### Örnek Senaryo:

```
Portföy Tarihsel Kayıtları:
- İlk Kayıt: 20 Kasım 2025 → ₺350,000
- Bugün: 27 Kasım 2025 → ₺306,380

YTD Hesaplaması (YANLIŞ):
₺306,380 - ₺350,000 = ₺-43,620 (-14.08%)
```

**SORUN:** Bu, **7 günlük performans**tı, yıllık performans DEĞİL!

## ✅ ÇÖZÜM

### 1. YTD Hesaplama Mantığı Güncellendi

`data_loader.py` dosyasında `get_timeframe_changes()` fonksiyonu düzeltildi:

```python
# YTD: SADECE yılın ilk birkaç gününde veri varsa hesapla
if year_mask.any():
    ydf = df[year_mask]
    first_date_of_year = ydf["Tarih"].min()
    
    # ÖNEMLI KONTROL: İlk kayıt Ocak ayının ilk 10 gününde mi?
    if first_date_of_year.month == 1 and first_date_of_year.day <= 10:
        # İlk kayıt Ocak ayının ilk 10 günündeyse, YTD hesaplama yapılabilir
        start_val = float(ydf["Değer_TRY"].iloc[0])
        diff = today_val - start_val
        pct = (diff / start_val * 100) if start_val > 0 else 0.0
        y_spark = list(ydf["Değer_TRY"])
        y_val, y_pct = diff, pct
    else:
        # İlk kayıt Ocak ayının ilk 10 gününden sonraysa, YTD hesaplama YAPMA
        # Çünkü bu, gerçek YTD performansı değil
        y_val, y_pct, y_spark = None, None, []
```

**Yeni Mantık:**
- ✅ İlk kayıt **1-10 Ocak** arasındaysa → YTD hesapla
- ❌ İlk kayıt **10 Ocak'tan sonra**ysa → YTD gösterme (yanıltıcı olur)

### 2. UI'da Açıklayıcı Mesajlar Eklendi

YTD verisi yoksa, artık açıklayıcı bir uyarı gösteriliyor:

```
ℹ️ YTD (Year-to-Date) Hesaplanamıyor: 
İlk veri kaydı 20 Kasım 2025 tarihinde başladı. 
Doğru YTD hesaplaması için 1 Ocak tarihinden itibaren veri gerekiyor.

💡 Çözüm: Ocak ayı başındaki portföy değerinizi manuel olarak ekleyebilir, 
veya sadece mevcut veri aralığındaki performansı izlemeye devam edebilirsiniz.
```

### 3. YTD Metriği Görünümü

Artık YTD metriği üç durumda olabilir:

1. **✅ YTD Mevcut:** `₺12,500 (+3.45%)` - Ocak ayı verisi var
2. **📊 Veri Yok:** Ocak ayı verisi yok, YTD hesaplanamıyor
3. **—:** Hiç tarihsel veri yok

## 🛠️ 1 OCAK VERİSİNİ MANUEL OLARAK EKLEME

Eğer 1 Ocak 2025 tarihindeki portföy değerinizi biliyorsanız, manuel olarak ekleyebilirsiniz:

### Adım 1: Google Sheets'i Açın

1. [Google Sheets](https://docs.google.com/spreadsheets/) adresine gidin
2. `PortfoyData` adlı dosyayı açın
3. `portfolio_history` sayfasına gidin (alt sekmelerden)

### Adım 2: Yeni Satır Ekleyin

Tabloya şu formatta satır ekleyin:

| Tarih | Değer_TRY | Değer_USD |
|-------|-----------|-----------|
| 2025-01-01 | [1 Ocak'taki TRY değeri] | [1 Ocak'taki USD değeri] |

**Örnek:**
```
Tarih: 2025-01-01
Değer_TRY: 320000
Değer_USD: 9411.76
```

### Adım 3: Kaydedin ve Yenileyin

1. Google Sheets'i kaydedin (otomatik kaydedilir)
2. Streamlit uygulamanızı yenileyin
3. YTD metriği artık doğru şekilde hesaplanacak

## 📊 YTD HESAPLAMASI NASIL ÇALIŞIR?

### Doğru YTD Hesaplama (Ocak verisi varsa):

```
1 Ocak Portföy Değeri: ₺320,000
Bugünkü Portföy Değeri: ₺306,380

YTD Performans:
₺306,380 - ₺320,000 = ₺-13,620 (-4.26%)
```

Bu, **gerçek yıllık performans**tır.

### Yanlış YTD Hesaplama (Kasım verisi kullanılırsa):

```
20 Kasım Portföy Değeri: ₺350,000  ← YANLIŞ BAŞLANGIÇ!
Bugünkü Portföy Değeri: ₺306,380

Yanlış "YTD":
₺306,380 - ₺350,000 = ₺-43,620 (-14.08%)
```

Bu, sadece **7 günlük performans**tır, yıllık DEĞİL!

## 🎯 SONUÇ

### Artık:

1. ✅ **Doğru YTD Hesaplama:** Sadece Ocak ayı verisi varsa YTD gösterilir
2. ✅ **Açıklayıcı Uyarılar:** YTD yoksa neden olmadığı açıklanır
3. ✅ **Manuel Veri Ekleme:** 1 Ocak verisini ekleyerek doğru YTD hesaplayabilirsiniz
4. ✅ **Yanıltıcı Metrikler Yok:** Artık yanlış YTD değerleri gösterilmez

### Gelecek İçin:

- **2026'da:** Uygulama 1 Ocak'tan itibaren her gün çalışırsa, 2026 YTD otomatik doğru olacak
- **2025 YTD İçin:** 1 Ocak 2025 verisini manuel eklemeniz gerekiyor (yukarıdaki adımlar)

## 📝 DEĞİŞTİRİLEN DOSYALAR

1. **`data_loader.py`:**
   - `get_timeframe_changes()` fonksiyonu → YTD kontrolü eklendi
   - Sadece Ocak ayı verisi varsa YTD hesaplar

2. **`portfoy.py`:**
   - `render_kral_infobar()` → YTD yok mesajı güncellendi
   - YTD uyarı mesajı eklendi (Ocak verisi yoksa gösterilir)

3. **`debug_ytd_calculation.py`:** (YENİ)
   - YTD hesaplamasını debug etmek için yardımcı script

4. **`YTD_FIX_README.md`:** (YENİ)
   - Bu doküman

## ❓ SSS (Sık Sorulan Sorular)

### S: 1 Ocak verimi nasıl bulurum?

**C:** Şu yöntemlerden birini kullanabilirsiniz:

1. **Banka ekstreleri:** 1 Ocak tarihli ekstreleri toplayın
2. **Not defteriniz:** O tarihte bir not aldıysanız
3. **Tahmini değer:** Yaklaşık değeri hatırlıyorsanız, ona yakın bir değer girin
4. **Ortalama:** Ocak-Şubat aralığındaki ortalama değeri kullanın

### S: 1 Ocak verisini eklemeden devam edebilir miyim?

**C:** Evet! Mevcut haftalık ve aylık performans metrikleri çalışmaya devam edecek. Sadece YTD metriği "📊 Veri Yok" olarak gösterilecek.

### S: 2026'da aynı sorun olur mu?

**C:** Hayır! Uygulama 1 Ocak 2026'dan itibaren düzenli çalışırsa, 2026 YTD otomatik olarak doğru hesaplanacak.

### S: Neden 10 gün toleransı var?

**C:** Bazı kullanıcılar 1 Ocak tatilde olabilir veya uygulamayı 2-3 gün sonra çalıştırabilir. Bu yüzden ilk 10 günlük kayıt kabul ediliyor.

## 🚀 ÖNEMLİ NOTLAR

1. **Günlük Çalıştırın:** Uygulamayı her gün en az bir kez çalıştırın ki tarihsel veri birikiyor olsun
2. **Yedekleme:** Google Sheets'teki `portfolio_history` tablosunu düzenli yedekleyin
3. **Veri Kontrolü:** Zaman zaman `debug_ytd_calculation.py` scriptini çalıştırarak veri durumunu kontrol edin

---

**Düzenleme Tarihi:** 27 Kasım 2025
**Versiyon:** 1.0.0
**Düzenleyen:** Claude Sonnet 4.5
