#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STL GARAGE — Product Manager
Добавление и обновление изделий в каталоге data/products.json с автоматической публикацией в канал.
"""

import os
import sys
import json
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
PRODUCTS_FILE = BASE_DIR / "data" / "products.json"

try:
    from channel_publisher import publish_product_card
except ImportError:
    from scripts.channel_publisher import publish_product_card


def load_products():
    if not PRODUCTS_FILE.exists():
        return []
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_products(products):
    PRODUCTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"[OK] Каталог локально обновлен: {len(products)} товаров в {PRODUCTS_FILE}")

    # Auto sync with GitHub Pages
    try:
        import subprocess
        subprocess.run(["git", "add", "data/products.json"], cwd=str(BASE_DIR), check=True)
        subprocess.run(["git", "commit", "-m", "chore: update products catalog"], cwd=str(BASE_DIR), check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE_DIR), check=True)
        print("[OK] Изменения автоматически отправлены на сайт (GitHub Pages)!")
    except Exception as e:
        print(f"[WARN] Ошибка авто-синхронизации с GitHub: {e}")


def add_product(item: dict, publish_to_telegram: bool = False):
    """
    Добавляет товар в базу каталога.
    """
    products = load_products()
    
    # Check if exists
    existing = next((p for p in products if p["id"] == item["id"]), None)
    if existing:
        print(f"[WARN] Товар с ID '{item['id']}' уже существует. Обновляем...")
        products = [p if p["id"] != item["id"] else item for p in products]
    else:
        products.insert(0, item)  # Newest first

    save_products(products)

    if publish_to_telegram:
        print(f"[TG] Публикация карточки товара '{item['title']}' в канал...")
        publish_product_card(item)

    return item


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Добавление товара в каталог STL Garage")
    parser.add_argument("--id", required=True, help="Уникальный slug/ID товара (например: esp32-case)")
    parser.add_argument("--title", required=True, help="Название товара")
    parser.add_argument("--price", type=int, required=True, help="Цена в рублях")
    parser.add_argument("--category", default="enclosures", choices=["enclosures", "auto", "organizers", "gadgets", "custom"])
    parser.add_argument("--material", default="PETG", help="Тип пластика (PETG, PLA, ABS, TPU)")
    parser.add_argument("--layer", default="0.16 мм", help="Высота слоя")
    parser.add_argument("--infill", default="30%", help="Заполнение")
    parser.add_argument("--desc", default="", help="Описание изделия")
    parser.add_argument("--post", action="store_true", help="Опубликовать в Telegram-канал @stl_garage")

    args = parser.parse_args()

    cat_names = {
        "enclosures": "РЭА и Корпуса",
        "auto": "Авто & Мастерская",
        "organizers": "Органайзеры & Инструмент",
        "gadgets": "Гаджеты & Стенды",
        "custom": "Индивидуальный заказ"
    }

    new_item = {
        "id": args.id,
        "title": args.title,
        "category": args.category,
        "category_name": cat_names.get(args.category, "Изделия"),
        "price": args.price,
        "old_price": None,
        "material": args.material,
        "layer_height": args.layer,
        "infill": args.infill,
        "weight_g": 50,
        "print_time_h": "2.0 ч",
        "dimensions": "По ТЗ",
        "in_stock": True,
        "badge": "НОВИНКА",
        "description": args.desc or f"Качественная деталь из {args.material}, напечатанная на высокоскоростном 3D-принтере Bambu Lab.",
        "features": [
          f"Печать из проверенного пластика {args.material}",
          "Точность размеров и аккуратная поверхность"
        ]
    }

    add_product(new_item, publish_to_telegram=args.post)
