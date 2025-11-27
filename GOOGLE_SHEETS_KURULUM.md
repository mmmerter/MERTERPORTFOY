# 📊 Google Sheets Kurulum Rehberi - Binance Futures

## 🎯 Genel Bakış

Binance Futures verilerinizin tarihsel olarak saklanması ve haftalık/aylık analizler yapılabilmesi için Google Sheets'te **2 yeni sayfa (sheet)** oluşturmanız gerekiyor.

## ✅ Yapılması Gerekenler

### 1️⃣ Ana Spreadsheet'inizi Açın

1. Google Sheets'te **"PortfoyData"** dosyanızı açın
2. Bu dosya zaten mevcut olmalı (mevcut portföy sisteminiz için kullanıyor)

### 2️⃣ Yeni Sheet'ler Oluşturun

Dosyanın altında **"+"** butonuna tıklayarak 2 yeni sayfa ekleyin:

#### Sheet 1: `futures_positions`
**Amaç:** Anlık pozisyon kayıtları (her güncellemede)

**Sütunlar (Header - 1. satır):**
```
Timestamp | Symbol | Side | Size | Entry Price | Mark Price | Unrealized PnL | Unrealized PnL % | Leverage | Liquidation Price | Margin Type | Notional
```

#### Sheet 2: `futures_daily_summary`
**Amaç:** Günlük özet (her gün 1 kayıt)

**Sütunlar (Header - 1. satır):**
```
Timestamp | Wallet Balance | Margin Balance | Available Balance | Unrealized PnL | Realized PnL 24h | Realized PnL 7d | Realized PnL 30d | Total PnL 24h | Num Positions | Num Long | Num Short | Total Notional
```

---

## 📋 Adım Adım Kurulum

### Adım 1: Yeni Sheets Oluşturun

1. **Google Sheets'te PortfoyData dosyanızı açın**

2. **Alt menüden "+" butonuna basın** (yeni sheet ekle)
   
3. **İlk sheet'i oluşturun:**
   - Sağ tıklayıp "Rename" deyin
   - Adını **`futures_positions`** yapın (tam olarak bu isim!)

4. **İkinci sheet'i oluşturun:**
   - Tekrar "+" butonuna basın
   - Adını **`futures_daily_summary`** yapın (tam olarak bu isim!)

### Adım 2: Header'ları Ekleyin

#### `futures_positions` sheet'ine:

**A1 hücresinden başlayarak bu başlıkları ekleyin:**

| A1 | B1 | C1 | D1 | E1 | F1 | G1 | H1 | I1 | J1 | K1 | L1 |
|----|----|----|----|----|----|----|----|----|----|----|-----|
| Timestamp | Symbol | Side | Size | Entry Price | Mark Price | Unrealized PnL | Unrealized PnL % | Leverage | Liquidation Price | Margin Type | Notional |

#### `futures_daily_summary` sheet'ine:

**A1 hücresinden başlayarak bu başlıkları ekleyin:**

| A1 | B1 | C1 | D1 | E1 | F1 | G1 | H1 | I1 | J1 | K1 | L1 | M1 |
|----|----|----|----|----|----|----|----|----|----|----|----|----|
| Timestamp | Wallet Balance | Margin Balance | Available Balance | Unrealized PnL | Realized PnL 24h | Realized PnL 7d | Realized PnL 30d | Total PnL 24h | Num Positions | Num Long | Num Short | Total Notional |

### Adım 3: Formatlama (Opsiyonel)

#### Header Formatı:
1. 1. satırı seçin (header satırı)
2. **Kalın** yapın (Bold)
3. Arka plan rengi: **Koyu mavi veya gri**
4. Yazı rengi: **Beyaz**
5. Hücreleri ortala (Center align)

#### Sütun Genişlikleri:
- **Timestamp**: 150-180px
- **Symbol**: 100px
- **Side**: 60px
- **Diğer sayısal**: 100-120px

---

## 🤖 Otomatik Oluşturma (Alternatif)

Eğer manuel oluşturmak istemezseniz, sistem otomatik oluşturacak ama **ilk kullanımda hata alabilirsiniz**. Daha güvenli yol manuel oluşturmaktır.

**Otomatik oluşturma için:**
1. Sheet'leri oluşturmayın
2. Dashboard'da "Sheets'e Kaydet" seçeneğini aktif edin
3. Sistem otomatik oluşturacak (ama bazen başarısız olabilir)

---

## 📊 Veri Yapısı

### `futures_positions` - Örnek Veri

| Timestamp | Symbol | Side | Size | Entry Price | Mark Price | Unrealized PnL | Unrealized PnL % | Leverage | Liquidation Price | Margin Type | Notional |
|-----------|--------|------|------|-------------|------------|----------------|------------------|----------|-------------------|-------------|----------|
| 2024-11-27 10:30:00 | BTCUSDT | LONG | 0.5 | 43500.0 | 44000.0 | 250.00 | 5.75 | 10 | 39500.0 | CROSS | 22000.0 |
| 2024-11-27 10:30:00 | ETHUSDT | SHORT | 2.0 | 2300.0 | 2250.0 | 100.00 | 4.35 | 5 | 2500.0 | ISOLATED | 4500.0 |

### `futures_daily_summary` - Örnek Veri

| Timestamp | Wallet Balance | Margin Balance | Available Balance | Unrealized PnL | Realized PnL 24h | Realized PnL 7d | Realized PnL 30d | Total PnL 24h | Num Positions | Num Long | Num Short | Total Notional |
|-----------|----------------|----------------|-------------------|----------------|------------------|-----------------|------------------|---------------|---------------|----------|-----------|----------------|
| 2024-11-27 00:00:00 | 10000.00 | 10500.00 | 5000.00 | 250.00 | 150.00 | 800.00 | 2500.00 | 400.00 | 5 | 3 | 2 | 50000.00 |
| 2024-11-26 00:00:00 | 9850.00 | 10350.00 | 4850.00 | 200.00 | 120.00 | 750.00 | 2400.00 | 320.00 | 4 | 2 | 2 | 45000.00 |

---

## 🔧 Sheet İzinleri

### Service Account Erişimi

Eğer zaten portföy sisteminiz Google Sheets kullanıyorsa, bu ayarlar zaten yapılmış olmalı:

1. ✅ Service account email'i dosyaya eklenmiş
2. ✅ **Editor** yetkisi verilmiş
3. ✅ Secrets.toml'da credentials mevcut

**Yeni sheet'ler otomatik olarak aynı izinleri alacak!**

---

## 📈 Haftalık/Aylık Raporlar İçin

### Otomatik Kayıt Nasıl Çalışır?

#### `futures_positions` Sheet'i:
- **Ne zaman güncellenir?** Her dashboard yenilendiğinde (30 saniyede bir)
- **Ne kaydedilir?** O anki tüm açık pozisyonlar
- **Amaç:** Pozisyon geçmişini tutmak, trend analizi

#### `futures_daily_summary` Sheet'i:
- **Ne zaman güncellenir?** Günde bir kez (ilk kullanımda)
- **Ne kaydedilir?** Günün özet verileri
- **Amaç:** Haftalık/aylık performans analizi

### Haftalık Analiz İçin:

`futures_daily_summary` sheet'inden **son 7 gün** verisini kullanın:

```excel
# Excel/Sheets formülü:
Haftalık PnL = SUM(F2:F8)  // Son 7 günün Realized PnL 24h
Ortalama Günlük = AVERAGE(F2:F8)
```

### Aylık Analiz İçin:

`futures_daily_summary` sheet'inden **son 30 gün** verisini kullanın:

```excel
# Excel/Sheets formülü:
Aylık PnL = SUM(F2:F31)  // Son 30 günün Realized PnL 24h
Ortalama Günlük = AVERAGE(F2:F31)
Win Rate = COUNTIF(F2:F31, ">0") / 30 * 100
```

---

## 🎯 Dashboard'da Aktif Etme

### Adım 1: Dashboard'u Açın

```bash
streamlit run portfoy.py
```

### Adım 2: Binance Futures Sekmesine Gidin

Üst menüden **"Binance Futures"** sekmesine tıklayın

### Adım 3: Sheets Kaydını Aktif Edin

**Sidebar'da (sol menü):**
1. Aşağı kaydırın
2. **"📝 Google Sheets"** bölümünü bulun
3. **"Sheets'e Kaydet"** checkbox'ını işaretleyin

### Adım 4: İlk Kaydı Bekleyin

- Dashboard yenilendiğinde otomatik kayıt başlayacak
- İlk kayıt 30 saniye içinde yapılacak
- Sheets'te verileri göreceksiniz

---

## ✅ Kontrol Listesi

Sheet kurulumunun doğru olduğunu kontrol edin:

### `futures_positions` Sheet:
- [ ] Sheet adı tam olarak **`futures_positions`** (küçük harf, alt çizgi)
- [ ] 12 sütun başlığı var
- [ ] Header satırı kalın ve renkli
- [ ] Sheet'e service account erişimi var

### `futures_daily_summary` Sheet:
- [ ] Sheet adı tam olarak **`futures_daily_summary`** (küçük harf, alt çizgi)
- [ ] 13 sütun başlığı var
- [ ] Header satırı kalın ve renkli
- [ ] Sheet'e service account erişimi var

### Dashboard Ayarları:
- [ ] "Sheets'e Kaydet" aktif
- [ ] Dashboard hata vermiyor
- [ ] İlk veriler sheets'e yazıldı

---

## 🐛 Sorun Giderme

### Hata: "Worksheet not found"

**Neden:** Sheet adı yanlış veya sheet yok

**Çözüm:**
1. Sheet adlarını kontrol edin (tam eşleşmeli!)
2. Büyük/küçük harf duyarlı
3. Boşluk veya alt çizgi kontrolü

**Doğru:**
- `futures_positions` ✅
- `futures_daily_summary` ✅

**Yanlış:**
- `Futures_Positions` ❌
- `futures positions` ❌
- `FuturesPositions` ❌

### Hata: "Permission denied"

**Neden:** Service account'un erişimi yok

**Çözüm:**
1. Google Sheets'te dosyayı açın
2. Sağ üst "Share" butonuna tıklayın
3. Service account email'ini ekleyin
4. "Editor" yetkisi verin

Service account email: `secrets.toml` dosyasında `client_email` alanında

### Hata: "Sheet is empty"

**Neden:** Header'lar eksik

**Çözüm:**
1. Her sheet'in 1. satırına header'ları ekleyin
2. Yukarıdaki tablolara bakın
3. Tam olarak aynı sırada olmalı

### Hata: "API quota exceeded"

**Neden:** Çok fazla yazma işlemi

**Çözüm:**
1. Otomatik yenileme süresini artırın (30s → 60s)
2. "Sheets'e Kaydet" seçeneğini geçici kapatın
3. 1-2 dakika bekleyip tekrar deneyin

---

## 📊 Gelişmiş Özellikler

### 1. Pivot Table Oluşturma

`futures_positions` sheet'inden pivot table:

**Rows:** Symbol
**Values:** SUM(Unrealized PnL)
**Filter:** Side (Long/Short)

### 2. Grafikler

#### Günlük PnL Grafiği:
```
Veri: futures_daily_summary
X ekseni: Timestamp
Y ekseni: Realized PnL 24h
Tip: Line Chart
```

#### Pozisyon Dağılımı:
```
Veri: futures_positions
Grupla: Side
Değer: COUNT(Symbol)
Tip: Pie Chart
```

### 3. Conditional Formatting

#### Pozitif/Negatif PnL:
- **Yeşil:** > 0
- **Kırmızı:** < 0

Formula:
```
=G2>0  // Yeşil (Unrealized PnL)
=G2<0  // Kırmızı
```

### 4. Otomatik Formüller

#### Toplam PnL (futures_positions):
```excel
=SUM(G:G)  // Tüm Unrealized PnL'leri topla
```

#### Ortalama Leverage:
```excel
=AVERAGE(I:I)  // Ortalama leverage
```

#### Pozisyon Sayısı:
```excel
=COUNTA(B:B)-1  // -1 header için
```

---

## 🎨 Önerilen Görünüm

### Sheet Renk Kodları:

#### `futures_positions`:
- **Header:** `#1a237e` (Koyu Mavi)
- **Pozitif PnL:** `#00e676` (Yeşil)
- **Negatif PnL:** `#ff5252` (Kırmızı)

#### `futures_daily_summary`:
- **Header:** `#004d40` (Koyu Teal)
- **Pozitif PnL:** `#00e676` (Yeşil)
- **Negatif PnL:** `#ff5252` (Kırmızı)

### Sütun Tipleri:

- **Timestamp:** Plain text veya Datetime
- **Fiyatlar:** Number (2 decimal)
- **PnL:** Number (2 decimal)
- **Percentage:** Percentage (2 decimal)
- **Leverage:** Number (0 decimal)
- **Counts:** Number (0 decimal)

---

## 📱 Mobil Erişim

Google Sheets mobil uygulaması ile:
1. Her yerden verilerinize erişin
2. Grafiklerinizi görün
3. PnL takibi yapın

---

## 🎉 Kurulum Tamamlandı!

Artık:
- ✅ Haftalık raporlar otomatik
- ✅ Aylık analizler mümkün
- ✅ Tarihsel veri birikiyor
- ✅ Trend analizi yapabilirsiniz

---

## 📝 Hızlı Kopya-Yapıştır

### futures_positions Headers:
```
Timestamp	Symbol	Side	Size	Entry Price	Mark Price	Unrealized PnL	Unrealized PnL %	Leverage	Liquidation Price	Margin Type	Notional
```

### futures_daily_summary Headers:
```
Timestamp	Wallet Balance	Margin Balance	Available Balance	Unrealized PnL	Realized PnL 24h	Realized PnL 7d	Realized PnL 30d	Total PnL 24h	Num Positions	Num Long	Num Short	Total Notional
```

**💡 İpucu:** Bu satırları kopyalayıp direkt Sheets'e yapıştırabilirsiniz! (Tab ile ayrılmış)

---

## 🚀 Sonraki Adımlar

1. ✅ Sheet'leri oluşturdunuz
2. ✅ Header'ları eklediniz
3. ▶️ Dashboard'u başlatın: `streamlit run portfoy.py`
4. ▶️ "Sheets'e Kaydet" seçeneğini aktif edin
5. ▶️ 30 saniye bekleyin
6. ▶️ Sheets'te verileri kontrol edin

**Başarılar! 🎊**

---

**Son Güncelleme:** 27 Kasım 2024
**Versiyon:** 1.0.0
