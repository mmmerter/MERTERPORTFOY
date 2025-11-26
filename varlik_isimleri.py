"""
Varlık isimlerini ve emojilerini modernize eden mapping modülü
"""

# Bilinen hisse kodları ve isimleri
BILINEN_VARLIKLAR = {
    # Türk Hisseleri - BIST
    "THYAO": "✈️ THYAO • Türk Hava Yolları",
    "AKBNK": "🏦 AKBNK • Akbank",
    "GARAN": "🏦 GARAN • Garanti BBVA",
    "ISCTR": "🏦 ISCTR • İş Bankası (C)",
    "YKBNK": "🏦 YKBNK • Yapı Kredi",
    "SASA": "🏭 SASA • Sasa Polyester",
    "TUPRS": "🛢️ TUPRS • Tüpraş",
    "EREGL": "🏭 EREGL • Ereğli Demir Çelik",
    "KCHOL": "🏢 KCHOL • Koç Holding",
    "SAHOL": "🏢 SAHOL • Sabancı Holding",
    "BIMAS": "🏪 BIMAS • BİM",
    "MGROS": "🏪 MGROS • Migros",
    "SOKM": "🏪 SOKM • Şok Marketler",
    "TKFEN": "🏗️ TKFEN • Tekfen Holding",
    "TRMET": "⚡ TRMET • Türk Metal",
    "GRID": "🏗️ GRID • Grid Holding",
    "ACLS": "🏗️ ACLS • Acıselsan",
    "ASELS": "🚀 ASELS • Aselsan",
    "SISE": "🏭 SISE • Şişe Cam",
    "PETKM": "⛽ PETKM • Petkim",
    "TOASO": "🚗 TOASO • Tofaş",
    "FROTO": "🚗 FROTO • Ford Otosan",
    "TTKOM": "📱 TTKOM • Türk Telekom",
    "TCELL": "📱 TCELL • Turkcell",
    "ENKA": "🏗️ ENKA • Enka İnşaat",
    "TTRAK": "🚜 TTRAK • Türk Traktör",
    
    # ABD Hisseleri
    "TSLA": "🚗 TSLA • Tesla",
    "AAPL": "🍎 AAPL • Apple",
    "MSFT": "💻 MSFT • Microsoft",
    "AMZN": "📦 AMZN • Amazon",
    "GOOGL": "🔍 GOOGL • Google (Alphabet)",
    "META": "👥 META • Meta (Facebook)",
    "NVDA": "🎮 NVDA • NVIDIA",
    "AMD": "💻 AMD • AMD",
    "NFLX": "🎬 NFLX • Netflix",
    "DIS": "🎭 DIS • Disney",
    "BABA": "🛒 BABA • Alibaba",
    "NIO": "🚗 NIO • NIO",
    "PLTR": "🔐 PLTR • Palantir",
    "COIN": "₿ COIN • Coinbase",
    "SQ": "💳 SQ • Block (Square)",
    "PYPL": "💳 PYPL • PayPal",
    "V": "💳 V • Visa",
    "MA": "💳 MA • Mastercard",
    "JPM": "🏦 JPM • JPMorgan Chase",
    "BAC": "🏦 BAC • Bank of America",
    "WMT": "🏪 WMT • Walmart",
    "KO": "🥤 KO • Coca-Cola",
    "PEP": "🥤 PEP • PepsiCo",
    "MCD": "🍔 MCD • McDonald's",
    "SBUX": "☕ SBUX • Starbucks",
    "NKE": "👟 NKE • Nike",
    "BA": "✈️ BA • Boeing",
    "GE": "⚡ GE • General Electric",
    "F": "🚗 F • Ford",
    "GM": "🚗 GM • General Motors",
    "T": "📱 T • AT&T",
    "VZ": "📱 VZ • Verizon",
    "INTC": "💻 INTC • Intel",
    "CSCO": "🌐 CSCO • Cisco",
    "ORCL": "💾 ORCL • Oracle",
    "CRM": "☁️ CRM • Salesforce",
    "ADBE": "🎨 ADBE • Adobe",
    "UBER": "🚕 UBER • Uber",
    "LYFT": "🚕 LYFT • Lyft",
    "ABNB": "🏠 ABNB • Airbnb",
    "SNAP": "👻 SNAP • Snapchat",
    "TWTR": "🐦 TWTR • Twitter",
    "SPOT": "🎵 SPOT • Spotify",
    "SHOP": "🛒 SHOP • Shopify",
    "ZM": "📹 ZM • Zoom",
    "DOCU": "📝 DOCU • DocuSign",
    "ROKU": "📺 ROKU • Roku",
    "SQ": "💳 SQ • Square",
    "RUT": "📊 RUT • Russell 2000",
    "GFS": "🏢 GFS • GlobalFoundries",
    "NB": "🏦 NB • NioCorp",
    "CRDO": "💻 CRDO • Credo Technology",
    "CEG": "⚡ CEG • Constellation Energy",
    "OSCR": "🏥 OSCR • Oscar Health",
    
    # Kripto Paralar
    "BTC": "₿ BTC • Bitcoin",
    "ETH": "Ξ ETH • Ethereum",
    "BNB": "🔶 BNB • Binance Coin",
    "ADA": "🔷 ADA • Cardano",
    "SOL": "☀️ SOL • Solana",
    "DOT": "🔴 DOT • Polkadot",
    "MATIC": "🟣 MATIC • Polygon",
    "AVAX": "🔺 AVAX • Avalanche",
    "DOGE": "🐕 DOGE • Dogecoin",
    "SHIB": "🐕 SHIB • Shiba Inu",
    "XRP": "💧 XRP • Ripple",
    "LTC": "🥈 LTC • Litecoin",
    
    # Emtia
    "Gram Altın (TL)": "🥇 Gram Altın",
    "Gram Gümüş (TL)": "🥈 Gram Gümüş",
    "Gram Altın": "🥇 Gram Altın",
    "Gram Gümüş": "🥈 Gram Gümüş",
    "Altın": "🥇 Altın",
    "Gümüş": "🥈 Gümüş",
    "Ons Altın": "🥇 Ons Altın",
    "Ons Gümüş": "🥈 Ons Gümüş",
    "Petrol": "🛢️ Petrol",
    "Doğalgaz": "🔥 Doğalgaz",
    
    # Para Birimleri
    "USD": "💵 ABD Doları",
    "EUR": "💶 Euro",
    "GBP": "💷 İngiliz Sterlini",
    "TRY": "💰 Türk Lirası",
    "TL": "💰 Türk Lirası",
    "JPY": "💴 Japon Yeni",
    "CHF": "🇨🇭 İsviçre Frangı",
    "CAD": "🇨🇦 Kanada Doları",
    "AUD": "🇦🇺 Avustralya Doları",
    
    # Fonlar (yaygın olanlar)
    "YHB": "📊 YHB • Yapı Kredi Emeklilik",
    "TTE": "📊 TTE • Tacirler Emeklilik",
    "MAC": "📊 MAC • Maxis Emeklilik",
    "AFT": "📊 AFT • Allianz Hayat Emeklilik",
    "ZPE": "📊 ZPE • Ziraat Emeklilik",
    "GAE": "📊 GAE • Garanti Emeklilik",
    "AEE": "📊 AEE • Aegon Emeklilik",
}

# Para birimi sembolleri
PARA_BIRIMI_EMOJILERI = {
    "TRY": "₺",
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
}


def modernize_varlik_adi(kod: str) -> str:
    """
    Varlık kodunu modernize eder.
    
    Args:
        kod: Varlık kodu (örn: "TSLA", "Gram Altın (TL)")
    
    Returns:
        Modernize edilmiş varlık adı
    """
    if not kod:
        return kod
    
    kod_str = str(kod).strip()
    
    # Bilinen varlık mı kontrol et
    if kod_str in BILINEN_VARLIKLAR:
        return BILINEN_VARLIKLAR[kod_str]
    
    # Kodun içinde parantez varsa ve bilinen değilse, orijinalini döndür
    if "(" in kod_str:
        # Emtia isimleri için özel kontrol
        if "Gram Altın" in kod_str:
            return "🥇 Gram Altın"
        elif "Gram Gümüş" in kod_str:
            return "🥈 Gram Gümüş"
        elif "Ons Altın" in kod_str:
            return "🥇 Ons Altın"
        elif "Ons Gümüş" in kod_str:
            return "🥈 Ons Gümüş"
    
    # Bilinmeyen varlıklar için emoji ekle
    # BIST hisseleri için kontrol (genelde 5 harf ve büyük harf)
    if len(kod_str) <= 6 and kod_str.isupper() and kod_str.isalpha():
        # Türk hissesi olabilir
        if any(tr_char in kod_str for tr_char in ['Ç', 'Ğ', 'İ', 'Ö', 'Ş', 'Ü']):
            return f"🇹🇷 {kod_str}"
        # ABD hissesi olabilir
        return f"🎯 {kod_str}"
    
    # Kripto kontrolü (genelde 3-4 harf ve büyük harf)
    if 2 <= len(kod_str) <= 5 and kod_str.isupper() and kod_str.isalpha():
        # Bilinen kripto değilse ama format uyuyorsa
        return f"₿ {kod_str}"
    
    # Varsayılan: emoji eklemeden döndür
    return f"🎯 {kod_str}"


def modernize_para_birimi(pb: str) -> str:
    """Para birimi kodunu emoji ile döndürür."""
    if pb in PARA_BIRIMI_EMOJILERI:
        return PARA_BIRIMI_EMOJILERI[pb]
    return pb


def modernize_sayi(sayi: float, para_birimi: str = None, ondalik: int = 2) -> str:
    """
    Sayıyı modern formatla gösterir.
    
    Args:
        sayi: Formatlanacak sayı
        para_birimi: Para birimi kodu (opsiyonel)
        ondalik: Ondalık basamak sayısı
    
    Returns:
        Formatlanmış sayı string'i
    """
    if para_birimi:
        pb_emoji = modernize_para_birimi(para_birimi)
        return f"{pb_emoji}{sayi:,.{ondalik}f}"
    return f"{sayi:,.{ondalik}f}"
