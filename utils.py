import re
import pandas as pd
import streamlit as st

ANALYSIS_COLS = [
    "Kod",
    "Pazar",
    "Tip",
    "Adet",
    "Maliyet",
    "Fiyat",
    "PB",
    "Değer",
    "Top. Kâr/Zarar",
    "Top. %",
    "Gün. Kâr/Zarar",
    "Notlar",
]

KNOWN_FUNDS = [
    "YHB",
    "TTE",
    "MAC",
    "AFT",
    "AFA",
    "YAY",
    "IPJ",
    "TCD",
    "NNF",
    "GMR",
    "TI2",
    "TI3",
    "IHK",
    "IDH",
    "OJT",
    "HKH",
    "IPB",
    "KZL",
    "RPD",
]

MARKET_DATA = {
    "BIST (Tümü)": ["THYAO", "GARAN", "ASELS", "TRMET"],
    "ABD": ["AAPL", "TSLA"],
    "KRIPTO": ["BTC", "ETH"],
    "FON": KNOWN_FUNDS,
    "EMTIA": ["Gram Altın", "Gram Gümüş"],
    "VADELI": ["BTC", "ETH", "SOL"],
    "NAKIT": ["TL", "USD", "EUR"],
}


def get_yahoo_symbol(kod, pazar):
    kod = str(kod).upper()

    # Özel mapping
    if kod == "TRMET":
        return "KOZAA.IS"

    if pazar == "NAKIT":
        return kod
    if pazar == "FON":
        return kod

    if "BIST" in pazar:
        return f"{kod}.IS" if not kod.endswith(".IS") else kod
    elif "KRIPTO" in pazar:
        return f"{kod}-USD" if not kod.endswith("-USD") else kod
    elif "EMTIA" in pazar:
        map_emtia = {
            "Altın ONS": "GC=F",
            "Gümüş ONS": "SI=F",
            "Petrol": "BZ=F",
            "Doğalgaz": "NG=F",
            "Bakır": "HG=F",
        }
        for k, v in map_emtia.items():
            if k in kod:
                return v
        return kod

    return kod


def smart_parse(text_val):
    if text_val is None:
        return 0.0
    val = str(text_val).strip()
    if not val:
        return 0.0

    # Rakam dışı her şeyi sil (., hariç)
    val = re.sub(r"[^\d.,]", "", val)

    # Birden fazla nokta varsa ve virgül yoksa -> ilk nokta hariç hepsini kaldır
    if val.count(".") > 1 and "," not in val:
        parts = val.split(".")
        val = f"{parts[0]}.{''.join(parts[1:])}"

    # Hem nokta hem virgül varsa -> binlik ayırıcıları temizle, virgülü ondalık yap
    if "." in val and "," in val:
        val = val.replace(".", "").replace(",", ".")
    elif "," in val:
        val = val.replace(",", ".")

    try:
        return float(val)
    except Exception:
        return 0.0


def styled_dataframe(df: pd.DataFrame):
    """Placeholder – artık tablolarda render_table kullanıyoruz."""
    return df


def render_table(df: pd.DataFrame):
    """
    Tüm sekmelerde tablo gösterimi:
    - Yazılar büyük ve kalın
    - Kâr/Zarar kolonları: pozitif yeşil, negatif kırmızı
    """
    if df.empty:
        st.info("Veri yok.")
        return

    # Gösterim için kopya
    display_df = df.copy()

    # Sayısal kolonları formatla
    num_cols = [
        col for col in display_df.columns
        if pd.api.types.is_numeric_dtype(display_df[col])
    ]
    for col in num_cols:
        display_df[col] = display_df[col].apply(
            lambda x: "" if pd.isna(x) else f"{x:,.2f}"
        )

    cols = list(display_df.columns)

    html = '<table class="custom-table"><thead><tr>'
    for c in cols:
        html += f"<th>{c}</th>"
    html += "</tr></thead><tbody>"

    for idx, row in display_df.iterrows():
        html += "<tr>"
        for c in cols:
            val = row[c]
            raw = df.loc[idx, c] if c in df.columns else None
            style = ""

            if c in ["Top. Kâr/Zarar", "Top. %", "Gün. Kâr/Zarar", "Kâr/Zarar"]:
                try:
                    v = float(raw)
                    if v > 0:
                        style = ' style="color:#00e676; font-weight:bold;"'
                    elif v < 0:
                        style = ' style="color:#ff5252; font-weight:bold;"'
                    else:
                        style = ' style="color:#cccccc; font-weight:bold;"'
                except Exception:
                    style = ' style="color:#cccccc; font-weight:bold;"'
            else:
                style = ' style="color:#ffffff; font-weight:600;"'

            html += f"<td{style}>{val}</td>"
        html += "</tr>"

    html += "</tbody></table>"

    st.markdown(html, unsafe_allow_html=True)
