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
from scripts.config import BOOSTY_URL, MASTER_USERNAME

def create_pinned_hub():
    text = (
        "🚀 <b>ДОБРО ПОЖАЛОВАТЬ В STL GARAGE!</b>\n"
        "<i>Лаборатория прецизионной 3D-печати и инженерной разработки</i>\n\n"
        "Мы создаем прочные технические изделия, корпуса для электроники, "
        "авто-аксессуары и индивидуальные детали на скоростных 3D-принтерах "
        "<b>Bambu Lab CoreXY</b> с точностью слоя от 0.08 мм.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🛠 <b>НАШИ ВОЗМОЖНОСТИ И МАТЕРИАЛЫ:</b>\n"
        "🔹 <b>Корпуса для электроники & РЭА:</b> посадка крышек в четверть с термозазором 0.2 мм, запрессованные латунные резьбовые втулки М2/М3.\n"
        "🔹 <b>Автомобильный кастом:</b> усиленные клипсы обшивки, адаптеры датчиков, заглушки из термостойкого ABS/ASA (до 105°C).\n"
        "🔹 <b>Мастерская & Органайзеры:</b> магнитные рейлинги, компактные кейсы под биты и свёрла, ложементы.\n"
        "🔹 <b>Демпферы & Эластомеры:</b> виброопоры, ножки и фиксаторы из гибкого полиуретана TPU 95A.\n"
        "🔹 <b>Индивидуальная печать:</b> по вашим STL, STEP, чертежам или эскизам от 2 часов!\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🧮 <b>ОНЛАЙН-СЕРВИСЫ И САЙТ:</b>\n"
        f"👉 <a href=\"{SITE_URL}\">equimag.github.io/stl-garage</a>\n"
        "• <b>3D-Калькулятор стоимости</b> — мгновенный онлайн-расчет по весу и материалу\n"
        "• <b>Инженерный каталог</b> с фотографиями, ценами и характеристиками\n"
        "• <b>Свободное скачивание CAD-моделей (.STEP)</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🗂 <b>БЫСТРАЯ НАВИГАЦИЯ ПО КАНАЛУ:</b>\n"
        "#каталог — готовые изделия и новинки\n"
        "#калькулятор — примеры расчетов и стоимость\n"
        "#кейсы — примеры заказов и решения «до/после»\n"
        "#инженерия — CAD-проекты и файлы STEP\n"
        "#авто — детали для авто и гаража\n"
        "#пластик — тесты и свойства PETG, ABS, TPU, Carbon\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📦 <b>КАК СДЕЛАТЬ ЗАКАЗ:</b>\n"
        "1. Нажмите кнопку <b>«💬 Написать мастеру»</b> ниже и отправьте ваш файл (.stl, .step, фото или чертёж) прямо в личку: @voovkamo.\n"
        "2. Согласуем материал, цвет, прочность и сроки.\n"
        "3. Отправляем готовые изделия по всей России: <b>СДЭК</b>, <b>Почта России</b>, <b>Яндекс Доставка</b>.\n\n"
        f"👤 <b>Инженер / Мастер:</b> @{MASTER_USERNAME}\n"
        f"🤖 <b>Бот-ассистент:</b> @{BOT_USERNAME}\n"
        f"🌐 <b>Наш сайт:</b> equimag.github.io/stl-garage"
    )

    buttons = [
        [
            {"text": "💬 Написать мастеру (@voovkamo)", "url": f"https://t.me/{MASTER_USERNAME}"}
        ],
        [
            {"text": "🧮 Онлайн-калькулятор", "url": f"{SITE_URL}#calculator"},
            {"text": "🌐 Каталог готовых деталей", "url": f"{SITE_URL}#catalog"}
        ],
        [
            {"text": "📦 Консультация по доставке / ТЗ", "url": f"https://t.me/{MASTER_USERNAME}?text=Здравствуйте!+Хочу+проконсультироваться+по+3D-печати"},
            {"text": "☕ Наборы на Boosty", "url": BOOSTY_URL}
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
