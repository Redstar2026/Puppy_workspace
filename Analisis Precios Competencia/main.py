"""
main.py  —  Orquestador: carga datos y genera Excel + HTML SW12-SW15.
"""
import sys, os

BASE = r"C:\Users\shern22\Documents\puppy_workspace\Analisis Precios Competencia"
sys.path.insert(0, BASE)

from data_loader import load_all
from excel_writer import write_excel
from html_writer import write_html

EXCEL_OUT = os.path.join(BASE, "Detalle_Semanal_SW12_SW15_20260515.xlsx")
HTML_OUT  = os.path.join(BASE, "competitive_analysis_SW12_SW15.html")


def main():
    print("[*] Cargando datos del Excel...", flush=True)
    data = load_all()

    print(f"  Paises: {list(data['countries'].keys())}", flush=True)
    for code, rows in data["countries"].items():
        print(f"  {code}: {len(rows)} competidores", flush=True)
    print(f"  Tendencias: {len(data['tendencias'])} registros", flush=True)

    print("[*] Generando Excel...", flush=True)
    write_excel(data, EXCEL_OUT)

    print("[*] Generando HTML...", flush=True)
    write_html(data, HTML_OUT)

    print("\n[OK] Todo listo!", flush=True)
    print(f"  Excel: {EXCEL_OUT}", flush=True)
    print(f"  HTML:  {HTML_OUT}", flush=True)


if __name__ == "__main__":
    main()
