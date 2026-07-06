import csv

with open('pricing_summary_output_6894_6987.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    sum_rows = list(reader)

criticos = [r for r in sum_rows if int(r.get('SKUS_DIFERENTE_PRECIO','0') or 0) > 0]
print(f'Families with deviations: {len(criticos)}')
print()
for r in sorted(criticos, key=lambda x: (-int(x.get('SKUS_DIFERENTE_PRECIO','0') or 0), -float(x.get('VENTAS_PRIMARIO','0') or 0))):
    pct = float(r.get('PCT_ALINEACION','0') or 0)
    print(f"  [{r['CODIGO_FAMILIA']}] CAT:{r['CATEGORY_NBR']} | {r['MARCA']:<20} | {r['FINELINE'][:30]:<30} | P.Prim: {r['PRECIO_PRIMARIO']:>8} | Diff: {r['SKUS_DIFERENTE_PRECIO']} | Aln: {pct:.1f}%")
