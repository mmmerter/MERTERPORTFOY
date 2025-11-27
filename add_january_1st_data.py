#!/usr/bin/env python3
"""
1 Ocak 2025 Portföy Verisini Manuel Ekleme Scripti

Bu script, Google Sheets'teki portfolio_history tablosuna 
1 Ocak 2025 tarihli portföy değerini ekler.

KULLANIM:
    python3 add_january_1st_data.py

İnteraktif olarak 1 Ocak'taki portföy değerinizi girmeniz istenecek.
"""

import sys
from datetime import datetime
import pandas as pd

try:
    from data_loader import (
        _get_gspread_client,
        read_portfolio_history,
        get_usd_try,
    )
except ImportError as e:
    print(f"❌ Hata: Gerekli modüller yüklenemedi: {e}")
    print("   Lütfen önce: pip install -r requirements.txt")
    sys.exit(1)

SHEET_NAME = "PortfoyData"

print("=" * 80)
print("1 OCAK 2025 PORTFÖY VERİSİNİ MANUEL EKLEME")
print("=" * 80)
print()

# Önce mevcut verileri kontrol et
print("📊 Mevcut Tarihsel Veriyi Kontrol Ediyorum...")
print("-" * 80)
history_df = read_portfolio_history()

if not history_df.empty:
    # 1 Ocak 2025 verisi var mı kontrol et
    history_df["Tarih"] = pd.to_datetime(history_df["Tarih"])
    jan_1_mask = (history_df["Tarih"].dt.date == datetime(2025, 1, 1).date())
    
    if jan_1_mask.any():
        existing_value = history_df.loc[jan_1_mask, "Değer_TRY"].iloc[0]
        print(f"⚠️  1 Ocak 2025 verisi ZATEN MEVCUT!")
        print(f"   Mevcut Değer: ₺{existing_value:,.2f}")
        print()
        response = input("Bu değeri güncellemek ister misiniz? (e/h): ").strip().lower()
        if response != "e":
            print("İşlem iptal edildi.")
            sys.exit(0)
        print()
        print("Mevcut değer GÜNCELLENECEK...")
        update_mode = True
    else:
        print("✅ 1 Ocak 2025 verisi yok, eklenecek.")
        update_mode = False
else:
    print("ℹ️  Tarihsel veri boş, yeni veri eklenecek.")
    update_mode = False

print()
print("-" * 80)
print("1 OCAK 2025 PORTFÖY DEĞERİNİ GİRİN")
print("-" * 80)
print()
print("💡 İpucu: 1 Ocak tarihindeki TOPLAM portföy değerinizi girin.")
print("   Banka ekstrelerini, not defterinizi veya tahmini değeri kullanabilirsiniz.")
print()

# TRY değerini al
while True:
    try:
        deger_try_str = input("1 Ocak Portföy Değeri (TRY) [örn: 320000]: ").strip()
        deger_try = float(deger_try_str.replace(",", "").replace(".", "").replace("₺", ""))
        if deger_try <= 0:
            print("❌ Değer 0'dan büyük olmalı!")
            continue
        break
    except ValueError:
        print("❌ Geçersiz değer! Lütfen sayı girin (örn: 320000)")

print()

# USD değerini al (opsiyonel)
print("USD değerini de girebilirsiniz veya otomatik hesaplatabilirsiniz.")
usd_choice = input("USD değerini manuel girmek ister misiniz? (e/h): ").strip().lower()

if usd_choice == "e":
    while True:
        try:
            deger_usd_str = input("1 Ocak Portföy Değeri (USD) [örn: 9411.76]: ").strip()
            deger_usd = float(deger_usd_str.replace(",", "").replace("$", ""))
            if deger_usd <= 0:
                print("❌ Değer 0'dan büyük olmalı!")
                continue
            break
        except ValueError:
            print("❌ Geçersiz değer! Lütfen sayı girin (örn: 9411.76)")
else:
    # 1 Ocak 2025 USD/TRY kurunu kullan (yaklaşık 34.0)
    usd_try_jan_1 = 34.0  # 1 Ocak 2025 yaklaşık kur
    deger_usd = deger_try / usd_try_jan_1
    print(f"ℹ️  USD değeri otomatik hesaplandı (kur: {usd_try_jan_1}): ${deger_usd:,.2f}")

print()
print("-" * 80)
print("ÖZET")
print("-" * 80)
print(f"Tarih: 1 Ocak 2025")
print(f"Değer (TRY): ₺{deger_try:,.2f}")
print(f"Değer (USD): ${deger_usd:,.2f}")
print()

# Onay al
response = input("Bu değerleri Google Sheets'e eklemek istiyor musunuz? (e/h): ").strip().lower()
if response != "e":
    print("İşlem iptal edildi.")
    sys.exit(0)

print()
print("📤 Google Sheets'e Yazılıyor...")
print("-" * 80)

try:
    client = _get_gspread_client()
    if client is None:
        print("❌ Google Sheets bağlantısı kurulamadı!")
        print("   Servis hesabı ayarlarını kontrol edin.")
        sys.exit(1)
    
    spreadsheet = client.open(SHEET_NAME)
    sheet = spreadsheet.worksheet("portfolio_history")
    
    # Tarih string'i
    date_str = "2025-01-01"
    
    if update_mode:
        # Mevcut satırı bul ve güncelle
        all_records = sheet.get_all_records()
        for idx, record in enumerate(all_records):
            if str(record.get("Tarih", ""))[:10] == date_str:
                # idx + 2 çünkü: +1 (0-indexed), +1 (header row)
                row_number = idx + 2
                sheet.update(f"B{row_number}:C{row_number}", [[float(deger_try), float(deger_usd)]])
                print(f"✅ 1 Ocak 2025 verisi GÜNCELLENDİ (satır {row_number})")
                break
    else:
        # Yeni satır ekle
        new_row = [date_str, float(deger_try), float(deger_usd)]
        sheet.append_row(new_row)
        print("✅ 1 Ocak 2025 verisi EKLENDI")
    
    print()
    print("=" * 80)
    print("BAŞARILI!")
    print("=" * 80)
    print()
    print("Artık YTD performansınız doğru şekilde hesaplanacak.")
    print("Streamlit uygulamanızı yenileyerek sonucu görebilirsiniz.")
    print()

except Exception as e:
    print(f"❌ HATA: {e}")
    print()
    print("Google Sheets'e yazılırken bir hata oluştu.")
    print("Manuel olarak eklemek için:")
    print()
    print("1. Google Sheets'i açın: https://docs.google.com/spreadsheets/")
    print("2. PortfoyData dosyasını bulun")
    print("3. portfolio_history sayfasına gidin")
    print("4. Yeni satır ekleyin:")
    print(f"   Tarih: {date_str}")
    print(f"   Değer_TRY: {deger_try}")
    print(f"   Değer_USD: {deger_usd}")
    sys.exit(1)
