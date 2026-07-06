import zipfile
import xml.etree.ElementTree as ET
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

fname = 'Promt Orginal Impactos.docx'

print(f"File exists: {os.path.exists(fname)}")
print(f"File size: {os.path.getsize(fname)} bytes")

try:
    with zipfile.ZipFile(fname) as z:
        print("Files inside DOCX:")
        for name in z.namelist():
            print(f"  {name}")

        if 'word/document.xml' in z.namelist():
            content = z.read('word/document.xml')
            print(f"\ndocument.xml size: {len(content)} bytes")

            root = ET.fromstring(content)
            ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

            lines = []
            for p in root.iter('{'+ns+'}p'):
                parts = [t.text or '' for t in p.iter('{'+ns+'}t')]
                line = ''.join(parts).strip()
                if line:
                    lines.append(line)

            print(f"\nExtracted {len(lines)} non-empty lines:\n")
            text = '\n'.join(lines)
            print(text)

            with open('prompt_original_text.txt', 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"\nSaved to prompt_original_text.txt")
        else:
            print("No word/document.xml found!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
