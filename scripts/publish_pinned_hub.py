#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STL GARAGE — Pinned Hub Post Publisher
Публикует стильный навигационный пост-хаб в канал @stl_garage и закрепляет его.
"""
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.channel_publisher import send_api_request, CHANNEL_ID, SITE_URL, BOT_USERNAME
from scripts.config import BOOSTY_URL

def create_pinned_hub():
    text = (
        "🚀 <b>ДОБРО ПОЖАЛОВАТЬ В STL GARAGE!</b>\n"
        "<i>Лаборатория прецизионной 3D-печати и инженерной разработки</i>\n\n"
        "Мы создаем прочные технические изделия, корпуса для электроники, "
        "авто-аксессуары и индивидуальные детали на скоростных 3D-принтерах "
        "<b>Bambu Lab CoreXY</b> с точностью слоя от 0.08 мм.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🌐 <b>НАШ ОФИЦИАЛЬНЫЙ САЙТ И СЕРВИСЫ:</b>\n"
        f"👉 <a href=\"{SITE_URL}\">equimag.github.io/stl-garage</a>\n\n"
        "На сайте вам доступны:\n"
        "• <b>Интерактивный 3D-калькулятор</b> — мгновенный онлайн-расчет стоимости печати вашей модели (STL / STEP)\n"
        "• <b>Каталог готовых изделий</b> с подробными фото и характеристиками\n"
        "• <b>CAD-модели (STEP)</b> для прямого скачивания\n"
        "• <b>Быстрое оформление заказа</b> в 1 клик с отправкой в Telegram\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🛠 <b>НА ЧЕМ МЫ СПЕЦИАЛИЗИРУЕМСЯ:</b>\n"
        "🔹 <b>Корпуса для электроники & РЭА:</b> посадка в четверть с термозазором 0.2 мм, запрессованные латунные втулки М2/М3.\n"
        "🔹 <b>Автомобильный кастом:</b> усиленные клипсы обшивки, адаптеры, заглушки из термостойкого ABS/ASA (до 105°C).\n"
        "🔹 <b>Мастерская & Органайзеры:</b> магнитные рейлинги, компактные кейсы под биты и свёрла, ложементы.\n"
        "🔹 <b>Демпферы & Эластомеры:</b> виброопоры, ножки и фиксаторы кабелей из гибкого полиуретана TPU 95A.\n"
        "🔹 <b>Индивидуальная печать:</b> по вашим STL, STEP, чертежам или эскизам.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🗂 <b>БЫСТРАЯ НАВИГАЦИЯ ПО КАНАЛУ:</b>\n"
        "#каталог — готовые изделия и новинки мастерской\n"
        "#калькулятор — примеры расчетов и стоимость печати\n"
        "#кейсы — сложные клиентские заказы и решения «до/после»\n"
        "#инженерия — CAD-проекты и файлы STEP\n"
        "#авто — детали для авто и гаража\n"
        "#пластик — тесты и свойства PETG, ABS, TPU, Carbon\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📦 <b>ДОСТАВКА И ОПЛАТА:</b>\n"
        "Отправляем по всей РФ: <b>СДЭК</b>, <b>Почта России</b>, <b>Яндекс Доставка</b>. Изготовление — от 2 часов!\n\n"
        "💬 <b>Связаться с мастером / Заказать:</b> 👉 @STLGarage_bot\n"
        "☕ <b>Поддержать проект & Наборы STL:</b> 👉 boosty.to/stl_garage/donate"
    )

    buttons = [
        [
            {"text": "🌐 Открыть сайт и каталог", "url": SITE_URL},
            {"text": "🧮 Онлайн-калькулятор", "url": f"{SITE_URL}#calculator"}
        ],
        [
            {"text": "💬 Заказать у мастера", "url": f"https://t.me/{BOT_USERNAME}"},
            {"text": "☕ STL-наборы на Boosty", "url": BOOSTY_URL}
        ]
    ]

    res = send_api_request("sendMessage", {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": buttons},
        "disable_web_page_preview": False
    })

    if res.get("ok"):
        msg_id = res["result"]["message_id"]
        print(f"[OK] Пост опубликован, message_id={msg_id}")
        pin_res = send_api_request("pinChatMessage", {
            "chat_id": CHANNEL_ID,
            "message_id": msg_id,
            "disable_notification": False
        })
        print(f"[OK] Закрепление поста: {pin_res}")
        return msg_id
    else:
        print(f"[FAIL] Ошибка публикации: {res}")
        return None

if __name__ == "__main__":
    create_pinned_hub()
