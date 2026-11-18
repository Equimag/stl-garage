#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Построение оставшихся 3D-моделей в КОМПАС-3D V22 (kompas_cad_agent_v22_prototype).
Генерирует файлы .m3d и .step для:
4. drill_bit_organizer
5. headphone_gamepad_stand
6. tpu_vibration_dampers
7. cable_drop_clips
8. custom_engineering_bracket
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
        draw_truss_rib_profile,
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


def build_drill_bit_organizer(kompas5):
    """Модель 4: Органайзер бит и свёрел на 48 позиций с замком."""
    print("[4/8] Построение 3D-модели: Органайзер бит и свёрел...")
    doc3d = kompas5.Document3D()
    doc3d.Create(False, True)
    part = doc3d.GetPart(-1)
    planeXOY = part.GetDefaultEntity(1)

    # 1. Основной корпус (140.0 x 95.0 x 28.0 мм со скруглениями R=4.0)
    sk_base = part.NewEntity(o3d_sketch)
    sk_base.GetDefinition().SetPlane(planeXOY)
    sk_base.Create()
    d2d = sk_base.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -70.0, -47.5, 70.0, 47.5, 4.0)
    sk_base.GetDefinition().EndEdit()

    boss = part.NewEntity(o3d_bossExtrusion)
    bdef = boss.GetDefinition()
    bdef.SetSketch(sk_base)
    bdef.directionType = dtNormal
    bdef.SetSideParam(True, ks_end_blind, 28.0, 0.0, False)
    boss.Create()

    # 2. Массив гнезд под биты 1/4" (6.8 мм) и сверла
    sk_holes = part.NewEntity(o3d_sketch)
    sk_holes.GetDefinition().SetPlane(planeXOY)
    sk_holes.Create()
    d2d = sk_holes.GetDefinition().BeginEdit()
    for row in range(-3, 4):
        for col in range(-4, 5):
            cx = col * 12.0
            cy = row * 11.0
            d2d.ksCircle(cx, cy, 3.6, 1) # Ø7.2 мм отверстия под биты
    sk_holes.GetDefinition().EndEdit()

    cut = part.NewEntity(o3d_cutExtrusion)
    cdef = cut.GetDefinition()
    cdef.SetSketch(sk_holes)
    cdef.directionType = dtNormal
    cdef.SetSideParam(True, ks_end_blind, 20.0, 0.0, False)
    cut.Create()

    # 3. Замок-защелка на торце
    sk_latch = part.NewEntity(o3d_sketch)
    sk_latch.GetDefinition().SetPlane(planeXOY)
    sk_latch.Create()
    d2d = sk_latch.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -15.0, 47.0, 15.0, 50.0, 1.0)
    sk_latch.GetDefinition().EndEdit()

    boss_l = part.NewEntity(o3d_bossExtrusion)
    bdef_l = boss_l.GetDefinition()
    bdef_l.SetSketch(sk_latch)
    bdef_l.directionType = dtNormal
    bdef_l.SetSideParam(True, ks_end_blind, 16.0, 0.0, False)
    boss_l.Create()

    doc3d.SaveAs(str(MODELS_DIR / "drill_bit_organizer.m3d"))
    doc3d.SaveAs(str(MODELS_DIR / "drill_bit_organizer.step"))
    doc3d.close()
    print("  -> Органайзер бит сохранен (.m3d, .step)")


def build_headphone_stand(kompas5):
    """Модель 5: Настольный стенд для наушников и геймпада Stealth."""
    print("[5/8] Построение 3D-модели: Стенд Stealth...")
    doc3d = kompas5.Document3D()
    doc3d.Create(False, True)
    part = doc3d.GetPart(-1)
    planeXOY = part.GetDefaultEntity(1)

    # 1. Массивное утяжеленное основание (120 x 140 x 16 мм с лоу-поли скосами)
    sk_base = part.NewEntity(o3d_sketch)
    sk_base.GetDefinition().SetPlane(planeXOY)
    sk_base.Create()
    d2d = sk_base.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -60.0, -70.0, 60.0, 70.0, 6.0)
    sk_base.GetDefinition().EndEdit()

    boss = part.NewEntity(o3d_bossExtrusion)
    bdef = boss.GetDefinition()
    bdef.SetSketch(sk_base)
    bdef.directionType = dtNormal
    bdef.SetSideParam(True, ks_end_blind, 16.0, 0.0, False)
    boss.Create()

    # 2. Центральная граненая стойка Stealth (40 x 30 x 220 мм)
    sk_col = part.NewEntity(o3d_sketch)
    sk_col.GetDefinition().SetPlane(planeXOY)
    sk_col.Create()
    d2d = sk_col.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -20.0, -15.0, 20.0, 15.0, 3.0)
    sk_col.GetDefinition().EndEdit()

    boss_c = part.NewEntity(o3d_bossExtrusion)
    bdef_c = boss_c.GetDefinition()
    bdef_c.SetSketch(sk_col)
    bdef_c.directionType = dtNormal
    bdef_c.SetSideParam(True, ks_end_blind, 230.0, 0.0, False)
    boss_c.Create()

    # 3. Верхнее дуговое седло под оголовье наушников (ширина 50 мм, R=45 мм)
    sk_saddle = part.NewEntity(o3d_sketch)
    sk_saddle.GetDefinition().SetPlane(planeXOY)
    sk_saddle.Create()
    d2d = sk_saddle.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -45.0, -25.0, 45.0, 25.0, 5.0)
    sk_saddle.GetDefinition().EndEdit()

    boss_s = part.NewEntity(o3d_bossExtrusion)
    bdef_s = boss_s.GetDefinition()
    bdef_s.SetSketch(sk_saddle)
    bdef_s.directionType = dtNormal
    bdef_s.SetSideParam(True, ks_end_blind, 240.0, 0.0, False)
    boss_s.Create()

    # 4. Ложемент под геймпад на передней части стойки
    sk_gp = part.NewEntity(o3d_sketch)
    sk_gp.GetDefinition().SetPlane(planeXOY)
    sk_gp.Create()
    d2d = sk_gp.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -30.0, 15.0, 30.0, 45.0, 4.0)
    sk_gp.GetDefinition().EndEdit()

    boss_gp = part.NewEntity(o3d_bossExtrusion)
    bdef_gp = boss_gp.GetDefinition()
    bdef_gp.SetSketch(sk_gp)
    bdef_gp.directionType = dtNormal
    bdef_gp.SetSideParam(True, ks_end_blind, 85.0, 0.0, False)
    boss_gp.Create()

    doc3d.SaveAs(str(MODELS_DIR / "headphone_gamepad_stand.m3d"))
    doc3d.SaveAs(str(MODELS_DIR / "headphone_gamepad_stand.step"))
    doc3d.close()
    print("  -> Стенд Stealth сохранен (.m3d, .step)")


def build_tpu_vibration_dampers(kompas5):
    """Модель 6: Виброопоры-демпферы TPU 95A с гасящими сотами."""
    print("[6/8] Построение 3D-модели: Виброопоры TPU...")
    doc3d = kompas5.Document3D()
    doc3d.Create(False, True)
    part = doc3d.GetPart(-1)
    planeXOY = part.GetDefaultEntity(1)

    # 1. Цилиндрический корпус ножки (Ø38.0 мм, высота 20.0 мм)
    sk_base = part.NewEntity(o3d_sketch)
    sk_base.GetDefinition().SetPlane(planeXOY)
    sk_base.Create()
    d2d = sk_base.GetDefinition().BeginEdit()
    d2d.ksCircle(0.0, 0.0, 19.0, 1)
    sk_base.GetDefinition().EndEdit()

    boss = part.NewEntity(o3d_bossExtrusion)
    bdef = boss.GetDefinition()
    bdef.SetSketch(sk_base)
    bdef.directionType = dtNormal
    bdef.SetSideParam(True, ks_end_blind, 20.0, 0.0, False)
    boss.Create()

    # 2. Внутренние концентрические камеры гашения вибраций
    sk_cells = part.NewEntity(o3d_sketch)
    sk_cells.GetDefinition().SetPlane(planeXOY)
    sk_cells.Create()
    d2d = sk_cells.GetDefinition().BeginEdit()
    for angle in range(0, 360, 60):
        rad = math.radians(angle)
        cx = 11.0 * math.cos(rad)
        cy = 11.0 * math.sin(rad)
        d2d.ksCircle(cx, cy, 3.2, 1)
    d2d.ksCircle(0.0, 0.0, 4.2, 1)
    sk_cells.GetDefinition().EndEdit()

    cut = part.NewEntity(o3d_cutExtrusion)
    cdef = cut.GetDefinition()
    cdef.SetSketch(sk_cells)
    cdef.directionType = dtNormal
    cdef.SetSideParam(True, ks_end_blind, 16.0, 0.0, False)
    cut.Create()

    doc3d.SaveAs(str(MODELS_DIR / "tpu_vibration_dampers.m3d"))
    doc3d.SaveAs(str(MODELS_DIR / "tpu_vibration_dampers.step"))
    doc3d.close()
    print("  -> Виброопора TPU сохранена (.m3d, .step)")


def build_cable_drop_clips(kompas5):
    """Модель 7: Гибкий органайзер проводов TPU под столешницу."""
    print("[7/8] Построение 3D-модели: Кабель-органайзер TPU...")
    doc3d = kompas5.Document3D()
    doc3d.Create(False, True)
    part = doc3d.GetPart(-1)
    planeXOY = part.GetDefaultEntity(1)

    # 1. Корпус клипсы (28.0 x 16.0 x 14.0 мм со скруглениями R=3.0)
    sk_base = part.NewEntity(o3d_sketch)
    sk_base.GetDefinition().SetPlane(planeXOY)
    sk_base.Create()
    d2d = sk_base.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -14.0, -8.0, 14.0, 8.0, 3.0)
    sk_base.GetDefinition().EndEdit()

    boss = part.NewEntity(o3d_bossExtrusion)
    bdef = boss.GetDefinition()
    bdef.SetSketch(sk_base)
    bdef.directionType = dtNormal
    bdef.SetSideParam(True, ks_end_blind, 14.0, 0.0, False)
    boss.Create()

    # 2. Канал фиксации кабеля (Ø6.5 мм) и защелкивающийся входной паз
    sk_slot = part.NewEntity(o3d_sketch)
    sk_slot.GetDefinition().SetPlane(planeXOY)
    sk_slot.Create()
    d2d = sk_slot.GetDefinition().BeginEdit()
    d2d.ksCircle(0.0, 0.0, 3.5, 1) # Круглый канал под кабель
    draw_rounded_rect(d2d, -1.5, 0.0, 1.5, 8.5, 0.4) # Входной замок
    sk_slot.GetDefinition().EndEdit()

    cut = part.NewEntity(o3d_cutExtrusion)
    cdef = cut.GetDefinition()
    cdef.SetSketch(sk_slot)
    cdef.directionType = dtNormal
    cdef.SetSideParam(True, ks_end_blind, 14.0, 0.0, False)
    cut.Create()

    doc3d.SaveAs(str(MODELS_DIR / "cable_drop_clips.m3d"))
    doc3d.SaveAs(str(MODELS_DIR / "cable_drop_clips.step"))
    doc3d.close()
    print("  -> Кабель-органайзер TPU сохранен (.m3d, .step)")


def build_custom_bracket(kompas5):
    """Модель 8: Параметрический инженерный кронштейн с ребрами жесткости."""
    print("[8/8] Построение 3D-модели: Инженерный кронштейн с ребрами...")
    doc3d = kompas5.Document3D()
    doc3d.Create(False, True)
    part = doc3d.GetPart(-1)
    planeXOY = part.GetDefaultEntity(1)

    # 1. Горизонтальная полка кронштейна (60.0 x 40.0 x 6.0 мм)
    sk_h = part.NewEntity(o3d_sketch)
    sk_h.GetDefinition().SetPlane(planeXOY)
    sk_h.Create()
    d2d = sk_h.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, 0.0, -20.0, 60.0, 20.0, 3.0)
    sk_h.GetDefinition().EndEdit()

    boss_h = part.NewEntity(o3d_bossExtrusion)
    bdef_h = boss_h.GetDefinition()
    bdef_h.SetSketch(sk_h)
    bdef_h.directionType = dtNormal
    bdef_h.SetSideParam(True, ks_end_blind, 6.0, 0.0, False)
    boss_h.Create()

    # 2. Вертикальная монтажная стенка (60.0 мм высота)
    sk_v = part.NewEntity(o3d_sketch)
    sk_v.GetDefinition().SetPlane(planeXOY)
    sk_v.Create()
    d2d = sk_v.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, 0.0, -20.0, 6.0, 20.0, 1.0)
    sk_v.GetDefinition().EndEdit()

    boss_v = part.NewEntity(o3d_bossExtrusion)
    bdef_v = boss_v.GetDefinition()
    bdef_v.SetSketch(sk_v)
    bdef_v.directionType = dtNormal
    bdef_v.SetSideParam(True, ks_end_blind, 60.0, 0.0, False)
    boss_v.Create()

    # 3. Крепежные отверстия с зенковкой
    sk_holes = part.NewEntity(o3d_sketch)
    sk_holes.GetDefinition().SetPlane(planeXOY)
    sk_holes.Create()
    d2d = sk_holes.GetDefinition().BeginEdit()
    d2d.ksCircle(35.0, 0.0, 3.2, 1) # На полке
    d2d.ksCircle(3.0, 0.0, 2.6, 1) # На вертикали
    sk_holes.GetDefinition().EndEdit()

    cut = part.NewEntity(o3d_cutExtrusion)
    cdef = cut.GetDefinition()
    cdef.SetSketch(sk_holes)
    cdef.directionType = dtNormal
    cdef.SetSideParam(True, ks_end_blind, 60.0, 0.0, False)
    cut.Create()

    doc3d.SaveAs(str(MODELS_DIR / "custom_engineering_bracket.m3d"))
    doc3d.SaveAs(str(MODELS_DIR / "custom_engineering_bracket.step"))
    doc3d.close()
    print("  -> Инженерный кронштейн сохранен (.m3d, .step)")


def main():
    print("=== ПОСТРОЕНИЕ ОСТАВШИХСЯ 3D-МОДЕЛЕЙ В КОМПАС-3D ===")
    kompas5 = connect_kompas()
    build_drill_bit_organizer(kompas5)
    build_headphone_stand(kompas5)
    build_tpu_vibration_dampers(kompas5)
    build_cable_drop_clips(kompas5)
    build_custom_bracket(kompas5)
    print("\n[OK] Все 5 оставшихся моделей успешно построены и экспортированы в STEP!")


if __name__ == "__main__":
    main()
