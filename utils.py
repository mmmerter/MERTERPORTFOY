import re
import pandas as pd

def smart_parse(text_val):
    """Gelen metni (1.000,50 veya 1,000.50) float sayıya çevirir."""
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
    """Dataframe sayı formatlarını düzenler."""
    if df.empty:
        return df

    format_dict = {}
    for col in df.columns:
        if df[col].dtype in ["float64", "float32", "int64", "int32"]:
            format_dict[col] = "{:,.2f}"

    try:
        return df.style.format(format_dict)
    except Exception:
        return df
