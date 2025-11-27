# 📊 Binance Futures API Entegrasyonu - Tam Dokümantasyon

## 🎯 Genel Bakış

Bu sistem, Binance Futures hesabınızdan **tüm verileri otomatik olarak çeker**, **PnL'inizi takip eder** ve **gerçek zamanlı olarak görüntüler**. Google Sheets'e otomatik kayıt yapar ve kapsamlı analizler sunar.

## ✨ Özellikler

### 🔥 Ana Özellikler
- ✅ **Gerçek Zamanlı Veri**: Pozisyonlar, fiyatlar, PnL anlık güncellenir
- ✅ **Otomatik PnL Takibi**: Realized ve unrealized PnL'i otomatik hesaplar
- ✅ **Google Sheets Entegrasyonu**: Tüm veriler otomatik kaydedilir
- ✅ **Kapsamlı Dashboard**: Modern ve kullanıcı dostu arayüz
- ✅ **Tarihsel Analiz**: Günlük, haftalık, aylık performans raporları
- ✅ **Risk Yönetimi**: Leverage, liquidation, margin bilgileri
- ✅ **Multi-Timeframe**: 24 saat, 7 gün, 30 gün bazlı analizler

### 📊 Çekilen Veriler

#### 1. Hesap Bilgileri
- Toplam cüzdan bakiyesi (USDT)
- Marjin bakiyesi
- Kullanılabilir bakiye
- Cross/isolated margin durumu

#### 2. Pozisyon Bilgileri
- Sembol (örn: BTCUSDT)
- Yön (Long/Short)
- Pozisyon büyüklüğü
- Giriş fiyatı
- Güncel mark fiyatı
- Unrealized PnL ($ ve %)
- Leverage
- Tasfiye (liquidation) fiyatı
- Marjin tipi (cross/isolated)
- Notional değer

#### 3. PnL Verileri
- **Unrealized PnL**: Açık pozisyonlardaki kar/zarar
- **Realized PnL**: Kapatılmış pozisyonlardan elde edilen kar/zarar
- Günlük PnL özeti (30 güne kadar)
- Kümülatif PnL
- Haftalık/Aylık performans

#### 4. Gelir Geçmişi
- **REALIZED_PNL**: Gerçekleşen kar/zarar
- **FUNDING_FEE**: Funding ücreti gelir/giderleri
- **COMMISSION**: İşlem komisyonları
- **INSURANCE_CLEAR**: Sigorta tasfiyesi
- **TRANSFER**: Transfer işlemleri

#### 5. İşlem Geçmişi
- Tüm alım/satım işlemleri
- İşlem fiyatı, miktarı, maliyeti
- İşlem ücretleri
- Tarih ve saat bilgisi

## 🚀 Kurulum

### 1. Gerekli Paketler

Öncelikle `requirements.txt` dosyanızda bu paketlerin olduğundan emin olun:

```txt
ccxt>=4.0.0
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
gspread>=5.11.0
oauth2client>=4.1.3
```

Kurulum:
```bash
pip install -r requirements.txt
```

### 2. Binance API Key Alma

#### Adım 1: Binance Hesabı
1. [Binance](https://www.binance.com) hesabınıza giriş yapın
2. Sağ üst köşeden **Profil > API Management** seçin

#### Adım 2: API Oluşturma
1. **Create API** butonuna tıklayın
2. **Label** olarak tanımlayıcı bir isim verin (örn: "Portfolio Tracker")
3. Güvenlik doğrulaması yapın (2FA, email, vb.)

#### Adım 3: İzinleri Ayarlama
**ÖNEMLİ**: Güvenlik için doğru izinleri verin!

✅ **Verilmesi Gereken İzinler:**
- ✅ **Enable Reading** (Okuma - ZORUNLU)
- ✅ **Enable Futures** (Futures - ZORUNLU)

❌ **VERİLMEMESİ GEREKEN İzinler:**
- ❌ **Enable Spot & Margin Trading** (Güvenlik riski)
- ❌ **Enable Withdrawals** (Güvenlik riski - ASLA vermeyin!)

#### Adım 4: IP Whitelist (Önerilen)
Ekstra güvenlik için:
1. **Restrict access to trusted IPs only** seçeneğini işaretleyin
2. Kullanacağınız IP adresini ekleyin
3. Dinamik IP kullanıyorsanız, IP whitelist kullanmayın (daha az güvenli ama pratik)

#### Adım 5: API Key ve Secret
1. **API Key** ve **Secret Key** gösterilecek
2. **Secret Key'i mutlaka kaydedin** - bir daha gösterilmeyecek!
3. Bu bilgileri güvenli bir yerde saklayın

### 3. Google Sheets Kurulumu (Opsiyonel)

Verilerinizi otomatik kaydetmek isterseniz:

1. Google Cloud Console'da bir proje oluşturun
2. Service Account oluşturun ve JSON key indirin
3. Streamlit secrets'a ekleyin:

`.streamlit/secrets.toml`:
```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

4. Google Sheets dosyanızı service account email ile paylaşın

## 📖 Kullanım

### Temel Kullanım

#### 1. Streamlit Uygulamasını Başlatma

Ana portföy uygulamanıza futures sayfasını ekleyin:

```python
# portfoy.py içinde
from futures_page import show_futures_dashboard

# Menüye ekleyin
selected = option_menu(
    menu_title="Ana Menü",
    options=["Dashboard", "Portföy", "Futures", "Haberler"],
    # ...
)

if selected == "Futures":
    show_futures_dashboard()
```

#### 2. Standalone Kullanım

Sadece Futures dashboard'unu çalıştırmak için:

```bash
streamlit run futures_page.py
```

### API Kullanımı (Python Kodu)

#### Temel Kullanım

```python
from binance_futures import BinanceFuturesAPI

# API bağlantısı
api = BinanceFuturesAPI(
    api_key="your_api_key",
    api_secret="your_api_secret",
    testnet=False  # False = gerçek hesap, True = test ağı
)

# Bağlantı testi
if api.test_connection():
    print("✅ Bağlantı başarılı!")
else:
    print("❌ Bağlantı başarısız!")
```

#### Hesap Bilgileri

```python
# Hesap bakiyesi
balance = api.get_account_balance()
print(f"Toplam Bakiye: ${balance['total_wallet_balance']:,.2f}")
print(f"Kullanılabilir: ${balance['available_balance']:,.2f}")
print(f"Unrealized PnL: ${balance['total_unrealized_pnl']:,.2f}")
```

#### Pozisyonları Çekme

```python
# Açık pozisyonlar
positions = api.get_open_positions()

for _, pos in positions.iterrows():
    print(f"Sembol: {pos['symbol']}")
    print(f"Yön: {pos['side']}")
    print(f"Miktar: {pos['size']}")
    print(f"PnL: ${pos['unrealized_pnl']:,.2f} ({pos['unrealized_pnl_percent']:.2f}%)")
    print(f"Leverage: {pos['leverage']}x")
    print("-" * 50)
```

#### PnL Analizi

```python
# Günlük PnL özeti (son 30 gün)
daily_pnl = api.get_daily_pnl_summary(days=30)

print(f"Toplam Realized PnL: ${daily_pnl['realized_pnl'].sum():,.2f}")
print(f"Ortalama Günlük PnL: ${daily_pnl['realized_pnl'].mean():,.2f}")

# En iyi ve en kötü günler
best_day = daily_pnl.loc[daily_pnl['realized_pnl'].idxmax()]
worst_day = daily_pnl.loc[daily_pnl['realized_pnl'].idxmin()]

print(f"\n✅ En iyi gün: {best_day['date']} - ${best_day['realized_pnl']:,.2f}")
print(f"❌ En kötü gün: {worst_day['date']} - ${worst_day['realized_pnl']:,.2f}")
```

#### Gelir Geçmişi

```python
# Tüm gelir türleri (son 30 gün)
income = api.get_income_history(days=30)

# Gelir tiplerine göre grupla
income_summary = income.groupby('income_type')['income'].sum()

for income_type, total in income_summary.items():
    print(f"{income_type}: ${total:,.2f}")

# Sadece funding fees
funding_fees = api.get_funding_fees(days=30)
total_funding = funding_fees['income'].sum()
print(f"\nToplam Funding Fee: ${total_funding:,.2f}")
```

#### İşlem Geçmişi

```python
# Belirli bir sembol için işlem geçmişi
trades = api.get_position_history(symbol="BTCUSDT", days=7)

for _, trade in trades.iterrows():
    print(f"{trade['timestamp']} - {trade['side']} {trade['amount']} @ ${trade['price']:,.2f}")
    print(f"  Realized PnL: ${trade['realized_pnl']:,.2f}")
```

#### Hesap Özeti (Dashboard için)

```python
# Kapsamlı özet
summary = api.get_account_summary()

print("=" * 60)
print("📊 HESAP ÖZETİ")
print("=" * 60)
print(f"Cüzdan Bakiyesi: ${summary['wallet_balance']:,.2f}")
print(f"Marjin Bakiyesi: ${summary['margin_balance']:,.2f}")
print(f"Kullanılabilir: ${summary['available_balance']:,.2f}")
print(f"\nUnrealized PnL: ${summary['unrealized_pnl']:,.2f}")
print(f"Realized PnL (24h): ${summary['realized_pnl_24h']:,.2f}")
print(f"Realized PnL (7d): ${summary['realized_pnl_7d']:,.2f}")
print(f"Realized PnL (30d): ${summary['realized_pnl_30d']:,.2f}")
print(f"\nAçık Pozisyonlar: {summary['num_positions']}")
print(f"  Long: {summary['num_long']} | Short: {summary['num_short']}")
print(f"Toplam Notional: ${summary['total_notional']:,.0f}")
print("=" * 60)
```

### Google Sheets'e Kaydetme

```python
from binance_futures import save_positions_to_sheet, save_daily_summary_to_sheet
from data_loader import _get_gspread_client

# Google Sheets client
client = _get_gspread_client()

# Pozisyonları kaydet
positions = api.get_open_positions()
save_positions_to_sheet(positions, client)

# Günlük özeti kaydet
summary = api.get_account_summary()
save_daily_summary_to_sheet(summary, client)

print("✅ Veriler Google Sheets'e kaydedildi!")
```

## 📈 Dashboard Özellikleri

### Ana Ekran

#### 1. Hesap Özeti Kartları
- **Cüzdan Bakiyesi**: Toplam USDT bakiyeniz
- **Marjin Bakiyesi**: Kullanılan + kullanılabilir marjin
- **Kullanılabilir Bakiye**: Yeni pozisyon açabileceğiniz miktar
- **Toplam Pozisyon**: Tüm pozisyonlarınızın notional değeri

#### 2. PnL Metrikleri
- **Gerçekleşmemiş PnL**: Açık pozisyonlardaki kar/zarar (%)
- **Realized PnL (24h)**: Son 24 saatte gerçekleşen kar/zarar
- **Realized PnL (7g)**: Son 7 günde gerçekleşen kar/zarar
- **Realized PnL (30g)**: Son 30 günde gerçekleşen kar/zarar

#### 3. Pozisyon Tablosu
Her pozisyon için:
- Sembol (BTCUSDT, ETHUSDT, vb.)
- Yön (🟢 Long / 🔴 Short)
- Miktar (contract sayısı)
- Giriş fiyatı
- Güncel mark fiyatı
- PnL ($ ve %)
- Leverage (kaç x)
- Tasfiye fiyatı
- Marjin tipi (Cross/Isolated)
- Notional değer

#### 4. Grafikler

**Pozisyon Dağılım Grafiği (Pie Chart)**
- Long vs Short oranı
- Notional bazlı dağılım

**Leverage Grafiği**
- Her sembol için leverage durumu
- Notional büyüklüğü
- Risk analizi

**Günlük PnL Grafiği**
- Bar chart: Günlük realized PnL
- Line chart: Kümülatif PnL
- Kazanan/kaybeden günler

#### 5. İstatistikler
- Toplam realized PnL
- Ortalama günlük PnL
- Kazanan gün oranı (win rate)
- En iyi gün PnL'i

### Ayarlar (Sidebar)

#### API Ayarları
- API Key girişi (güvenli password field)
- API Secret girişi (güvenli password field)
- Testnet seçeneği

#### Yenileme Ayarları
- 🔄 Otomatik yenile (30 saniye)
- Manuel yenileme butonu

#### Google Sheets Ayarları
- Otomatik kayıt aktif/pasif
- Kayıt durumu göstergesi

## 🔐 Güvenlik

### ✅ Güvenlik En İyi Uygulamaları

1. **API İzinleri**
   - ✅ Sadece "Reading" ve "Futures" izni verin
   - ❌ "Enable Withdrawals" iznini ASLA vermeyin
   - ❌ "Enable Spot & Margin Trading" gerekmiyorsa vermeyin

2. **IP Whitelist**
   - Mümkünse IP whitelist kullanın
   - Sabit IP'niz yoksa VPN kullanın

3. **API Key Saklama**
   - API key'leri asla kod içinde saklamayın
   - Environment variables veya Streamlit secrets kullanın
   - Git'e commit etmeyin (`.gitignore`)

4. **Secrets Yönetimi**
   ```bash
   # .gitignore dosyanıza ekleyin
   .streamlit/secrets.toml
   .env
   *.key
   ```

5. **Düzenli Kontrol**
   - API key'lerinizi düzenli kontrol edin
   - Kullanılmayan key'leri silin
   - Şüpheli aktivite varsa hemen key'i iptal edin

### ⚠️ Yaygın Hatalar ve Çözümler

#### Hata: "Invalid API Key"
**Neden**: API key yanlış veya iptal edilmiş
**Çözüm**: 
- API key'i kontrol edin
- Binance'te yeni key oluşturun
- IP whitelist ayarlarını kontrol edin

#### Hata: "Timestamp for this request is outside of the recvWindow"
**Neden**: Sistem saati yanlış
**Çözüm**:
```python
# ccxt otomatik düzeltir, ama manuel:
exchange = ccxt.binance({
    'options': {'adjustForTimeDifference': True}
})
```

#### Hata: "Insufficient permissions"
**Neden**: API key'de Futures izni yok
**Çözüm**: Binance'te API key ayarlarından "Enable Futures" aktif edin

#### Hata: Rate Limit
**Neden**: Çok fazla istek gönderildi
**Çözüm**: 
```python
# enableRateLimit ile otomatik
exchange = ccxt.binance({
    'enableRateLimit': True
})
```

## 📊 Veri Yapıları

### Positions DataFrame

```python
{
    'symbol': str,                    # Örn: 'BTCUSDT'
    'side': str,                      # 'LONG' veya 'SHORT'
    'size': float,                    # Pozisyon büyüklüğü
    'entry_price': float,             # Giriş fiyatı
    'mark_price': float,              # Güncel mark fiyatı
    'unrealized_pnl': float,          # Gerçekleşmemiş kar/zarar ($)
    'unrealized_pnl_percent': float,  # Gerçekleşmemiş kar/zarar (%)
    'leverage': int,                  # Leverage (örn: 10)
    'liquidation_price': float,       # Tasfiye fiyatı
    'margin_type': str,               # 'CROSS' veya 'ISOLATED'
    'notional': float,                # Pozisyon değeri ($)
    'timestamp': datetime             # Veri zamanı
}
```

### Account Summary

```python
{
    'wallet_balance': float,          # Toplam cüzdan bakiyesi
    'margin_balance': float,          # Marjin bakiyesi
    'available_balance': float,       # Kullanılabilir bakiye
    'unrealized_pnl': float,          # Toplam unrealized PnL
    'realized_pnl_24h': float,        # 24 saat realized PnL
    'realized_pnl_7d': float,         # 7 gün realized PnL
    'realized_pnl_30d': float,        # 30 gün realized PnL
    'total_pnl_24h': float,           # Toplam PnL (realized + unrealized)
    'num_positions': int,             # Pozisyon sayısı
    'num_long': int,                  # Long pozisyon sayısı
    'num_short': int,                 # Short pozisyon sayısı
    'total_notional': float,          # Toplam notional değer
    'timestamp': datetime             # Veri zamanı
}
```

### Daily PnL DataFrame

```python
{
    'date': date,                     # Tarih
    'realized_pnl': float,            # Günlük realized PnL
    'cumulative_pnl': float           # Kümülatif PnL
}
```

### Income History DataFrame

```python
{
    'timestamp': datetime,            # Tarih/saat
    'symbol': str,                    # Sembol
    'income_type': str,               # Gelir tipi (REALIZED_PNL, FUNDING_FEE, vb.)
    'income': float,                  # Gelir miktarı
    'asset': str,                     # Varlık (USDT)
    'info': str                       # Ek bilgi
}
```

## 🎨 Özelleştirme

### Dashboard Renkleri

```python
# futures_page.py içinde
# Yeşil (kazanç)
GREEN = "#00e676"
# Kırmızı (kayıp)
RED = "#ff5252"
# Mavi (neutral)
BLUE = "#2196f3"
```

### Cache Süreleri

```python
# Pozisyonlar: 30 saniye
@st.cache_data(ttl=30)

# Hesap özeti: 60 saniye
@st.cache_data(ttl=60)

# PnL özeti: 5 dakika
@st.cache_data(ttl=300)
```

### Otomatik Yenileme

```python
# futures_page.py sonunda
if st.session_state.get('auto_refresh', False):
    import time
    time.sleep(30)  # 30 saniye bekle
    st.rerun()      # Sayfayı yenile
```

## 📝 Google Sheets Yapısı

### Sheet 1: futures_positions
Güncel pozisyonlar (her güncellemede yenilenir)

| Timestamp | Symbol | Side | Size | Entry Price | Mark Price | Unrealized PnL | ... |
|-----------|--------|------|------|-------------|------------|----------------|-----|
| 2024-11-27 10:30:00 | BTCUSDT | LONG | 0.5 | 43500.0 | 44000.0 | +250.00 | ... |

### Sheet 2: futures_daily_summary
Günlük özet (her gün bir kayıt)

| Timestamp | Wallet Balance | Margin Balance | Unrealized PnL | Realized PnL 24h | ... |
|-----------|----------------|----------------|----------------|------------------|-----|
| 2024-11-27 00:00:00 | 10000.00 | 10500.00 | +250.00 | +150.00 | ... |

## 🔧 İleri Seviye Kullanım

### Custom Indicators

Kendi göstergelerinizi ekleyin:

```python
def calculate_win_rate(daily_pnl_df):
    """Kazanan gün oranını hesapla"""
    winning_days = len(daily_pnl_df[daily_pnl_df['realized_pnl'] > 0])
    total_days = len(daily_pnl_df)
    return (winning_days / total_days * 100) if total_days > 0 else 0

def calculate_sharpe_ratio(daily_pnl_df, risk_free_rate=0.0):
    """Sharpe ratio hesapla"""
    returns = daily_pnl_df['realized_pnl'].pct_change().dropna()
    excess_returns = returns - risk_free_rate
    return excess_returns.mean() / excess_returns.std() if len(returns) > 0 else 0

def calculate_max_drawdown(daily_pnl_df):
    """Maximum drawdown hesapla"""
    cumulative = daily_pnl_df['cumulative_pnl']
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()
```

### Webhook Entegrasyonu

Trading bot'larınızdan webhook ile veri alın:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook/position', methods=['POST'])
def webhook_position():
    """Trading bot'tan pozisyon bildirimi"""
    data = request.json
    symbol = data['symbol']
    side = data['side']
    size = data['size']
    
    # Kaydet
    # ...
    
    return {'status': 'success'}
```

### Alarm Sistemi

PnL bazlı alarmlar:

```python
def check_pnl_alerts(summary, thresholds):
    """PnL alarmlarını kontrol et"""
    alerts = []
    
    # Unrealized PnL kontrolü
    if summary['unrealized_pnl'] < thresholds['unrealized_pnl_min']:
        alerts.append({
            'type': 'danger',
            'message': f"⚠️ Unrealized PnL kritik seviyede: ${summary['unrealized_pnl']:,.2f}"
        })
    
    # Günlük PnL kontrolü
    if summary['realized_pnl_24h'] < thresholds['daily_pnl_min']:
        alerts.append({
            'type': 'warning',
            'message': f"📉 Günlük PnL hedefin altında: ${summary['realized_pnl_24h']:,.2f}"
        })
    
    return alerts

# Kullanım
thresholds = {
    'unrealized_pnl_min': -500,  # -$500'un altında alarm
    'daily_pnl_min': 0           # Günlük kayıpda alarm
}

alerts = check_pnl_alerts(summary, thresholds)
for alert in alerts:
    if alert['type'] == 'danger':
        st.error(alert['message'])
    else:
        st.warning(alert['message'])
```

## 🤝 Destek ve Katkı

### Hata Raporlama
GitHub issues üzerinden hata raporlayabilirsiniz.

### Geliştirme
Pull request'ler memnuniyetle karşılanır!

### İletişim
Sorularınız için:
- GitHub Discussions
- Email: [email protected]

## 📜 Lisans

MIT License - Detaylar için LICENSE dosyasına bakın.

## ⚠️ Sorumluluk Reddi

Bu yazılım **sadece bilgilendirme amaçlıdır** ve **yatırım tavsiyesi değildir**. 

- Kripto para ticareti yüksek risk içerir
- Kaybedebileceğinizden fazlasını yatırmayın
- Veriler gerçek zamanlı olmayabilir
- API bağlantı sorunları olabilir
- Yazılım "olduğu gibi" sağlanır, garanti verilmez

**KENDİ RİSKİNİZE KULLANIN!**

---

## 🎉 İyi Ticaret Günleri Dileriz!

Bu dokümantasyonu beğendiyseniz ⭐ vermeyi unutmayın!

**Son Güncelleme**: 27 Kasım 2024
