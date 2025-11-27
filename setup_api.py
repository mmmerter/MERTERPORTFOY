#!/usr/bin/env python3
"""
Binance Futures API Kurulum Scripti
===================================
Bu script API anahtarlarınızı güvenli şekilde kaydeder
"""

import os
from pathlib import Path

def main():
    print("=" * 70)
    print("🔐 BINANCE FUTURES API KURULUM")
    print("=" * 70)
    
    print("\n📋 Kurulum Adımları:")
    print("1. Binance'te API anahtarı oluşturun")
    print("2. ⚠️  'Enable Reading' ve 'Enable Futures' izinlerini VERİN")
    print("3. ❌ 'Enable Withdrawals' iznini VERMEYİN (güvenlik!)")
    print("4. API key ve secret'i aşağıya girin\n")
    
    # API bilgilerini al
    print("─" * 70)
    api_key = input("Binance API Key girin: ").strip()
    
    if not api_key:
        print("\n❌ API key boş olamaz!")
        return False
    
    api_secret = input("Binance API Secret girin: ").strip()
    
    if not api_secret:
        print("\n❌ API secret boş olamaz!")
        return False
    
    # Testnet kullanılsın mı
    testnet_input = input("Testnet kullanılsın mı? (evet/hayır, varsayılan: hayır): ").strip().lower()
    testnet = testnet_input in ['evet', 'e', 'yes', 'y']
    
    print("\n" + "─" * 70)
    print("📝 GİRİLEN BİLGİLER:")
    print(f"   API Key: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else ''}")
    print(f"   API Secret: {api_secret[:5]}...{api_secret[-5:] if len(api_secret) > 10 else ''}")
    print(f"   Testnet: {'Evet' if testnet else 'Hayır'}")
    
    confirm = input("\nBu bilgiler doğru mu? (evet/hayır): ").strip().lower()
    
    if confirm not in ['evet', 'e', 'yes', 'y']:
        print("\n❌ Kurulum iptal edildi")
        return False
    
    # .streamlit klasörünü oluştur
    streamlit_dir = Path(".streamlit")
    streamlit_dir.mkdir(exist_ok=True)
    
    # secrets.toml dosyasını oluştur
    secrets_file = streamlit_dir / "secrets.toml"
    
    secrets_content = f"""# Binance Futures API Ayarları
# =================================
# Bu dosya otomatik olarak oluşturuldu
# Oluşturma tarihi: {Path(__file__).stat().st_mtime}

[binance_futures]
api_key = "{api_key}"
api_secret = "{api_secret}"
testnet = {str(testnet).lower()}


# Google Sheets API Ayarları (opsiyonel)
# ========================================
# Google Sheets entegrasyonu için gerekli
# Şimdilik boş bırakabilirsiniz

[gcp_service_account]
# type = "service_account"
# project_id = "your-project-id"
# private_key_id = "..."
# private_key = "..."
# client_email = "..."
# client_id = "..."
"""
    
    try:
        with open(secrets_file, 'w') as f:
            f.write(secrets_content)
        
        print("\n✅ secrets.toml dosyası oluşturuldu!")
        print(f"   Konum: {secrets_file.absolute()}")
        
    except Exception as e:
        print(f"\n❌ HATA: Dosya oluşturulamadı: {str(e)}")
        return False
    
    # Test önerisi
    print("\n" + "=" * 70)
    print("🧪 SONRAKİ ADIM: Bağlantıyı test edin")
    print("=" * 70)
    print("\nTerminal'de şu komutu çalıştırın:")
    print("\n   python3 test_binance_connection.py")
    print("\nBu komut API bağlantınızı test edecek ve:")
    print("  ✓ Hesap bakiyenizi gösterecek")
    print("  ✓ Açık pozisyonlarınızı listeleyecek")
    print("  ✓ Son 7 gün PnL özetini verecek")
    
    print("\n" + "=" * 70)
    print("✅ KURULUM TAMAMLANDI!")
    print("=" * 70)
    
    print("\n📚 Yardım için:")
    print("   • BINANCE_API_KURULUM.md - Detaylı kurulum rehberi")
    print("   • README_BINANCE_FUTURES.md - Genel bilgiler")
    print("\n🚀 Dashboard'u başlatmak için:")
    print("   streamlit run portfoy.py")
    
    print("\n" + "=" * 70)
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Kurulum iptal edildi")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Beklenmeyen hata: {str(e)}")
        exit(1)
