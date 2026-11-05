import os
from PIL import Image, ImageDraw, ImageFont

def create_app_icon(size):
    # Create image with RGBA
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Background Rounded Rectangle
    corner_radius = int(size * 0.22)
    # Gradient simulation with concentric rounded rectangles
    for i in range(corner_radius):
        factor = i / corner_radius
        # Interpolate color from #FF3838 to #FF6B81
        r = int(255)
        g = int(56 + (107 - 56) * factor)
        b = int(56 + (129 - 56) * factor)
        draw.rounded_rectangle(
            [i, i, size - 1 - i, size - 1 - i],
            radius=corner_radius - i,
            fill=(r, g, b, 255)
        )

    # 2. Subtle glossy highlight at top
    highlight = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(highlight)
    h_draw.ellipse(
        [-size * 0.2, -size * 0.4, size * 1.2, size * 0.6],
        fill=(255, 255, 255, 30)
    )
    img = Image.alpha_composite(img, highlight)
    draw = ImageDraw.Draw(img)

    # 3. Draw Shopping Bag silhouette (white)
    bag_w = int(size * 0.54)
    bag_h = int(size * 0.50)
    bag_left = (size - bag_w) // 2
    bag_top = int(size * 0.32)

    # Draw bag body
    draw.rounded_rectangle(
        [bag_left, bag_top, bag_left + bag_w, bag_top + bag_h],
        radius=int(size * 0.08),
        fill=(255, 255, 255, 245)
    )

    # Draw bag handle
    handle_w = int(size * 0.24)
    handle_h = int(size * 0.22)
    handle_left = (size - handle_w) // 2
    handle_top = bag_top - int(handle_h * 0.5)
    handle_thickness = max(2, int(size * 0.04))

    draw.arc(
        [handle_left, handle_top, handle_left + handle_w, handle_top + handle_h],
        start=180, end=360,
        fill=(255, 255, 255, 245),
        width=handle_thickness
    )

    # 4. Draw bold "%50" in vibrant red inside the bag
    text_content = "%50"
    try:
        font_size = int(bag_h * 0.46)
        # Try Arial or default
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except Exception:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text_content, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    text_x = (size - text_w) // 2
    text_y = bag_top + (bag_h - text_h) // 2 - int(size * 0.02)

    draw.text((text_x, text_y), text_content, fill=(235, 47, 60, 255), font=font)

    # 5. Small flame badge on the top right of the bag
    badge_r = int(size * 0.12)
    bx = bag_left + bag_w - badge_r
    by = bag_top - int(badge_r * 0.4)
    draw.ellipse([bx - badge_r, by - badge_r, bx + badge_r, by + badge_r], fill=(255, 177, 66, 255))
    draw.ellipse([bx - int(badge_r * 0.6), by - int(badge_r * 0.6), bx + int(badge_r * 0.6), by + int(badge_r * 0.6)], fill=(255, 71, 87, 255))

    return img

def main():
    sizes = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }

    base_dir = r"c:\Users\suley\OneDrive\AntigravitySync\projects\Discount App\android\app\src\main\res"

    for folder, size in sizes.items():
        folder_path = os.path.join(base_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        icon = create_app_icon(size)
        target_path = os.path.join(folder_path, "ic_launcher.png")
        icon.save(target_path, "PNG")
        print(f"Generated {target_path} ({size}x{size})")

    # Also save a 512x512 high-res icon in assets for store listing and splash
    assets_dir = r"c:\Users\suley\OneDrive\AntigravitySync\projects\Discount App\assets\icons"
    os.makedirs(assets_dir, exist_ok=True)
    high_res = create_app_icon(512)
    high_res.save(os.path.join(assets_dir, "app_logo.png"), "PNG")
    print(f"Generated high-res 512x512 logo at {assets_dir}\\app_logo.png")

if __name__ == "__main__":
    main()
