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
    """Reconstruct SQL text from a Word document XML, paragraph by paragraph."""
    with zipfile.ZipFile(filepath) as z:
        with z.open('word/document.xml') as xml:
            content = xml.read().decode('utf-8')

    paragraphs = re.split(r'<w:p[ >]', content)
    lines = []
    for para in paragraphs:
        texts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', para)
        line = unescape(''.join(texts))
        if line.strip():
            lines.append(line)

    return '\n'.join(lines)


def strip_title_line(query_text):
    """Remove the first line (document title) from the query."""
    lines = query_text.split('\n')
    # First non-SQL line is the doc title — skip it
    sql_lines = []
    started = False
    for line in lines:
        if not started:
            # Start after first line that looks like a title (no SQL keywords)
            upper = line.strip().upper()
            if upper.startswith('WITH ') or upper.startswith('SELECT '):
                started = True
                sql_lines.append(line)
        else:
            sql_lines.append(line)
    return '\n'.join(sql_lines)


def wrap_with_tipo(query_text, label):
    """
    Wrap a CTE-based query in a subquery and add tipo_de_medicion column.
    BigQuery supports: SELECT * FROM (WITH ... SELECT ...)
    Strategy: add the label col to the final SELECT from SALIDA.
    """
    # The final SELECT is expected to be "SELECT * FROM SALIDA" or similar
    # Let's inject tipo_de_medicion into the final SELECT
    # Find the last SELECT statement (after all CTEs)
    # Pattern: wrap whole thing as subquery
    cleaned = query_text.strip()
    wrapped = (
        f"-- ============================================\n"
        f"-- TIPO: {label}\n"
        f"-- ============================================\n"
        f"SELECT\n"
        f"  *,\n"
        f"  '{label}' AS tipo_de_medicion\n"
        f"FROM (\n"
        f"{cleaned}\n"
        f")"
    )
    return wrapped


def build_union_all(queries_dict):
    """Build a UNION ALL query from all extracted queries."""
    parts = []
    for label, query_text in queries_dict.items():
        sql = strip_title_line(query_text)
        wrapped = wrap_with_tipo(sql, label)
        parts.append(wrapped)

    union_sql = '\n\nUNION ALL\n\n'.join(parts)
    return union_sql


def main():
    queries = {}
    for filename, label in FILES.items():
        path = os.path.join(FOLDER, filename)
        print(f"Reading: {filename} -> {label}")
        query_text = extract_query_from_docx(path)
        queries[label] = query_text
        print(f"  Chars extracted: {len(query_text)}")

    final_sql = build_union_all(queries)

    out_path = r'C:\Users\shern22\Documents\puppy_workspace\UNION_ALL_PxQ.sql'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(final_sql)

    print(f"\n✅ Query guardado en: {out_path}")
    print(f"Total chars: {len(final_sql)}")
    print("\n--- PREVIEW (first 1500 chars) ---")
    print(final_sql[:1500])
    print("\n--- PREVIEW (last 800 chars) ---")
    print(final_sql[-800:])


if __name__ == '__main__':
    main()
