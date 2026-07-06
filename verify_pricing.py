import csv

with open('pricing_detail_output.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    detail_rows = list(reader)
    fieldnames = reader.fieldnames

print(f'Detail CSV: {len(detail_rows)} rows, {len(fieldnames)} columns')
new_cols = ['CODIGO_FAMILIA','AGRUPACION','ESTADO_PRECIO','DIFERENCIA_PRECIO','PRECIO_PRIMARIO','ROTACION']
for c in new_cols:
    print(f'  {c}: sample = {detail_rows[0].get(c,"MISSING")}')

print()

with open('pricing_summary_output.csv', 'r', encoding='utf-8') as f:
    reader2 = csv.DictReader(f)
    sum_rows = list(reader2)

print(f'Summary CSV: {len(sum_rows)} rows')
criticos = [r for r in sum_rows if int(r.get('SKUS_DIFERENTE_PRECIO','0') or 0) > 0]
print(f'Families with price deviation ({len(criticos)}):')
for r in sorted(criticos, key=lambda x: -int(x.get('SKUS_DIFERENTE_PRECIO','0') or 0)):
    print(f'  [{r["CODIGO_FAMILIA"]}] {r["MARCA"]} | {r["FINELINE"][:35]} | P.Primario: {r["PRECIO_PRIMARIO"]} | SKUs-diff: {r["SKUS_DIFERENTE_PRECIO"]} | Aln: {float(r["PCT_ALINEACION"]):.1f}%')
