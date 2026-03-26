"""Main v4: carga datos y genera el reporte HTML interactivo con Canvas."""
import json, os
from html_assembler import build_html

WORKSPACE = r"C:\Users\shern22\Documents\puppy_workspace"


def load_json(name):
    with open(os.path.join(WORKSPACE, name), encoding='utf-8') as f:
        return json.load(f)


def safe_int(v):
    try: return int(v or 0)
    except: return 0


def normalize(records, int_fields):
    for r in records:
        for f in int_fields:
            r[f] = safe_int(r.get(f))
    return records


def main():
    print("[*] Cargando datos...", flush=True)
    int_q1 = ['ano', 'mes', 'semana', 'cnt_precio_normal', 'cnt_precio_oferta', 'cnt_mayoreo']
    int_q3 = ['ano', 'mes', 'cnt_precio_normal', 'cnt_precio_oferta', 'cnt_mayoreo']

    q1  = normalize(load_json('query1_semanal.json'),  int_q1)
    q3  = normalize(load_json('query3_mensual.json'),  int_q3)
    idx = load_json('query_index.json')
    print(f"[OK] Q1:{len(q1)} | Q3:{len(q3)} | IDX:{len(idx)}", flush=True)

    print("[*] Serializando JSON...", flush=True)
    q1_json  = json.dumps(q1,  ensure_ascii=False)
    q3_json  = json.dumps(q3,  ensure_ascii=False)
    idx_json = json.dumps(idx, ensure_ascii=False)

    print("[*] Ensamblando HTML...", flush=True)
    html = build_html(q1_json, q3_json, idx_json)

    out = os.path.join(WORKSPACE, 'reporte_precios_cam.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)

    size_mb = os.path.getsize(out) / 1024 / 1024
    print(f"[OK] Reporte: {out}")
    print(f"     Tamano: {size_mb:.1f} MB")
    print(f"     Datos: Q1={len(q1)}, Q3={len(q3)}, IDX={len(idx)} filas")


if __name__ == '__main__':
    main()
