import zipfile
import xml.etree.ElementTree as ET

def read_docx(path):
    with zipfile.ZipFile(path) as z:
        xml_content = z.read('word/document.xml')
    tree = ET.fromstring(xml_content.decode('utf-8'))
    W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    paragraphs = []
    for para in tree.iter('{' + W + '}p'):
        runs = [t.text for t in para.iter('{' + W + '}t') if t.text]
        line = ''.join(runs)
        paragraphs.append(line)
    return '\n'.join(p for p in paragraphs if p.strip())

texto = read_docx('Prompt.docx')

with open('prompt_leido.txt', 'w', encoding='utf-8') as f:
    f.write(texto)

print(f'Listo. {len(texto)} caracteres, {len(texto.splitlines())} lineas.')
