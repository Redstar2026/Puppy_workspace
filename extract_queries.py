import zipfile
import os
import re
from html import unescape

FOLDER = r'C:\Users\shern22\OneDrive - Walmart Inc\Documentos\puppy_workspace\Analisis PxQ'

FILES = {
    'QUERY ANALISIS MEDICION TRANSFERENCIAS.docx': 'Medicion Trans',
    'QUERY MEDICON ROTACIONES.docx': 'Medicion ROT',
    'QUERY MEDICION LOGICA ACTUAL.docx': 'Medicion LOGICA ACTUAL',
}

def extract_query_from_docx(filepath):
    """Reconstruct SQL text from a Word document XML."""
    with zipfile.ZipFile(filepath) as z:
        with z.open('word/document.xml') as xml:
            content = xml.read().decode('utf-8')

    # Parse paragraph by paragraph to preserve line structure
    paragraphs = re.split(r'<w:p[ >]', content)
    lines = []
    for para in paragraphs:
        texts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', para)
        line = unescape(''.join(texts))
        if line.strip():
            lines.append(line)

    full_text = '\n'.join(lines)
    return full_text


def main():
    queries = {}
    for filename, label in FILES.items():
        path = os.path.join(FOLDER, filename)
        print(f"\n{'='*60}")
        print(f"Extracting: {filename}")
        print(f"Label: {label}")
        print('='*60)
        query_text = extract_query_from_docx(path)
        queries[label] = query_text
        print(query_text[:500])
        print(f"... (total chars: {len(query_text)})")

    return queries


if __name__ == '__main__':
    main()
