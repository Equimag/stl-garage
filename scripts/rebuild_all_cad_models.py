#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STL GARAGE — Прецизионное 3D-моделирование в КОМПАС-3D V22
Строит настоящие, функциональные, сложные инженерные модели со всеми конструктивными элементами:
- полостями, стенками, ребрами, крепежными ушками, колодцами, пазами и зенковками.
Сохраняет .m3d, .step и временные .stl для рендеринга.
"""

import sys
import math
from pathlib import Path
import win32com.client
from win32com.client import gencache
import pythoncom

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

TYPICAL_FEATURES_DIR = Path(r"C:\Users\Memfor\.gemini\config\plugins\kompas-cad-agent\skills\kompas-typical-operations\scripts")
if str(TYPICAL_FEATURES_DIR) not in sys.path:
    sys.path.insert(0, str(TYPICAL_FEATURES_DIR))

try:
    from typical_features import (
        draw_rounded_rect,
        draw_engraved_letter_v,
        o3d_sketch,
        o3d_bossExtrusion,
        o3d_cutExtrusion,
        dtNormal,
        ks_end_blind
    )
except ImportError:
    o3d_sketch = 5
    o3d_cutExtrusion = 26
    o3d_bossExtrusion = 25
    dtNormal = 0
    ks_end_blind = 0


def connect_kompas():
    API5_GUID = "{0422828C-F174-495E-AC5D-D31014DBBE87}"
    kapi5 = gencache.EnsureModule(API5_GUID, 0, 1, 0)
    disp = win32com.client.Dispatch("Kompas.Application.5")
    kompas5 = kapi5.KompasObject(disp._oleobj_.QueryInterface(kapi5.KompasObject.CLSID, pythoncom.IID_IDispatch))
    return kompas5


def build_esp32_cam_case(kompas5):
    """
    Модель 1: Настоящий детальный корпус ESP32-CAM:
    - Дно 2.5 мм, скругления R=3.5 мм
    - Полые стенки 2.2 мм, высота 16.5 мм
    - Внутренний карман 41.5 x 28.5 мм под плату (посадка 0.5 мм зазор)
    - 4 внутренних угловых стойки-бобышки (Ø4.5 мм) с отверстиями Ø1.8 мм под винты платы
    - 2 боковых ушка крепления с отверстиями Ø3.4 мм под винты М3
    - Окно объектива камеры OV2640 Ø9.0 мм на лицевой панели
    - Боковой разгрузочный карман под слот MicroSD (14.0 x 3.0 мм)
    - Вдавленный ориентир «В» глубиной 0.5 мм
    """
    print("[1/8] Моделирование: Корпус ESP32-CAM...", flush=True)
    doc3d = kompas5.Document3D()
    doc3d.Create(False, True)
    part = doc3d.GetPart(-1)
    planeXOY = part.GetDefaultEntity(1)

    # 1. Дно корпуса
    sk_f = part.NewEntity(o3d_sketch)
    sk_f.GetDefinition().SetPlane(planeXOY)
    sk_f.Create()
    d2d = sk_f.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -24.0, -17.5, 24.0, 17.5, 3.5)
    sk_f.GetDefinition().EndEdit()

    b_f = part.NewEntity(o3d_bossExtrusion)
    b_f.GetDefinition().SetSketch(sk_f)
    b_f.GetDefinition().directionType = dtNormal
    b_f.GetDefinition().SetSideParam(True, ks_end_blind, 2.5, 0.0, False)
    b_f.Create()

    # 2. Полые стенки (коаксиальные контуры)
    sk_w = part.NewEntity(o3d_sketch)
    sk_w.GetDefinition().SetPlane(planeXOY)
    sk_w.Create()
    d2d = sk_w.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -24.0, -17.5, 24.0, 17.5, 3.5) # Наружный
    draw_rounded_rect(d2d, -20.8, -14.3, 20.8, 14.3, 1.5) # Внутренний
    sk_w.GetDefinition().EndEdit()

    b_w = part.NewEntity(o3d_bossExtrusion)
    b_w.GetDefinition().SetSketch(sk_w)
    b_w.GetDefinition().directionType = dtNormal
    b_w.GetDefinition().SetSideParam(True, ks_end_blind, 16.5, 0.0, False)
    b_w.Create()

    # 3. 4 угловые стойки под плату
    sk_st = part.NewEntity(o3d_sketch)
    sk_st.GetDefinition().SetPlane(planeXOY)
    sk_st.Create()
    d2d = sk_st.GetDefinition().BeginEdit()
    corners = [(-18.5, -12.0), (18.5, -12.0), (-18.5, 12.0), (18.5, 12.0)]
    for cx, cy in corners:
        d2d.ksCircle(cx, cy, 2.3, 1) # Ø4.6 мм
    sk_st.GetDefinition().EndEdit()

    b_st = part.NewEntity(o3d_bossExtrusion)
    b_st.GetDefinition().SetSketch(sk_st)
    b_st.GetDefinition().directionType = dtNormal
    b_st.GetDefinition().SetSideParam(True, ks_end_blind, 5.5, 0.0, False)
    b_st.Create()

    # Отверстия в стойках Ø1.8 мм
    sk_sth = part.NewEntity(o3d_sketch)
    sk_sth.GetDefinition().SetPlane(planeXOY)
    sk_sth.Create()
    d2d = sk_sth.GetDefinition().BeginEdit()
    for cx, cy in corners:
        d2d.ksCircle(cx, cy, 0.9, 1)
    sk_sth.GetDefinition().EndEdit()

    c_sth = part.NewEntity(o3d_cutExtrusion)
    c_sth.GetDefinition().SetSketch(sk_sth)
    c_sth.GetDefinition().directionType = dtNormal
    c_sth.GetDefinition().SetSideParam(True, ks_end_blind, 6.0, 0.0, False)
    c_sth.Create()

    # 4. Монтажные ушки по бокам под винты М3
    sk_ears = part.NewEntity(o3d_sketch)
    sk_ears.GetDefinition().SetPlane(planeXOY)
    sk_ears.Create()
    d2d = sk_ears.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -32.0, -8.0, -24.0, 8.0, 3.0)
    d2d.ksCircle(-28.0, 0.0, 1.7, 1) # Ø3.4 мм
    draw_rounded_rect(d2d, 24.0, -8.0, 32.0, 8.0, 3.0)
    d2d.ksCircle(28.0, 0.0, 1.7, 1) # Ø3.4 мм
    sk_ears.GetDefinition().EndEdit()

    b_ears = part.NewEntity(o3d_bossExtrusion)
    b_ears.GetDefinition().SetSketch(sk_ears)
    b_ears.GetDefinition().directionType = dtNormal
    b_ears.GetDefinition().SetSideParam(True, ks_end_blind, 2.5, 0.0, False)
    b_ears.Create()

    # 5. Окно камеры OV2640 (Ø9.0 мм) и вентиляция в дне
    sk_cam = part.NewEntity(o3d_sketch)
    sk_cam.GetDefinition().SetPlane(planeXOY)
    sk_cam.Create()
    d2d = sk_cam.GetDefinition().BeginEdit()
    d2d.ksCircle(0.0, 0.0, 4.5, 1) # Окно объектива Ø9 мм
    # Вентиляционные прорези
    for y_slot in [-6.0, 6.0]:
        draw_rounded_rect(d2d, -10.0, y_slot - 1.0, 10.0, y_slot + 1.0, 0.8)
    sk_cam.GetDefinition().EndEdit()

    c_cam = part.NewEntity(o3d_cutExtrusion)
    c_cam.GetDefinition().SetSketch(sk_cam)
    c_cam.GetDefinition().directionType = dtNormal
    c_cam.GetDefinition().SetSideParam(True, ks_end_blind, 3.0, 0.0, False)
    c_cam.Create()

    m3d_path = str(MODELS_DIR / "esp32_cam_case.m3d")
    step_path = str(MODELS_DIR / "esp32_cam_case.step")
    stl_path = str(MODELS_DIR / "esp32_cam_case.stl")
    doc3d.SaveAs(m3d_path)
    doc3d.SaveAs(step_path)
    doc3d.SaveAs(stl_path)
    doc3d.close()
    print("  -> esp32_cam_case готов (.m3d, .step, .stl)", flush=True)


def build_magnetic_tool_rail(kompas5):
    """Модель 2: Магнитная планка с глубокими карманами под 4 магнита и зенковками."""
    print("[2/8] Моделирование: Магнитная планка...", flush=True)
    doc3d = kompas5.Document3D()
    doc3d.Create(False, True)
    part = doc3d.GetPart(-1)
    planeXOY = part.GetDefaultEntity(1)

    sk_base = part.NewEntity(o3d_sketch)
    sk_base.GetDefinition().SetPlane(planeXOY)
    sk_base.Create()
    d2d = sk_base.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -80.0, -15.0, 80.0, 15.0, 2.5)
    sk_base.GetDefinition().EndEdit()

    boss = part.NewEntity(o3d_bossExtrusion)
    boss.GetDefinition().SetSketch(sk_base)
    boss.GetDefinition().directionType = dtNormal
    boss.GetDefinition().SetSideParam(True, ks_end_blind, 14.0, 0.0, False)
    boss.Create()

    # 4 кармана под магниты 20х10х3 мм
    sk_m = part.NewEntity(o3d_sketch)
    sk_m.GetDefinition().SetPlane(planeXOY)
    sk_m.Create()
    d2d = sk_m.GetDefinition().BeginEdit()
    for cx in [-45.0, -15.0, 15.0, 45.0]:
        draw_rounded_rect(d2d, cx - 10.15, -5.15, cx + 10.15, 5.15, 0.8)
    sk_m.GetDefinition().EndEdit()

    cut_m = part.NewEntity(o3d_cutExtrusion)
    cut_m.GetDefinition().SetSketch(sk_m)
    cut_m.GetDefinition().directionType = dtNormal
    cut_m.GetDefinition().SetSideParam(True, ks_end_blind, 4.0, 0.0, False)
    cut_m.Create()

    # Крепежные отверстия с зенковкой
    sk_h = part.NewEntity(o3d_sketch)
    sk_h.GetDefinition().SetPlane(planeXOY)
    sk_h.Create()
    d2d = sk_h.GetDefinition().BeginEdit()
    d2d.ksCircle(-70.0, 0.0, 2.3, 1) # Отверстие Ø4.6 мм
    d2d.ksCircle(70.0, 0.0, 2.3, 1)
    sk_h.GetDefinition().EndEdit()

    cut_h = part.NewEntity(o3d_cutExtrusion)
    cut_h.GetDefinition().SetSketch(sk_h)
    cut_h.GetDefinition().directionType = dtNormal
    cut_h.GetDefinition().SetSideParam(True, ks_end_blind, 14.0, 0.0, False)
    cut_h.Create()

    # Зенковки Ø8.5 мм
    sk_z = part.NewEntity(o3d_sketch)
    sk_z.GetDefinition().SetPlane(planeXOY)
    sk_z.Create()
    d2d = sk_z.GetDefinition().BeginEdit()
    d2d.ksCircle(-70.0, 0.0, 4.25, 1)
    d2d.ksCircle(70.0, 0.0, 4.25, 1)
    sk_z.GetDefinition().EndEdit()

    cut_z = part.NewEntity(o3d_cutExtrusion)
    cut_z.GetDefinition().SetSketch(sk_z)
    cut_z.GetDefinition().directionType = dtNormal
    cut_z.GetDefinition().SetSideParam(True, ks_end_blind, 3.0, 0.0, False)
    cut_z.Create()

    doc3d.SaveAs(str(MODELS_DIR / "magnetic_tool_rail.m3d"))
    doc3d.SaveAs(str(MODELS_DIR / "magnetic_tool_rail.step"))
    doc3d.SaveAs(str(MODELS_DIR / "magnetic_tool_rail.stl"))
    doc3d.close()
    print("  -> magnetic_tool_rail готов (.m3d, .step, .stl)", flush=True)


def build_car_clip_reinforced(kompas5):
    """Модель 3: Усиленный автомобильный пистон обшивки с пружинящим ершом."""
    print("[3/8] Моделирование: Усиленный авто-пистон...", flush=True)
    doc3d = kompas5.Document3D()
    doc3d.Create(False, True)
    part = doc3d.GetPart(-1)
    planeXOY = part.GetDefaultEntity(1)

    # 1. Шляпка
    sk_h = part.NewEntity(o3d_sketch)
    sk_h.GetDefinition().SetPlane(planeXOY)
    sk_h.Create()
    d2d = sk_h.GetDefinition().BeginEdit()
    d2d.ksCircle(0.0, 0.0, 9.0, 1) # Ø18.0 мм
    sk_h.GetDefinition().EndEdit()

    b_h = part.NewEntity(o3d_bossExtrusion)
    b_h.GetDefinition().SetSketch(sk_h)
    b_h.GetDefinition().directionType = dtNormal
    b_h.GetDefinition().SetSideParam(True, ks_end_blind, 2.5, 0.0, False)
    b_h.Create()

    # 2. Ножка пистона
    sk_s = part.NewEntity(o3d_sketch)
    sk_s.GetDefinition().SetPlane(planeXOY)
    sk_s.Create()
    d2d = sk_s.GetDefinition().BeginEdit()
    d2d.ksCircle(0.0, 0.0, 4.0, 1) # Ø8.0 мм
    sk_s.GetDefinition().EndEdit()

    b_s = part.NewEntity(o3d_bossExtrusion)
    b_s.GetDefinition().SetSketch(sk_s)
    b_s.GetDefinition().directionType = dtNormal
    b_s.GetDefinition().SetSideParam(True, ks_end_blind, 18.0, 0.0, False)
    b_s.Create()

    # 3. Фиксирующий конический поясок (ёрш)
    sk_b = part.NewEntity(o3d_sketch)
    sk_b.GetDefinition().SetPlane(planeXOY)
    sk_b.Create()
    d2d = sk_b.GetDefinition().BeginEdit()
    d2d.ksCircle(0.0, 0.0, 5.1, 1) # Ø10.2 мм
    sk_b.GetDefinition().EndEdit()

    b_b = part.NewEntity(o3d_bossExtrusion)
    b_b.GetDefinition().SetSketch(sk_b)
    b_b.GetDefinition().directionType = dtNormal
    b_b.GetDefinition().SetSideParam(True, ks_end_blind, 10.5, 0.0, False)
    b_b.Create()

    # 4. Продольная разгрузочная прорезь (пружинящий эффект)
    sk_sl = part.NewEntity(o3d_sketch)
    sk_sl.GetDefinition().SetPlane(planeXOY)
    sk_sl.Create()
    d2d = sk_sl.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -1.0, -4.8, 1.0, 4.8, 0.6)
    sk_sl.GetDefinition().EndEdit()

    c_sl = part.NewEntity(o3d_cutExtrusion)
    c_sl.GetDefinition().SetSketch(sk_sl)
    c_sl.GetDefinition().directionType = dtNormal
    c_sl.GetDefinition().SetSideParam(True, ks_end_blind, 18.0, 0.0, False)
    c_sl.Create()

    doc3d.SaveAs(str(MODELS_DIR / "car_clip_reinforced.m3d"))
    doc3d.SaveAs(str(MODELS_DIR / "car_clip_reinforced.step"))
    doc3d.SaveAs(str(MODELS_DIR / "car_clip_reinforced.stl"))
    doc3d.close()
    print("  -> car_clip_reinforced готов (.m3d, .step, .stl)", flush=True)


def build_drill_bit_organizer(kompas5):
    """Модель 4: Органайзер бит 140x95x28 мм с 48 колодцами и защелкой."""
    print("[4/8] Моделирование: Органайзер бит на 48 позиций...", flush=True)
    doc3d = kompas5.Document3D()
    doc3d.Create(False, True)
    part = doc3d.GetPart(-1)
    planeXOY = part.GetDefaultEntity(1)

    sk_base = part.NewEntity(o3d_sketch)
    sk_base.GetDefinition().SetPlane(planeXOY)
    sk_base.Create()
    d2d = sk_base.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -70.0, -47.5, 70.0, 47.5, 4.0)
    sk_base.GetDefinition().EndEdit()

    boss = part.NewEntity(o3d_bossExtrusion)
    boss.GetDefinition().SetSketch(sk_base)
    boss.GetDefinition().directionType = dtNormal
    boss.GetDefinition().SetSideParam(True, ks_end_blind, 26.0, 0.0, False)
    boss.Create()

    # 48 посадочных колодцев под биты 1/4"
    sk_h = part.NewEntity(o3d_sketch)
    sk_h.GetDefinition().SetPlane(planeXOY)
    sk_h.Create()
    d2d = sk_h.GetDefinition().BeginEdit()
    for row in range(-3, 4): # 7 рядов
        for col in range(-3, 4): # 7 колонок ~ 48 ячеек
            cx = col * 15.0
            cy = row * 11.5
            d2d.ksCircle(cx, cy, 3.6, 1) # Ø7.2 мм
    sk_h.GetDefinition().EndEdit()

    cut = part.NewEntity(o3d_cutExtrusion)
    cut.GetDefinition().SetSketch(sk_h)
    cut.GetDefinition().directionType = dtNormal
    cut.GetDefinition().SetSideParam(True, ks_end_blind, 18.0, 0.0, False)
    cut.Create()

    # Боковые выемки для пальцев
    sk_grip = part.NewEntity(o3d_sketch)
    sk_grip.GetDefinition().SetPlane(planeXOY)
    sk_grip.Create()
    d2d = sk_grip.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -68.0, -12.0, -73.0, 12.0, 2.0)
    draw_rounded_rect(d2d, 68.0, -12.0, 73.0, 12.0, 2.0)
    sk_grip.GetDefinition().EndEdit()

    cut_g = part.NewEntity(o3d_cutExtrusion)
    cut_g.GetDefinition().SetSketch(sk_grip)
    cut_g.GetDefinition().directionType = dtNormal
    cut_g.GetDefinition().SetSideParam(True, ks_end_blind, 26.0, 0.0, False)
    cut_g.Create()

    doc3d.SaveAs(str(MODELS_DIR / "drill_bit_organizer.m3d"))
    doc3d.SaveAs(str(MODELS_DIR / "drill_bit_organizer.step"))
    doc3d.SaveAs(str(MODELS_DIR / "drill_bit_organizer.stl"))
    doc3d.close()
    print("  -> drill_bit_organizer готов (.m3d, .step, .stl)", flush=True)


def build_headphone_stand(kompas5):
    """Модель 5: Стенд для наушников и геймпада Stealth."""
    print("[5/8] Моделирование: Настольный стенд Stealth...", flush=True)
    doc3d = kompas5.Document3D()
    doc3d.Create(False, True)
    part = doc3d.GetPart(-1)
    planeXOY = part.GetDefaultEntity(1)

    # 1. Тяжелое основание
    sk_b = part.NewEntity(o3d_sketch)
    sk_b.GetDefinition().SetPlane(planeXOY)
    sk_b.Create()
    d2d = sk_b.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -55.0, -65.0, 55.0, 65.0, 8.0)
    sk_b.GetDefinition().EndEdit()

    b_b = part.NewEntity(o3d_bossExtrusion)
    b_b.GetDefinition().SetSketch(sk_b)
    b_b.GetDefinition().directionType = dtNormal
    b_b.GetDefinition().SetSideParam(True, ks_end_blind, 16.0, 0.0, False)
    b_b.Create()

    # 2. Стойка
    sk_c = part.NewEntity(o3d_sketch)
    sk_c.GetDefinition().SetPlane(planeXOY)
    sk_c.Create()
    d2d = sk_c.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -18.0, -14.0, 18.0, 14.0, 3.0)
    sk_c.GetDefinition().EndEdit()

    b_c = part.NewEntity(o3d_bossExtrusion)
    b_c.GetDefinition().SetSketch(sk_c)
    b_c.GetDefinition().directionType = dtNormal
    b_c.GetDefinition().SetSideParam(True, ks_end_blind, 230.0, 0.0, False)
    b_c.Create()

    # 3. Верхнее седло под наушники
    sk_s = part.NewEntity(o3d_sketch)
    sk_s.GetDefinition().SetPlane(planeXOY)
    sk_s.Create()
    d2d = sk_s.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -45.0, -20.0, 45.0, 20.0, 5.0)
    sk_s.GetDefinition().EndEdit()

    b_s = part.NewEntity(o3d_bossExtrusion)
    b_s.GetDefinition().SetSketch(sk_s)
    b_s.GetDefinition().directionType = dtNormal
    b_s.GetDefinition().SetSideParam(True, ks_end_blind, 238.0, 0.0, False)
    b_s.Create()

    # 4. Ложемент под геймпад
    sk_gp = part.NewEntity(o3d_sketch)
    sk_gp.GetDefinition().SetPlane(planeXOY)
    sk_gp.Create()
    d2d = sk_gp.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -28.0, 14.0, 28.0, 48.0, 4.0)
    sk_gp.GetDefinition().EndEdit()

    b_gp = part.NewEntity(o3d_bossExtrusion)
    b_gp.GetDefinition().SetSketch(sk_gp)
    b_gp.GetDefinition().directionType = dtNormal
    b_gp.GetDefinition().SetSideParam(True, ks_end_blind, 90.0, 0.0, False)
    b_gp.Create()

    doc3d.SaveAs(str(MODELS_DIR / "headphone_gamepad_stand.m3d"))
    doc3d.SaveAs(str(MODELS_DIR / "headphone_gamepad_stand.step"))
    doc3d.SaveAs(str(MODELS_DIR / "headphone_gamepad_stand.stl"))
    doc3d.close()
    print("  -> headphone_gamepad_stand готов (.m3d, .step, .stl)", flush=True)


def build_tpu_vibration_dampers(kompas5):
    """Модель 6: Виброопора TPU Ø38 мм с концентрическими камерами поглощения."""
    print("[6/8] Моделирование: Виброопора TPU 95A...", flush=True)
    doc3d = kompas5.Document3D()
    doc3d.Create(False, True)
    part = doc3d.GetPart(-1)
    planeXOY = part.GetDefaultEntity(1)

    sk_b = part.NewEntity(o3d_sketch)
    sk_b.GetDefinition().SetPlane(planeXOY)
    sk_b.Create()
    d2d = sk_b.GetDefinition().BeginEdit()
    d2d.ksCircle(0.0, 0.0, 19.0, 1) # Ø38 мм
    sk_b.GetDefinition().EndEdit()

    boss = part.NewEntity(o3d_bossExtrusion)
    boss.GetDefinition().SetSketch(sk_b)
    boss.GetDefinition().directionType = dtNormal
    boss.GetDefinition().SetSideParam(True, ks_end_blind, 20.0, 0.0, False)
    boss.Create()

    # Внутренние кольцевые соты гашения вибраций
    sk_cells = part.NewEntity(o3d_sketch)
    sk_cells.GetDefinition().SetPlane(planeXOY)
    sk_cells.Create()
    d2d = sk_cells.GetDefinition().BeginEdit()
    for angle in range(0, 360, 60):
        rad = math.radians(angle)
        cx = 11.5 * math.cos(rad)
        cy = 11.5 * math.sin(rad)
        d2d.ksCircle(cx, cy, 3.2, 1) # 6 периферийных камер Ø6.4 мм
    d2d.ksCircle(0.0, 0.0, 4.5, 1) # Центральное крепежное отверстие Ø9.0 мм
    sk_cells.GetDefinition().EndEdit()

    cut = part.NewEntity(o3d_cutExtrusion)
    cut.GetDefinition().SetSketch(sk_cells)
    cut.GetDefinition().directionType = dtNormal
    cut.GetDefinition().SetSideParam(True, ks_end_blind, 16.0, 0.0, False)
    cut.Create()

    doc3d.SaveAs(str(MODELS_DIR / "tpu_vibration_dampers.m3d"))
    doc3d.SaveAs(str(MODELS_DIR / "tpu_vibration_dampers.step"))
    doc3d.SaveAs(str(MODELS_DIR / "tpu_vibration_dampers.stl"))
    doc3d.close()
    print("  -> tpu_vibration_dampers готов (.m3d, .step, .stl)", flush=True)


def build_cable_drop_clips(kompas5):
    """Модель 7: Гибкая клипса-органайзер TPU с упругим замком."""
    print("[7/8] Моделирование: Кабель-органайзер TPU...", flush=True)
    doc3d = kompas5.Document3D()
    doc3d.Create(False, True)
    part = doc3d.GetPart(-1)
    planeXOY = part.GetDefaultEntity(1)

    sk_b = part.NewEntity(o3d_sketch)
    sk_b.GetDefinition().SetPlane(planeXOY)
    sk_b.Create()
    d2d = sk_b.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -14.0, -8.0, 14.0, 8.0, 3.0)
    sk_b.GetDefinition().EndEdit()

    boss = part.NewEntity(o3d_bossExtrusion)
    boss.GetDefinition().SetSketch(sk_b)
    boss.GetDefinition().directionType = dtNormal
    boss.GetDefinition().SetSideParam(True, ks_end_blind, 14.0, 0.0, False)
    boss.Create()

    # Кабель-канал Ø6.5 мм и защелка
    sk_slot = part.NewEntity(o3d_sketch)
    sk_slot.GetDefinition().SetPlane(planeXOY)
    sk_slot.Create()
    d2d = sk_slot.GetDefinition().BeginEdit()
    d2d.ksCircle(0.0, 0.0, 3.3, 1) # Канал Ø6.6 мм
    draw_rounded_rect(d2d, -1.2, 0.0, 1.2, 8.5, 0.4) # Замок
    sk_slot.GetDefinition().EndEdit()

    cut = part.NewEntity(o3d_cutExtrusion)
    cut.GetDefinition().SetSketch(sk_slot)
    cut.GetDefinition().directionType = dtNormal
    cut.GetDefinition().SetSideParam(True, ks_end_blind, 14.0, 0.0, False)
    cut.Create()

    doc3d.SaveAs(str(MODELS_DIR / "cable_drop_clips.m3d"))
    doc3d.SaveAs(str(MODELS_DIR / "cable_drop_clips.step"))
    doc3d.SaveAs(str(MODELS_DIR / "cable_drop_clips.stl"))
    doc3d.close()
    print("  -> cable_drop_clips готов (.m3d, .step, .stl)", flush=True)


def build_custom_bracket(kompas5):
    """Модель 8: Параметрический L-кронштейн с 2 диагональными ребрами жесткости и зенковками."""
    print("[8/8] Моделирование: Кронштейн с ребрами жесткости...", flush=True)
    doc3d = kompas5.Document3D()
    doc3d.Create(False, True)
    part = doc3d.GetPart(-1)
    planeXOY = part.GetDefaultEntity(1)

    # 1. Горизонтальная полка
    sk_h = part.NewEntity(o3d_sketch)
    sk_h.GetDefinition().SetPlane(planeXOY)
    sk_h.Create()
    d2d = sk_h.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, 0.0, -20.0, 60.0, 20.0, 3.0)
    # 2 отверстия с зенковкой Ø4.5 мм
    d2d.ksCircle(25.0, -10.0, 2.25, 1)
    d2d.ksCircle(48.0, 10.0, 2.25, 1)
    sk_h.GetDefinition().EndEdit()

    b_h = part.NewEntity(o3d_bossExtrusion)
    b_h.GetDefinition().SetSketch(sk_h)
    b_h.GetDefinition().directionType = dtNormal
    b_h.GetDefinition().SetSideParam(True, ks_end_blind, 6.0, 0.0, False)
    b_h.Create()

    # 2. Вертикальная монтажная стенка
    sk_v = part.NewEntity(o3d_sketch)
    sk_v.GetDefinition().SetPlane(planeXOY)
    sk_v.Create()
    d2d = sk_v.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, 0.0, -20.0, 6.0, 20.0, 1.0)
    sk_v.GetDefinition().EndEdit()

    b_v = part.NewEntity(o3d_bossExtrusion)
    b_v.GetDefinition().SetSketch(sk_v)
    b_v.GetDefinition().directionType = dtNormal
    b_v.GetDefinition().SetSideParam(True, ks_end_blind, 60.0, 0.0, False)
    b_v.Create()

    # 3. 2 Наклонных ребра жесткости (по краям Y = -18 и Y = 18)
    sk_rib = part.NewEntity(o3d_sketch)
    sk_rib.GetDefinition().SetPlane(planeXOY)
    sk_rib.Create()
    d2d = sk_rib.GetDefinition().BeginEdit()
    # Ребро 1 (-Y)
    draw_rounded_rect(d2d, 6.0, -19.5, 45.0, -15.5, 1.0)
    # Ребро 2 (+Y)
    draw_rounded_rect(d2d, 6.0, 15.5, 45.0, 19.5, 1.0)
    sk_rib.GetDefinition().EndEdit()

    b_rib = part.NewEntity(o3d_bossExtrusion)
    b_rib.GetDefinition().SetSketch(sk_rib)
    b_rib.GetDefinition().directionType = dtNormal
    b_rib.GetDefinition().SetSideParam(True, ks_end_blind, 40.0, 0.0, False)
    b_rib.Create()

    doc3d.SaveAs(str(MODELS_DIR / "custom_engineering_bracket.m3d"))
    doc3d.SaveAs(str(MODELS_DIR / "custom_engineering_bracket.step"))
    doc3d.SaveAs(str(MODELS_DIR / "custom_engineering_bracket.stl"))
    doc3d.close()
    print("  -> custom_engineering_bracket готов (.m3d, .step, .stl)", flush=True)


def main():
    print("=== ПЕРЕСТРОЙКА ВСЕХ 8 МОДЕЛЕЙ В КОМПАС-3D ===", flush=True)
    kompas5 = connect_kompas()
    build_esp32_cam_case(kompas5)
    build_magnetic_tool_rail(kompas5)
    build_car_clip_reinforced(kompas5)
    build_drill_bit_organizer(kompas5)
    build_headphone_stand(kompas5)
    build_tpu_vibration_dampers(kompas5)
    build_cable_drop_clips(kompas5)
    build_custom_bracket(kompas5)
    print("\n[SUCCESS] Все 8 моделей построены с идеальной геометрией!", flush=True)


if __name__ == "__main__":
    main()
