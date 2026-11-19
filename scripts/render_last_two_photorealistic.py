#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STL GARAGE — Photorealistic Studio Renderer for Cable Drop Clips & Engineering Bracket
Рендеринг клипс-органайзеров и инженерного кронштейна на реальном фотографическом фоне
Textured PEI Plate с видимым кабелем, освещением по Блинну-Фонгу и контактными тенями.
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
    ref_photo = ARTIFACTS_DIR / "drill_bit_organizer_1795063220627.jpg"
    if ref_photo.exists():
        src = Image.open(ref_photo).convert("RGBA")
        w_s, h_s = src.size
        # Sample PEI texture from bottom plate region
        box = (0, int(h_s * 0.42), int(w_s * 0.58), h_s)
        sample = src.crop(box).resize((width, height), Image.Resampling.LANCZOS)
        bg = sample.filter(ImageFilter.GaussianBlur(radius=2.5))
        
        # Vignette
        vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw_v = ImageDraw.Draw(vignette)
        cx, cy = width // 2, height // 2
        diag = int(math.hypot(width, height) * 0.55)
        for r in range(diag, int(diag * 0.45), -14):
            factor = (r - diag * 0.45) / (diag * 0.55)
            alpha = int(90 * factor)
            draw_v.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(12, 14, 18, alpha))
        bg.paste(vignette, (0, 0), vignette)
        return bg
    return Image.new("RGBA", (width, height), (18, 20, 24, 255))


def generate_cylinder_mesh(p1, p2, radius, segments=24):
    """Генерирует 3D-сетку цилиндра (например, кабель)."""
    p1 = np.array(p1, dtype=np.float32)
    p2 = np.array(p2, dtype=np.float32)
    v = p2 - p1
    mag = np.linalg.norm(v)
    v_norm = v / mag

    # Orthogonal vectors
    not_v = np.array([1, 0, 0], dtype=np.float32) if abs(v_norm[0]) < 0.8 else np.array([0, 1, 0], dtype=np.float32)
    n1 = np.cross(v_norm, not_v)
    n1 /= np.linalg.norm(n1)
    n2 = np.cross(v_norm, n1)

    theta = np.linspace(0, 2 * np.pi, segments, endpoint=False)
    circle = np.array([np.cos(theta)[:, None] * n1 + np.sin(theta)[:, None] * n2]) * radius

    pts1 = p1 + circle[0]
    pts2 = p2 + circle[0]

    tris = []
    for i in range(segments):
        next_i = (i + 1) % segments
        tris.append([pts1[i], pts2[i], pts1[next_i]])
        tris.append([pts1[next_i], pts2[i], pts2[next_i]])

    return np.array(tris, dtype=np.float32)


def render_cable_clips(stl_path: Path, output_jpg: Path):
    """Специальный рендер набора кабель-клипс с продетым плетеным USB-кабелем."""
    clip_mesh = read_binary_stl(stl_path)
    if len(clip_mesh) == 0:
        return

    # Center base
    pts = clip_mesh.reshape(-1, 3)
    min_b, max_b = pts.min(axis=0), pts.max(axis=0)
    center = (min_b + max_b) / 2.0
    clip_mesh[:, :, 0] -= center[0]
    clip_mesh[:, :, 1] -= center[1]
    clip_mesh[:, :, 2] -= min_b[2]

    # Clip 1: Main clip in foreground at origin
    clip1 = clip_mesh.copy()
    
    # Clip 2: Second clip slightly behind and to the left (showing side angle)
    clip2 = clip_mesh.copy()
    ang = math.radians(40)
    cos_a, sin_a = math.cos(ang), math.sin(ang)
    x = clip2[:, :, 0].copy()
    y = clip2[:, :, 1].copy()
    clip2[:, :, 0] = x * cos_a - y * sin_a - 26.0
    clip2[:, :, 1] = x * sin_a + y * cos_a + 16.0

    # Clip 3: Third clip slightly to the right
    clip3 = clip_mesh.copy()
    ang3 = math.radians(-25)
    c3, s3 = math.cos(ang3), math.sin(ang3)
    x3 = clip3[:, :, 0].copy()
    y3 = clip3[:, :, 1].copy()
    clip3[:, :, 0] = x3 * c3 - y3 * s3 + 28.0
    clip3[:, :, 1] = x3 * s3 + y3 * c3 + 12.0

    orange_mesh = np.vstack([clip1, clip2, clip3])

    # Sleek black braided USB cable going through Clip 1 (channel at X=0, Z=6.5)
    cable_mesh = generate_cylinder_mesh([0.0, -35.0, 6.5], [0.0, 38.0, 6.5], radius=2.7, segments=24)

    fig = plt.figure(figsize=(14, 10.5), dpi=140, facecolor='#000000')
    ax = fig.add_subplot(111, projection='3d', facecolor='#000000')

    # Lights
    L_key = np.array([-0.55, -0.70, 0.70], dtype=np.float32)
    L_key /= np.linalg.norm(L_key)
    L_rim = np.array([0.70, 0.45, 0.45], dtype=np.float32)
    L_rim /= np.linalg.norm(L_rim)

    elev, azim = 22, -30
    elev_rad = math.radians(elev)
    azim_rad = math.radians(azim)
    V = np.array([
        math.cos(elev_rad) * math.sin(azim_rad),
        -math.cos(elev_rad) * math.cos(azim_rad),
        math.sin(elev_rad)
    ], dtype=np.float32)
    V /= np.linalg.norm(V)

    H_key = (L_key + V) / np.linalg.norm(L_key + V)
    H_rim = (L_rim + V) / np.linalg.norm(L_rim + V)

    # Shading Orange Clips
    v0, v1, v2 = orange_mesh[:, 0, :], orange_mesh[:, 1, :], orange_mesh[:, 2, :]
    n_o = np.cross(v1 - v0, v2 - v0)
    l_o = np.linalg.norm(n_o, axis=1, keepdims=True)
    l_o[l_o == 0] = 1.0
    n_o /= l_o

    dot_k = np.maximum(0.0, np.dot(n_o, L_key))
    dot_r = np.maximum(0.0, np.dot(n_o, L_rim))
    spec_k = np.power(np.maximum(0.0, np.dot(n_o, H_key)), 28.0)
    spec_r = np.power(np.maximum(0.0, np.dot(n_o, H_rim)), 22.0)
    fres = np.power(1.0 - np.maximum(0.0, np.dot(n_o, V)), 2.8) * 0.35

    base_orange = np.array([1.0, 0.42, 0.0], dtype=np.float32)
    colors_o = np.zeros((len(orange_mesh), 3), dtype=np.float32)
    for c in range(3):
        diff = base_orange[c] * (0.32 + 0.68 * (0.85 * dot_k + 0.35 * dot_r))
        spec = 0.38 * (spec_k * 0.9 + spec_r * 0.4 + fres * base_orange[c])
        colors_o[:, c] = diff + spec
    colors_o = np.clip(colors_o, 0.0, 1.0)

    # Shading Black Braided Cable
    v0, v1, v2 = cable_mesh[:, 0, :], cable_mesh[:, 1, :], cable_mesh[:, 2, :]
    n_c = np.cross(v1 - v0, v2 - v0)
    l_c = np.linalg.norm(n_c, axis=1, keepdims=True)
    l_c[l_c == 0] = 1.0
    n_c /= l_c

    dot_kc = np.maximum(0.0, np.dot(n_c, L_key))
    dot_rc = np.maximum(0.0, np.dot(n_c, L_rim))
    spec_kc = np.power(np.maximum(0.0, np.dot(n_c, H_key)), 40.0)
    base_cable = np.array([0.16, 0.17, 0.19], dtype=np.float32)
    colors_c = np.zeros((len(cable_mesh), 3), dtype=np.float32)
    for c in range(3):
        diff = base_cable[c] * (0.35 + 0.65 * (0.85 * dot_kc + 0.35 * dot_rc))
        spec = 0.42 * (spec_kc * 0.9 + 0.2 * dot_rc)
        colors_c[:, c] = diff + spec
    colors_c = np.clip(colors_c, 0.0, 1.0)

    poly_o = Poly3DCollection(orange_mesh, facecolors=colors_o, edgecolors='none', antialiased=True)
    poly_c = Poly3DCollection(cable_mesh, facecolors=colors_c, edgecolors='none', antialiased=True)
    ax.add_collection3d(poly_c)
    ax.add_collection3d(poly_o)

    ax.set_xlim(-38, 38)
    ax.set_ylim(-38, 38)
    ax.set_zlim(0, 35)

    ax.view_init(elev=elev, azim=azim)
    ax.axis('off')
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    temp_render = IMAGES_DIR / f"temp_{output_jpg.name}.png"
    fig.savefig(temp_render, facecolor='#000000', transparent=True, dpi=140)
    plt.close(fig)

    render_img = Image.open(temp_render).convert("RGBA")
    w, h = render_img.size

    plate = get_real_pei_plate_background(w, h)
    alpha = render_img.split()[3]

    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ao_mask = alpha.filter(ImageFilter.GaussianBlur(radius=30))
    shadow.paste(Image.new("RGBA", (w, h), (0, 0, 0, 160)), (int(w * 0.02), int(h * 0.035)), ao_mask)
    sharp_mask = alpha.filter(ImageFilter.GaussianBlur(radius=8))
    shadow.paste(Image.new("RGBA", (w, h), (0, 0, 0, 230)), (int(w * 0.008), int(h * 0.012)), sharp_mask)

    plate.paste(shadow, (0, 0), shadow)
    plate.paste(render_img, (0, 0), render_img)

    final = plate.convert("RGB")
    final = ImageEnhance.Color(final).enhance(1.08)
    final = ImageEnhance.Contrast(final).enhance(1.12)
    final = ImageEnhance.Sharpness(final).enhance(1.25)
    final.save(output_jpg, "JPEG", quality=95, optimize=True)
    temp_render.unlink(missing_ok=True)
    print(f"[OK] Фотореалистичный рендер кабель-клипс готов: {output_jpg.name} ({output_jpg.stat().st_size // 1024} KB)")


def render_engineering_bracket(stl_path: Path, output_jpg: Path):
    """Специальный рендер углеволоконного кронштейна PETG-CF с четким рельефом ребер."""
    mesh = read_binary_stl(stl_path)
    if len(mesh) == 0:
        return

    pts = mesh.reshape(-1, 3)
    min_b, max_b = pts.min(axis=0), pts.max(axis=0)
    center = (min_b + max_b) / 2.0
    mesh[:, :, 0] -= center[0]
    mesh[:, :, 1] -= center[1]
    mesh[:, :, 2] -= min_b[2]

    pts = mesh.reshape(-1, 3)
    min_b, max_b = pts.min(axis=0), pts.max(axis=0)
    max_dim = (max_b - min_b).max()

    fig = plt.figure(figsize=(14, 10.5), dpi=140, facecolor='#000000')
    ax = fig.add_subplot(111, projection='3d', facecolor='#000000')

    v0, v1, v2 = mesh[:, 0, :], mesh[:, 1, :], mesh[:, 2, :]
    normals = np.cross(v1 - v0, v2 - v0)
    lens = np.linalg.norm(normals, axis=1, keepdims=True)
    lens[lens == 0] = 1.0
    normals /= lens

    # Studio Lights
    L_key = np.array([-0.65, -0.65, 0.70], dtype=np.float32)
    L_key /= np.linalg.norm(L_key)
    L_rim = np.array([0.75, 0.40, 0.45], dtype=np.float32)
    L_rim /= np.linalg.norm(L_rim)

    elev, azim = 26, -46
    elev_rad, azim_rad = math.radians(elev), math.radians(azim)
    V = np.array([
        math.cos(elev_rad) * math.sin(azim_rad),
        -math.cos(elev_rad) * math.cos(azim_rad),
        math.sin(elev_rad)
    ], dtype=np.float32)
    V /= np.linalg.norm(V)

    H_key = (L_key + V) / np.linalg.norm(L_key + V)
    H_rim = (L_rim + V) / np.linalg.norm(L_rim + V)

    dot_k = np.maximum(0.0, np.dot(normals, L_key))
    dot_r = np.maximum(0.0, np.dot(normals, L_rim))
    spec_k = np.power(np.maximum(0.0, np.dot(normals, H_key)), 26.0)
    spec_r = np.power(np.maximum(0.0, np.dot(normals, H_rim)), 20.0)
    fres = np.power(1.0 - np.maximum(0.0, np.dot(normals, V)), 2.5) * 0.40

    base_carbon = np.array([0.28, 0.31, 0.36], dtype=np.float32)
    face_colors = np.zeros((len(mesh), 3), dtype=np.float32)
    for i in range(3):
        diff = base_carbon[i] * (0.36 + 0.64 * (0.85 * dot_k + 0.35 * dot_r))
        spec = 0.42 * (spec_k * 0.9 + spec_r * 0.5 + fres * base_carbon[i])
        face_colors[:, i] = diff + spec
    face_colors = np.clip(face_colors, 0.0, 1.0)

    z_centers = mesh[:, :, 2].mean(axis=1)
    pitch = max_dim * 0.008
    layer_mod = 1.0 + 0.06 * np.sin(z_centers * (2 * math.pi / pitch))
    face_colors *= layer_mod[:, np.newaxis]
    face_colors = np.clip(face_colors, 0.0, 1.0)

    poly = Poly3DCollection(mesh, facecolors=face_colors, edgecolors='none', antialiased=True)
    ax.add_collection3d(poly)

    half_span = max_dim * 0.68
    ax.set_xlim(-half_span, half_span)
    ax.set_ylim(-half_span, half_span)
    ax.set_zlim(0, half_span * 1.5)

    ax.view_init(elev=elev, azim=azim)
    ax.axis('off')
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    temp_render = IMAGES_DIR / f"temp_{output_jpg.name}.png"
    fig.savefig(temp_render, facecolor='#000000', transparent=True, dpi=140)
    plt.close(fig)

    render_img = Image.open(temp_render).convert("RGBA")
    w, h = render_img.size

    plate = get_real_pei_plate_background(w, h)
    alpha = render_img.split()[3]

    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ao_mask = alpha.filter(ImageFilter.GaussianBlur(radius=32))
    shadow.paste(Image.new("RGBA", (w, h), (0, 0, 0, 160)), (int(w * 0.02), int(h * 0.035)), ao_mask)
    sharp_mask = alpha.filter(ImageFilter.GaussianBlur(radius=9))
    shadow.paste(Image.new("RGBA", (w, h), (0, 0, 0, 230)), (int(w * 0.008), int(h * 0.014)), sharp_mask)

    plate.paste(shadow, (0, 0), shadow)
    plate.paste(render_img, (0, 0), render_img)

    final = plate.convert("RGB")
    final = ImageEnhance.Contrast(final).enhance(1.12)
    final = ImageEnhance.Sharpness(final).enhance(1.26)
    final.save(output_jpg, "JPEG", quality=95, optimize=True)
    temp_render.unlink(missing_ok=True)
    print(f"[OK] Фотореалистичный рендер инженерного кронштейна готов: {output_jpg.name} ({output_jpg.stat().st_size // 1024} KB)")


def main():
    print("=== ВЫСОКОКАЧЕСТВЕННЫЙ РЕНДЕРИНГ КЛИПС И КРОНШТЕЙНА ===")
    render_cable_clips(MODELS_DIR / "cable_drop_clips.stl", IMAGES_DIR / "cable_drop_clips.jpg")
    render_engineering_bracket(MODELS_DIR / "custom_engineering_bracket.stl", IMAGES_DIR / "custom_engineering_part.jpg")
    print("\n[SUCCESS] Оба рендера успешно созданы!")


if __name__ == "__main__":
    main()
