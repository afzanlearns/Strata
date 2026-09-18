import pymupdf
doc = pymupdf.open(r'C:\Users\Afzan Khan\Documents\Strata\data\raw\gwra2025_blockwise.pdf')
import re
for i, page in enumerate(doc):
    t = page.get_text()
    if re.search(r'(?i)punjab', t):
        for tab in page.find_tables():
            for r in tab.extract():
                cat = str(r[4]).strip() if len(r) >= 5 else ''
                if cat.lower() not in ('safe', 'critical', 'salinity', 'categorization', 'none', ''):
                    print(f'page {i}: row={r}')
        break
print('--- raw text grep ---')
for i, page in enumerate(doc):
    t = page.get_text()
    if re.search(r'(?i)punjab', t):
        for line in t.split('\n'):
            if re.search(r'(?i)exploit|semi|critic', line):
                print(f'page {i}: {line!r}')
