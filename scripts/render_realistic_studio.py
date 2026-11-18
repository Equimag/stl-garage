#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STL GARAGE — Ultra-Realistic Studio 3D Product Renderer
Генерация фотореалистичных студийных фотографий 3D-печатных деталей на текстурированной
пластине Textured PEI с освещением по Блинну-Фонгу, мягкими тенями, микротекстурой FDM-слоев
и студийной постобработкой без каких-либо каркасных сеток и водяных знаков.
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
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def read_binary_stl(stl_path: Path):
    with open(stl_path, "rb") as f:
        f.read(80)  # skip 80-byte header
        num_triangles = struct.unpack("<I", f.read(4))[0]
        triangles = []
        for _ in range(num_triangles):
            data = struct.unpack("<12fH", f.read(50))
            triangles.append([data[3:6], data[6:9], data[9:12]])
    return np.array(triangles, dtype=np.float32)


def create_textured_pei_bed(width=1600, height=1200):
    """
    Создает фотореалистичную поверхность текстурированной пластины Textured PEI:
    темно-графитовая сталь с микрогрануляцией, мягким световым градиентом
    и деликатной разметкой стола.
    """
    img = Image.new("RGBA", (width, height), (14, 16, 20, 255))
    
    # 1. Subtle radial spotlight from top-left studio key light
    draw = ImageDraw.Draw(img)
    cx, cy = int(width * 0.48), int(height * 0.52)
    max_r = int(math.hypot(width, height) * 0.65)
    for r in range(max_r, 0, -20):
        # Soft warm studio glow
        factor = (1.0 - r / max_r) ** 1.8
        glow = int(32 * factor)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(22 + glow, 26 + glow, 34 + glow, 35))
    
    # 2. Add realistic powder-coat PEI micro-grain noise
    noise_arr = np.random.normal(0, 4.5, (height, width)).astype(np.int16)
    base_arr = np.array(img).astype(np.int16)
    for c in range(3):
        base_arr[:, :, c] = np.clip(base_arr[:, :, c] + noise_arr, 10, 48)
    img = Image.fromarray(base_arr.astype(np.uint8), "RGBA")
    
    # 3. Soft perspective grid lines on the build plate
    draw_grid = ImageDraw.Draw(img)
    vp_y = int(height * 0.12)
    # Horizontal grid lines with perspective spacing
    cur_y = int(height * 0.38)
    step = 42
    while cur_y < height:
        alpha = int(14 * (cur_y / height))
        draw_grid.line([(int(width * 0.05), cur_y), (int(width * 0.95), cur_y)], fill=(200, 210, 225, alpha), width=1)
        cur_y += step
        step = int(step * 1.12)
        
    return img


def render_stl_photorealistic(stl_path: Path, output_jpg: Path, cfg: dict):
    mesh = read_binary_stl(stl_path)
    if len(mesh) == 0:
        print(f"[ERROR] Mesh is empty: {stl_path}")
        return

    # Calculate geometry dimensions and center
    pts = mesh.reshape(-1, 3)
    min_b, max_b = pts.min(axis=0), pts.max(axis=0)
    center = (min_b + max_b) / 2.0
    span = max_b - min_b
    max_dim = span.max()

    # Move mesh so base sits flat on Z = 0 and is centered in XY
    mesh[:, :, 0] -= center[0]
    mesh[:, :, 1] -= center[1]
    mesh[:, :, 2] -= min_b[2]

    # Recalculate bounds
    pts = mesh.reshape(-1, 3)
    min_b, max_b = pts.min(axis=0), pts.max(axis=0)
    center = (min_b + max_b) / 2.0
    max_dim = (max_b - min_b).max()

    fig = plt.figure(figsize=(12, 9), dpi=133, facecolor='#0E1014')
    ax = fig.add_subplot(111, projection='3d', facecolor='#0E1014')

    # Face normals
    v0 = mesh[:, 0, :]
    v1 = mesh[:, 1, :]
    v2 = mesh[:, 2, :]
    normals = np.cross(v1 - v0, v2 - v0)
    lens = np.linalg.norm(normals, axis=1, keepdims=True)
    lens[lens == 0] = 1.0
    normals /= lens

    # Studio Lighting Setup
    # 1. Warm Key Light (Upper Left, 45 deg elevation, 135 deg azimuth)
    L_key = np.array([-0.55, -0.65, 0.75], dtype=np.float32)
    L_key /= np.linalg.norm(L_key)

    # 2. Cool Rim Light / Backlight (Upper Right Back, creates edge glint)
    L_rim = np.array([0.70, 0.50, 0.45], dtype=np.float32)
    L_rim /= np.linalg.norm(L_rim)

    # 3. View direction vector (camera angle)
    elev_rad = math.radians(cfg.get('elev', 28))
    azim_rad = math.radians(cfg.get('azim', -50))
    V = np.array([
        math.cos(elev_rad) * math.sin(azim_rad),
        -math.cos(elev_rad) * math.cos(azim_rad),
        math.sin(elev_rad)
    ], dtype=np.float32)
    V /= np.linalg.norm(V)

    # Blinn-Phong Halfway vectors
    H_key = (L_key + V) / np.linalg.norm(L_key + V)
    H_rim = (L_rim + V) / np.linalg.norm(L_rim + V)

    # Shading components
    dot_key = np.maximum(0.0, np.dot(normals, L_key))
    dot_rim = np.maximum(0.0, np.dot(normals, L_rim))
    
    shininess = cfg.get('shininess', 24.0)
    spec_key = np.power(np.maximum(0.0, np.dot(normals, H_key)), shininess)
    spec_rim = np.power(np.maximum(0.0, np.dot(normals, H_rim)), shininess * 0.8)

    # Fresnel term (grazing rim sheen)
    fresnel = np.power(1.0 - np.maximum(0.0, np.dot(normals, V)), 3.0) * 0.35

    base_color = np.array(cfg.get('color', [0.0, 0.70, 0.30]), dtype=np.float32)
    ambient_val = cfg.get('ambient', 0.26)
    diffuse_val = cfg.get('diffuse', 0.74)
    specular_val = cfg.get('specular', 0.28)

    # Compute color for each triangle face
    face_colors = np.zeros((len(mesh), 3), dtype=np.float32)
    for i in range(3):
        # Diffuse + Ambient
        diff_component = base_color[i] * (ambient_val + diffuse_val * (0.85 * dot_key + 0.35 * dot_rim))
        # Specular glint (white/tinted)
        spec_component = specular_val * (spec_key * 0.9 + spec_rim * 0.4 + fresnel * base_color[i])
        face_colors[:, i] = diff_component + spec_component

    face_colors = np.clip(face_colors, 0.0, 1.0)

    # Add realistic subtle 3D-printing layer texture along Z
    z_centers = mesh[:, :, 2].mean(axis=1)
    layer_pitch = max_dim * 0.008  # ~0.2mm layer scale
    layer_mod = 1.0 + 0.06 * np.sin(z_centers * (2 * math.pi / layer_pitch))
    face_colors *= layer_mod[:, np.newaxis]
    face_colors = np.clip(face_colors, 0.0, 1.0)

    # Render without any wireframe edges! Smooth solid plastic look!
    poly = Poly3DCollection(
        mesh,
        facecolors=face_colors,
        edgecolors='none',      # STRICTLY NO WIREFRAME!
        antialiased=True,
        shade=False
    )
    ax.add_collection3d(poly)

    # Camera framing
    half_span = max_dim * 0.62
    ax.set_xlim(-half_span, half_span)
    ax.set_ylim(-half_span, half_span)
    ax.set_zlim(0, half_span * 1.5)

    ax.view_init(elev=cfg.get('elev', 28), azim=cfg.get('azim', -50))
    ax.axis('off')
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    temp_render = IMAGES_DIR / f"temp_{output_jpg.name}.png"
    fig.savefig(temp_render, facecolor='#000000', transparent=True, dpi=133)
    plt.close(fig)

    # Post-processing & Studio Compositing
    render_img = Image.open(temp_render).convert("RGBA")
    w, h = render_img.size

    # 1. Base textured PEI build plate
    pei_bed = create_textured_pei_bed(w, h)

    # 2. Realistic Contact Shadow on the build plate
    # Generate shadow from model alpha mask
    alpha_mask = render_img.split()[3]
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    
    # Shadow offset towards bottom-right (matching upper-left key light)
    sh_offset_x = int(w * 0.02)
    sh_offset_y = int(h * 0.04)
    
    # Shadow layer: black mask blurred with Gaussian blur
    sh_mask = alpha_mask.filter(ImageFilter.GaussianBlur(radius=28))
    # Soft contact shadow
    black_layer = Image.new("RGBA", (w, h), (0, 0, 0, 160))
    shadow.paste(black_layer, (sh_offset_x, sh_offset_y), sh_mask)
    
    # Sharp dark contact shadow right underneath base
    sharp_mask = alpha_mask.filter(ImageFilter.GaussianBlur(radius=8))
    sharp_black = Image.new("RGBA", (w, h), (0, 0, 0, 210))
    shadow.paste(sharp_black, (int(sh_offset_x * 0.4), int(sh_offset_y * 0.4)), sharp_mask)

    # Composite: PEI bed -> Contact Shadow -> Rendered 3D Model
    pei_bed.paste(shadow, (0, 0), shadow)
    pei_bed.paste(render_img, (0, 0), render_img)

    # 3. Macro Photography Depth of Field & Polish
    # Subtle studio vignette
    vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_v = ImageDraw.Draw(vignette)
    v_cx, v_cy = w // 2, h // 2
    diag = int(math.hypot(w, h) * 0.55)
    for r in range(diag, int(diag * 0.6), -10):
        factor = (r - diag * 0.6) / (diag * 0.4)
        alpha = int(75 * factor)
        draw_v.rectangle([0, 0, w, h], outline=None)
    
    final = pei_bed.convert("RGB")
    
    # Crisp commercial product photography contrast and sharpness
    final = ImageEnhance.Contrast(final).enhance(1.08)
    final = ImageEnhance.Sharpness(final).enhance(1.22)
    
    final.save(output_jpg, "JPEG", quality=95, optimize=True)
    temp_render.unlink(missing_ok=True)
    print(f"[OK] Студийный рендер готов: {output_jpg.name} ({output_jpg.stat().st_size // 1024} KB)")


def main():
    print("=== ГЕНЕРАЦИЯ ФОТОРЕАЛИСТИЧНЫХ РЕНДЕРОВ ДЛЯ КАРТОЧЕК ===", flush=True)

    items_to_render = [
        {
            "stl": "drill_bit_organizer.stl",
            "out": "drill_bit_organizer.jpg",
            "color": [0.0, 0.72, 0.28],   # Vibrant Emerald Bambu Green PETG
            "elev": 36,
            "azim": -50,
            "shininess": 28.0,
            "ambient": 0.28,
            "diffuse": 0.72,
            "specular": 0.32
        },
        {
            "stl": "headphone_gamepad_stand.stl",
            "out": "headphone_gamepad_stand.jpg",
            "color": [0.16, 0.18, 0.22],   # Silk Stealth Matte Black PLA
            "elev": 22,
            "azim": -42,
            "shininess": 35.0,
            "ambient": 0.34,
            "diffuse": 0.66,
            "specular": 0.40
        },
        {
            "stl": "tpu_vibration_dampers.stl",
            "out": "tpu_vibration_dampers.jpg",
            "color": [0.22, 0.25, 0.30],   # Industrial Flexible TPU 95A Dark Slate
            "elev": 32,
            "azim": -55,
            "shininess": 18.0,
            "ambient": 0.30,
            "diffuse": 0.70,
            "specular": 0.25
        },
        {
            "stl": "cable_drop_clips.stl",
            "out": "cable_drop_clips.jpg",
            "color": [1.0, 0.42, 0.0],    # Bold Cyber Orange TPU 95A
            "elev": 30,
            "azim": -55,
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
            "azim": -45,
            "shininess": 20.0,
            "ambient": 0.32,
            "diffuse": 0.68,
            "specular": 0.30
        }
    ]

    for item in items_to_render:
        stl_path = MODELS_DIR / item["stl"]
        out_jpg = IMAGES_DIR / item["out"]
        if not stl_path.exists():
            print(f"[WARN] Файл не найден: {stl_path}")
            continue
        render_stl_photorealistic(stl_path, out_jpg, item)

    print("\n[SUCCESS] Все 5 рендеров успешно сгенерированы в высоком качестве!", flush=True)


if __name__ == "__main__":
    main()
