#!/usr/bin/env python3
"""
Gerçek portföy verilerini kontrol et ve kar/zarar hesaplamasını doğrula
"""

import pandas as pd
from datetime import datetime
from data_loader import read_portfolio_history, read_history_fon, get_data_from_sheet

print("=" * 80)
print("PORTFÖY VERİ KONTROLÜ - GERÇEK KAR/ZARAR ANALİZİ")
print("=" * 80)
print()

# 1. Tarihsel veriyi oku
print("📊 Tarihsel Veriyi Okuyorum...")
print("-" * 80)
history_df = read_portfolio_history()

if history_df.empty:
    print("❌ Tarihsel veri bulunamadı!")
    print("   Bu, YTD hesaplamasının yapılamayacağı anlamına gelir.")
    print()
else:
    print(f"✅ {len(history_df)} kayıt bulundu")
    print()
    
    # Tarihleri parse et
    history_df["Tarih"] = pd.to_datetime(history_df["Tarih"])
    history_df = history_df.sort_values("Tarih")
    
    # İlk ve son kayıtlar
    first_record = history_df.iloc[0]
    last_record = history_df.iloc[-1]
    
    print("🔍 İLK KAYIT (Başlangıç Noktası):")
    print(f"  Tarih: {first_record['Tarih'].strftime('%d %B %Y (%A)')}")
    print(f"  Değer (TRY): ₺{first_record['Değer_TRY']:,.2f}")
    print()
    
    print("🔍 SON KAYIT (Bugün):")
    print(f"  Tarih: {last_record['Tarih'].strftime('%d %B %Y (%A)')}")
    print(f"  Değer (TRY): ₺{last_record['Değer_TRY']:,.2f}")
    print()
    
    # Değişim hesapla
    diff = last_record['Değer_TRY'] - first_record['Değer_TRY']
    pct = (diff / first_record['Değer_TRY'] * 100) if first_record['Değer_TRY'] > 0 else 0
    days = (last_record['Tarih'] - first_record['Tarih']).days
    
    print("📈 HESAPLANAN PERFORMANS:")
    print(f"  Zaman Aralığı: {days} gün ({first_record['Tarih'].strftime('%d %b')} - {last_record['Tarih'].strftime('%d %b')})")
    print(f"  Değer Değişimi: ₺{diff:,.2f}")
    print(f"  Yüzde Değişim: {pct:+.2f}%")
    print()
    
    if abs(diff + 43620) < 1000:  # -43620'ye yakınsa
        print("🔴 SORUN BULUNDU!")
        print("   Hesaplanan değişim -43,620 TL'ye yakın.")
        print("   Ama sen Kasım'dan beri bu kadar zarar etmediğini söylüyorsun.")
        print()
    
    # Tüm kayıtları göster
    print("📋 TÜM KAYITLAR:")
    print("-" * 80)
    display_df = history_df[["Tarih", "Değer_TRY", "Değer_USD"]].copy()
    display_df["Tarih"] = display_df["Tarih"].dt.strftime("%Y-%m-%d %A")
    display_df["Değer_TRY"] = display_df["Değer_TRY"].apply(lambda x: f"₺{x:,.0f}")
    display_df["Değer_USD"] = display_df["Değer_USD"].apply(lambda x: f"${x:,.0f}")
    print(display_df.to_string(index=False))
    print()

# 2. FON verisini kontrol et (subtract logic için)
print("=" * 80)
print("FON VERİSİ KONTROLÜ (Subtract Logic)")
print("=" * 80)
print()

history_fon = read_history_fon()
if history_fon.empty:
    print("ℹ️  Fon tarihçesi boş. Subtract logic uygulanmayacak.")
else:
    history_fon["Tarih"] = pd.to_datetime(history_fon["Tarih"])
    history_fon = history_fon.sort_values("Tarih")
    print(f"✅ {len(history_fon)} fon kaydı bulundu")
    print()
    
    first_fon = history_fon.iloc[0]
    last_fon = history_fon.iloc[-1]
    
    print("🔍 İLK FON KAYDI:")
    print(f"  Tarih: {first_fon['Tarih'].strftime('%d %B %Y')}")
    print(f"  Fon Değeri: ₺{first_fon['Değer_TRY']:,.2f}")
    print()
    
    print("🔍 SON FON KAYDI:")
    print(f"  Tarih: {last_fon['Tarih'].strftime('%d %B %Y')}")
    print(f"  Fon Değeri: ₺{last_fon['Değer_TRY']:,.2f}")
    print()

# 3. Şu anki portföyü kontrol et (Google Sheets'ten)
print("=" * 80)
print("GÜNCEL PORTFÖY KONTROLÜ (Google Sheets)")
print("=" * 80)
print()

current_portfolio = get_data_from_sheet()
if current_portfolio.empty:
    print("❌ Google Sheets'ten portföy verisi okunamadı")
else:
    print(f"✅ {len(current_portfolio)} varlık bulundu")
    print()
    
    # Portföy varlıklarını filtrele (Takip hariç)
    portfoy_mask = current_portfolio["Tip"].astype(str).str.contains("Portfoy|Portföy", case=False, na=False)
    portfoy_only = current_portfolio[portfoy_mask].copy()
    
    if not portfoy_only.empty:
        print("📊 GÜNCEL PORTFÖY ÖZETİ:")
        print("-" * 80)
        
        # Pazar bazlı özet
        pazar_summary = portfoy_only.groupby("Pazar").agg({
            "Kod": "count",
        }).reset_index()
        pazar_summary.columns = ["Pazar", "Varlık Sayısı"]
        print(pazar_summary.to_string(index=False))
        print()
        
        # Maliyet ve değer kontrolü yapabilmek için fiyat hesapla
        # Not: Gerçek hesaplama için tüm mantığı çalıştırmak gerekir
        print("⚠️  Gerçek değer hesaplaması için uygulamayı çalıştırmanız gerekiyor.")
        print("    Ancak Google Sheets'teki ham verileri görebilirsiniz:")
        print()
        
        # Ham veriyi göster
        display_cols = ["Kod", "Pazar", "Adet", "Maliyet"]
        if all(col in portfoy_only.columns for col in display_cols):
            print("📋 PORTFÖY VARLIKLARI (Ham Veri):")
            print("-" * 80)
            display_portfolio = portfoy_only[display_cols].copy()
            display_portfolio["Adet"] = display_portfolio["Adet"].apply(lambda x: f"{float(x):,.2f}" if x else "0")
            display_portfolio["Maliyet"] = display_portfolio["Maliyet"].apply(lambda x: f"₺{float(x):,.2f}" if x else "₺0")
            print(display_portfolio.to_string(index=False, max_rows=20))
            if len(display_portfolio) > 20:
                print(f"... ve {len(display_portfolio) - 20} varlık daha")
            print()

print("=" * 80)
print("ANALİZ SONUCU")
print("=" * 80)
print()

if not history_df.empty:
    print("🔍 SORUN TESPİTİ:")
    print()
    
    if abs(diff + 43620) < 1000:
        print("1. ❌ Hesaplanan performans -43,620 TL'ye yakın")
        print(f"   İlk kayıt: ₺{first_record['Değer_TRY']:,.2f} ({first_record['Tarih'].strftime('%d %B')})")
        print(f"   Son kayıt: ₺{last_record['Değer_TRY']:,.2f} ({last_record['Tarih'].strftime('%d %B')})")
        print()
        print("   Olası Nedenler:")
        print("   a) İlk kayıt ÇOK YÜKSEK bir değerle kaydedilmiş olabilir")
        print("   b) Son kayıt ÇOK DÜŞÜK bir değerle kaydedilmiş olabilir")
        print("   c) Fonlar yanlış hesaplanıyor olabilir (subtract logic)")
        print("   d) Bir varlık türü yanlış fiyatlanıyor olabilir")
        print()
        print("2. 💡 ÖNERİ:")
        print(f"   a) {first_record['Tarih'].strftime('%d %B')} tarihinde portföyünüzün değeri")
        print(f"      gerçekten ₺{first_record['Değer_TRY']:,.2f} miydi?")
        print()
        print(f"   b) Bugün portföyünüzün değeri gerçekten ₺{last_record['Değer_TRY']:,.2f} mi?")
        print()
        print("   c) Eğer bu değerler yanlışsa, Google Sheets'teki 'portfolio_history'")
        print("      tablosunu kontrol edin ve yanlış kayıtları düzeltin.")
    else:
        print("✅ Hesaplanan performans -43,620 TL DEĞİL")
        print(f"   Gerçek performans: ₺{diff:,.2f} ({pct:+.2f}%)")
        print()
        print("   Bu durumda, UI'da gösterilen değer farklı bir yerden geliyor olabilir.")

print()
print("=" * 80)
