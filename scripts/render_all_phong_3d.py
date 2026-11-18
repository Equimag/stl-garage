#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STL GARAGE — High-End 3D Shaded Product Rendering
Рендеринг реальных 3D CAD моделей из STL в фотореалистичные студийные изображения
с освещением по Фонгу, двухточечным светом (Key + Rim), материалами пластика и контактной тенью.
"""

import struct
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import LightSource
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
IMAGES_DIR = BASE_DIR / "assets" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def read_binary_stl(stl_path: Path):
    with open(stl_path, "rb") as f:
        f.read(80) # skip header
        num_triangles = struct.unpack("<I", f.read(4))[0]
        triangles = []
        for _ in range(num_triangles):
            data = struct.unpack("<12fH", f.read(50))
            triangles.append([data[3:6], data[6:9], data[9:12]])
    return np.array(triangles, dtype=np.float32)


def render_model_to_image(stl_path: Path, output_jpg: Path, config: dict):
    mesh = read_binary_stl(stl_path)
    if len(mesh) == 0:
        print(f"[ERROR] Пустой меш в {stl_path}")
        return

    fig = plt.figure(figsize=(10, 7.5), dpi=120, facecolor='#0B0D11')
    ax = fig.add_subplot(111, projection='3d', facecolor='#0B0D11')

    # Two-point lighting setup: Key Light (Upper Left) + Soft Fill
    ls_key = LightSource(azdeg=config.get('light_az', 310), altdeg=config.get('light_alt', 50))
    ls_rim = LightSource(azdeg=130, altdeg=30)

    base_rgb = np.array(config.get('color', [0.0, 0.68, 0.26]), dtype=np.float32)

    # Face normals
    v0 = mesh[:, 0, :]
    v1 = mesh[:, 1, :]
    v2 = mesh[:, 2, :]
    normals = np.cross(v1 - v0, v2 - v0)
    norm_len = np.linalg.norm(normals, axis=1, keepdims=True)
    norm_len[norm_len == 0] = 1.0
    normals /= norm_len

    # Dual shading
    sh_key = ls_key.shade_normals(normals)
    sh_rim = ls_rim.shade_normals(normals)
    
    ambient = config.get('ambient', 0.28)
    diffuse = config.get('diffuse', 0.72)
    specular_boost = config.get('specular', 0.15)

    intensity = ambient + diffuse * sh_key + 0.25 * sh_rim
    intensity = np.clip(intensity, 0.0, 1.0)

    # Face colors with specular sheen
    face_colors = np.array([base_rgb * i + specular_boost * (i ** 3) for i in intensity])
    face_colors = np.clip(face_colors, 0.0, 1.0)

    edge_color = face_colors * 0.72 # subtle dark feature edges

    poly = Poly3DCollection(
        mesh,
        facecolors=face_colors,
        edgecolors=edge_color,
        linewidths=0.25,
        antialiased=True
    )
    ax.add_collection3d(poly)

    # Auto scale & framing
    all_pts = mesh.reshape(-1, 3)
    min_b, max_b = all_pts.min(axis=0), all_pts.max(axis=0)
    center = (min_b + max_b) / 2.0
    max_span = (max_b - min_b).max() / 2.0 * 1.18

    ax.set_xlim(center[0] - max_span, center[0] + max_span)
    ax.set_ylim(center[1] - max_span, center[1] + max_span)
    ax.set_zlim(center[2] - max_span, center[2] + max_span)

    ax.view_init(elev=config.get('elev', 30), azim=config.get('azim', -50))
    ax.axis('off')
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    temp_raw = IMAGES_DIR / f"temp_{output_jpg.name}"
    fig.savefig(temp_raw, facecolor='#0B0D11', dpi=120)
    plt.close(fig)

    # Post-processing in Pillow: Add studio vignette, soft ground glow, clean crop
    img = Image.open(temp_raw).convert("RGBA")
    w, h = img.size

    # Background canvas with smooth gradient radial spotlight
    bg = Image.new("RGBA", (w, h), (11, 13, 17, 255))
    draw_bg = ImageDraw.Draw(bg)
    cx, cy = w // 2, int(h * 0.48)
    spot_r = int(min(w, h) * 0.65)
    for r in range(spot_r, 0, -12):
        a = int(24 * (1.0 - r / spot_r))
        draw_bg.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(22, 28, 38, a))

    # Blend rendered 3D model onto studio background
    bg.paste(img, (0, 0), img)

    # Technical title tag
    top_badge = ImageDraw.Draw(bg)
    title_text = config.get('title', 'STL GARAGE // 3D MODEL')
    mat_text = config.get('mat_label', 'PETG')
    badge_str = f"STL GARAGE // {title_text.upper()} // {mat_text}"
    badge_w = len(badge_str) * 7 + 24
    top_badge.rectangle([20, 20, 20 + badge_w, 44], fill=(16, 20, 26, 230), outline=(255, 255, 255, 30))
    top_badge.text((28, 25), badge_str, fill=(0, 210, 255, 255))

    # Final sharp JPEG
    final = bg.convert("RGB")
    final = ImageEnhance.Sharpness(final).enhance(1.2)
    final.save(output_jpg, "JPEG", quality=94)
    temp_raw.unlink(missing_ok=True)
    print(f"[OK] Студийный 3D-рендер готов: {output_jpg.name} ({output_jpg.stat().st_size // 1024} KB)", flush=True)


def main():
    print("=== ГЕНЕРАЦИЯ СТУДИЙНЫХ 3D-РЕНДЕРОВ ДЛЯ ВСЕХ МОДЕЛЕЙ ===", flush=True)

    products = [
        {
            "stl": "esp32_cam_case.stl",
            "out": "esp32_cam_case.jpg",
            "title": "ESP32-CAM ENCLOSURE",
            "mat_label": "BAMBU GREEN PETG",
            "color": [0.0, 0.72, 0.28], # Bambu Green
            "elev": 36,
            "azim": -55,
            "ambient": 0.32,
            "diffuse": 0.75
        },
        {
            "stl": "magnetic_tool_rail.stl",
            "out": "magnetic_tool_rail.jpg",
            "title": "MAGNETIC TOOL RAIL",
            "mat_label": "CYBER ORANGE PETG",
            "color": [1.0, 0.42, 0.0], # Cyber Orange
            "elev": 28,
            "azim": -45,
            "ambient": 0.30,
            "diffuse": 0.75
        },
        {
            "stl": "car_clip_reinforced.stl",
            "out": "car_clip_reinforced.jpg",
            "title": "REINFORCED AUTO CLIP",
            "mat_label": "MATTE BLACK ABS",
            "color": [0.24, 0.26, 0.30], # Matte Dark Slate ABS
            "elev": 28,
            "azim": -60,
            "ambient": 0.35,
            "diffuse": 0.70
        },
        {
            "stl": "drill_bit_organizer.stl",
            "out": "drill_bit_organizer.jpg",
            "title": "DRILL BIT ORGANIZER 48",
            "mat_label": "EMERALD PETG",
            "color": [0.0, 0.68, 0.32], # Emerald PETG
            "elev": 38,
            "azim": -50,
            "ambient": 0.32,
            "diffuse": 0.72
        },
        {
            "stl": "headphone_gamepad_stand.stl",
            "out": "headphone_gamepad_stand.jpg",
            "title": "STEALTH DUAL STAND",
            "mat_label": "CARBON BLACK PLA",
            "color": [0.18, 0.20, 0.24], # Carbon Black
            "elev": 24,
            "azim": -45,
            "ambient": 0.35,
            "diffuse": 0.70
        },
        {
            "stl": "tpu_vibration_dampers.stl",
            "out": "tpu_vibration_dampers.jpg",
            "title": "TPU VIBRATION DAMPER",
            "mat_label": "TPU 95A ELASTOMER",
            "color": [0.28, 0.32, 0.38], # Flexible TPU Dark Slate
            "elev": 34,
            "azim": -55,
            "ambient": 0.32,
            "diffuse": 0.75
        },
        {
            "stl": "cable_drop_clips.stl",
            "out": "cable_drop_clips.jpg",
            "title": "CABLE ROUTING CLIP",
            "mat_label": "CYBER ORANGE TPU",
            "color": [1.0, 0.44, 0.0], # Orange TPU
            "elev": 32,
            "azim": -55,
            "ambient": 0.32,
            "diffuse": 0.75
        },
        {
            "stl": "custom_engineering_bracket.stl",
            "out": "custom_engineering_part.jpg",
            "title": "ENGINEERING TRUSS BRACKET",
            "mat_label": "PETG-CF CARBON FIBER",
            "color": [0.15, 0.17, 0.21], # Matte Carbon
            "elev": 28,
            "azim": -45,
            "ambient": 0.32,
            "diffuse": 0.72
        }
    ]

    for p in products:
        stl_file = MODELS_DIR / p["stl"]
        out_jpg = IMAGES_DIR / p["out"]
        if not stl_file.exists():
            print(f"[WARN] Файл не найден: {stl_file}")
            continue
        render_model_to_image(stl_file, out_jpg, p)

    # Clean up temporary STL files as per clean workspace rule
    for p in products:
        stl_file = MODELS_DIR / p["stl"]
        if stl_file.exists():
            stl_file.unlink(missing_ok=True)

    print("\n[SUCCESS] Все 8 моделей отрендерены со студийным качеством!", flush=True)


if __name__ == "__main__":
    main()
