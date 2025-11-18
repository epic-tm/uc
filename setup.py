import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# -----------------------------------------------------------
# GitHub import utilities
# -----------------------------------------------------------
RAW_BASE = "https://raw.githubusercontent.com/epic-tm/uc/main/"

def load_image(path: str) -> Image.Image:
    url = RAW_BASE + path
    r = requests.get(url)
    r.raise_for_status()
    return Image.open(BytesIO(r.content)).convert("RGBA")

def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    url = RAW_BASE + path
    data = requests.get(url).content
    return ImageFont.truetype(BytesIO(data), size=size)

def load_json(path: str):
    import json
    url = RAW_BASE + path
    return json.loads(requests.get(url).text)

# -----------------------------------------------------------
# Achievement generator
# -----------------------------------------------------------

def generate_achievement(title: str, subtitle: str, icon_path: str, output_path: str):
    TITLE_COLOR = (255, 255, 85)
    TEXT_COLOR = (255, 255, 255)

    # load assets from GitHub repo
    font_title = load_font("assets/fonts/Minecraft.ttf", 22)
    font_sub = load_font("assets/fonts/Minecraft.ttf", 18)

    icon = load_image(icon_path)

    slice_path = "assets/achievement/"
    parts = {
        "tl": load_image(slice_path + "topleft.png"),
        "tm": load_image(slice_path + "topmiddle.png"),
        "tr": load_image(slice_path + "topright.png"),
        "ml": load_image(slice_path + "middleleft.png"),
        "mm": load_image(slice_path + "middlemiddle.png"),
        "mr": load_image(slice_path + "middleright.png"),
        "bl": load_image(slice_path + "bottomleft.png"),
        "bm": load_image(slice_path + "bottommiddle.png"),
        "br": load_image(slice_path + "bottomright.png"),
    }

    temp = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(temp)

    title_w, title_h = draw.textsize(title, font=font_title)
    sub_w, sub_h = draw.textsize(subtitle, font=font_sub)

    content_width = max(title_w, sub_w) + icon.width + 20
    content_height = icon.height + 10
    content_width = max(content_width, 150)

    w = content_width + 20
    h = content_height + 20

    final = Image.new("RGBA", (w, h))

    # Corners
    final.paste(parts["tl"], (0, 0))
    final.paste(parts["tr"], (w - parts["tr"].width, 0))
    final.paste(parts["bl"], (0, h - parts["bl"].height))
    final.paste(parts["br"], (w - parts["br"].width, h - parts["br"].height))

    # Stretch edges
    tm = parts["tm"].resize((w - parts["tl"].width - parts["tr"].width, parts["tm"].height))
    bm = parts["bm"].resize((w - parts["bl"].width - parts["br"].width, parts["bm"].height))

    final.paste(tm, (parts["tl"].width, 0))
    final.paste(bm, (parts["bl"].width, h - parts["bm"].height))

    ml = parts["ml"].resize((parts["ml"].width, h - parts["tl"].height - parts["bl"].height))
    mr = parts["mr"].resize((parts["mr"].width, h - parts["tr"].height - parts["br"].height))

    final.paste(ml, (0, parts["tl"].height))
    final.paste(mr, (w - parts["mr"].width, parts["tr"].height))

    mm = parts["mm"].resize(
        (
            w - parts["ml"].width - parts["mr"].width,
            h - parts["tm"].height - parts["bm"].height,
        )
    )
    final.paste(mm, (parts["ml"].width, parts["tm"].height))

    draw = ImageDraw.Draw(final)
    final.paste(icon, (12, (h - icon.height) // 2), icon)

    tx = icon.width + 20
    ty = 8

    draw.text((tx, ty), title, font=font_title, fill=TITLE_COLOR)
    draw.text((tx, ty + title_h + 2), subtitle, font=font_sub, fill=TEXT_COLOR)

    final.save(output_path)


# -----------------------------------------------------------
# Batch generation from achievements.json
# -----------------------------------------------------------

def generate_all_from_json(json_path: str, output_folder: str):
    import os
    data = load_json(json_path)

    os.makedirs(output_folder, exist_ok=True)

    for ach in data:
        out = f"{output_folder}/{ach['id']}.png"
        generate_achievement(
            ach["title"],
            ach["subtitle"],
            ach["icon"],
            out
        )
        print("Generated:", out)
