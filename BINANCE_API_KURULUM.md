# 🔐 Binance Futures API Kurulum Rehberi

## ⚠️ ÖNEMLİ: Futures API İzni Mutlaka Gerekli!

API bağlantısının çalışması için Binance'te API anahtarı oluştururken **mutlaka "Enable Futures" seçeneğini işaretlemelisiniz**.

---

## 📝 Adım Adım Kurulum

### 1️⃣ Binance'te API Anahtarı Oluşturma

1. **Binance'e giriş yapın**: https://www.binance.com
2. **Profil** > **API Management** sayfasına gidin
3. **Create API** butonuna tıklayın
4. **API Key Label** girin (örn: "Portfolio Tracker")

#### ✅ İzinler (Permissions) - ÇOK ÖNEMLİ!

API oluştururken şu izinleri **mutlaka** verin:

```
✅ Enable Reading          (ZORUNLU - okuma izni)
✅ Enable Futures          (ZORUNLU - futures hesabı için)
❌ Enable Spot & Margin    (opsiyonel - spot için değil)
❌ Enable Withdrawals      (ASLA VERMEYİN! - güvenlik riski)
```

**⚠️ UYARI**: "Enable Futures" seçeneği işaretli değilse API bağlantısı başarısız olur!

5. **2FA** doğrulaması yapın (Email + SMS)
6. **API Key** ve **Secret Key**'i kaydedin

---

### 2️⃣ API Bilgilerini Kaydetme

API anahtarlarınızı `.streamlit/secrets.toml` dosyasına kaydetmeniz gerekiyor:

#### Otomatik Yöntem (Önerilen):

Terminal'de şu komutu çalıştırın:

```bash
python3 setup_api.py
```

Script size API key ve secret soracak, otomatik olarak kaydedecek.

#### Manuel Yöntem:

`.streamlit/secrets.toml` dosyasını açın ve düzenleyin:

```toml
[binance_futures]
api_key = "BURAYA_API_KEY_YAPIŞTIRIN"
api_secret = "BURAYA_API_SECRET_YAPIŞTIRIN"
testnet = false
```

**Örnek** (gerçek key kullanmayın!):
```toml
[binance_futures]
api_key = "kCBcBwlB9FlgWbWZj8L9K3pXyH2mN5qS7tU9vW1xA4bC6dE8fG0h"
api_secret = "9pZF8K3jL5mN7qS0tU2vX4yA6bC8dE1fG3hJ5k"
testnet = false
```

---

### 3️⃣ Bağlantıyı Test Etme

API bağlantınızı test edin:

```bash
python3 test_binance_connection.py
```

#### Başarılı Test Çıktısı:

```
✅ API bilgileri secrets'tan alındı
✅ Bağlantı başarılı!
💰 Bakiye: $1,234.56
📍 3 açık pozisyon bulundu
```

#### Başarısız Test - Olası Hatalar:

**1. "Invalid API Key"**
```
❌ Bağlantı başarısız!
HATA: Invalid API key
```

**Çözüm:**
- API key'i doğru kopyaladığınızdan emin olun
- Başında/sonunda boşluk olmamalı
- Tırnak işaretleri içinde olmalı

**2. "Invalid API Secret"**
```
❌ Bağlantı başarısız!
HATA: Invalid signature
```

**Çözüm:**
- API secret'i doğru kopyaladığınızdan emin olun
- Secret sadece 1 kere gösterilir, yeniden oluşturmanız gerekebilir

**3. "Futures API Not Enabled"**
```
❌ Bağlantı başarısız!
HATA: This API key doesn't have permission for this request
```

**Çözüm:**
- Binance'te API Management sayfasına gidin
- API key'inizi bulun, **Edit** tıklayın
- **"Enable Futures"** kutucuğunu işaretleyin
- 2FA doğrulaması yapın
- Kaydedin ve tekrar deneyin

**4. "IP Restriction"**
```
❌ Bağlantı başarısız!
HATA: IP address not allowed
```

**Çözüm:**
- API key'in IP whitelist'i varsa:
  - Binance'te API Management'e gidin
  - "Edit restrictions" tıklayın
  - Şu anki IP'nizi ekleyin veya "Unrestricted" seçin
  - (Güvenlik için IP whitelist önerilir ama test için kaldırabilirsiniz)

---

### 4️⃣ Dashboard'u Başlatma

Test başarılıysa dashboard'u başlatın:

```bash
streamlit run portfoy.py
```

Tarayıcınızda açılacak, üst menüden **"Binance Futures"** sekmesine tıklayın.

---

## 🔒 Güvenlik İpuçları

### ✅ Yapılması Gerekenler

1. **Sadece Okuma İzni**
   - ✅ "Enable Reading" - ZORUNLU
   - ✅ "Enable Futures" - ZORUNLU
   - ❌ "Enable Withdrawals" - ASLA VERMEYİN!

2. **IP Whitelist** (Önerilen)
   - Mümkünse sadece kendi IP'nizi ekleyin
   - Daha güvenli ama her IP değişiminde güncellemeniz gerekir

3. **Secrets Dosyası Koruması**
   - `.streamlit/secrets.toml` dosyası `.gitignore`'da
   - Asla GitHub'a commit edilmeyecek
   - Kimseyle paylaşmayın

4. **Düzenli Kontrol**
   - API activity'yi düzenli kontrol edin
   - Şüpheli aktivite görürseniz hemen API key'i silin

### ❌ Yapılmaması Gerekenler

1. ❌ "Enable Withdrawals" iznini vermeyin
2. ❌ API key'i sosyal medyada paylaşmayın
3. ❌ Screenshot'larda API key görünmesin
4. ❌ Public GitHub repo'larına commit etmeyin

---

## 🐛 Sorun Giderme

### Sık Karşılaşılan Sorunlar

| Sorun | Sebep | Çözüm |
|-------|-------|-------|
| Invalid API key | Yanlış key | secrets.toml'ı kontrol edin |
| Invalid signature | Yanlış secret | Secret'i yeniden girin |
| Permission denied | Futures izni yok | **"Enable Futures" işaretleyin** |
| IP not allowed | IP kısıtlaması | IP'nizi whitelist'e ekleyin |
| Timestamp error | Saat senkron değil | Sistem saatinizi düzeltin |

### Test Komutu

Herhangi bir sorunda bu komutu çalıştırın:

```bash
python3 test_binance_connection.py
```

Çıktı size sorunun ne olduğunu gösterecektir.

---

## 📞 Yardım

### Hala Çalışmıyor mu?

1. **Secrets dosyasını kontrol edin:**
   ```bash
   cat .streamlit/secrets.toml
   ```
   
2. **API key'in izinlerini kontrol edin:**
   - Binance > API Management
   - API key'inizi bulun
   - "Edit" tıklayın
   - "Enable Futures" işaretli mi?

3. **Test scriptini çalıştırın:**
   ```bash
   python3 test_binance_connection.py
   ```
   
   Hata mesajı size ne yapmanız gerektiğini söyleyecek.

---

## ✅ Başarı Kontrolü

API doğru kurulduğunda:

1. ✅ Test scripti başarıyla çalışır
2. ✅ Bakiyeniz görünür
3. ✅ Pozisyonlarınız listelenir
4. ✅ Dashboard'da veriler yüklenir

---

## 🎯 Özet Checklist

Kurulum tamamlandığında kontrol edin:

- [ ] Binance'te API key oluşturdum
- [ ] **"Enable Futures" seçeneğini işaretledim** ⚠️ ÖNEMLİ!
- [ ] "Enable Reading" seçeneğini işaretledim
- [ ] "Enable Withdrawals" seçeneğini işaretLEMEDİM
- [ ] API key ve secret'i `.streamlit/secrets.toml`'a kaydettim
- [ ] `python3 test_binance_connection.py` başarılı
- [ ] Dashboard'da veriler görünüyor

---

**Son Güncelleme**: 27 Kasım 2024  
**Durum**: ✅ Hazır  

Başarılı ticaret günleri! 🚀📈
