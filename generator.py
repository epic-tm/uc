from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os, json, requests

# Toggle to use GitHub raw URLs (set RAW_BASE to empty for local assets)
RAW_BASE = ""  # e.g. "https://raw.githubusercontent.com/epic-tm/uc/main/"

def _load_bytes_from_github(path):
    url = RAW_BASE + path
    r = requests.get(url)
    r.raise_for_status()
    return r.content

def load_image_local_or_github(path):
    if RAW_BASE:
        return Image.open(BytesIO(_load_bytes_from_github(path))).convert("RGBA")
    else:
        return Image.open(path).convert("RGBA")

def load_font_local_or_github(path, size=18):
    if RAW_BASE:
        data = _load_bytes_from_github(path)
        return ImageFont.truetype(BytesIO(data), size=size)
    else:
        return ImageFont.truetype(path, size=size)

def draw_rounded_panel(w, h, radius=8):
    im = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(im)
    # outer border
    d.rounded_rectangle((0,0,w-1,h-1), radius=radius, outline=(90,90,90,255), fill=(16,16,16,230))
    # inner darker area to mimic Minecraft
    d.rounded_rectangle((4,4,w-5,h-5), radius=radius-2, outline=None, fill=(18,18,18,230))
    return im

def generate_achievement(title, subtitle, icon_path, output_path, font_path=None):
    # load icon (supports GitHub raw or local)
    try:
        if RAW_BASE and icon_path.startswith("http"):
            icon = Image.open(BytesIO(requests.get(icon_path).content)).convert("RGBA")
        elif RAW_BASE:
            icon = load_image_local_or_github(icon_path)
        else:
            icon = Image.open(icon_path).convert("RGBA")
    except Exception as e:
        # fallback icon: small square
        icon = Image.new("RGBA", (40,40), (180,180,180,255))
    # fonts
    try:
        if font_path:
            font_title = load_font_local_or_github(font_path, 22)
            font_sub = load_font_local_or_github(font_path, 18)
        else:
            # Try to use a system font fallback
            font_title = ImageFont.truetype(\"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf\", 22)
            font_sub = ImageFont.truetype(\"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf\", 18)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # see if 9-slices exist (local or github)
    slice_base = os.path.join('assets','achievement')
    slices_exist = True
    needed = ['topleft.png','topmiddle.png','topright.png','middleleft.png','middlemiddle.png','middleright.png','bottomleft.png','bottommiddle.png','bottomright.png']
    for s in needed:
        p = os.path.join(slice_base, s)
        if RAW_BASE:
            # assume slices exist in repo if RAW_BASE provided
            continue
        if not os.path.exists(p):
            slices_exist = False
            break

    # Measure text
    tmp = Image.new('RGBA', (10,10))
    draw_tmp = ImageDraw.Draw(tmp)
    title_w, title_h = draw_tmp.textsize(title, font=font_title)
    sub_w, sub_h = draw_tmp.textsize(subtitle, font=font_sub)
    content_width = max(title_w, sub_w) + icon.width + 24
    content_height = max(icon.height, title_h + sub_h + 6) + 12
    content_width = max(content_width, 150)
    w = content_width + 20
    h = content_height + 20

    if slices_exist and not RAW_BASE:
        # assemble 9-slice (local)
        parts = {k: Image.open(os.path.join(slice_base, k)).convert('RGBA') for k in ['topleft.png','topmiddle.png','topright.png','middleleft.png','middlemiddle.png','middleright.png','bottomleft.png','bottommiddle.png','bottomright.png']}
        # map simple keys
        tl = parts['topleft.png']; tm = parts['topmiddle.png']; tr = parts['topright.png']
        ml = parts['middleleft.png']; mm = parts['middlemiddle.png']; mr = parts['middleright.png']
        bl = parts['bottomleft.png']; bm = parts['bottommiddle.png']; br = parts['bottomright.png']

        out = Image.new('RGBA', (w,h))
        out.paste(tl, (0,0))
        out.paste(tr, (w-tr.width,0))
        out.paste(bl, (0,h-bl.height))
        out.paste(br, (w-br.width,h-br.height))
        tm_r = tm.resize((w - tl.width - tr.width, tm.height))
        bm_r = bm.resize((w - bl.width - br.width, bm.height))
        out.paste(tm_r, (tl.width,0))
        out.paste(bm_r, (bl.width,h-bm.height))
        ml_r = ml.resize((ml.width, h - tl.height - bl.height))
        mr_r = mr.resize((mr.width, h - tr.height - br.height))
        out.paste(ml_r, (0, tl.height))
        out.paste(mr_r, (w - mr.width, tr.height))
        mm_r = mm.resize((w - ml.width - mr.width, h - tm.height - bm.height))
        out.paste(mm_r, (ml.width, tm.height))
    else:
        out = draw_rounded_panel(w, h, radius=8)

    # draw icon and text
    draw = ImageDraw.Draw(out)
    icon_y = (h - icon.height) // 2
    out.paste(icon, (12, icon_y), icon)
    tx = icon.width + 24
    ty = 8
    draw.text((tx, ty), title, font=font_title, fill=(255,255,85,255))
    draw.text((tx, ty + title_h + 4), subtitle, font=font_sub, fill=(255,255,255,255))

    out.save(output_path)
    print('Saved', output_path)

def generate_all_from_json(json_path, output_folder='generated'):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with open(json_path,'r',encoding='utf-8') as f:
        data = json.load(f)
    for ach in data:
        out = os.path.join(output_folder, ach.get('id','unk') + '.png')
        generate_achievement(ach.get('title','NoTitle'), ach.get('subtitle',''), ach.get('icon','assets/icons/icon_pickaxe.png'), out)
