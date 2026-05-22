import zipfile, xml.etree.ElementTree as ET, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
fname = 'Promnt Análisis Semanal de Impactos Modelo.docx'

with zipfile.ZipFile(fname) as z:
    content = z.read('word/document.xml')

root = ET.fromstring(content)
ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

lines = []
for p in root.iter('{'+ns+'}p'):
    parts = [t.text or '' for t in p.iter('{'+ns+'}t')]
    line = ''.join(parts).strip()
    if line:
        lines.append(line)

with open('prompt_text.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f"OK: {len(lines)} lines written to prompt_text.txt")
