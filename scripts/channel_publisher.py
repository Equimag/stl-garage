#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STL GARAGE — Telegram Channel Publisher
Автономная публикация постов, новинок каталога и анонсов в канал @stl_garage.
Работает на стандартной библиотеке Python без внешних зависимостей.
"""

import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path

# Load config
try:
    from config import BOT_TOKEN, CHANNEL_ID, CHANNEL_USERNAME, BOT_USERNAME, SITE_URL
except ImportError:
    from scripts.config import BOT_TOKEN, CHANNEL_ID, CHANNEL_USERNAME, BOT_USERNAME, SITE_URL


def send_api_request(method: str, payload: dict) -> dict:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"[ERROR] HTTP {e.code}: {err_body}", file=sys.stderr)
        return {"ok": False, "error": err_body}
    except Exception as e:
        print(f"[ERROR] Request failed: {e}", file=sys.stderr)
        return {"ok": False, "error": str(e)}


def publish_post(text: str, inline_buttons: list = None, disable_web_page_preview: bool = False) -> dict:
    """Публикация текстового сообщения в канал @stl_garage с кнопками."""
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": disable_web_page_preview
    }

    if inline_buttons:
        payload["reply_markup"] = {
            "inline_keyboard": inline_buttons
        }

    res = send_api_request("sendMessage", payload)
    if res.get("ok"):
        msg_id = res["result"]["message_id"]
        print(f"[SUCCESS] Пост опубликован в @{CHANNEL_USERNAME}: id={msg_id}")
    else:
        print(f"[FAILED] Ошибка публикации: {res}")
    return res


def publish_product_card(product: dict, webapp_url: str = None) -> dict:
    """Форматированная публикация карточки товара из каталога."""
    title = product.get("title", "Новое изделие")
    price = product.get("price", 0)
    material = product.get("material", "PETG")
    layer = product.get("layer_height", "0.16 мм")
    infill = product.get("infill", "30%")
    desc = product.get("description", "")
    dims = product.get("dimensions", "")

    text = f"⚡ <b>НОВИНКА В МАСТЕРСКОЙ // STL GARAGE</b>\n\n"
    text += f"📦 <b>{title}</b>\n\n"
    text += f"{desc}\n\n"
    text += f"🔧 <b>Инженерные параметры:</b>\n"
    text += f"• Пластик: <code>{material}</code>\n"
    text += f"• Высота слоя: <code>{layer}</code>\n"
    text += f"• Заполнение: <code>{infill}</code>\n"
    if dims:
        text += f"• Габариты: <code>{dims}</code>\n"
    text += f"\n💰 <b>Стоимость:</b> <b>{price} ₽</b>\n"
    text += f"📍 Доставка по РФ (СДЭК, Почта России)\n\n"
    text += f"#3dпечать #{material.split()[0].lower()} #stl_garage #товары"

    # Standard order buttons
    target_url = webapp_url or SITE_URL
    buttons = [
        [
            {"text": "🛒 Заказать на сайте", "url": target_url},
            {"text": "💬 Написать мастеру", "url": f"https://t.me/{BOT_USERNAME}"}
        ]
    ]

    return publish_post(text, inline_buttons=buttons)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        custom_text = " ".join(sys.argv[1:])
        publish_post(custom_text)
    else:
        print("Использование: python channel_publisher.py 'Текст поста'")
