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
    from config import BOT_TOKEN, CHANNEL_ID, CHANNEL_USERNAME, BOT_USERNAME, SITE_URL, MASTER_USERNAME
except ImportError:
    from scripts.config import BOT_TOKEN, CHANNEL_ID, CHANNEL_USERNAME, BOT_USERNAME, SITE_URL, MASTER_USERNAME


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


def send_photo(photo_path: str, caption: str, inline_buttons: list = None) -> dict:
    """Отправка фотографии в канал @stl_garage с подписью и кнопками."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    
    photo_file = Path(photo_path)
    if not photo_file.exists():
        print(f"[WARN] Файл фото не найден: {photo_path}, отправляем как текст.")
        return publish_post(caption, inline_buttons=inline_buttons)

    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = bytearray()

    def add_field(name, value):
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        body.extend(f"{value}\r\n".encode("utf-8"))

    add_field("chat_id", str(CHANNEL_ID))
    add_field("caption", caption)
    add_field("parse_mode", "HTML")

    if inline_buttons:
        add_field("reply_markup", json.dumps({"inline_keyboard": inline_buttons}))

    # Add photo
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="photo"; filename="{photo_file.name}"\r\n'.encode("utf-8"))
    body.extend(b"Content-Type: image/jpeg\r\n\r\n")
    with open(photo_file, "rb") as f:
        body.extend(f.read())
    body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        url,
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )

    try:
        with urllib.request.urlopen(req, timeout=25) as res:
            resp = json.loads(res.read().decode("utf-8"))
            if resp.get("ok"):
                msg_id = resp["result"]["message_id"]
                print(f"[SUCCESS] Фото и карточка опубликованы в @{CHANNEL_USERNAME}: id={msg_id}")
            return resp
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        print(f"[ERROR] sendPhoto HTTP {e.code}: {err_body}", file=sys.stderr)
        if "can't parse entities" in err_body:
            print("[WARN] Ошибка HTML сущностей в sendPhoto, отправляем с очищенным текстом...")
            clean_cap = re.sub(r'<[^>]+>', '', caption)
            return publish_post(clean_cap, inline_buttons=inline_buttons)
        return publish_post(caption, inline_buttons=inline_buttons)
    except Exception as e:
        print(f"[ERROR] sendPhoto failed: {e}", file=sys.stderr)
        return publish_post(caption, inline_buttons=inline_buttons)


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
        # Fallback: retry without HTML parse_mode if entity error
        if "can't parse entities" in str(res.get("error", "")):
            print("[WARN] Ошибка парсинга HTML, отправляем чистым текстом без тегов...")
            clean_text = re.sub(r'<[^>]+>', '', text)
            payload["text"] = clean_text
            payload.pop("parse_mode", None)
            res = send_api_request("sendMessage", payload)
            if res.get("ok"):
                print(f"[SUCCESS] Пост опубликован в @{CHANNEL_USERNAME} (plain text): id={res['result']['message_id']}")
                return res
        print(f"[FAILED] Ошибка публикации: {res}")
    return res


def publish_product_card(product: dict, photo_path: str = None, webapp_url: str = None) -> dict:
    """Форматированная публикация карточки товара из каталога."""
    title = product.get("title", "Новое изделие")
    price = product.get("price", 0)
    material = product.get("material", "PETG")
    layer = product.get("layer_height", "0.16 мм")
    infill = product.get("infill", "30%")
    desc = product.get("description", "")
    dims = product.get("dimensions", "")

    text = f"⚡ <b>НОВИНКА // STL GARAGE</b>\n\n"
    text += f"📦 <b>{title}</b>\n\n"
    text += f"{desc}\n\n"
    text += f"🔧 <b>Инженерные параметры детали:</b>\n"
    text += f"• Материал: <code>{material}</code>\n"
    text += f"• Высота слоя: <code>{layer}</code>\n"
    text += f"• Заполнение: <code>{infill}</code>\n"
    if dims:
        text += f"• Габариты: <code>{dims}</code>\n"
    text += f"\n💰 <b>Стоимость:</b> <b>{price} ₽</b>\n"
    text += f"🚀 <i>Быстрая печать на Bambu Lab и отправка в день готовности</i>\n"
    text += f"📍 Доставка по РФ (СДЭК, Почта России)\n\n"
    mat_tag = material.split('/')[0].split()[0].lower()
    text += f"#3dпечать #bambulab #{mat_tag} #stl_garage #производство"

    target_url = webapp_url or SITE_URL
    buttons = [
        [
            {"text": "🛒 Открыть в каталоге", "url": target_url},
            {"text": "💬 Заказать у мастера (@voovkamo)", "url": f"https://t.me/{MASTER_USERNAME}"}
        ]
    ]

    if photo_path and Path(photo_path).exists():
        return send_photo(photo_path, text, inline_buttons=buttons)

    return publish_post(text, inline_buttons=buttons)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        custom_text = " ".join(sys.argv[1:])
        publish_post(custom_text)
    else:
        print("Использование: python channel_publisher.py 'Текст поста'")
