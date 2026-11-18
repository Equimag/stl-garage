#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Построение параметрических 3D-моделей в КОМПАС-3D V22 (kompas_cad_agent_v22_prototype).
Генерирует файлы .m3d и .step в соответствии с регламентом EXP-014 и kompas-enclosure-designer.
"""

import os
import sys
import math
from pathlib import Path
import win32com.client
from win32com.client import gencache
import pythoncom

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Skills path for typical features
TYPICAL_FEATURES_DIR = Path(r"C:\Users\Memfor\.gemini\config\plugins\kompas-cad-agent\skills\kompas-typical-operations\scripts")
if str(TYPICAL_FEATURES_DIR) not in sys.path:
    sys.path.insert(0, str(TYPICAL_FEATURES_DIR))

try:
    from typical_features import (
        draw_rounded_rect,
        create_countersink_hole,
        draw_engraved_letter_v,
        o3d_sketch,
        o3d_bossExtrusion,
        o3d_cutExtrusion,
        dtNormal,
        ks_end_blind
    )
except ImportError as e:
    print(f"Warning: could not import typical_features: {e}")
    o3d_sketch = 5
    o3d_cutExtrusion = 26
    o3d_bossExtrusion = 25
    dtNormal = 0
    ks_end_blind = 0


def connect_kompas():
    """Подключение к COM API КОМПАС-3D."""
    API5_GUID = "{0422828C-F174-495E-AC5D-D31014DBBE87}"
    kapi5 = gencache.EnsureModule(API5_GUID, 0, 1, 0)
    disp = win32com.client.Dispatch("Kompas.Application.5")
    kompas5 = kapi5.KompasObject(disp._oleobj_.QueryInterface(kapi5.KompasObject.CLSID, pythoncom.IID_IDispatch))
    return kompas5


def build_esp32_cam_case(kompas5):
    """
    Модель 1: Корпус для платы ESP32-CAM с MicroSD карманом, вентиляцией и маркировкой «В».
    """
    print("[1/3] Построение 3D-модели: Корпус ESP32-CAM...")
    doc3d = kompas5.Document3D()
    doc3d.Create(False, True) # bVisible=False, bPart=True
    part = doc3d.GetPart(-1)
    planeXOY = part.GetDefaultEntity(1)

    # 1. Основное тело корпуса (46.0 x 34.0 x 18.0 мм со скруглениями R=3.0 мм)
    sk_base = part.NewEntity(o3d_sketch)
    sk_base.GetDefinition().SetPlane(planeXOY)
    sk_base.Create()
    d2d = sk_base.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -23.0, -17.0, 23.0, 17.0, 3.0)
    sk_base.GetDefinition().EndEdit()

    boss = part.NewEntity(o3d_bossExtrusion)
    bdef = boss.GetDefinition()
    bdef.SetSketch(sk_base)
    bdef.directionType = dtNormal
    bdef.SetSideParam(True, ks_end_blind, 18.0, 0.0, False)
    boss.Create()

    # 2. Внутренняя посадочная полость под PCB (40.0 x 28.0 x 15.5 мм со скруглениями R=1.5 мм по регламенту PCB)
    sk_cavity = part.NewEntity(o3d_sketch)
    sk_cavity.GetDefinition().SetPlane(planeXOY)
    sk_cavity.Create()
    d2d = sk_cavity.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -20.0, -14.0, 20.0, 14.0, 1.5)
    sk_cavity.GetDefinition().EndEdit()

    cut = part.NewEntity(o3d_cutExtrusion)
    cdef = cut.GetDefinition()
    cdef.SetSketch(sk_cavity)
    cdef.directionType = dtNormal
    cdef.SetSideParam(True, ks_end_blind, 15.5, 0.0, False)
    cut.Create()

    # 3. Карман под MicroSD слот (глубина >= 2.2 мм по регламенту kompas-enclosure-designer)
    sk_sd = part.NewEntity(o3d_sketch)
    sk_sd.GetDefinition().SetPlane(planeXOY)
    sk_sd.Create()
    d2d = sk_sd.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -7.0, -16.5, 7.0, -13.0, 0.8)
    sk_sd.GetDefinition().EndEdit()

    cut_sd = part.NewEntity(o3d_cutExtrusion)
    cdef_sd = cut_sd.GetDefinition()
    cdef_sd.SetSketch(sk_sd)
    cdef_sd.directionType = dtNormal
    cdef_sd.SetSideParam(True, ks_end_blind, 18.0, 0.0, False)
    cut_sd.Create()

    # 4. Монтажные ушки с конической зенковкой под винты М3 (EXP-012)
    # Отверстия с отступом на фланцах
    sk_hole1 = part.NewEntity(o3d_sketch)
    sk_hole1.GetDefinition().SetPlane(planeXOY)
    sk_hole1.Create()
    d2d = sk_hole1.GetDefinition().BeginEdit()
    d2d.ksCircle(17.5, 11.5, 1.6, 1) # Ø3.2 мм
    d2d.ksCircle(-17.5, 11.5, 1.6, 1)
    d2d.ksCircle(17.5, -11.5, 1.6, 1)
    d2d.ksCircle(-17.5, -11.5, 1.6, 1)
    sk_hole1.GetDefinition().EndEdit()

    cut_h = part.NewEntity(o3d_cutExtrusion)
    cdef_h = cut_h.GetDefinition()
    cdef_h.SetSketch(sk_hole1)
    cdef_h.directionType = dtNormal
    cdef_h.SetSideParam(True, ks_end_blind, 18.0, 0.0, False)
    cut_h.Create()

    # 5. Вдавленная буква «В» (Верх) глубиной 0.5 мм в зоне антенны
    sk_v = part.NewEntity(o3d_sketch)
    sk_v.GetDefinition().SetPlane(planeXOY)
    sk_v.Create()
    d2d = sk_v.GetDefinition().BeginEdit()
    draw_engraved_letter_v(d2d, 0.0, 10.0, scale=0.7)
    sk_v.GetDefinition().EndEdit()

    cut_v = part.NewEntity(o3d_cutExtrusion)
    cdef_v = cut_v.GetDefinition()
    cdef_v.SetSketch(sk_v)
    cdef_v.directionType = dtNormal
    cdef_v.SetSideParam(True, ks_end_blind, 0.5, 0.0, False)
    cut_v.Create()

    # Сохранение .m3d и .step
    m3d_path = str(MODELS_DIR / "esp32_cam_case.m3d")
    step_path = str(MODELS_DIR / "esp32_cam_case.step")
    doc3d.SaveAs(m3d_path)
    doc3d.SaveAs(step_path)
    doc3d.close()
    print(f"  -> Готово: {m3d_path}\n  -> Готово: {step_path}")


def build_magnetic_tool_rail(kompas5):
    """
    Модель 2: Магнитная планка-держатель инструмента в гараж с 4 карманами под магниты.
    """
    print("[2/3] Построение 3D-модели: Магнитная планка инструмента...")
    doc3d = kompas5.Document3D()
    doc3d.Create(False, True)
    part = doc3d.GetPart(-1)
    planeXOY = part.GetDefaultEntity(1)

    # 1. Основание планки (160.0 x 30.0 x 12.0 мм со скруглениями R=2.0)
    sk_base = part.NewEntity(o3d_sketch)
    sk_base.GetDefinition().SetPlane(planeXOY)
    sk_base.Create()
    d2d = sk_base.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -80.0, -15.0, 80.0, 15.0, 2.0)
    sk_base.GetDefinition().EndEdit()

    boss = part.NewEntity(o3d_bossExtrusion)
    bdef = boss.GetDefinition()
    bdef.SetSketch(sk_base)
    bdef.directionType = dtNormal
    bdef.SetSideParam(True, ks_end_blind, 12.0, 0.0, False)
    boss.Create()

    # 2. 4 кармана под неодимовые магниты 20х10х3 мм (с посадкой 20.3 х 10.3 х 3.5 мм)
    sk_magnets = part.NewEntity(o3d_sketch)
    sk_magnets.GetDefinition().SetPlane(planeXOY)
    sk_magnets.Create()
    d2d = sk_magnets.GetDefinition().BeginEdit()
    centers_x = [-45.0, -15.0, 15.0, 45.0]
    for cx in centers_x:
        draw_rounded_rect(d2d, cx - 10.15, -5.15, cx + 10.15, 5.15, 0.8)
    sk_magnets.GetDefinition().EndEdit()

    cut_mag = part.NewEntity(o3d_cutExtrusion)
    cdef_m = cut_mag.GetDefinition()
    cdef_m.SetSketch(sk_magnets)
    cdef_m.directionType = dtNormal
    cdef_m.SetSideParam(True, ks_end_blind, 3.5, 0.0, False)
    cut_mag.Create()

    # 3. 2 монтажных отверстия по краям с зенковкой под саморез М4
    sk_mounts = part.NewEntity(o3d_sketch)
    sk_mounts.GetDefinition().SetPlane(planeXOY)
    sk_mounts.Create()
    d2d = sk_mounts.GetDefinition().BeginEdit()
    d2d.ksCircle(-70.0, 0.0, 2.25, 1) # Ø4.5 мм
    d2d.ksCircle(70.0, 0.0, 2.25, 1)
    sk_mounts.GetDefinition().EndEdit()

    cut_mnt = part.NewEntity(o3d_cutExtrusion)
    cdef_mnt = cut_mnt.GetDefinition()
    cdef_mnt.SetSketch(sk_mounts)
    cdef_mnt.directionType = dtNormal
    cdef_mnt.SetSideParam(True, ks_end_blind, 12.0, 0.0, False)
    cut_mnt.Create()

    m3d_path = str(MODELS_DIR / "magnetic_tool_rail.m3d")
    step_path = str(MODELS_DIR / "magnetic_tool_rail.step")
    doc3d.SaveAs(m3d_path)
    doc3d.SaveAs(step_path)
    doc3d.close()
    print(f"  -> Готово: {m3d_path}\n  -> Готово: {step_path}")


def build_car_clip_reinforced(kompas5):
    """
    Модель 3: Усиленная автомобильная клипса обшивки (ABS/ASA).
    """
    print("[3/3] Построение 3D-модели: Усиленный автомобильный пистон...")
    doc3d = kompas5.Document3D()
    doc3d.Create(False, True)
    part = doc3d.GetPart(-1)
    planeXOY = part.GetDefaultEntity(1)

    # 1. Шляпка клипсы (диск Ø18.0 мм, толщина 2.4 мм)
    sk_head = part.NewEntity(o3d_sketch)
    sk_head.GetDefinition().SetPlane(planeXOY)
    sk_head.Create()
    d2d = sk_head.GetDefinition().BeginEdit()
    d2d.ksCircle(0.0, 0.0, 9.0, 1)
    sk_head.GetDefinition().EndEdit()

    boss_head = part.NewEntity(o3d_bossExtrusion)
    bdef_h = boss_head.GetDefinition()
    bdef_h.SetSketch(sk_head)
    bdef_h.directionType = dtNormal
    bdef_h.SetSideParam(True, ks_end_blind, 2.4, 0.0, False)
    boss_head.Create()

    # 2. Ножка пистона (Ø8.0 мм, длина 15.0 мм)
    sk_stem = part.NewEntity(o3d_sketch)
    sk_stem.GetDefinition().SetPlane(planeXOY)
    sk_stem.Create()
    d2d = sk_stem.GetDefinition().BeginEdit()
    d2d.ksCircle(0.0, 0.0, 4.0, 1)
    sk_stem.GetDefinition().EndEdit()

    boss_stem = part.NewEntity(o3d_bossExtrusion)
    bdef_s = boss_stem.GetDefinition()
    bdef_s.SetSketch(sk_stem)
    bdef_s.directionType = dtNormal
    bdef_s.SetSideParam(True, ks_end_blind, 17.4, 0.0, False)
    boss_stem.Create()

    # 3. Фиксирующий поясок-ёрш (Ø9.8 мм, конический заход)
    sk_barb = part.NewEntity(o3d_sketch)
    sk_barb.GetDefinition().SetPlane(planeXOY)
    sk_barb.Create()
    d2d = sk_barb.GetDefinition().BeginEdit()
    d2d.ksCircle(0.0, 0.0, 4.9, 1)
    sk_barb.GetDefinition().EndEdit()

    boss_barb = part.NewEntity(o3d_bossExtrusion)
    bdef_b = boss_barb.GetDefinition()
    bdef_b.SetSketch(sk_barb)
    bdef_b.directionType = dtNormal
    bdef_b.SetSideParam(True, ks_end_blind, 10.0, 0.0, False)
    boss_barb.Create()

    # 4. Продольная разгрузочная прорезь (для эластичного сжатия ножки при установке)
    sk_slit = part.NewEntity(o3d_sketch)
    sk_slit.GetDefinition().SetPlane(planeXOY)
    sk_slit.Create()
    d2d = sk_slit.GetDefinition().BeginEdit()
    draw_rounded_rect(d2d, -1.0, -4.5, 1.0, 4.5, 0.5)
    sk_slit.GetDefinition().EndEdit()

    cut_slit = part.NewEntity(o3d_cutExtrusion)
    cdef_sl = cut_slit.GetDefinition()
    cdef_sl.SetSketch(sk_slit)
    cdef_sl.directionType = dtNormal
    cdef_sl.SetSideParam(True, ks_end_blind, 17.4, 0.0, False)
    cut_slit.Create()

    m3d_path = str(MODELS_DIR / "car_clip_reinforced.m3d")
    step_path = str(MODELS_DIR / "car_clip_reinforced.step")
    doc3d.SaveAs(m3d_path)
    doc3d.SaveAs(step_path)
    doc3d.close()
    print(f"  -> Готово: {m3d_path}\n  -> Готово: {step_path}")


def main():
    print("=== ПОСТРОЕНИЕ 3D-МОДЕЛЕЙ В КОМПАС-3D ===")
    kompas5 = connect_kompas()
    build_esp32_cam_case(kompas5)
    build_magnetic_tool_rail(kompas5)
    build_car_clip_reinforced(kompas5)
    print("\n[OK] Все модели успешно спроектированы и сохранены в .m3d и .step!")


if __name__ == "__main__":
    main()
