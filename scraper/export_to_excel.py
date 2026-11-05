import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Load live catalog
with open('assets/data/live_deals.json', 'r', encoding='utf-8') as f:
    deals = json.load(f)

print(f"Loaded {len(deals)} deals for Excel export.")

wb = openpyxl.Workbook()
# Remove default sheet
wb.remove(wb.active)

# Color themes
HEADER_BG = "1E272E"       # Dark Slate
HEADER_FONT_COLOR = "FFFFFF"
ACCENT_RED = "FF4757"
LIGHT_GRAY_FILL = "F8F9FA"
BORDER_GRAY = "DFE4EA"

header_fill = PatternFill(start_color=HEADER_BG, end_color=HEADER_BG, fill_type="solid")
header_font = Font(name="Calibri", size=11, bold=True, color=HEADER_FONT_COLOR)
center_align = Alignment(horizontal="center", vertical="center", wrap_text=False)
left_align = Alignment(horizontal="left", vertical="center", wrap_text=False)
right_align = Alignment(horizontal="right", vertical="center", wrap_text=False)

thin_border = Border(
    left=Side(style='thin', color=BORDER_GRAY),
    right=Side(style='thin', color=BORDER_GRAY),
    top=Side(style='thin', color=BORDER_GRAY),
    bottom=Side(style='thin', color=BORDER_GRAY)
)

discount_font = Font(name="Calibri", size=11, bold=True, color="D63031")
price_font = Font(name="Calibri", size=11, bold=True, color="00823B")
link_font = Font(name="Calibri", size=10, underline="single", color="0984E3")

columns = [
    ("No", 6, center_align),
    ("Kategori", 15, center_align),
    ("Mağaza", 14, center_align),
    ("Ürün Başlığı", 55, left_align),
    ("Orijinal Fiyat", 16, right_align),
    ("İndirimli Fiyat", 16, right_align),
    ("Kazanç (Fark)", 16, right_align),
    ("İndirim Oranı", 15, center_align),
    ("Ürün Linki (Doğrudan Mağaza)", 45, left_align),
    ("Ürün Görseli", 35, left_align),
]

def create_sheet(title, items):
    ws = wb.create_sheet(title=title)
    ws.views.sheetView[0].showGridLines = True
    
    # Write Headers
    for col_idx, (col_name, col_width, _) in enumerate(columns, start=1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = thin_border
        ws.column_dimensions[get_column_letter(col_idx)].width = col_width
    
    ws.row_dimensions[1].height = 26
    
    # Write Rows
    for row_idx, item in enumerate(items, start=2):
        ws.row_dimensions[row_idx].height = 22
        
        orig_p = float(item.get('originalPrice', 0))
        disc_p = float(item.get('discountedPrice', 0))
        diff_p = orig_p - disc_p
        rate = int(item.get('discountRate', 0))
        prod_url = item.get('productUrl', '')
        img_url = item.get('imageUrl', '')
        
        # Zebra striping
        row_fill = None
        if row_idx % 2 == 1:
            row_fill = PatternFill(start_color=LIGHT_GRAY_FILL, end_color=LIGHT_GRAY_FILL, fill_type="solid")
            
        c_no = ws.cell(row=row_idx, column=1, value=row_idx - 1)
        c_no.alignment = center_align
        
        c_cat = ws.cell(row=row_idx, column=2, value=item.get('category', ''))
        c_cat.alignment = center_align
        
        c_store = ws.cell(row=row_idx, column=3, value=item.get('store', ''))
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
        
        # Clickable Hyperlink for product URL
        c_url = ws.cell(row=row_idx, column=9, value="Mağazaya Git ↗")
        c_url.hyperlink = prod_url
        c_url.font = link_font
        c_url.alignment = center_align
        
        # Clickable Hyperlink for image URL
        c_img = ws.cell(row=row_idx, column=10, value="Görseli Aç ↗")
        c_img.hyperlink = img_url
        c_img.font = link_font
        c_img.alignment = center_align
        
        # Apply borders and row fills
        for col_i in range(1, len(columns) + 1):
            cell = ws.cell(row=row_idx, column=col_i)
            cell.border = thin_border
            if row_fill:
                cell.fill = row_fill
                
    # Freeze header row
    ws.freeze_panes = "A2"
    
    # Auto-filter
    last_col = get_column_letter(len(columns))
    ws.auto_filter.ref = f"A1:{last_col}{len(items) + 1}"

# 1. Main Sheet: All deals
create_sheet("Tüm İndirimler (216)", deals)

# 2. Category Sheets
for cat in ['Teknoloji', 'Moda', 'Ev & Yaşam', 'Kozmetik']:
    cat_items = [d for d in deals if d.get('category') == cat]
    create_sheet(cat, cat_items)

excel_path = r"c:\Users\suley\OneDrive\AntigravitySync\projects\Discount App\YariFiyatina_Urun_Listesi.xlsx"
wb.save(excel_path)
print(f"Successfully created Excel file at: {excel_path}")

# Also create CSV file for convenience
import csv
csv_path = r"c:\Users\suley\OneDrive\AntigravitySync\projects\Discount App\YariFiyatina_Urun_Listesi.csv"
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(["No", "Kategori", "Mağaza", "Ürün Başlığı", "Orijinal Fiyat (TL)", "İndirimli Fiyat (TL)", "Fark / Kazanç (TL)", "İndirim Oranı", "Ürün Linki", "Görsel Linki"])
    for idx, d in enumerate(deals, start=1):
        orig_p = float(d.get('originalPrice', 0))
        disc_p = float(d.get('discountedPrice', 0))
        writer.writerow([
            idx,
            d.get('category', ''),
            d.get('store', ''),
            d.get('title', ''),
            f"{orig_p:.2f}".replace('.', ','),
            f"{disc_p:.2f}".replace('.', ','),
            f"{(orig_p - disc_p):.2f}".replace('.', ','),
            f"%{d.get('discountRate', 0)}",
            d.get('productUrl', ''),
            d.get('imageUrl', '')
        ])
print(f"Successfully created CSV file at: {csv_path}")
