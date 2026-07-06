import csv
rows = []
with open('prcng_info_store4076_sw22_cat6894_6987.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)
cats = {}
for r in rows:
    c = r['CATEGORY_NBR']
    cats[c] = cats.get(c, 0) + 1
print('Total rows:', len(rows))
print('Rows by category:', cats)
