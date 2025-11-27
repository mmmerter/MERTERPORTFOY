#!/usr/bin/env python3
"""
Maliyet ve Fiyat kontrolü - Nerede sorun var?
"""

import pandas as pd
import yfinance as yf
from data_loader import get_data_from_sheet, get_tefas_data, get_usd_try
from utils import get_yahoo_symbol

print("=" * 80)
print("MALİYET VE FİYAT KONTROLÜ - -43 BİN TL SORUNUNU BULALIM")
print("=" * 80)
print()

# 1. Google Sheets'ten portföy verisini çek
print("📊 Google Sheets'ten portföy verisi çekiliyor...")
portfoy_df = get_data_from_sheet()

if portfoy_df.empty:
    print("❌ Google Sheets'ten veri çekilemedi!")
    print("   Lütfen internet bağlantınızı ve secrets ayarlarınızı kontrol edin.")
    exit(1)

print(f"✅ {len(portfoy_df)} varlık bulundu")
print()

# Sadece portföy varlıklarını al (Takip hariç)
portfoy_mask = portfoy_df["Tip"].astype(str).str.contains("Portfoy|Portföy", case=False, na=False)
portfoy_only = portfoy_df[portfoy_mask].copy()

if portfoy_only.empty:
    print("❌ Portföy varlığı bulunamadı!")
    exit(1)

print(f"✅ {len(portfoy_only)} portföy varlığı bulundu")
print()

# USD/TRY kuru
usd_try = get_usd_try()
print(f"💱 USD/TRY Kuru: {usd_try:.2f}")
print()

# 2. Her varlık için maliyet ve güncel fiyatı kontrol et
print("=" * 80)
print("VARLIK BAZINDA MALİYET VE FİYAT KONTROLÜ")
print("=" * 80)
print()

problems = []
total_maliyet_try = 0
total_deger_try = 0

for idx, row in portfoy_only.iterrows():
    kod = str(row.get("Kod", ""))
    pazar = str(row.get("Pazar", ""))
    adet = float(row.get("Adet", 0) or 0)
    maliyet = float(row.get("Maliyet", 0) or 0)
    
    if adet == 0:
        continue
    
    print(f"🔍 {kod} ({pazar})")
    print(f"   Adet: {adet:,.2f}")
    print(f"   Maliyet (Alış Fiyatı): {maliyet:,.2f}")
    
    # Para birimini belirle
    pazar_upper = pazar.upper()
    kod_upper = kod.upper()
    
    if "BIST" in pazar_upper or "TL" in kod_upper or "FON" in pazar_upper or "EMTIA" in pazar_upper or "NAKIT" in pazar_upper:
        asset_currency = "TRY"
    else:
        asset_currency = "USD"
    
    print(f"   Para Birimi: {asset_currency}")
    
    # Güncel fiyatı çek
    curr_price = 0
    
    try:
        if "NAKIT" in pazar_upper:
            if kod_upper == "TL":
                curr_price = 1.0
            elif kod_upper == "USD":
                curr_price = usd_try
            else:
                curr_price = 1.0
        elif "FON" in pazar_upper:
            price, _ = get_tefas_data(kod)
            curr_price = price if price else 0
        elif "GRAM GÜMÜŞ" in kod_upper or "Gram Gümüş" in kod:
            # Ons gümüş fiyatı
            ticker = yf.Ticker("SI=F")
            h = ticker.history(period="5d")
            if not h.empty:
                ons_price = h["Close"].iloc[-1]
                curr_price = (ons_price * usd_try) / 31.1035
        elif "GRAM ALTIN" in kod_upper or "Gram Altın" in kod:
            # Ons altın fiyatı
            ticker = yf.Ticker("GC=F")
            h = ticker.history(period="5d")
            if not h.empty:
                ons_price = h["Close"].iloc[-1]
                curr_price = (ons_price * usd_try) / 31.1035
        else:
            # Yahoo Finance
            symbol = get_yahoo_symbol(kod, pazar)
            ticker = yf.Ticker(symbol)
            h = ticker.history(period="5d")
            if not h.empty:
                curr_price = h["Close"].iloc[-1]
            else:
                # Daha uzun period
                h = ticker.history(period="1mo")
                if not h.empty:
                    curr_price = h["Close"].iloc[-1]
    except Exception as e:
        print(f"   ⚠️  Fiyat çekilemedi: {e}")
    
    print(f"   Güncel Fiyat: {curr_price:,.2f} {asset_currency}")
    
    # Değerleri hesapla (TRY bazında)
    maliyet_total = maliyet * adet
    deger_total = curr_price * adet
    
    if asset_currency == "USD":
        maliyet_total_try = maliyet_total * usd_try
        deger_total_try = deger_total * usd_try
    else:
        maliyet_total_try = maliyet_total
        deger_total_try = deger_total
    
    kz = deger_total_try - maliyet_total_try
    
    print(f"   Yatırılan (TRY): ₺{maliyet_total_try:,.2f}")
    print(f"   Güncel Değer (TRY): ₺{deger_total_try:,.2f}")
    print(f"   Kâr/Zarar: ₺{kz:,.2f}")
    
    total_maliyet_try += maliyet_total_try
    total_deger_try += deger_total_try
    
    # Sorunları tespit et
    if curr_price == 0:
        problems.append({
            "Kod": kod,
            "Sorun": "Güncel fiyat çekilemedi (0)",
            "Etki": f"₺{maliyet_total_try:,.2f} değerinde varlık eksik hesaplandı"
        })
        print(f"   ❌ SORUN: Güncel fiyat 0!")
    
    if curr_price == maliyet and curr_price > 0:
        problems.append({
            "Kod": kod,
            "Sorun": "Güncel fiyat = Maliyet (fallback kullanılmış)",
            "Etki": "Kâr/zarar hesaplanamadı"
        })
        print(f"   ⚠️  Fiyat maliyet ile aynı (fallback)")
    
    if maliyet > curr_price * 10 and curr_price > 0:
        problems.append({
            "Kod": kod,
            "Sorun": f"Maliyet çok yüksek! (Maliyet: {maliyet:,.2f}, Fiyat: {curr_price:,.2f})",
            "Etki": f"Gerçek dışı zarar: ₺{abs(kz):,.2f}"
        })
        print(f"   ❌ SORUN: Maliyet güncel fiyattan 10 kat fazla!")
    
    if curr_price > maliyet * 10 and maliyet > 0:
        problems.append({
            "Kod": kod,
            "Sorun": f"Fiyat çok yüksek! (Maliyet: {maliyet:,.2f}, Fiyat: {curr_price:,.2f})",
            "Etki": f"Gerçek dışı kâr: ₺{kz:,.2f}"
        })
        print(f"   ⚠️  Fiyat maliyetten 10 kat fazla")
    
    print()

# Toplam özet
print("=" * 80)
print("TOPLAM ÖZET")
print("=" * 80)
print()
print(f"Toplam Yatırılan (Maliyet): ₺{total_maliyet_try:,.2f}")
print(f"Toplam Güncel Değer: ₺{total_deger_try:,.2f}")
print()
total_kz = total_deger_try - total_maliyet_try
print(f"TOPLAM KÂR/ZARAR: ₺{total_kz:,.2f}")
print()

if abs(total_kz + 43620) < 5000:
    print("🔴 SORUN TESPİT EDİLDİ!")
    print(f"   Hesaplanan toplam kâr/zarar ({total_kz:,.0f} TL) -43,620 TL'ye yakın.")
    print()

# Sorunları listele
if problems:
    print("=" * 80)
    print(f"⚠️  {len(problems)} SORUN TESPİT EDİLDİ")
    print("=" * 80)
    print()
    
    for i, problem in enumerate(problems, 1):
        print(f"{i}. {problem['Kod']}")
        print(f"   Sorun: {problem['Sorun']}")
        print(f"   Etki: {problem['Etki']}")
        print()
    
    print("💡 ÇÖZÜMLEassistant:")
    print("   1. Google Sheets'teki 'PortfoyData' dosyasını açın")
    print("   2. Yukarıdaki sorunlu varlıkların 'Maliyet' kolonunu kontrol edin")
    print("   3. Yanlış girilmiş maliyet değerlerini düzeltin")
    print("   4. Uygulamayı yenileyin")
else:
    print("✅ Belirgin bir sorun tespit edilmedi.")
    print()
    print("   Ancak toplam kâr/zarar -43,000 TL gösteriyorsa:")
    print("   - Google Sheets'teki tüm maliyet değerlerini tek tek kontrol edin")
    print("   - Özellikle USD varlıkları için maliyet TL olarak girilmiş olabilir")
    print("   - Veya TL varlıkları için maliyet USD olarak girilmiş olabilir")

print()
print("=" * 80)
