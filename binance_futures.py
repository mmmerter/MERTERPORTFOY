"""
Binance Futures API Entegrasyon Modülü
======================================
Bu modül Binance Futures hesabınızdan tüm verileri çeker:
- Açık pozisyonlar ve PnL
- Hesap bakiyesi ve marjin bilgileri
- İşlem geçmişi
- Gerçekleşmemiş ve gerçekleşmiş kar/zarar
- Pozisyon riski ve leverage bilgileri
"""

import ccxt
import pandas as pd
from datetime import datetime, timedelta
import time
from typing import Dict, List, Tuple, Optional
import streamlit as st


class BinanceFuturesAPI:
    """Binance Futures API ile etkileşim için ana sınıf"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Binance Futures API bağlantısı başlat
        
        Args:
            api_key: Binance API anahtarı
            api_secret: Binance API secret
            testnet: Test ağı kullanılacak mı (varsayılan: False)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        # CCXT exchange nesnesi
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
                'adjustForTimeDifference': True
            }
        })
        
        if testnet:
            self.exchange.set_sandbox_mode(True)
    
    def get_account_balance(self) -> Dict:
        """
        Hesap bakiyesi ve marjin bilgilerini çeker
        
        Returns:
            dict: Bakiye bilgileri
                - total_wallet_balance: Toplam cüzdan bakiyesi (USDT)
                - total_unrealized_pnl: Gerçekleşmemiş toplam kar/zarar
                - total_margin_balance: Toplam marjin bakiyesi
                - available_balance: Kullanılabilir bakiye
                - assets: Detaylı varlık bilgileri
        """
        try:
            balance = self.exchange.fetch_balance()
            
            result = {
                'total_wallet_balance': 0.0,
                'total_unrealized_pnl': 0.0,
                'total_margin_balance': 0.0,
                'available_balance': 0.0,
                'assets': []
            }
            
            # USDT bazlı bilgileri al
            if 'USDT' in balance['total']:
                result['total_wallet_balance'] = float(balance['total'].get('USDT', 0))
                result['available_balance'] = float(balance['free'].get('USDT', 0))
            
            # Detaylı bakiye bilgisi
            if 'info' in balance and 'assets' in balance['info']:
                for asset in balance['info']['assets']:
                    if float(asset['walletBalance']) > 0:
                        result['assets'].append({
                            'asset': asset['asset'],
                            'wallet_balance': float(asset['walletBalance']),
                            'unrealized_profit': float(asset['unrealizedProfit']),
                            'margin_balance': float(asset['marginBalance']),
                            'available_balance': float(asset['availableBalance'])
                        })
                        
                        if asset['asset'] == 'USDT':
                            result['total_unrealized_pnl'] = float(asset['unrealizedProfit'])
                            result['total_margin_balance'] = float(asset['marginBalance'])
            
            return result
            
        except Exception as e:
            raise Exception(f"Bakiye bilgisi alınamadı: {str(e)}")
    
    def get_open_positions(self) -> pd.DataFrame:
        """
        Açık pozisyonları çeker
        
        Returns:
            DataFrame: Açık pozisyon bilgileri
                Kolonlar: symbol, side, size, entry_price, mark_price, 
                         unrealized_pnl, unrealized_pnl_percent, leverage, 
                         liquidation_price, margin_type, notional
        """
        try:
            positions = self.exchange.fetch_positions()
            
            open_positions = []
            for pos in positions:
                # Sadece açık pozisyonları al (contracts != 0)
                contracts = float(pos.get('contracts', 0))
                if contracts == 0:
                    continue
                
                info = pos.get('info', {})
                
                # Pozisyon yönü
                side = 'LONG' if contracts > 0 else 'SHORT'
                
                # Fiyat bilgileri
                entry_price = float(pos.get('entryPrice', 0))
                mark_price = float(pos.get('markPrice', 0))
                liquidation_price = float(pos.get('liquidationPrice', 0))
                
                # PnL hesaplama
                unrealized_pnl = float(pos.get('unrealizedPnl', 0))
                notional = float(pos.get('notional', 0))
                
                # PnL yüzdesi
                if notional != 0:
                    unrealized_pnl_percent = (unrealized_pnl / abs(notional)) * 100
                else:
                    unrealized_pnl_percent = 0.0
                
                # Leverage
                leverage = int(pos.get('leverage', 1))
                
                # Marjin tipi
                margin_type = info.get('marginType', 'cross').upper()
                
                open_positions.append({
                    'symbol': pos['symbol'],
                    'side': side,
                    'size': abs(contracts),
                    'entry_price': entry_price,
                    'mark_price': mark_price,
                    'unrealized_pnl': unrealized_pnl,
                    'unrealized_pnl_percent': unrealized_pnl_percent,
                    'leverage': leverage,
                    'liquidation_price': liquidation_price,
                    'margin_type': margin_type,
                    'notional': abs(notional),
                    'timestamp': datetime.now()
                })
            
            df = pd.DataFrame(open_positions)
            
            if not df.empty:
                # Sıralama: En yüksek notional önce
                df = df.sort_values('notional', ascending=False)
            
            return df
            
        except Exception as e:
            raise Exception(f"Pozisyonlar alınamadı: {str(e)}")
    
    def get_position_history(self, symbol: Optional[str] = None, 
                           days: int = 7) -> pd.DataFrame:
        """
        Pozisyon geçmişini çeker (kapatılmış işlemler)
        
        Args:
            symbol: Spesifik sembol (None ise tümü)
            days: Kaç gün geriye gidilecek
        
        Returns:
            DataFrame: İşlem geçmişi
        """
        try:
            since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            trades = []
            if symbol:
                # Tek sembol için
                symbol_trades = self.exchange.fetch_my_trades(symbol, since=since)
                trades.extend(symbol_trades)
            else:
                # Tüm açık pozisyonlar için işlem geçmişi
                positions = self.get_open_positions()
                for sym in positions['symbol'].unique():
                    try:
                        symbol_trades = self.exchange.fetch_my_trades(sym, since=since)
                        trades.extend(symbol_trades)
                        time.sleep(0.1)  # Rate limit
                    except:
                        continue
            
            if not trades:
                return pd.DataFrame()
            
            # DataFrame'e dönüştür
            trade_data = []
            for trade in trades:
                trade_data.append({
                    'timestamp': datetime.fromtimestamp(trade['timestamp'] / 1000),
                    'symbol': trade['symbol'],
                    'side': trade['side'].upper(),
                    'price': float(trade['price']),
                    'amount': float(trade['amount']),
                    'cost': float(trade['cost']),
                    'fee': float(trade['fee']['cost']) if trade.get('fee') else 0,
                    'fee_currency': trade['fee']['currency'] if trade.get('fee') else '',
                    'realized_pnl': float(trade['info'].get('realizedPnl', 0))
                })
            
            df = pd.DataFrame(trade_data)
            df = df.sort_values('timestamp', ascending=False)
            
            return df
            
        except Exception as e:
            raise Exception(f"İşlem geçmişi alınamadı: {str(e)}")
    
    def get_income_history(self, income_type: Optional[str] = None, 
                          days: int = 30) -> pd.DataFrame:
        """
        Gelir geçmişini çeker (realized PnL, funding fees, vb.)
        
        Args:
            income_type: Gelir tipi (REALIZED_PNL, FUNDING_FEE, COMMISSION, vb.)
            days: Kaç gün geriye gidilecek
        
        Returns:
            DataFrame: Gelir geçmişi
        """
        try:
            since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            # Binance-specific API call
            params = {
                'startTime': since,
            }
            
            if income_type:
                params['incomeType'] = income_type
            
            # fetch_income is a binance-specific method
            income_data = self.exchange.fapiPrivateGetIncome(params)
            
            if not income_data:
                return pd.DataFrame()
            
            # DataFrame'e dönüştür
            income_records = []
            for record in income_data:
                income_records.append({
                    'timestamp': datetime.fromtimestamp(int(record['time']) / 1000),
                    'symbol': record['symbol'],
                    'income_type': record['incomeType'],
                    'income': float(record['income']),
                    'asset': record['asset'],
                    'info': record.get('info', '')
                })
            
            df = pd.DataFrame(income_records)
            df = df.sort_values('timestamp', ascending=False)
            
            return df
            
        except Exception as e:
            raise Exception(f"Gelir geçmişi alınamadı: {str(e)}")
    
    def get_daily_pnl_summary(self, days: int = 30) -> pd.DataFrame:
        """
        Günlük PnL özetini çeker
        
        Args:
            days: Kaç gün geriye gidilecek
        
        Returns:
            DataFrame: Günlük PnL özeti
        """
        try:
            # Realized PnL gelirlerini al
            income_df = self.get_income_history(income_type='REALIZED_PNL', days=days)
            
            if income_df.empty:
                return pd.DataFrame()
            
            # Günlük grupla
            income_df['date'] = income_df['timestamp'].dt.date
            
            daily_summary = income_df.groupby('date').agg({
                'income': 'sum'
            }).reset_index()
            
            daily_summary.columns = ['date', 'realized_pnl']
            daily_summary = daily_summary.sort_values('date', ascending=False)
            
            # Kümülatif PnL
            daily_summary['cumulative_pnl'] = daily_summary['realized_pnl'][::-1].cumsum()[::-1]
            
            return daily_summary
            
        except Exception as e:
            raise Exception(f"Günlük PnL özeti alınamadı: {str(e)}")
    
    def get_funding_fees(self, days: int = 30) -> pd.DataFrame:
        """
        Funding fee geçmişini çeker
        
        Args:
            days: Kaç gün geriye gidilecek
        
        Returns:
            DataFrame: Funding fee geçmişi
        """
        try:
            return self.get_income_history(income_type='FUNDING_FEE', days=days)
        except Exception as e:
            raise Exception(f"Funding fee geçmişi alınamadı: {str(e)}")
    
    def get_account_summary(self) -> Dict:
        """
        Hesap özet bilgilerini çeker (dashboard için)
        
        Returns:
            dict: Özet bilgiler
        """
        try:
            balance = self.get_account_balance()
            positions = self.get_open_positions()
            
            # Toplam PnL hesaplamaları
            total_unrealized_pnl = balance['total_unrealized_pnl']
            
            # Son 24 saat realized PnL
            daily_pnl = self.get_daily_pnl_summary(days=1)
            realized_pnl_24h = daily_pnl['realized_pnl'].sum() if not daily_pnl.empty else 0.0
            
            # Son 7 gün realized PnL
            weekly_pnl = self.get_daily_pnl_summary(days=7)
            realized_pnl_7d = weekly_pnl['realized_pnl'].sum() if not weekly_pnl.empty else 0.0
            
            # Son 30 gün realized PnL
            monthly_pnl = self.get_daily_pnl_summary(days=30)
            realized_pnl_30d = monthly_pnl['realized_pnl'].sum() if not monthly_pnl.empty else 0.0
            
            # Pozisyon sayıları
            num_positions = len(positions)
            num_long = len(positions[positions['side'] == 'LONG']) if not positions.empty else 0
            num_short = len(positions[positions['side'] == 'SHORT']) if not positions.empty else 0
            
            # Risk metrikleri
            total_notional = positions['notional'].sum() if not positions.empty else 0.0
            
            return {
                'wallet_balance': balance['total_wallet_balance'],
                'margin_balance': balance['total_margin_balance'],
                'available_balance': balance['available_balance'],
                'unrealized_pnl': total_unrealized_pnl,
                'realized_pnl_24h': realized_pnl_24h,
                'realized_pnl_7d': realized_pnl_7d,
                'realized_pnl_30d': realized_pnl_30d,
                'total_pnl_24h': total_unrealized_pnl + realized_pnl_24h,
                'num_positions': num_positions,
                'num_long': num_long,
                'num_short': num_short,
                'total_notional': total_notional,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            raise Exception(f"Hesap özeti alınamadı: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        API bağlantısını test eder
        
        Returns:
            bool: Bağlantı başarılı mı
        """
        try:
            self.exchange.fetch_balance()
            return True
        except Exception as e:
            print(f"Bağlantı testi başarısız: {str(e)}")
            return False


# ==========================================================
#   Google Sheets Entegrasyonu
# ==========================================================

def save_positions_to_sheet(positions_df: pd.DataFrame, client):
    """
    Pozisyonları Google Sheets'e kaydeder
    
    Args:
        positions_df: Pozisyon DataFrame'i
        client: gspread client
    """
    try:
        from datetime import datetime
        
        sheet_name = "PortfoyData"
        spreadsheet = client.open(sheet_name)
        
        # futures_positions sheet'ini al veya oluştur
        try:
            worksheet = spreadsheet.worksheet("futures_positions")
        except:
            worksheet = spreadsheet.add_worksheet(
                title="futures_positions",
                rows=1000,
                cols=20
            )
        
        # Header
        headers = ['Timestamp', 'Symbol', 'Side', 'Size', 'Entry Price', 
                  'Mark Price', 'Unrealized PnL', 'Unrealized PnL %', 
                  'Leverage', 'Liquidation Price', 'Margin Type', 'Notional']
        
        # Veriyi hazırla
        data = [headers]
        for _, row in positions_df.iterrows():
            data.append([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                row['symbol'],
                row['side'],
                row['size'],
                row['entry_price'],
                row['mark_price'],
                row['unrealized_pnl'],
                row['unrealized_pnl_percent'],
                row['leverage'],
                row['liquidation_price'],
                row['margin_type'],
                row['notional']
            ])
        
        # Güncelle
        worksheet.clear()
        worksheet.update('A1', data)
        
    except Exception as e:
        print(f"Pozisyonlar kaydedilemedi: {str(e)}")


def save_daily_summary_to_sheet(summary: Dict, client):
    """
    Günlük özeti Google Sheets'e kaydeder
    
    Args:
        summary: Özet bilgileri
        client: gspread client
    """
    try:
        from datetime import datetime
        
        sheet_name = "PortfoyData"
        spreadsheet = client.open(sheet_name)
        
        # futures_daily_summary sheet'ini al veya oluştur
        try:
            worksheet = spreadsheet.worksheet("futures_daily_summary")
        except:
            worksheet = spreadsheet.add_worksheet(
                title="futures_daily_summary",
                rows=5000,
                cols=15
            )
            # Header ekle
            headers = ['Timestamp', 'Wallet Balance', 'Margin Balance', 
                      'Available Balance', 'Unrealized PnL', 'Realized PnL 24h',
                      'Realized PnL 7d', 'Realized PnL 30d', 'Total PnL 24h',
                      'Num Positions', 'Num Long', 'Num Short', 'Total Notional']
            worksheet.update('A1', [headers])
        
        # Bugünün kaydını kontrol et
        today_str = datetime.now().strftime('%Y-%m-%d')
        records = worksheet.get_all_records()
        
        # Bugün için kayıt varsa güncelleme
        existing_row = None
        for idx, record in enumerate(records):
            if record.get('Timestamp', '')[:10] == today_str:
                existing_row = idx + 2  # +2 because of header and 0-indexing
                break
        
        # Yeni satır
        new_row = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            summary['wallet_balance'],
            summary['margin_balance'],
            summary['available_balance'],
            summary['unrealized_pnl'],
            summary['realized_pnl_24h'],
            summary['realized_pnl_7d'],
            summary['realized_pnl_30d'],
            summary['total_pnl_24h'],
            summary['num_positions'],
            summary['num_long'],
            summary['num_short'],
            summary['total_notional']
        ]
        
        if existing_row:
            # Güncelle
            worksheet.update(f'A{existing_row}', [new_row])
        else:
            # Yeni ekle
            worksheet.append_row(new_row)
        
    except Exception as e:
        print(f"Günlük özet kaydedilemedi: {str(e)}")


# ==========================================================
#   Streamlit Cache Fonksiyonları
# ==========================================================

@st.cache_resource
def get_futures_api(api_key: str, api_secret: str, testnet: bool = False):
    """
    Binance Futures API nesnesini cache'leyerek döndürür
    
    Args:
        api_key: API key
        api_secret: API secret
        testnet: Testnet kullan mı
    
    Returns:
        BinanceFuturesAPI instance
    """
    return BinanceFuturesAPI(api_key, api_secret, testnet)


@st.cache_data(ttl=30)
def get_cached_positions(_api: BinanceFuturesAPI) -> pd.DataFrame:
    """
    Pozisyonları cache'leyerek döndürür (30 saniye)
    """
    return _api.get_open_positions()


@st.cache_data(ttl=60)
def get_cached_summary(_api: BinanceFuturesAPI) -> Dict:
    """
    Hesap özetini cache'leyerek döndürür (60 saniye)
    """
    return _api.get_account_summary()


@st.cache_data(ttl=300)
def get_cached_daily_pnl(_api: BinanceFuturesAPI, days: int = 30) -> pd.DataFrame:
    """
    Günlük PnL özetini cache'leyerek döndürür (5 dakika)
    """
    return _api.get_daily_pnl_summary(days)


@st.cache_data(ttl=300)
def get_cached_income_history(_api: BinanceFuturesAPI, days: int = 30) -> pd.DataFrame:
    """
    Gelir geçmişini cache'leyerek döndürür (5 dakika)
    """
    return _api.get_income_history(days=days)
