# 🚀 STL GARAGE — Лаборатория 3D-печати и кастомных деталей

> **Современный, быстрый и бесплатный сайт-каталог изделий 3D-печати, без ограничений открывающийся в РФ (GitHub Pages + Telegram Mini App) с автопостингом в канал [@stl_garage](https://t.me/stl_garage).**

---

## ⚡ Быстрый старт

### 1. Локальный предпросмотр (в 1 клик)
Запустите файл:
```bat
start_preview.bat
```
или выполните в терминале:
```bash
python -m http.server 8080
```
И откройте в браузере: `http://localhost:8080`.

---

## 📂 Структура проекта

```
c:\Users\Memfor\Site\
├── index.html                 # Главная страница (адаптирована для браузеров и Telegram Mini App)
├── css/
│   └── style.css              # Дизайн-система High-Tech 3D (Dark Graphite, Bambu Green, Cyber Orange)
├── js/
│   ├── app.js                 # Каталог, фильтры по категориям, поиск, модальные окна, корзина
│   ├── calculator.js          # Калькулятор расчета стоимости по весу, пластику и времени
│   └── tg-order.js            # Отправка заказов в Telegram Bot API / Mini App
├── data/
│   └── products.json          # База товаров с инженерными спецификациями
├── scripts/
│   ├── config.py              # Токен бота @STLGarage_bot и ID канала @stl_garage
│   ├── channel_publisher.py   # Скрипт публикации постов и анонсов в Telegram-канал
│   └── add_product.py         # Добавление товаров в каталог + автопост
├── .github/workflows/
│   └── deploy.yml             # Автодеплой на бесплатный GitHub Pages при git push
├── start_preview.bat          # 1-клик запуск локального сервера
└── README.md                  # Документация
```

---

## 🛠 Автоматизация через ИИ-агента

Вы можете поручать мне управление сайтом и каналом простыми фразами:

1. **Добавить новое изделие:**
   > *«Добавь в каталог держатель для телефона, пластик PETG, цена 350 руб, описание... и опубликуй новинку в Telegram»*
   
   Агент автоматически запишет товар в `data/products.json` и вызовет `python scripts/add_product.py --post`.

2. **Опубликовать произвольный пост в канал @stl_garage:**
   > *«Опубликуй в канале новость: приехала новая катушка эластомера TPU 95A, принимаем заказы на мягкие демпферы»*
   
   Агент выполнит публикацию через `python scripts/channel_publisher.py`.

3. **Изменить цены или наличие:**
   > *«Поставь на корпус ESP32 цену 500 рублей и сделай плашку В наличии»*

---

## 🌐 Бесплатный запуск на GitHub Pages (0 ₽ навсегда, доступно в РФ)

1. Создайте бесплатный репозиторий на [GitHub](https://github.com/new).
2. Запушьте код из этой папки:
   ```bash
   git init
   git add .
   git commit -m "Initial commit STL Garage store"
   git remote add origin https://github.com/ВАШ_АККАУНТ/ВАШ_РЕПОЗИТОРИЙ.git
   git branch -M main
   git push -u origin main
   ```
3. В настройках репозитория на GitHub: **Settings $\rightarrow$ Pages $\rightarrow$ Build and deployment $\rightarrow$ Source: GitHub Actions**.
4. Сайт станет доступен по адресу `https://ваш-логин.github.io/имя-репозитория/` без блокировок и без VPN по всей России!

---

## 📱 Подключение как Telegram Mini App (Каталог внутри Telegram)

Чтобы сайт открывался прямо внутри Telegram по кнопке в канале или боте:
1. Откройте в Telegram диалог с **@BotFather**.
2. Отправьте команду `/mybots` $\rightarrow$ выберите `@STLGarage_bot`.
3. Перейдите: **Bot Settings $\rightarrow$ Menu Button $\rightarrow$ Configure menu button**.
4. Введите URL вашего сайта (например, ссылку на GitHub Pages) и название кнопки, например: **«🛒 Каталог 3D»**.
5. Теперь любой подписчик канала или посетитель бота сможет открыть полноэкранный магазин прямо внутри Telegram!
