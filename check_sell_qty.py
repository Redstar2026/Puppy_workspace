import csv
rows = []
with open('prcng_info_store4076_sw22_cat6894_6987.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)
sell_qty_vals = set(r['SELL_QTY'] for r in rows)
print('SELL_QTY unique values:', sorted(sell_qty_vals)[:20])
print('Total rows available:', len(rows))
