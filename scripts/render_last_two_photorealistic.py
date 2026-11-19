#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STL GARAGE — Photorealistic Studio Renderer for Cable Drop Clips & Engineering Bracket
Рендеринг оставшихся двух моделей на реальном фотографическом фоне Textured PEI Plate
с освещением по Блинну-Фонгу, мягкими тенями, текстурой FDM-слоев и макро-фокусом.
"""

import struct
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
IMAGES_DIR = BASE_DIR / "assets" / "images"
ARTIFACTS_DIR = Path(r"C:\Users\Memfor\.gemini\antigravity\brain\459c17d2-7c77-4a50-a2f0-4d1c7b9c5c41")


def read_binary_stl(stl_path: Path):
    with open(stl_path, "rb") as f:
        f.read(80)
        num_triangles = struct.unpack("<I", f.read(4))[0]
        triangles = []
        for _ in range(num_triangles):
            data = struct.unpack("<12fH", f.read(50))
            triangles.append([data[3:6], data[6:9], data[9:12]])
    return np.array(triangles, dtype=np.float32)


def get_real_pei_plate_background(width=1600, height=1200):
    """
    Создает фотореалистичный фон стола 3D-принтера, используя текстуру PEI
    из уже сгенерированных высокодетализированных студийных снимков.
    """
    ref_photo = ARTIFACTS_DIR / "drill_bit_organizer_1795063220627.jpg"
    if ref_photo.exists():
        src = Image.open(ref_photo).convert("RGBA")
        # Crop background region (bottom-left / perimeter area where build plate is visible)
        w_s, h_s = src.size
        # Sample PEI texture
        box = (0, int(h_s * 0.45), int(w_s * 0.5), h_s)
        sample = src.crop(box).resize((width, height), Image.Resampling.LANCZOS)
        # Apply gentle blur to emulate shallow depth of field in background
        bg = sample.filter(ImageFilter.GaussianBlur(radius=3))
        # Add smooth vignette towards edges
        vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw_v = ImageDraw.Draw(vignette)
        cx, cy = width // 2, height // 2
        diag = int(math.hypot(width, height) * 0.55)
        for r in range(diag, int(diag * 0.5), -12):
            factor = (r - diag * 0.5) / (diag * 0.5)
            alpha = int(95 * factor)
            draw_v.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(10, 12, 16, alpha))
        bg.paste(vignette, (0, 0), vignette)
        return bg
    
    # Fallback procedural
    bg = Image.new("RGBA", (width, height), (18, 20, 24, 255))
    return bg


def render_to_photo(stl_path: Path, output_jpg: Path, cfg: dict):
    mesh = read_binary_stl(stl_path)
    if len(mesh) == 0:
        print(f"[ERROR] Mesh is empty: {stl_path}")
        return

    pts = mesh.reshape(-1, 3)
    min_b, max_b = pts.min(axis=0), pts.max(axis=0)
    center = (min_b + max_b) / 2.0
    span = max_b - min_b
    max_dim = span.max()

    # Center XY, place base on Z=0
    mesh[:, :, 0] -= center[0]
    mesh[:, :, 1] -= center[1]
    mesh[:, :, 2] -= min_b[2]

    # Recalculate
    pts = mesh.reshape(-1, 3)
    min_b, max_b = pts.min(axis=0), pts.max(axis=0)
    center = (min_b + max_b) / 2.0
    max_dim = (max_b - min_b).max()

    fig = plt.figure(figsize=(14, 10.5), dpi=140, facecolor='#000000')
    ax = fig.add_subplot(111, projection='3d', facecolor='#000000')

    # Face normals
    v0 = mesh[:, 0, :]
    v1 = mesh[:, 1, :]
    v2 = mesh[:, 2, :]
    normals = np.cross(v1 - v0, v2 - v0)
    lens = np.linalg.norm(normals, axis=1, keepdims=True)
    lens[lens == 0] = 1.0
    normals /= lens

    # Studio Lights
    L_key = np.array([-0.60, -0.65, 0.75], dtype=np.float32)
    L_key /= np.linalg.norm(L_key)

    L_rim = np.array([0.75, 0.45, 0.40], dtype=np.float32)
    L_rim /= np.linalg.norm(L_rim)

    elev_rad = math.radians(cfg.get('elev', 28))
    azim_rad = math.radians(cfg.get('azim', -50))
    V = np.array([
        math.cos(elev_rad) * math.sin(azim_rad),
        -math.cos(elev_rad) * math.cos(azim_rad),
        math.sin(elev_rad)
    ], dtype=np.float32)
    V /= np.linalg.norm(V)

    H_key = (L_key + V) / np.linalg.norm(L_key + V)
    H_rim = (L_rim + V) / np.linalg.norm(L_rim + V)

    dot_key = np.maximum(0.0, np.dot(normals, L_key))
    dot_rim = np.maximum(0.0, np.dot(normals, L_rim))

    shininess = cfg.get('shininess', 32.0)
    spec_key = np.power(np.maximum(0.0, np.dot(normals, H_key)), shininess)
    spec_rim = np.power(np.maximum(0.0, np.dot(normals, H_rim)), shininess * 0.75)
    fresnel = np.power(1.0 - np.maximum(0.0, np.dot(normals, V)), 2.8) * 0.30

    base_color = np.array(cfg.get('color', [0.0, 0.70, 0.30]), dtype=np.float32)
    ambient_val = cfg.get('ambient', 0.28)
    diffuse_val = cfg.get('diffuse', 0.72)
    specular_val = cfg.get('specular', 0.35)

    face_colors = np.zeros((len(mesh), 3), dtype=np.float32)
    for i in range(3):
        diff = base_color[i] * (ambient_val + diffuse_val * (0.85 * dot_key + 0.35 * dot_rim))
        spec = specular_val * (spec_key * 0.9 + spec_rim * 0.4 + fresnel * base_color[i])
        face_colors[:, i] = diff + spec

    face_colors = np.clip(face_colors, 0.0, 1.0)

    # 0.16mm layer line micro-texture
    z_centers = mesh[:, :, 2].mean(axis=1)
    pitch = max_dim * 0.007
    layer_mod = 1.0 + 0.05 * np.sin(z_centers * (2 * math.pi / pitch))
    face_colors *= layer_mod[:, np.newaxis]
    face_colors = np.clip(face_colors, 0.0, 1.0)

    # Render without wireframe edges
    poly = Poly3DCollection(
        mesh,
        facecolors=face_colors,
        edgecolors='none',
        antialiased=True,
        shade=False
    )
    ax.add_collection3d(poly)

    half_span = max_dim * 0.65
    ax.set_xlim(-half_span, half_span)
    ax.set_ylim(-half_span, half_span)
    ax.set_zlim(0, half_span * 1.5)

    ax.view_init(elev=cfg.get('elev', 28), azim=cfg.get('azim', -50))
    ax.axis('off')
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    temp_render = IMAGES_DIR / f"temp_{output_jpg.name}.png"
    fig.savefig(temp_render, facecolor='#000000', transparent=True, dpi=140)
    plt.close(fig)

    render_img = Image.open(temp_render).convert("RGBA")
    w, h = render_img.size

    # 1. Base Plate from real photograph
    plate = get_real_pei_plate_background(w, h)

    # 2. Multi-tier Realistic Contact Shadows
    alpha_mask = render_img.split()[3]
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    # Soft broad ambient occlusion
    ao_mask = alpha_mask.filter(ImageFilter.GaussianBlur(radius=32))
    ao_layer = Image.new("RGBA", (w, h), (0, 0, 0, 150))
    shadow.paste(ao_layer, (int(w * 0.02), int(h * 0.035)), ao_mask)

    # Sharp ground contact shadow
    sharp_mask = alpha_mask.filter(ImageFilter.GaussianBlur(radius=9))
    sharp_layer = Image.new("RGBA", (w, h), (0, 0, 0, 220))
    shadow.paste(sharp_layer, (int(w * 0.008), int(h * 0.015)), sharp_mask)

    # 3. Composite layers
    plate.paste(shadow, (0, 0), shadow)
    plate.paste(render_img, (0, 0), render_img)

    # 4. Polish photo: subtle contrast, warmth, and macro sharpness
    final = plate.convert("RGB")
    final = ImageEnhance.Color(final).enhance(1.06)
    final = ImageEnhance.Contrast(final).enhance(1.10)
    final = ImageEnhance.Sharpness(final).enhance(1.24)

    final.save(output_jpg, "JPEG", quality=95, optimize=True)
    temp_render.unlink(missing_ok=True)
    print(f"[OK] Фотореалистичный рендер сохранен: {output_jpg.name} ({output_jpg.stat().st_size // 1024} KB)")


def main():
    print("=== РЕНДЕРИНГ ФИНАЛЬНЫХ МОДЕЛЕЙ НА СТОЛЕ ПРИНТЕРА ===")

    items = [
        {
            "stl": "cable_drop_clips.stl",
            "out": "cable_drop_clips.jpg",
            "color": [1.0, 0.42, 0.0],     # Cyber Orange TPU 95A
            "elev": 32,
            "azim": -52,
            "shininess": 26.0,
            "ambient": 0.28,
            "diffuse": 0.72,
            "specular": 0.35
        },
        {
            "stl": "custom_engineering_bracket.stl",
            "out": "custom_engineering_part.jpg",
            "color": [0.15, 0.17, 0.20],   # Carbon Fiber Matte PETG-CF
            "elev": 26,
            "azim": -46,
            "shininess": 22.0,
            "ambient": 0.32,
            "diffuse": 0.68,
            "specular": 0.30
        }
    ]

    for item in items:
        stl_path = MODELS_DIR / item["stl"]
        out_jpg = IMAGES_DIR / item["out"]
        if not stl_path.exists():
            print(f"[ERROR] STL не найден: {stl_path}")
            continue
        render_to_photo(stl_path, out_jpg, item)

    print("\n[SUCCESS] Финальные модели успешно отрендерены со студийным качеством на столе принтера!")


if __name__ == "__main__":
    main()
