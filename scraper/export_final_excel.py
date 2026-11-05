import json
import csv
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Load verified catalog
with open('scraper/final_verified_catalog.json', 'r', encoding='utf-8') as f:
    deals = json.load(f)

print(f"Loaded {len(deals)} verified deals for Excel generation.")

wb = openpyxl.Workbook()
wb.remove(wb.active) # Remove default sheet

# Colors
HEADER_BG = "1E272E"       # Dark Slate
HEADER_FONT_COLOR = "FFFFFF"
LIGHT_GRAY_FILL = "F8F9FA"
BORDER_GRAY = "DFE4EA"
SUCCESS_BG = "E8F5E9"      # Light Green
SUCCESS_FONT = "2E7D32"    # Dark Green

header_fill = PatternFill(start_color=HEADER_BG, end_color=HEADER_BG, fill_type="solid")
header_font = Font(name="Segoe UI", size=11, bold=True, color=HEADER_FONT_COLOR)
center_align = Alignment(horizontal="center", vertical="center", wrap_text=False)
left_align = Alignment(horizontal="left", vertical="center", wrap_text=False)
right_align = Alignment(horizontal="right", vertical="center", wrap_text=False)

thin_border = Border(
    left=Side(style='thin', color=BORDER_GRAY),
    right=Side(style='thin', color=BORDER_GRAY),
    top=Side(style='thin', color=BORDER_GRAY),
    bottom=Side(style='thin', color=BORDER_GRAY)
)

success_fill = PatternFill(start_color=SUCCESS_BG, end_color=SUCCESS_BG, fill_type="solid")
success_font = Font(name="Segoe UI", size=10, bold=True, color=SUCCESS_FONT)
discount_font = Font(name="Segoe UI", size=11, bold=True, color="D63031")
price_font = Font(name="Segoe UI", size=11, bold=True, color="00823B")
link_font = Font(name="Segoe UI", size=10, underline="single", color="0984E3")

columns = [
    ("No", 6, center_align),
    ("Kategori", 15, center_align),
    ("Platform", 14, center_align),
    ("Ürün Başlığı", 55, left_align),
    ("Sayfada Çizili Fiyat", 20, right_align),
    ("Sayfada Satış Fiyatı", 20, right_align),
    ("Net Kazanç (TL)", 16, right_align),
    ("İndirim Oranı", 15, center_align),
    ("Sayfadaki Çift Fiyat", 26, center_align),
    ("Doğrulama Sonucu", 35, center_align),
    ("Ürün Linki (Doğrudan Mağaza)", 50, left_align),
    ("Ürün Görseli", 35, left_align),
]

def create_sheet(sheet_title, items):
    ws = wb.create_sheet(title=sheet_title)
    ws.views.sheetView[0].showGridLines = True
    
    # Headers
    for col_idx, (col_name, col_width, _) in enumerate(columns, start=1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = thin_border
        ws.column_dimensions[get_column_letter(col_idx)].width = col_width
    ws.row_dimensions[1].height = 28
    
    # Rows
    for row_idx, item in enumerate(items, start=2):
        ws.row_dimensions[row_idx].height = 24
        orig_p = float(item.get('originalPrice', 0))
        disc_p = float(item.get('discountedPrice', 0))
        diff_p = orig_p - disc_p
        rate = int(item.get('discountRate', 0))
        prod_url = item.get('productUrl', '')
        img_url = item.get('imageUrl', '')
        
        row_fill = None
        if row_idx % 2 == 1:
            row_fill = PatternFill(start_color=LIGHT_GRAY_FILL, end_color=LIGHT_GRAY_FILL, fill_type="solid")
            
        c_no = ws.cell(row=row_idx, column=1, value=row_idx - 1)
        c_no.alignment = center_align
        
        c_cat = ws.cell(row=row_idx, column=2, value=item.get('category', ''))
        c_cat.alignment = center_align
        
        c_store = ws.cell(row=row_idx, column=3, value=item.get('store', 'Idefix'))
        c_store.alignment = center_align
        
        c_title = ws.cell(row=row_idx, column=4, value=item.get('title', ''))
        c_title.alignment = left_align
        
        c_orig = ws.cell(row=row_idx, column=5, value=orig_p)
        c_orig.number_format = '#,##0.00 "TL"'
        c_orig.alignment = right_align
        
        c_disc = ws.cell(row=row_idx, column=6, value=disc_p)
        c_disc.number_format = '#,##0.00 "TL"'
        c_disc.font = price_font
        c_disc.alignment = right_align
        
        c_diff = ws.cell(row=row_idx, column=7, value=diff_p)
        c_diff.number_format = '#,##0.00 "TL"'
        c_diff.alignment = right_align
        
        c_rate = ws.cell(row=row_idx, column=8, value=f"%{rate}")
        c_rate.font = discount_font
        c_rate.alignment = center_align
        
        c_dual = ws.cell(row=row_idx, column=9, value=f"{orig_p:,.2f} TL -> {disc_p:,.2f} TL")
        c_dual.alignment = center_align
        
        c_status = ws.cell(row=row_idx, column=10, value="✅ BAŞARILI - Sayfada Çift Fiyat Teyit Edildi")
        c_status.fill = success_fill
        c_status.font = success_font
        c_status.alignment = center_align
        
        c_link = ws.cell(row=row_idx, column=11, value="Ürünü Mağazada Aç ↗")
        c_link.hyperlink = prod_url
        c_link.font = link_font
        c_link.alignment = left_align
        
        c_img = ws.cell(row=row_idx, column=12, value="Görseli Görüntüle ↗")
        c_img.hyperlink = img_url
        c_img.font = link_font
        c_img.alignment = left_align
        
        for c in [c_no, c_cat, c_store, c_title, c_orig, c_disc, c_diff, c_rate, c_dual, c_status, c_link, c_img]:
            c.border = thin_border
            if row_fill and c != c_status:
                c.fill = row_fill

# 1. Main Sheet (All 200 Deals)
create_sheet(f"Tüm İndirimler ({len(deals)})", deals)

# 2. Category Sheets (50 each)
for cat in ['Teknoloji', 'Moda', 'Ev & Yaşam', 'Kozmetik']:
    cat_items = [d for d in deals if d.get('category') == cat]
    create_sheet(f"{cat} ({len(cat_items)})", cat_items)

excel_path = "YariFiyatina_Urun_Listesi_Dogrulanmis.xlsx"
wb.save(excel_path)
print(f"Successfully generated {excel_path}!")

try:
    wb.save("YariFiyatina_Urun_Listesi.xlsx")
    print("Also successfully updated YariFiyatina_Urun_Listesi.xlsx!")
except Exception as e:
    print("Notice: YariFiyatina_Urun_Listesi.xlsx is currently open in Excel. Saved updated copy to YariFiyatina_Urun_Listesi_Dogrulanmis.xlsx.")

# Export matching CSV with UTF-8 BOM
csv_path = "YariFiyatina_Urun_Listesi_Dogrulanmis.csv"

with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow([
        "No", "Kategori", "Platform", "Ürün Başlığı", 
        "Sayfada Çizili Fiyat (TL)", "Sayfada Satış Fiyatı (TL)", "Net Kazanç (TL)", 
        "İndirim Oranı", "Sayfadaki Çift Fiyat", "Doğrulama Sonucu", 
        "Ürün Linki", "Ürün Görseli"
    ])
    for idx, d in enumerate(deals, start=1):
        orig = float(d.get('originalPrice', 0))
        disc = float(d.get('discountedPrice', 0))
        diff = orig - disc
        rate = d.get('discountRate', 0)
        writer.writerow([
            idx,
            d.get('category'),
            d.get('store', 'Idefix'),
            d.get('title'),
            f"{orig:.2f}",
            f"{disc:.2f}",
            f"{diff:.2f}",
            f"%{rate}",
            f"{orig:.2f} TL -> {disc:.2f} TL",
            "✅ BAŞARILI - Sayfada Çift Fiyat Teyit Edildi",
            d.get('productUrl'),
            d.get('imageUrl')
        ])
print(f"Successfully generated {csv_path}!")
