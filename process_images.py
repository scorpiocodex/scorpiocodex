import os
from PIL import Image, ImageDraw

base_dir = r"c:\Users\scorp\dev\python\Project\github\assets"

# 1. Process Banner
banner_path = os.path.join(base_dir, "banner.png")
if os.path.exists(banner_path):
    img = Image.open(banner_path).convert("RGBA")
    w, h = img.size
    target_h = w // 3
    
    if h > target_h:
        top = (h - target_h) // 2
        bottom = top + target_h
        img_cropped = img.crop((0, top, w, bottom))
        img_cropped.save(banner_path)
        print("Banner cropped to 3:1.")

# 2. Process Avatar (Make circular)
avatar_path = os.path.join(base_dir, "avatar.png")
if os.path.exists(avatar_path):
    img = Image.open(avatar_path).convert("RGBA")
    w, h = img.size
    
    # ensure it's square
    m = min(w, h)
    l = (w - m) // 2
    t = (h - m) // 2
    r = l + m
    b = t + m
    img = img.crop((l, t, r, b))
    
    # create circular mask
    mask = Image.new("L", (m, m), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, m, m), fill=255)
    
    # apply mask
    out = Image.new("RGBA", (m, m), (0,0,0,0))
    out.paste(img, (0, 0), mask)
    out.save(avatar_path)
    print("Avatar made circular.")
