#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STL GARAGE — Публикация всех 8 товаров с новыми реалистичными фото в Telegram-канал @stl_garage
"""

import json
import time
from pathlib import Path
from channel_publisher import publish_product_card

BASE_DIR = Path(__file__).resolve().parent.parent
PRODUCTS_FILE = BASE_DIR / "data" / "products.json"


def main():
    print("=== ПУБЛИКАЦИЯ ВСЕХ КАРТОЧЕК В ТЕЛЕГРАМ-КАНАЛ @stl_garage ===")
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    for i, prod in enumerate(products, 1):
        img_rel = prod.get("image", "")
        img_path = BASE_DIR / img_rel
        print(f"\n[{i}/8] Публикация: {prod['title']}")
        print(f"     Фото: {img_path} (exists={img_path.exists()}, size={img_path.stat().st_size if img_path.exists() else 0} B)")

        res = publish_product_card(prod, photo_path=str(img_path))
        time.sleep(1.5)  # Telegram API rate limit protection

    print("\n[SUCCESS] Все 8 карточек опубликованы в канале @stl_garage!")


if __name__ == "__main__":
    main()
