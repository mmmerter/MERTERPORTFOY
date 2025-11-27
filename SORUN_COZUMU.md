# 🔧 API Bağlantı Sorunu Çözümü

## 🎯 Sorununuz

**"API bağlantısı başarısız"** hatası alıyorsunuz. 

## ✅ Çözüm

API bağlantısının çalışması için 2 şey gerekiyor:

### 1️⃣ Binance'te "Enable Futures" İznini Açın

**EVET, Binance'te API oluştururken mutlaka "Enable Futures" seçeneğini işaretlemeniz gerekiyor!**

#### Nasıl Yapılır:

1. Binance'e giriş yapın: https://www.binance.com
2. **Profil** > **API Management** sayfasına gidin
3. Mevcut API key'iniz varsa:
   - **Edit** butonuna tıklayın
   - **"Enable Futures"** kutucuğunu işaretleyin ✅
   - **"Enable Reading"** kutucuğunu işaretleyin ✅
   - ❌ **"Enable Withdrawals"** ASLA İŞARETLEMEYİN (güvenlik!)
   - 2FA doğrulaması yapın
   - Kaydedin

4. Yeni API key oluşturacaksanız:
   - **Create API** tıklayın
   - İsim verin (örn: "Portfolio Tracker")
   - **"Enable Reading"** ✅
   - **"Enable Futures"** ✅
   - ❌ **"Enable Withdrawals"** ASLA
   - 2FA yapın
   - API Key ve Secret'i kaydedin (Secret sadece 1 kere gösterilir!)

### 2️⃣ API Bilgilerinizi Sisteme Kaydedin

Size 3 yöntem hazırladım:

#### 🚀 YÖNTEM 1: Otomatik Kurulum (ÖNERİLEN)

Terminal'de şu komutu çalıştırın:

```bash
python3 setup_api.py
```

Script size soracak:
- Binance API Key
- Binance API Secret
- Testnet kullanılsın mı (hayır deyin)

Bilgileri girince otomatik olarak kaydedecek.

#### ✏️ YÖNTEM 2: Manuel Düzenleme

`.streamlit/secrets.toml` dosyasını açın ve düzenleyin:

```toml
[binance_futures]
api_key = "BURAYA_API_KEY_YAPIŞTIRIN"
api_secret = "BURAYA_API_SECRET_YAPIŞTIRIN"
testnet = false
```

**Örnek** (gerçek değil!):
```toml
[binance_futures]
api_key = "kCBcBwlB9FlgWbWZj8L9K3pXyH2mN5qS7tU9vW1xA4bC6dE8fG0h"
api_secret = "9pZF8K3jL5mN7qS0tU2vX4yA6bC8dE1fG3hJ5k"
testnet = false
```

#### 📝 YÖNTEM 3: Nano Editor ile

```bash
nano .streamlit/secrets.toml
```

Dosyayı düzenleyin, Ctrl+O ile kaydedin, Ctrl+X ile çıkın.

---

## 🧪 Test Edin

Kurulumu tamamladıktan sonra test edin:

```bash
python3 test_binance_connection.py
```

### ✅ Başarılı Çıktı:

```
✅ API bilgileri secrets'tan alındı
✅ Bağlantı başarılı!

💰 Bakiye:
   Toplam Cüzdan: $1,234.56
   Marjin Bakiyesi: $1,234.56
   Kullanılabilir: $234.56
   Unrealized PnL: $12.34

📍 AÇIK POZİSYONLAR
✅ 2 açık pozisyon bulundu:

🟢 BTCUSDT
   Yön: LONG | Leverage: 10x
   ...
```

### ❌ Hala Başarısız mı?

**1. "Invalid API key" Hatası:**
- API key'i doğru kopyaladınız mı?
- Başında/sonunda boşluk var mı?
- secrets.toml'da tırnak içinde mi?

**2. "Permission denied" Hatası:**
- Binance'te "Enable Futures" işaretli mi? ⚠️
- Binance'te "Enable Reading" işaretli mi? ⚠️

**3. "Invalid signature" Hatası:**
- API secret doğru mu?
- Secret'i yeniden kopyalayın (dikkatli!)

**4. "IP not allowed" Hatası:**
- API key'de IP kısıtlaması var mı?
- Binance > API Management > Edit restrictions
- IP'nizi ekleyin veya "Unrestricted" seçin

---

## 🚀 Dashboard'u Başlatın

Test başarılıysa artık dashboard'u başlatabilirsiniz:

```bash
streamlit run portfoy.py
```

Tarayıcınızda açılacak. Üst menüden **"Binance Futures"** sekmesine tıklayın.

---

## 📋 Kontrol Listesi

Kurulum tamamlandığında:

- [ ] Binance'te API key oluşturdum
- [ ] **"Enable Futures" işaretledim** ⚠️ EN ÖNEMLİ!
- [ ] **"Enable Reading" işaretledim** ⚠️
- [ ] "Enable Withdrawals" işaretlemedim ✅
- [ ] API key ve secret'i `.streamlit/secrets.toml`'a kaydettim
- [ ] `python3 test_binance_connection.py` başarılı ✅
- [ ] Dashboard'da veriler görünüyor ✅

---

## 🔐 Güvenlik Hatırlatması

- ✅ Sadece "Reading" ve "Futures" izni verin
- ❌ ASLA "Enable Withdrawals" vermeyin!
- 🔒 API key'i kimseyle paylaşmayın
- 🔒 Screenshot'larda gizleyin
- 🔒 GitHub'a commit etmeyin (zaten .gitignore'da)

---

## 📞 Yardım

### Hazır Dosyalar:

1. **setup_api.py** - Otomatik kurulum scripti
2. **test_binance_connection.py** - Bağlantı test scripti
3. **BINANCE_API_KURULUM.md** - Detaylı kurulum rehberi
4. **.streamlit/secrets.toml** - API bilgileri (siz dolduracaksınız)

### Komutlar:

```bash
# Kurulum
python3 setup_api.py

# Test
python3 test_binance_connection.py

# Dashboard
streamlit run portfoy.py
```

---

## 🎉 Özet

**Sorun**: API bağlantısı başarısız

**Ana Sebep**: Binance'te "Enable Futures" seçeneği işaretli değil

**Çözüm**:
1. Binance > API Management > Edit
2. ✅ "Enable Futures" işaretle
3. ✅ "Enable Reading" işaretle
4. Kaydet
5. API bilgilerini `.streamlit/secrets.toml`'a gir
6. Test et: `python3 test_binance_connection.py`
7. Çalıştır: `streamlit run portfoy.py`

---

**İyi ticaret günleri! 🚀📈**
