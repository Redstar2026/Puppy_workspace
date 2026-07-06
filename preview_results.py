import json
from pathlib import Path

BASE = Path(r"C:\Users\shern22\Documents\puppy_workspace\bigquery_results")

files = [
    ("s1a_pais.json",  "S1A - por PAIS"),
    ("s1b_div.json",   "S1B - por PAIS + DIVISION"),
    ("s1c_cat.json",   "S1C - por PAIS + DIV + CATEGORIA"),
    ("s1d_tier.json",  "S1D - por PAIS + TIER"),
]

for fname, label in files:
    data = json.loads((BASE / fname).read_text(encoding="utf-8"))
    print(f"\n{'='*70}")
    print(f"  {label}  ({len(data):,} filas)")
    print(f"{'='*70}")
    for r in data:
        parts = []
        for k, v in r.items():
            if isinstance(v, float):
                parts.append(f"{k}={v:.4f}")
            else:
                parts.append(f"{k}={v}")
        print("  " + " | ".join(parts))
