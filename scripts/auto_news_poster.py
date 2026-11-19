#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STL GARAGE — Автономный AI-новостник 3D-печати
Сбор новостей из проверенных RSS-лент, адаптация через Google Gemini и публикация в @stl_garage.
"""

import sys
import os
import re
import json
import time
import datetime
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path

# Determine project root directory whether running from scripts/ or root
current_dir = Path(__file__).resolve().parent
if current_dir.name == "scripts":
    ROOT_DIR = current_dir.parent
else:
    ROOT_DIR = current_dir

sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "scripts"))

try:
    from config import BOT_TOKEN, CHANNEL_ID, CHANNEL_USERNAME, BOT_USERNAME, SITE_URL, GEMINI_API_KEY
    from channel_publisher import send_photo, publish_post
except ImportError:
    from scripts.config import BOT_TOKEN, CHANNEL_ID, CHANNEL_USERNAME, BOT_USERNAME, SITE_URL, GEMINI_API_KEY
    from scripts.channel_publisher import send_photo, publish_post

HISTORY_FILE = ROOT_DIR / "data" / "published_news.json"
TEMP_DIR = ROOT_DIR / "scratch"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8'
}

NEWS_FEEDS = [
    {
        "name": "3D Printing Industry",
        "url": "https://3dprintingindustry.com/feed/",
        "lang": "en"
    },
    {
        "name": "3DPrint.com",
        "url": "https://3dprint.com/feed/",
        "lang": "en"
    },
    {
        "name": "3D Natives",
        "url": "https://www.3dnatives.com/en/feed/",
        "lang": "en"
    },
    {
        "name": "3DToday News",
        "url": "https://3dtoday.ru/rss/news",
        "lang": "ru"
    },
    {
        "name": "Tom's Hardware 3D",
        "url": "https://www.tomshardware.com/feeds/tag/3d-printer",
        "lang": "en"
    }
]


def load_history() -> list:
    """Загрузка истории опубликованных новостей."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Ошибка чтения {HISTORY_FILE}: {e}")
        return []


def save_history(history: list):
    """Сохранение истории опубликованных новостей (храним последние 200 записей)."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    trimmed = history[-200:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, ensure_ascii=False, indent=2)


def fetch_feed_items(feed_info: dict) -> list:
    """Парсинг RSS-ленты и извлечение кандидатов."""
    items_found = []
    try:
        req = urllib.request.Request(feed_info["url"], headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = resp.read()
            root = ET.fromstring(content)

            for item in root.findall(".//item"):
                title = item.find("title")
                link = item.find("link")
                if title is None or link is None or not title.text or not link.text:
                    continue

                title_text = title.text.strip()
                link_text = link.text.strip()

                desc = item.find("description")
                desc_text = desc.text.strip() if desc is not None and desc.text else ""
                clean_desc = re.sub(r"<[^>]+>", " ", desc_text).strip()

                # Поиск изображения прямо в тегах RSS
                image_url = None
                for child in item:
                    # Enclosure
                    if child.tag == "enclosure" and child.attrib.get("type", "").startswith("image/"):
                        image_url = child.attrib.get("url")
                        break
                    # Media content or thumbnail
                    if "content" in child.tag or "thumbnail" in child.tag:
                        u = child.attrib.get("url")
                        if u and any(ext in u.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                            image_url = u
                            break

                items_found.append({
                    "title": title_text,
                    "link": link_text,
                    "desc": clean_desc[:1000],
                    "image": image_url,
                    "source": feed_info["name"],
                    "lang": feed_info["lang"]
                })
    except Exception as e:
        print(f"[WARN] Ошибка загрузки ленты {feed_info['name']}: {e}")

    return items_found


def extract_web_image(article_url: str) -> str:
    """Извлечение og:image из HTML страницы статьи."""
    try:
        req = urllib.request.Request(article_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            match = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
            if not match:
                match = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', html, re.I)
            if not match:
                match = re.search(r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
            if match:
                img = match.group(1).strip()
                if img.startswith("//"):
                    img = "https:" + img
                return img
    except Exception as e:
        print(f"[WARN] Не удалось извлечь изображение со страницы {article_url}: {e}")
    return ""


def upgrade_to_full_image_url(url: str) -> str:
    """Удаление суффиксов масштабирования (-150x100 и т.д.) для получения оригинального разрешения."""
    if not url:
        return url
    return re.sub(r'-\d+x\d+(\.[a-zA-Z]+)$', r'\1', url)


def download_image(image_url: str) -> Path:
    """Скачивание изображения во временную папку."""
    if not image_url:
        return None
    image_url = upgrade_to_full_image_url(image_url)
    try:
        req = urllib.request.Request(image_url, headers=HEADERS)
        dest_path = TEMP_DIR / "news_banner.jpg"
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            if len(data) > 1024:
                with open(dest_path, "wb") as f:
                    f.write(data)
                return dest_path
    except Exception as e:
        print(f"[WARN] Ошибка скачивания фото {image_url}: {e}")
    return None


def generate_post_content(article: dict) -> str:
    """Генерация Telegram-поста через Google Gemini API с надежными повторами."""
    prompt = f"""
Ты — ведущий инженерный редактор Telegram-канала о 3D-печати "STL GARAGE".
Твоя задача — превратить свежую мировую новость 3D-индустрии в качественный, увлекательный и структурированный пост на русском языке.

Правила оформления:
1. Заголовок: яркий, с подходящим тематическим эмодзи, на русском языке, обернут строго в <b>Заголовок</b> (без Markdown **).
2. Вводка (1-2 емких предложения): о чем речь, почему это интересно или какую проблему решает.
3. Главное (список из 2-3 пунктов через эмодзи ▫️): ключевые технические параметры, цифры, используемые материалы или технологии.
4. Практическая польза (1 предложение с эмодзи 💡): кому это пригодится (мейкерам, сервисам, заводам, автоиндустрии).
5. Ссылка на первоисточник: строго в формате 🔗 <a href="{article['link']}">Читать в источнике</a>
6. Хэштеги: 3-5 тематических хэштегов (например: #3Dпечать #технологии #инженерия #новости).
7. Форматирование: СТРОГО HTML теги Telegram (<b>, <i>, <a>, <code>). НЕ используй Markdown (**жирный**, [ссылка](url)).
8. Ограничение длины: СТРОГО от 450 до 750 символов! Текст должен легко читаться под фото и не превышать лимит подписи Telegram.

Данные новости:
Источник: {article['source']}
Заголовок оригинала: {article['title']}
Краткое описание: {article['desc']}
Ссылка: {article['link']}
"""

    models_to_try = [
        "gemini-3.5-flash-lite",
        "gemini-flash-lite-latest",
        "gemini-3.1-flash-lite-preview",
        "gemini-3.8-flash"
    ]

    for attempt in range(3):
        for model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.65,
                    "maxOutputTokens": 2000
                }
            }
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        full_text = "".join(p.get("text", "") for p in parts if "text" in p).strip()
                        full_text = re.sub(r"^```(?:html)?\s*", "", full_text, flags=re.I)
                        full_text = re.sub(r"\s*```$", "", full_text)

                        # Закрытие незакрытых тегов HTML
                        for tag in ['b', 'i', 'code']:
                            o = len(re.findall(rf'<{tag}>', full_text, re.I))
                            c = len(re.findall(rf'</{tag}>', full_text, re.I))
                            if o > c:
                                full_text += f"</{tag}>" * (o - c)
                        if '<a ' in full_text and '</a>' not in full_text:
                            full_text += '</a>'

                        if len(full_text) >= 250:
                            return full_text
                        else:
                            print(f"[WARN] Слишком короткий текст ({len(full_text)} симв.), пробуем еще...")
            except urllib.error.HTTPError as e:
                # 503 или 429 - временная нагрузка, пробуем следующую модель
                time.sleep(1.5)
            except Exception as e:
                time.sleep(1.0)
        time.sleep(2)

    raise RuntimeError("Не удалось сгенерировать пост через Gemini API после всех попыток.")


def publish_one_news(dry_run: bool = False) -> bool:
    """Главный цикл отбора и публикации одной свежей новости."""
    print("=" * 60)
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] STL GARAGE AUTO-NEWS POSTER")
    print("=" * 60)

    history = load_history()
    published_urls = {item["url"] for item in history if "url" in item}
    print(f"[INFO] Ранее опубликовано новостей: {len(published_urls)}")

    candidates = []
    for feed in NEWS_FEEDS:
        print(f"[INFO] Сканирование {feed['name']}...")
        items = fetch_feed_items(feed)
        for it in items:
            if it["link"] not in published_urls:
                candidates.append(it)

    print(f"[INFO] Найдено свежих неопубликованных кандидатов: {len(candidates)}")

    if not candidates:
        print("[INFO] Свежих новостей пока нет. Пропуск до следующего запуска.")
        return True

    chosen = candidates[0]
    print(f"\n[SELECTED] {chosen['source']}: {chosen['title']}")
    print(f"[URL] {chosen['link']}")

    # Получение изображения
    image_url = chosen.get("image")
    if not image_url:
        print("[INFO] Поиск обложки на странице статьи...")
        image_url = extract_web_image(chosen["link"])

    local_image = None
    if image_url:
        print(f"[INFO] Скачивание фото: {image_url}")
        local_image = download_image(image_url)

    # Генерация текста через Gemini
    print("[INFO] Генерация описания через Gemini AI...")
    post_text = generate_post_content(chosen)
    print("\n--- СФОРМИРОВАННЫЙ ПОСТ ---")
    print(post_text)
    print("---------------------------\n")

    if dry_run:
        print("[DRY RUN] Публикация пропущена (тестовый режим).")
        if local_image and local_image.exists():
            local_image.unlink()
        return True

    # Кнопки под постом
    buttons = [
        [
            {"text": "💬 Заказать печать / Чат", "url": f"https://t.me/{BOT_USERNAME}"},
            {"text": "🌐 Каталог STL GARAGE", "url": SITE_URL}
        ]
    ]

    # Публикация
    res = None
    if local_image and local_image.exists():
        print(f"[INFO] Отправка фотопоста в @{CHANNEL_USERNAME}...")
        res = send_photo(str(local_image), post_text, inline_buttons=buttons)
    else:
        print(f"[INFO] Отправка текстового поста в @{CHANNEL_USERNAME}...")
        res = publish_post(post_text, inline_buttons=buttons)

    # Очистка временного файла
    if local_image and local_image.exists():
        try:
            local_image.unlink()
        except Exception:
            pass

    if res and res.get("ok"):
        msg_id = res["result"]["message_id"]
        history.append({
            "url": chosen["link"],
            "title": chosen["title"],
            "source": chosen["source"],
            "published_at": datetime.datetime.now().isoformat(),
            "message_id": msg_id
        })
        save_history(history)
        print(f"[SUCCESS] Новость успешно опубликована (msg_id={msg_id}) и занесена в историю.")
        return True
    else:
        print(f"[ERROR] Не удалось опубликовать: {res}")
        return False


if __name__ == "__main__":
    is_dry = "--dry-run" in sys.argv
    success = publish_one_news(dry_run=is_dry)
    sys.exit(0 if success else 1)
