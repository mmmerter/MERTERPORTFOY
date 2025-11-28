"""
Günlük K/Z Sorununu Teşhis Et ve Düzelt
======================================

Bu script:
1. Bugünün baz fiyatlarını kontrol eder
2. Günlük K/Z hesaplamasını adım adım gösterir
3. Sorunlu varlıkları tespit eder
4. Baz fiyatları düzeltme seçeneği sunar
"""

import sys
import pandas as pd
from datetime import datetime
import pytz

# Streamlit'siz çalışması için mock ekliyoruz
class MockStreamlit:
    class session_state:
        _data = {}
        def get(self, key, default=None):
            return self._data.get(key, default)
        def __setitem__(self, key, value):
            self._data[key] = value
    
    class secrets:
        pass
    
    def warning(self, msg):
        print(f"⚠️  {msg}")
    
    def error(self, msg):
        print(f"❌ {msg}")
    
    def info(self, msg):
        print(f"ℹ️  {msg}")
    
    def success(self, msg):
        print(f"✅ {msg}")

# Mock streamlit import
sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

# Şimdi gerçek modülleri import et
from data_loader import (
    get_data_from_sheet,
    get_usd_try,
    get_daily_base_prices,
    _get_daily_base_sheet,
    should_update_daily_base,
)
from utils import smart_parse

def diagnose_daily_kz():
    """Günlük K/Z sorununu teşhis eder."""
    
    print("\n" + "="*70)
    print("🔍 GÜNLÜK K/Z TEŞHİS ARACI")
    print("="*70)
    
    # Türkiye saati
    turkey_tz = pytz.timezone('Europe/Istanbul')
    now_turkey = datetime.now(turkey_tz)
    print(f"\n⏰ Türkiye Saati: {now_turkey.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Portföy verisini çek
    print("\n📊 Portföy verisi çekiliyor...")
    portfoy_df = get_data_from_sheet()
    
    if portfoy_df.empty:
        print("❌ Portföy verisi bulunamadı!")
        return
    
    spot_only = portfoy_df[portfoy_df["Tip"] == "Portfoy"].copy()
    print(f"✅ {len(spot_only)} varlık bulundu")
    
    # 2. USD/TRY kurunu al
    usd_try = get_usd_try()
    print(f"💱 USD/TRY Kuru: {usd_try:.4f}")
    
    # 3. Bugünün baz fiyatlarını çek
    print("\n📋 Bugünün baz fiyatları kontrol ediliyor...")
    daily_base_prices = get_daily_base_prices()
    
    if daily_base_prices.empty:
        print("⚠️  Bugün için baz fiyat kaydı yok!")
        print("    Bu durumda günlük K/Z önceki günün kapanış fiyatına göre hesaplanır.")
        return
    
    print(f"✅ {len(daily_base_prices)} varlık için baz fiyat bulundu")
    print(f"\nBaz Fiyat Kayıt Zamanı: 00:30 (otomatik reset)")
    
    # 4. Baz fiyatları göster
    print("\n" + "-"*70)
    print("BAZ FİYATLAR (00:30'da kaydedilen)")
    print("-"*70)
    for _, row in daily_base_prices.iterrows():
        kod = row["Kod"]
        fiyat = float(row["Fiyat"])
        pb = row.get("PB", "TRY")
        print(f"{kod:15s} | Baz Fiyat: {fiyat:12,.4f} {pb}")
    
    # 5. Her varlık için detaylı analiz
    print("\n" + "="*70)
    print("GÜNLÜK K/Z HESAPLAMA ANALİZİ")
    print("="*70)
    
    total_daily_kz = 0
    problem_assets = []
    
    for _, row in spot_only.iterrows():
        kod = row["Kod"]
        adet = smart_parse(row.get("Adet", 0))
        maliyet = smart_parse(row.get("Maliyet", 0))
        fiyat = smart_parse(row.get("Fiyat", 0))
        deger = smart_parse(row.get("Değer", 0))
        gunluk_kz_old = smart_parse(row.get("Gün. Kâr/Zarar", 0))
        
        # Varlığın para birimi
        pazar = str(row.get("Pazar", "")).upper()
        if "BIST" in pazar or "FON" in pazar or "EMTIA" in pazar or "NAKIT" in pazar:
            pb = "TRY"
        else:
            pb = "USD"
        
        # Baz fiyatı bul
        base_row = daily_base_prices[daily_base_prices["Kod"] == kod]
        
        if base_row.empty:
            # Baz fiyat yoksa eski yöntemi kullan
            print(f"\n{kod}:")
            print(f"  ⚠️  Baz fiyat bulunamadı, eski yöntem kullanılıyor")
            print(f"  Günlük K/Z (eski): {gunluk_kz_old:,.2f} TRY")
            total_daily_kz += gunluk_kz_old
            continue
        
        base_price = float(base_row.iloc[0]["Fiyat"])
        base_pb = base_row.iloc[0].get("PB", "TRY")
        
        # Mevcut değer (TRY bazında)
        if pb == "USD":
            current_value_try = fiyat * adet * usd_try
        else:
            current_value_try = fiyat * adet
        
        # Baz değer (TRY bazında)
        if base_pb == "USD":
            base_value_try = base_price * adet * usd_try
        else:
            base_value_try = base_price * adet
        
        # Günlük K/Z (00:30 bazında)
        daily_kz = current_value_try - base_value_try
        daily_pct = ((current_value_try - base_value_try) / base_value_try * 100) if base_value_try > 0 else 0
        
        # Fiyat değişimi
        price_change_pct = ((fiyat - base_price) / base_price * 100) if base_price > 0 else 0
        
        print(f"\n{kod}:")
        print(f"  Adet: {adet:,.2f}")
        print(f"  Para Birimi: {pb}")
        print(f"  Baz Fiyat (00:30): {base_price:,.4f} {base_pb}")
        print(f"  Güncel Fiyat: {fiyat:,.4f} {pb}")
        print(f"  Fiyat Değişimi: {price_change_pct:+.2f}%")
        print(f"  Baz Değer: {base_value_try:,.2f} TRY")
        print(f"  Güncel Değer: {current_value_try:,.2f} TRY")
        print(f"  Günlük K/Z: {daily_kz:+,.2f} TRY ({daily_pct:+.2f}%)")
        
        total_daily_kz += daily_kz
        
        # Anormal değişimleri tespit et (10%'den fazla düşüş/artış)
        if abs(daily_pct) > 10:
            problem_assets.append({
                "Kod": kod,
                "Günlük K/Z": daily_kz,
                "Günlük %": daily_pct,
                "Baz Fiyat": base_price,
                "Güncel Fiyat": fiyat,
            })
            print(f"  ⚠️  ANORMAL DEĞİŞİM TESPİT EDİLDİ!")
    
    # 6. Özet
    print("\n" + "="*70)
    print("ÖZET")
    print("="*70)
    print(f"Toplam Günlük K/Z: {total_daily_kz:+,.2f} TRY")
    
    if problem_assets:
        print(f"\n⚠️  {len(problem_assets)} varlıkta anormal değişim tespit edildi:")
        for asset in problem_assets:
            print(f"  - {asset['Kod']}: {asset['Günlük K/Z']:+,.2f} TRY ({asset['Günlük %']:+.2f}%)")
    else:
        print("\n✅ Anormal değişim tespit edilmedi")
    
    # 7. Sorun tespiti ve çözüm önerileri
    print("\n" + "="*70)
    print("TEŞHİS VE ÇÖZÜMLer")
    print("="*70)
    
    if total_daily_kz < -50000:
        print("\n❌ BÜYÜK ZARAR TESPİT EDİLDİ (-50,000 TRY'den fazla)")
        print("\nOlası Nedenler:")
        print("1. Baz fiyatlar yanlış zamanda/yanlış değerlerle kaydedilmiş")
        print("2. Piyasa gerçekten büyük düşüş yaşamış")
        print("3. Para birimi dönüşümlerinde hata var")
        
        print("\n🔧 ÇÖZÜMLer:")
        print("\nSeçenek 1: Baz Fiyatları Sıfırla (Önerilen)")
        print("  → Bugünün baz fiyatlarını sil ve yeniden kaydet")
        print("  → Komut: python3 fix_gunluk_kz.py --reset-base-prices")
        
        print("\nSeçenek 2: Manuel İnceleme")
        print("  → Google Sheets'te 'daily_base_prices' sayfasını aç")
        print("  → Bugünün tarihine ait kayıtları kontrol et")
        print(f"  → Tarih: {now_turkey.strftime('%Y-%m-%d')}")
        
        print("\nSeçenek 3: Baz Fiyat Sisteminidevre Dışı Bırak")
        print("  → Eski yönteme geri dön (önceki günün kapanış fiyatı)")
        print("  → daily_base_prices sheet'ini kaldır veya boşalt")
    
    return problem_assets, total_daily_kz

def reset_base_prices():
    """Bugünün baz fiyatlarını siler."""
    
    print("\n" + "="*70)
    print("🔄 BAZ FİYATLARI SIFIRLAMA")
    print("="*70)
    
    turkey_tz = pytz.timezone('Europe/Istanbul')
    now_turkey = datetime.now(turkey_tz)
    today_str = now_turkey.strftime("%Y-%m-%d")
    
    print(f"\n⚠️  Bugünün ({today_str}) baz fiyatları silinecek!")
    print("    Uygulama bir sonraki çalıştırmada yeni baz fiyatları kaydedecek.")
    
    response = input("\nDevam etmek istiyor musunuz? (evet/hayir): ")
    
    if response.lower() not in ["evet", "e", "yes", "y"]:
        print("❌ İşlem iptal edildi.")
        return
    
    try:
        sheet = _get_daily_base_sheet()
        if sheet is None:
            print("❌ Baz fiyat sheet'ine erişilemedi!")
            return
        
        # Tüm kayıtları al
        data = sheet.get_all_records()
        
        if not data:
            print("ℹ️  Zaten hiç kayıt yok.")
            return
        
        # Bugüne ait kayıtları bul ve sil
        rows_to_delete = []
        for i, row in enumerate(data, start=2):  # 2'den başla (header 1. satır)
            if str(row.get("Tarih", "")) == today_str:
                rows_to_delete.append(i)
        
        if not rows_to_delete:
            print(f"ℹ️  Bugün ({today_str}) için kayıt bulunamadı.")
            return
        
        print(f"\n🗑️  {len(rows_to_delete)} satır silinecek...")
        
        # Satırları geriden başlayarak sil (index karışmaması için)
        for row_idx in sorted(rows_to_delete, reverse=True):
            sheet.delete_rows(row_idx)
        
        print(f"✅ Bugünün baz fiyatları başarıyla silindi!")
        print("\n💡 Şimdi yapmanız gerekenler:")
        print("   1. Uygulamayı yeniden başlatın")
        print("   2. Uygulama otomatik olarak yeni baz fiyatları kaydedecek")
        print("   3. Günlük K/Z değerleri sıfırdan başlayacak")
        
        # Cache'i temizle
        try:
            get_daily_base_prices.clear()
            print("   4. Cache temizlendi ✓")
        except:
            pass
    
    except Exception as e:
        print(f"❌ Hata oluştu: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset-base-prices":
        reset_base_prices()
    else:
        problem_assets, total_daily_kz = diagnose_daily_kz()
        
        # Eğer büyük zarar varsa, reset seçeneği sun
        if total_daily_kz < -50000:
            print("\n" + "="*70)
            response = input("\nBaz fiyatları sıfırlamak ister misiniz? (evet/hayir): ")
            if response.lower() in ["evet", "e", "yes", "y"]:
                reset_base_prices()
