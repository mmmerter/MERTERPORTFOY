#!/usr/bin/env python3
"""
YTD Performans Hesaplama Hata Ayıklama Scripti

Bu script, YTD performans hesaplamasının neden yanlış olduğunu tespit eder.
"""

import pandas as pd
from datetime import datetime
from data_loader import read_portfolio_history, get_timeframe_changes, get_history_summary

print("=" * 80)
print("YTD PERFORMANS HATA AYIKLAMA")
print("=" * 80)
print()

# 1. Tarihsel veri özetini al
print("📊 Tarihsel Veri Özeti:")
print("-" * 80)
summary = get_history_summary()
print(f"Durum: {summary['status']}")
print(f"Mesaj: {summary['message']}")
print(f"Veri Günü: {summary['days']}")
print(f"En Eski Kayıt: {summary['oldest']}")
print(f"En Yeni Kayıt: {summary['newest']}")
print(f"Toplam Kayıt: {summary['records']}")
print()

# 2. Tarihsel veriyi oku
print("📁 Tarihsel Veriyi Okuyorum...")
print("-" * 80)
history_df = read_portfolio_history()

if history_df.empty:
    print("❌ Tarihsel veri bulunamadı!")
    print("   Google Sheets'te 'portfolio_history' tablosu boş veya erişilemiyor.")
    exit(1)

print(f"✅ {len(history_df)} kayıt bulundu")
print()

# 3. Bu yılın verilerini filtrele
print("📅 2025 Yılı Verileri:")
print("-" * 80)
history_df["Tarih"] = pd.to_datetime(history_df["Tarih"])
year_2025 = history_df[history_df["Tarih"].dt.year == 2025].copy()

if year_2025.empty:
    print("❌ 2025 yılına ait hiç kayıt yok!")
    print("   YTD hesaplaması yapılamıyor.")
    exit(1)

year_2025 = year_2025.sort_values("Tarih")
print(f"✅ 2025 yılında {len(year_2025)} kayıt var")
print()

# 4. İlk ve son kayıtları göster
print("🔍 İLK ve SON Kayıtlar:")
print("-" * 80)
print("\nİLK KAYIT (YTD başlangıç noktası):")
first_record = year_2025.iloc[0]
print(f"  Tarih: {first_record['Tarih'].strftime('%Y-%m-%d')}")
print(f"  Değer (TRY): ₺{first_record['Değer_TRY']:,.2f}")
print(f"  Değer (USD): ${first_record.get('Değer_USD', 0):,.2f}")

print("\nSON KAYIT (bugün):")
last_record = year_2025.iloc[-1]
print(f"  Tarih: {last_record['Tarih'].strftime('%Y-%m-%d')}")
print(f"  Değer (TRY): ₺{last_record['Değer_TRY']:,.2f}")
print(f"  Değer (USD): ${last_record.get('Değer_USD', 0):,.2f}")
print()

# 5. YTD hesaplama
print("🧮 YTD Performans Hesaplama:")
print("-" * 80)
start_val = float(first_record["Değer_TRY"])
today_val = float(last_record["Değer_TRY"])
diff = today_val - start_val
pct = (diff / start_val * 100) if start_val > 0 else 0.0

print(f"Başlangıç Değeri: ₺{start_val:,.2f} ({first_record['Tarih'].strftime('%Y-%m-%d')})")
print(f"Güncel Değer: ₺{today_val:,.2f} ({last_record['Tarih'].strftime('%Y-%m-%d')})")
print(f"Fark: ₺{diff:,.2f}")
print(f"Yüzde: {pct:+.2f}%")
print()

# 6. SORUN TESPİTİ
print("🔴 SORUN TESPİTİ:")
print("-" * 80)

# İlk kayıt ocak ayında mı?
first_date = first_record['Tarih']
if first_date.month == 1 and first_date.day == 1:
    print("✅ İlk kayıt 1 Ocak'ta - YTD hesaplama doğru başlangıç noktasından yapılıyor")
elif first_date.month == 1 and first_date.day <= 3:
    print(f"⚠️  İlk kayıt {first_date.day} Ocak'ta - Kabul edilebilir")
else:
    print(f"❌ SORUN BULUNDU!")
    print(f"   İlk kayıt {first_date.strftime('%d %B %Y')} tarihinde.")
    print(f"   Bu, yıl başından beri değil, sadece {first_date.strftime('%d %B')} tarihinden beri olan değişim!")
    print()
    print("   🔍 Olası Nedenler:")
    print("   1. Tarihsel veri sadece birkaç gün önce kaydedilmeye başlandı")
    print("   2. Yıl başındaki veriler Google Sheets'ten silinmiş olabilir")
    print("   3. portfolio_history tablosu yeni oluşturuldu")
    print()
    print("   💡 Çözüm Önerileri:")
    print("   1. Ocak ayına ait verileri manuel olarak ekleyin")
    print("   2. YTD hesaplamasını devre dışı bırakın (yetersiz veri)")
    print("   3. Sadece mevcut veri aralığındaki performansı gösterin")

print()

# 7. Tüm kayıtları göster (küçük tablo)
print("📋 TÜM KAYITLAR (Son 10):")
print("-" * 80)
display_df = year_2025[["Tarih", "Değer_TRY", "Değer_USD"]].tail(10).copy()
display_df["Tarih"] = display_df["Tarih"].dt.strftime("%Y-%m-%d")
display_df["Değer_TRY"] = display_df["Değer_TRY"].apply(lambda x: f"₺{x:,.0f}")
display_df["Değer_USD"] = display_df["Değer_USD"].apply(lambda x: f"${x:,.0f}")
print(display_df.to_string(index=False))
print()

# 8. get_timeframe_changes ile karşılaştır
print("🔄 get_timeframe_changes() Fonksiyonu Çıktısı:")
print("-" * 80)
timeframe = get_timeframe_changes(history_df)
if timeframe:
    if timeframe["ytd"] is not None:
        ytd_val, ytd_pct = timeframe["ytd"]
        print(f"YTD Değer: ₺{ytd_val:,.2f}")
        print(f"YTD Yüzde: {ytd_pct:+.2f}%")
        print()
        print("✅ Fonksiyon YTD değeri döndürdü")
        
        # Manuel hesaplama ile karşılaştır
        if abs(ytd_val - diff) < 1 and abs(ytd_pct - pct) < 0.01:
            print("✅ Manuel hesaplama ile aynı sonucu veriyor")
        else:
            print("⚠️  Manuel hesaplama ile farklı sonuç!")
            print(f"   Fonksiyon: ₺{ytd_val:,.2f} ({ytd_pct:+.2f}%)")
            print(f"   Manuel: ₺{diff:,.2f} ({pct:+.2f}%)")
    else:
        print("⚠️  Fonksiyon YTD için None döndürdü (yetersiz veri)")
else:
    print("❌ Fonksiyon None döndürdü")

print()
print("=" * 80)
print("ÖZET")
print("=" * 80)
print()

if first_date.month > 1 or first_date.day > 5:
    print("🔴 YTD HESAPLAMA HATALI!")
    print()
    print(f"Gösterilen YTD performansı ({pct:+.2f}%) YANLIŞ çünkü:")
    print(f"- Başlangıç noktası {first_date.strftime('%d %B %Y')} (yıl başı DEĞİL)")
    print(f"- Bu sadece {(last_record['Tarih'] - first_date).days} günlük performans")
    print()
    print("Gerçek yıl başından beri performansı hesaplamak için:")
    print("1. 1 Ocak 2025 tarihindeki portföy değerini bulun")
    print("2. portfolio_history tablosuna manuel olarak ekleyin")
    print("3. Veya YTD metriğini devre dışı bırakın")
else:
    print("✅ YTD hesaplama doğru başlangıç noktasından yapılıyor")
    print(f"   (1 Ocak veya çok yakın: {first_date.strftime('%d %B %Y')})")

print()
print("=" * 80)
