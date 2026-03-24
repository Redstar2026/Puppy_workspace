"""Script para generar reporte HTML de analisis PGMB SW7 vs SW8 2026."""
import json
import os

WORKDIR = r"C:\Users\shern22\Documents\puppy_workspace"


def load_json(filename):
    path = os.path.join(WORKDIR, filename)
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def pivot_segmentos(data):
    """Pivota filas de segmentos a columnas por (PAIS, DIVISION, CATEGORIA)."""
    pivot = {}
    for row in data:
        key = (row["PAIS"], row["DIVISION"], row["CATEGORIA"])
        if key not in pivot:
            pivot[key] = {
                "PAIS": row["PAIS"], "DIVISION": row["DIVISION"],
                "CATEGORIA": row["CATEGORIA"],
                "Bajo": 0, "Subio": 0, "Mantiene": 0, "Nuevo": 0,
            }
        seg = row["segmento"]
        if seg in ("Bajo", "Subio", "Mantiene", "Nuevo"):
            pivot[key][seg] = int(row["cantidad"])
    result = []
    for val in pivot.values():
        val["Total"] = val["Bajo"] + val["Subio"] + val["Mantiene"] + val["Nuevo"]
        result.append(val)
    return sorted(result, key=lambda x: (x["PAIS"], x["DIVISION"], x["CATEGORIA"]))


def _safe_float(val, decimals=6):
    try:
        return round(float(val), decimals) if val is not None else 0.0
    except (ValueError, TypeError):
        return 0.0


def process_q3(data):
    """PG por PAIS/DIVISION/CATEGORIA. Formula: SUM(Factor_calc)/SUM(Peso_calc)."""
    result = []
    for row in data:
        pg_val = row.get("pg")
        if pg_val is None:
            continue
        try:
            pg_float = round(float(pg_val), 6)
        except (ValueError, TypeError):
            continue
        result.append({
            "PAIS":            row["PAIS"],
            "DIVISION":        row["DIVISION"],
            "CATEGORIA":       row["CATEGORIA"],
            "total_items":     int(row["total_items"]),
            "sum_factor_calc": _safe_float(row.get("sum_factor_calc")),
            "sum_peso_calc":   _safe_float(row.get("sum_peso_calc")),
            "pg":              pg_float,
            "avg_price_gap":   _safe_float(row.get("avg_price_gap")),
        })
    result.sort(key=lambda x: x["pg"])
    return result


def process_q4(data):
    """PG por PAIS/DIVISION/CATEGORIA/ITEM con clasificacion de outliers."""
    result = []
    for row in data:
        pg_val = row.get("pg")
        if pg_val is None:
            continue
        try:
            pg_float = round(float(pg_val), 6)
        except (ValueError, TypeError):
            continue
        result.append({
            "PAIS":            row["PAIS"],
            "DIVISION":        row["DIVISION"],
            "CATEGORIA":       row["CATEGORIA"],
            "ITEM":            str(row["ITEM"]),
            "item_descrip":    row.get("item_descrip") or "",
            "brand_name":      row.get("brand_name")  or "",
            "total_rows":      int(row.get("total_rows", 0) or 0),
            "sum_factor_calc": _safe_float(row.get("sum_factor_calc")),
            "sum_peso_calc":   _safe_float(row.get("sum_peso_calc")),
            "pg":              pg_float,
            "avg_price_gap":   _safe_float(row.get("avg_price_gap")),
            "tipo_outlier":    row.get("tipo_outlier", "Normal"),
            "lower_bound":     _safe_float(row.get("lower_bound")),
            "upper_bound":     _safe_float(row.get("upper_bound")),
        })
    result.sort(key=lambda x: x["pg"])
    return result


def get_kpis(data):
    return {
        "bajo":     sum(r["Bajo"]     for r in data),
        "subio":    sum(r["Subio"]    for r in data),
        "mantiene": sum(r["Mantiene"] for r in data),
        "nuevo":    sum(r["Nuevo"]    for r in data),
    }


def main():
    print("Cargando datos...")
    q1_raw = load_json("result_q1.json")
    q2_raw = load_json("result_q2.json")
    q3_raw = load_json("result_q3.json")
    q4_raw = load_json("result_q4.json")

    print("Procesando Q1 (Competidor)...")
    q1 = pivot_segmentos(q1_raw)
    print(f"  -> {len(q1)} combinaciones PAIS/DIVISION/CATEGORIA")

    print("Procesando Q2 (Walmart)...")
    q2 = pivot_segmentos(q2_raw)
    print(f"  -> {len(q2)} combinaciones PAIS/DIVISION/CATEGORIA")

    print("Procesando Q3 (Price Gap agregado)...")
    q3 = process_q3(q3_raw)
    print(f"  -> {len(q3)} combinaciones con datos validos")

    print("Procesando Q4 (Outliers por item)...")
    q4 = process_q4(q4_raw)
    n_neg = sum(1 for r in q4 if r["tipo_outlier"] == "Outlier Negativo")
    n_pos = sum(1 for r in q4 if r["tipo_outlier"] == "Outlier Positivo")
    print(f"  -> {len(q4)} items | {n_neg} outliers negativos | {n_pos} positivos")

    all_rows = q1 + q2
    paises     = sorted({r["PAIS"]     for r in all_rows})
    divisiones = sorted({r["DIVISION"] for r in all_rows})
    categorias = sorted({r["CATEGORIA"]for r in all_rows})

    kpi_comp = get_kpis(q1)
    kpi_wm   = get_kpis(q2)

    print("Generando HTML...")
    from html_builder import render_html
    html = render_html(q1, q2, q3, q4, paises, divisiones, categorias, kpi_comp, kpi_wm)

    out = os.path.join(WORKDIR, "reporte_pgmb_sw7_sw8.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] Reporte generado: {out}")
    return out


if __name__ == "__main__":
    main()
