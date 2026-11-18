#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STL GARAGE — 3D Model Rendering Pipeline
Рендеринг 3D-моделей напрямую из КОМПАС-3D V22 с постобработкой под фото на Textured PEI столе.
"""

import os
import sys
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import win32com.client
from win32com.client import gencache
import pythoncom

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
IMAGES_DIR = BASE_DIR / "assets" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def rgb_to_kompas_color(r, g, b):
    return int(b) * 65536 + int(g) * 256 + int(r)


def connect_kompas():
    API5_GUID = "{0422828C-F174-495E-AC5D-D31014DBBE87}"
    kapi5 = gencache.EnsureModule(API5_GUID, 0, 1, 0)
    disp = win32com.client.Dispatch("Kompas.Application.5")
    kompas5 = kapi5.KompasObject(disp._oleobj_.QueryInterface(kapi5.KompasObject.CLSID, pythoncom.IID_IDispatch))
    return kompas5


def apply_pei_and_layer_texture(raw_image_path: str, output_image_path: str, item_info: dict):
    """
    Постобработка: текстурированная пластина Textured PEI, слойные линии FDM и студийный свет.
    """
    img = Image.open(raw_image_path).convert("RGBA")
    w, h = img.size

    # 1. Create Textured Dark Studio Canvas
    canvas = Image.new("RGBA", (w, h), (13, 15, 18, 255))
    draw = ImageDraw.Draw(canvas)

    # Gradient radial studio lighting
    cx, cy = w // 2, int(h * 0.45)
    max_r = int(math.hypot(w, h) * 0.55)
    for r in range(max_r, 0, -15):
        alpha = int(35 * (1.0 - r / max_r))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(22, 28, 36, alpha))

    # PEI textured grid lines (subtle micro-texture)
    grid_spacing = 32
    for x in range(0, w, grid_spacing):
        draw.line([(x, 0), (x, h)], fill=(255, 255, 255, 6), width=1)
    for y in range(0, h, grid_spacing):
        draw.line([(0, y), (w, y)], fill=(255, 255, 255, 6), width=1)

    # 2. Extract model by removing white/light background and apply filament color tinting
    datas = img.getdata()
    new_data = []
    tint_r, tint_g, tint_b = item_info.get("color", (0, 174, 66))

    for item in datas:
        # Check if pixel is background (near white / light grey)
        if item[0] > 235 and item[1] > 235 and item[2] > 235:
            new_data.append((0, 0, 0, 0)) # transparent background
        elif item[0] > 215 and item[1] > 215 and item[2] > 215:
            diff = max(item[0], item[1], item[2]) - 215
            alpha = max(0, min(255, int(255 - diff * 15)))
            new_data.append((item[0], item[1], item[2], alpha))
        else:
            # Model pixel: calculate grayscale luminance
            lum = (item[0] * 0.299 + item[1] * 0.587 + item[2] * 0.114) / 255.0
            
            # Apply filament color modulation
            # Highlight boost on lit facets, deep rich shade on shadowed facets
            pr = min(255, int(tint_r * (0.3 + 0.9 * lum)))
            pg = min(255, int(tint_g * (0.3 + 0.9 * lum)))
            pb = min(255, int(tint_b * (0.3 + 0.9 * lum)))
            new_data.append((pr, pg, pb, 255))

    img.putdata(new_data)

    # 3. Add soft contact shadow under part
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    bbox = img.getbbox()
    if bbox:
        bx1, by1, bx2, by2 = bbox
        s_draw.ellipse([bx1 + 10, by2 - 25, bx2 - 10, by2 + 35], fill=(0, 0, 0, 160))
        shadow = shadow.filter(ImageFilter.GaussianBlur(18))
        canvas.paste(shadow, (0, 0), shadow)

    # 4. Paste 3D model
    canvas.paste(img, (0, 0), img)

    # 5. Overlay fine FDM layer lines (0.16mm effect) across the model
    layer_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    l_draw = ImageDraw.Draw(layer_overlay)
    step_px = 3
    for y in range(0, h, step_px):
        l_draw.line([(0, y), (w, y)], fill=(0, 0, 0, 22), width=1)
        l_draw.line([(0, y + 1), (w, y + 1)], fill=(255, 255, 255, 12), width=1)

    # Mask layer lines only onto model opaque pixels
    mask = img.split()[3]
    canvas.paste(layer_overlay, (0, 0), mask)

    # 6. Technical Engineering Watermark / Badge
    top_badge = ImageDraw.Draw(canvas)
    tag_text = f"STL GARAGE // {item_info.get('material', 'PETG')} // LAYER {item_info.get('layer', '0.16mm')}"
    top_badge.rectangle([24, 24, 24 + len(tag_text) * 8 + 16, 48], fill=(18, 22, 28, 220), outline=(255, 255, 255, 30))
    top_badge.text((32, 28), tag_text, fill=(0, 174, 66, 255))

    # Convert to RGB and save optimized JPEG
    final_rgb = canvas.convert("RGB")
    enhancer = ImageEnhance.Sharpness(final_rgb)
    final_rgb = enhancer.enhance(1.25)
    final_rgb.save(output_image_path, "JPEG", quality=92)
    print(f"[OK] Фотореалистичный рендер сохранен: {output_image_path}")


def render_all_models():
    kompas5 = connect_kompas()

    tasks = [
        {
            "m3d": "drill_bit_organizer.m3d",
            "out": "drill_bit_organizer.jpg",
            "color": (0, 174, 66), # Bambu Green
            "material": "PETG EMERALD",
            "layer": "0.20mm"
        },
        {
            "m3d": "headphone_gamepad_stand.m3d",
            "out": "headphone_gamepad_stand.jpg",
            "color": (32, 36, 42), # Matte Black
            "material": "PLA MATTE STEALTH",
            "layer": "0.16mm"
        },
        {
            "m3d": "tpu_vibration_dampers.m3d",
            "out": "tpu_vibration_dampers.jpg",
            "color": (40, 44, 52), # TPU dark grey
            "material": "TPU 95A ELASTOMER",
            "layer": "0.20mm"
        },
        {
            "m3d": "cable_drop_clips.m3d",
            "out": "cable_drop_clips.jpg",
            "color": (255, 107, 0), # Cyber Orange
            "material": "TPU 95A ORANGE",
            "layer": "0.20mm"
        },
        {
            "m3d": "custom_engineering_bracket.m3d",
            "out": "custom_engineering_part.jpg",
            "color": (24, 28, 34), # Carbon PETG
            "material": "PETG-CF CARBON",
            "layer": "0.12mm"
        }
    ]

    for t in tasks:
        m3d_file = str(MODELS_DIR / t["m3d"])
        out_jpg = str(IMAGES_DIR / t["out"])
        raw_tmp = str(IMAGES_DIR / f"raw_{t['out']}")

        if not Path(m3d_file).exists():
            print(f"[WARN] Файл не найден: {m3d_file}")
            continue

        print(f"Рендеринг {t['m3d']} в КОМПАС-3D...", flush=True)
        doc3d = kompas5.Document3D()
        if not doc3d.Open(m3d_file, False):
            print(f"[ERROR] Не удалось открыть: {m3d_file}", flush=True)
            continue

        rp = doc3d.RasterFormatParam()
        doc3d.SaveAsToRasterFormat(raw_tmp, rp)
        doc3d.close()

        if Path(raw_tmp).exists():
            apply_pei_and_layer_texture(raw_tmp, out_jpg, t)
            try:
                os.remove(raw_tmp)
            except: pass


if __name__ == "__main__":
    render_all_models()
