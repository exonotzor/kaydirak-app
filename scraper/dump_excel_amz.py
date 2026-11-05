import zipfile
import xml.etree.ElementTree as ET
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with zipfile.ZipFile('YariFiyatina_Urun_Listesi.xlsx', 'r') as z:
    rels = {}
    if 'xl/worksheets/_rels/sheet1.xml.rels' in z.namelist():
        tree = ET.fromstring(z.read('xl/worksheets/_rels/sheet1.xml.rels'))
        for r in tree.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
            rels[r.attrib['Id']] = r.attrib.get('Target', '')
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
            text = ''.join(t.text for t in si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t') if t.text)
            shared.append(text)
    sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    hl_map = {hl.attrib.get('ref'): rels.get(hl.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'), '') for hl in sheet.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}hyperlink')}
    
    rows = sheet.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row')
    for r_idx, r in enumerate(rows[1:], start=2):
        row_dict = {}
        for c in r.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
            ref = c.attrib.get('r', '')
            col = ''.join(x for x in ref if x.isalpha())
            v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            val = ''
            if v is not None and v.text:
                val = shared[int(v.text)] if c.attrib.get('t') == 's' else v.text
            row_dict[col] = val
        if row_dict.get('C') == 'Amazon TR':
            cat = row_dict.get('B')
            title = row_dict.get('D')
            url = hl_map.get(f'I{r_idx}')
            img = hl_map.get(f'J{r_idx}')
            orig_p = row_dict.get('E')
            sale_p = row_dict.get('F')
            rate = row_dict.get('H')
            print(f"{r_idx:3d}. [{cat}] %{rate} | {orig_p} -> {sale_p} | {title[:35]} | {url}")
