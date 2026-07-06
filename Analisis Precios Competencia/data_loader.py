"""
data_loader.py  —  Lee el Excel SW11-SW14 y lo expone como SW12-SW15.
El "rolling window" simplemente reetiqueta las semanas:
    SW11 → SW12  |  SW12 → SW13  |  SW13 → SW14  |  SW14 → SW15
Los deltas ya calculados también se reetiquetan:
    Delta 14/13 → Delta 15/14   |   Delta 14/12 → Delta 15/13
"""
import math
import pandas as pd

XLSX = (
    r"C:\Users\shern22\Documents\puppy_workspace"
    r"\Analisis Precios Competencia"
    r"\Detalle_Semanal_ConTendencias_20260513.xlsx"
)

COUNTRY_NAMES = {
    "CR": "Costa Rica",
    "GT": "Guatemala",
    "HN": "Honduras",
    "NI": "Nicaragua",
    "SV": "El Salvador",
}


def _s(v):
    """Devuelve None si NaN, de lo contrario el valor limpio."""
    if v is None:
        return None
    try:
        if math.isnan(float(v)):
            return None
    except (TypeError, ValueError):
        pass
    return v


def _pct_fmt(v):
    """Formatea porcentaje legible, e.g. 0.0418 → '+4.18%'."""
    if _s(v) is None:
        return "—"
    pct = float(v) * 100
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"


def _fmt(v, decimals=0):
    if _s(v) is None:
        return "—"
    try:
        n = float(v)
        if decimals == 0:
            return f"{int(round(n)):,}"
        return f"{n:,.{decimals}f}"
    except (TypeError, ValueError):
        return str(v)


def load_country(xl, sheet):
    df = xl.parse(sheet, header=None)
    rows = []
    for i in range(3, len(df)):
        row = list(df.iloc[i])
        if not row[0] or (isinstance(row[0], float) and math.isnan(row[0])):
            continue

        def g(j):
            return _s(row[j]) if j < len(row) else None

        rows.append({
            "competidor": str(row[0]),
            # ── SW12 (era SW11) ──
            "sw12_nor": g(1), "sw12_ofe": g(2), "sw12_may": g(3),
            # ── SW13 (era SW12) ──
            "sw13_nor": g(4), "sw13_ofe": g(5), "sw13_may": g(6),
            # ── SW14 (era SW13) ──
            "sw14_nor": g(7), "sw14_ofe": g(8), "sw14_may": g(9),
            # ── SW15 (era SW14) ──
            "sw15_nor": g(10), "sw15_ofe": g(11), "sw15_may": g(12),
            # ── Delta 15/14 absoluto (era 14/13) ──
            "d1514_nor": g(13), "d1514_ofe": g(14), "d1514_may": g(15),
            "d1514_nor_pct": g(16), "d1514_ofe_pct": g(17), "d1514_may_pct": g(18),
            # ── Delta 15/13 absoluto (era 14/12) ──
            "d1513_nor": g(19), "d1513_ofe": g(20), "d1513_may": g(21),
            "d1513_nor_pct": g(22), "d1513_ofe_pct": g(23), "d1513_may_pct": g(24),
            # ── UPCs / Cats SW15 ──
            "upcs_sw15": g(25), "cats_sw15": g(26),
        })
    return rows


def load_resumen(xl):
    df = xl.parse("RESUMEN", header=None)
    result = []
    for i in range(2, 7):
        row = list(df.iloc[i])
        if not row[0] or (isinstance(row[0], float) and math.isnan(row[0])):
            continue
        result.append({
            "pais": str(row[0]),
            "competidores": _s(row[1]),
            "total_normal_sw15": _s(row[2]),
            "total_ofertas_sw15": _s(row[3]),
            "total_mayoreo_sw15": _s(row[4]),
            "upcs_prom_sw15": _s(row[5]),
            "tendencia_general": str(row[6]) if _s(row[6]) else "—",
        })
    return result


def load_tendencias(xl):
    df = xl.parse("TENDENCIAS", header=None)
    result = []
    for i in range(2, len(df)):
        row = list(df.iloc[i])
        if not row[0] or (isinstance(row[0], float) and math.isnan(row[0])):
            continue
        result.append({
            "clasificacion": str(row[0]),
            "pais": str(row[1]),
            "competidor": str(row[2]),
            "tendencia_sostenida": str(row[3]),
            "sw12_total": _s(row[4]),   # era SW11
            "sw15_total": _s(row[5]),   # era SW14
            "d_total": _s(row[6]),
            "d_pct_total": _s(row[7]),
            "d_normal": _s(row[8]),
            "d_pct_normal": _s(row[9]),
            "d_oferta": _s(row[10]),
            "d_pct_oferta": _s(row[11]),
            "d_mayoreo": _s(row[12]),
            "d_pct_mayoreo": _s(row[13]),
            "upcs_sw15": _s(row[14]),
            "cats_sw15": _s(row[15]),
        })
    return result


def load_all():
    xl = pd.ExcelFile(XLSX)
    data = {
        "resumen": load_resumen(xl),
        "tendencias": load_tendencias(xl),
        "countries": {code: load_country(xl, code) for code in COUNTRY_NAMES},
    }
    return data
