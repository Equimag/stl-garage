"""
Обновленный генератор рекламной брошюры 3D-печати (2 на А4) с акцентом на «3D-ПЕЧАТЬ».
Слово 3D-ПЕЧАТЬ сделано максимально крупным, жирным и доминирующим.
"""
import os
import subprocess
import qrcode
import qrcode.image.svg
from PIL import Image

def get_qr_svg(url, box_size=8):
    factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(url, image_factory=factory, box_size=box_size, border=0)
    import io
    buf = io.BytesIO()
    img.save(buf)
    svg_str = buf.getvalue().decode('utf-8')
    if '<?xml' in svg_str:
        svg_str = svg_str.split('?>', 1)[1].strip()
    return svg_str

def generate_flyer():
    qr_tg_main = get_qr_svg('https://t.me/stl_garage', box_size=7)
    qr_tg_mini = get_qr_svg('https://t.me/stl_garage', box_size=3)
    qr_site_box = get_qr_svg('https://revermag.github.io/stl-garage/', box_size=5)

    icon_gear = '''<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>'''
    icon_car = '''<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 16H9m10 0h3v-3.15a1 1 0 0 0-.84-.99L16 11l-2.7-3.6a1 1 0 0 0-.8-.4H7.5a1 1 0 0 0-.8.4L4 11l-5.16.86A1 1 0 0 0-2 12.85V16h3"></path><circle cx="6.5" cy="16.5" r="2.5"></circle><circle cx="16.5" cy="16.5" r="2.5"></circle></svg>'''
    icon_home = '''<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>'''
    icon_ruler = '''<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.3 8.7l-6-6a1 1 0 0 0-1.4 0l-11 11a1 1 0 0 0 0 1.4l6 6a1 1 0 0 0 1.4 0l11-11a1 1 0 0 0 0-1.4z"></path><line x1="7.5" y1="10.5" x2="9.5" y2="8.5"></line><line x1="10.5" y1="13.5" x2="12.5" y2="11.5"></line><line x1="13.5" y1="16.5" x2="15.5" y2="14.5"></line></svg>'''
    icon_lightning = '''<svg width="11" height="11" viewBox="0 0 24 24" fill="#000" stroke="#000" stroke-width="1"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>'''
    icon_shield = '''<svg width="11" height="11" viewBox="0 0 24 24" fill="#000" stroke="#000" stroke-width="1"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'''
    icon_ruble = '''<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.5"><path d="M6 3h7a5 5 0 0 1 5 5 5 5 0 0 1-5 5H6zm0 10h8m-8 4h5M6 3v18"></path></svg>'''
    icon_tg = '''<svg width="12" height="12" viewBox="0 0 24 24" fill="#fff"><path d="M12 0C5.37 0 0 5.37 0 12s5.37 12 12 12 12-5.37 12-12S18.63 0 12 0zm5.56 8.16l-1.92 9.07c-.14.65-.53.81-1.07.51l-2.95-2.18-1.42 1.37c-.16.16-.29.29-.6.29l.21-3.01 5.48-4.95c.24-.21-.05-.33-.37-.12l-6.77 4.26-2.92-.91c-.63-.2-.64-.63.13-.93l11.4-4.39c.53-.19.99.13.83.99z"/></svg>'''

    flyer_single_html = f'''
        <div class="flyer-border">

          <!-- 1. Верхняя полоса: Бренд и гео-привязка -->
          <div class="brand-bar">
            <div class="brand-info">
              <span class="brand-name">STL GARAGE</span>
              <span class="brand-dot">•</span>
              <span class="brand-sub">МАСТЕРСКАЯ ДЕТАЛЕЙ</span>
            </div>
            <div class="neighbor-badge dynamic-badge">ВАШ СОСЕДСКИЙ МАСТЕР</div>
          </div>

          <!-- 2. ГЛАВНЫЙ ГИГАНТСКИЙ ЗАГОЛОВОК: 3D-ПЕЧАТЬ -->
          <div class="hero-box">
            <div class="hero-main-title">3D-ПЕЧАТЬ</div>
            <div class="hero-black-stripe">
              <span>ИЗГОТОВЛЕНИЕ И РЕМОНТ ДЕТАЛЕЙ</span>
            </div>
          </div>

          <!-- 3. Понятный подзаголовок проблемы / решения -->
          <div class="problem-hook-bar">
            <div class="problem-lead">СЛОМАЛАСЬ ПЛАСТИКОВАЯ ДЕТАЛЬ? НЕ СПЕШИТЕ ВЫБРАСЫВАТЬ!</div>
            <div class="problem-sub">
              Снимем размеры и напечатаем <strong>точную прочную копию по обломкам или фото</strong> прямо в нашем районе. Быстрее и в 5-10 раз дешевле покупки новой техники!
            </div>
          </div>

          <!-- 4. Сетка услуг (2х2 карточки поломок) -->
          <div class="services-grid">
            <div class="service-card">
              <div class="card-title">
                <span class="card-icon">{icon_gear}</span>
                <span>Бытовая техника</span>
              </div>
              <ul class="card-list">
                <li>Шестерни мясорубок, комбайнов, блендеров</li>
                <li>Ручки холодильников, духовок, защёлки</li>
                <li>Колёсики пылесосов, чемоданов, роликов</li>
              </ul>
            </div>

            <div class="service-card">
              <div class="card-title">
                <span class="card-icon">{icon_car}</span>
                <span>Авто, мото & вело</span>
              </div>
              <ul class="card-list">
                <li>Клипсы, пистоны обшивки, заглушки дисков</li>
                <li>Крепления фар, шестерни стеклоподъёмников</li>
                <li>Кронштейны, переходники, детали салона</li>
              </ul>
            </div>

            <div class="service-card">
              <div class="card-title">
                <span class="card-icon">{icon_home}</span>
                <span>Дом, сантехника, ремонт</span>
              </div>
              <ul class="card-list">
                <li>Крепления карнизов, ручки окон и дверей</li>
                <li>Переходники для шлангов, насадки пылесоса</li>
                <li>Направляющие ящиков, держатели инструмента</li>
              </ul>
            </div>

            <div class="service-card">
              <div class="card-title">
                <span class="card-icon">{icon_ruler}</span>
                <span>По сломанному образцу</span>
              </div>
              <ul class="card-list">
                <li>Снимем точные размеры даже с осколков!</li>
                <li>Индивидуальные корпуса для РЭА и датчиков</li>
                <li>Инженерный пластик (PETG, ABS, нейлон, TPU)</li>
              </ul>
            </div>
          </div>

          <!-- 5. Преимущества (3 колонки) -->
          <div class="benefits-bar">
            <div class="benefit-item">
              <div class="benefit-head">{icon_lightning} СРОЧНО ОТ 2 Ч.</div>
              <div class="benefit-desc">Печать в день заказа</div>
            </div>
            <div class="benefit-item">
              <div class="benefit-head">{icon_shield} КРЕПЧЕ ЗАВОДА</div>
              <div class="benefit-desc">Ударопрочные термопласты</div>
            </div>
            <div class="benefit-item">
              <div class="benefit-head">{icon_ruble} ЭКОНОМИЯ ДО 90%</div>
              <div class="benefit-desc">Дешевле нового узла</div>
            </div>
          </div>

          <!-- 6. Блок заказа и QR-кода -->
          <div class="order-action-box">
            <div class="qr-container">
              <div class="qr-svg-wrapper">
                {qr_tg_main}
              </div>
              <div class="qr-caption">SCAN ME В ТГ</div>
            </div>

            <div class="order-instructions">
              <div class="order-steps-title">
                <span>КАК СДЕЛАТЬ ЗАКАЗ:</span>
              </div>
              <div class="steps-list">
                <div>1. <strong>Сфотографируйте</strong> сломанную деталь</div>
                <div>2. <strong>Отправьте</strong> фото в Telegram или WhatsApp</div>
                <div>3. Рассчитаем стоимость и срок <strong>за 10 минут!</strong></div>
              </div>

              <div class="contact-highlight">
                <div class="contact-row">
                  <span class="contact-label">ТЕЛЕФОН:</span>
                  <span class="contact-phone dynamic-phone">+7 (___) ___-__-__</span>
                </div>
                <div class="contact-row">
                  <span class="contact-label" style="display:flex;align-items:center;gap:3px;">{icon_tg} TELEGRAM:</span>
                  <span class="contact-tg dynamic-tg">@stl_garage</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 7А. Отрывные корешки (для режима tabs) -->
          <div class="tear-tabs-container tabs-section">
            <div class="tear-guide">
              <span>✂ Оторвите талончик с контактами:</span>
              <span>3D-ПЕЧАТЬ ДЕТАЛЕЙ РЯДОМ С ВАМИ ✂</span>
            </div>
            <div class="tabs-row">
              <div class="tab-coupon">
                <div class="tab-cut-scissors">✂</div>
                <div class="tab-text-vertical">
                  <span class="tab-title">3D-ПЕЧАТЬ</span>
                  <span class="tab-service">Ремонт деталей</span>
                  <span class="tab-contact dynamic-phone-short">+7 (___) ___-__-__</span>
                  <span class="tab-tg dynamic-tg">@stl_garage</span>
                </div>
                <div class="tab-mini-qr">{qr_tg_mini}</div>
              </div>

              <div class="tab-coupon">
                <div class="tab-cut-scissors">✂</div>
                <div class="tab-text-vertical">
                  <span class="tab-title">3D-ПЕЧАТЬ</span>
                  <span class="tab-service">Ремонт деталей</span>
                  <span class="tab-contact dynamic-phone-short">+7 (___) ___-__-__</span>
                  <span class="tab-tg dynamic-tg">@stl_garage</span>
                </div>
                <div class="tab-mini-qr">{qr_tg_mini}</div>
              </div>

              <div class="tab-coupon">
                <div class="tab-cut-scissors">✂</div>
                <div class="tab-text-vertical">
                  <span class="tab-title">3D-ПЕЧАТЬ</span>
                  <span class="tab-service">Ремонт деталей</span>
                  <span class="tab-contact dynamic-phone-short">+7 (___) ___-__-__</span>
                  <span class="tab-tg dynamic-tg">@stl_garage</span>
                </div>
                <div class="tab-mini-qr">{qr_tg_mini}</div>
              </div>

              <div class="tab-coupon">
                <div class="tab-cut-scissors">✂</div>
                <div class="tab-text-vertical">
                  <span class="tab-title">3D-ПЕЧАТЬ</span>
                  <span class="tab-service">Ремонт деталей</span>
                  <span class="tab-contact dynamic-phone-short">+7 (___) ___-__-__</span>
                  <span class="tab-tg dynamic-tg">@stl_garage</span>
                </div>
                <div class="tab-mini-qr">{qr_tg_mini}</div>
              </div>

              <div class="tab-coupon">
                <div class="tab-cut-scissors">✂</div>
                <div class="tab-text-vertical">
                  <span class="tab-title">3D-ПЕЧАТЬ</span>
                  <span class="tab-service">Ремонт деталей</span>
                  <span class="tab-contact dynamic-phone-short">+7 (___) ___-__-__</span>
                  <span class="tab-tg dynamic-tg">@stl_garage</span>
                </div>
                <div class="tab-mini-qr">{qr_tg_mini}</div>
              </div>

              <div class="tab-coupon">
                <div class="tab-cut-scissors">✂</div>
                <div class="tab-text-vertical">
                  <span class="tab-title">3D-ПЕЧАТЬ</span>
                  <span class="tab-service">Ремонт деталей</span>
                  <span class="tab-contact dynamic-phone-short">+7 (___) ___-__-__</span>
                  <span class="tab-tg dynamic-tg">@stl_garage</span>
                </div>
                <div class="tab-mini-qr">{qr_tg_mini}</div>
              </div>
            </div>
          </div>

          <!-- 7Б. Полноразмерный блок с ценами (для режима prices) -->
          <div class="prices-mode-block prices-section">
            <div class="prices-title">
              <span>ОРИЕНТИРОВОЧНЫЕ ЦЕНЫ:</span>
              <span class="badge-mini">ОТ 100 РУБЛЕЙ</span>
            </div>
            <div class="prices-grid-layout">
              <div class="prices-table">
                <div class="price-row">
                  <span>Клипсы, пистоны, фиксаторы:</span>
                  <span class="price-val">от 100 ₽</span>
                </div>
                <div class="price-row">
                  <span>Шестерни блендеров / мясорубок:</span>
                  <span class="price-val">от 250 ₽</span>
                </div>
                <div class="price-row">
                  <span>Ручки холодильников, духовок, окон:</span>
                  <span class="price-val">от 350 ₽</span>
                </div>
                <div class="price-row">
                  <span>Защёлки, колёсики, заглушки:</span>
                  <span class="price-val">от 150 ₽</span>
                </div>
                <div class="price-row">
                  <span>Кронштейны, переходники, фланцы:</span>
                  <span class="price-val">от 300 ₽</span>
                </div>
                <div class="price-row">
                  <span>Корпуса для электроники и РЭА:</span>
                  <span class="price-val">от 400 ₽</span>
                </div>
              </div>

              <div class="catalog-link-box">
                <div class="catalog-qr-wrap">{qr_site_box}</div>
                <div class="catalog-qr-desc">
                  <strong>КАТАЛОГ ГОТОВЫХ ДЕТАЛЕЙ</strong>
                  <span>revermag.github.io/stl-garage</span>
                </div>
              </div>
            </div>
          </div>

        </div>
    '''

    html_content = f'''<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Рекламное объявление 3D-печати — 2 на А4 (STL GARAGE)</title>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      -webkit-font-smoothing: antialiased;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: #232730;
      color: #000000;
      margin: 0;
      padding: 20px 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      min-height: 100vh;
    }}

    /* Панель управления (не печатается) */
    .control-panel {{
      background: #ffffff;
      width: 297mm;
      max-width: 95vw;
      border-radius: 8px;
      padding: 16px 20px;
      margin-bottom: 20px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
      border-left: 6px solid #000000;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}

    .panel-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
      border-bottom: 2px solid #eee;
      padding-bottom: 10px;
    }}

    .panel-title {{
      font-size: 18px;
      font-weight: 800;
      color: #111;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .panel-actions {{
      display: flex;
      gap: 10px;
      align-items: center;
    }}

    .btn {{
      padding: 10px 20px;
      font-size: 14px;
      font-weight: 800;
      border-radius: 6px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.15s ease;
      border: none;
    }}

    .btn-print {{
      background: #000000;
      color: #ffffff;
    }}

    .btn-print:hover {{
      background: #333333;
      transform: translateY(-1px);
    }}

    .panel-inputs {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
    }}

    .input-group {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .input-group label {{
      font-size: 11px;
      font-weight: 800;
      color: #444;
      text-transform: uppercase;
      letter-spacing: 1px;
    }}

    .input-group input, .input-group select {{
      padding: 8px 10px;
      font-size: 14px;
      border: 1.5px solid #bbb;
      border-radius: 5px;
      font-family: inherit;
      color: #000;
      background: #fdfdfd;
    }}

    .input-group input:focus, .input-group select:focus {{
      border-color: #000;
      outline: none;
      background: #fff;
    }}

    .panel-hint {{
      font-size: 12px;
      color: #555;
      background: #f4f5f7;
      padding: 8px 12px;
      border-radius: 5px;
      display: flex;
      align-items: center;
      gap: 8px;
      line-height: 1.4;
    }}

    /* Печатный лист А4 Альбомный (297 x 210 мм) */
    .sheet-wrapper {{
      box-shadow: 0 15px 40px rgba(0, 0, 0, 0.5);
      background: #ffffff;
    }}

    .page-a4 {{
      width: 297mm;
      height: 210mm;
      background: #ffffff;
      color: #000000;
      display: flex;
      flex-direction: row;
      position: relative;
      overflow: hidden;
      page-break-after: avoid;
      page-break-inside: avoid;
    }}

    /* Центральная разделительная линия реза */
    .sheet-cut-divider {{
      position: absolute;
      top: 0;
      bottom: 0;
      left: 148.5mm;
      width: 0;
      border-left: 1.5px dashed #000000;
      z-index: 100;
      pointer-events: none;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .cut-label {{
      position: absolute;
      background: #ffffff;
      padding: 4px 6px;
      font-size: 8pt;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 1px;
      white-space: nowrap;
      transform: rotate(-90deg);
      border: 1px dashed #000000;
    }}

    /* Половина А5 */
    .flyer {{
      width: 148.5mm;
      height: 210mm;
      box-sizing: border-box;
      padding: 4.5mm 5.5mm 3.5mm 5.5mm;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
      background: #ffffff;
      overflow: hidden;
    }}

    .flyer-border {{
      border: 2px solid #000000;
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 2.8mm 3mm 0mm 3mm;
      position: relative;
    }}

    /* 1. Верхняя полоса бренда */
    .brand-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1.5px solid #000000;
      padding-bottom: 1.2mm;
      margin-bottom: 1.2mm;
    }}

    .brand-info {{
      display: flex;
      align-items: center;
      gap: 5px;
    }}

    .brand-name {{
      font-size: 8pt;
      font-weight: 900;
      letter-spacing: 0.8px;
    }}

    .brand-dot {{
      font-size: 8pt;
      font-weight: 900;
    }}

    .brand-sub {{
      font-size: 6pt;
      font-weight: 700;
      letter-spacing: 1px;
      color: #333;
    }}

    .neighbor-badge {{
      background: #000000;
      color: #ffffff;
      font-size: 6.2pt;
      font-weight: 800;
      padding: 1.8px 5px;
      border-radius: 2px;
      text-transform: uppercase;
      letter-spacing: 0.3px;
      white-space: nowrap;
    }}

    /* 2. ГИГАНТСКИЙ ЗАГОЛОВОК 3D-ПЕЧАТЬ */
    .hero-box {{
      border: 2.5px solid #000000;
      border-radius: 4px;
      text-align: center;
      margin-bottom: 1.5mm;
      background: #ffffff;
      overflow: hidden;
    }}

    .hero-main-title {{
      font-size: 28pt;
      font-weight: 950;
      line-height: 1.05;
      letter-spacing: 2px;
      color: #000000;
      padding: 1.2mm 2mm 0.8mm 2mm;
      text-transform: uppercase;
    }}

    .hero-black-stripe {{
      background: #000000;
      color: #ffffff;
      font-size: 9pt;
      font-weight: 900;
      letter-spacing: 1px;
      text-transform: uppercase;
      padding: 1.2mm 2mm;
      line-height: 1.1;
    }}

    /* 3. Проблема / Решение */
    .problem-hook-bar {{
      text-align: center;
      margin-bottom: 1.6mm;
      padding: 0 1mm;
    }}

    .problem-lead {{
      font-size: 7.8pt;
      font-weight: 900;
      text-transform: uppercase;
      color: #000;
      letter-spacing: 0.2px;
      line-height: 1.15;
    }}

    .problem-sub {{
      font-size: 6.5pt;
      font-weight: 600;
      line-height: 1.25;
      color: #222;
      margin-top: 1px;
    }}

    .problem-sub strong {{
      font-weight: 900;
      text-decoration: underline;
    }}

    /* 4. Сетка услуг (2х2) */
    .services-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.6mm;
      margin-bottom: 1.6mm;
    }}

    .service-card {{
      border: 1.5px solid #000000;
      border-radius: 3px;
      padding: 1.6mm 2mm;
      background: #ffffff;
      display: flex;
      flex-direction: column;
    }}

    .card-title {{
      font-size: 6.8pt;
      font-weight: 900;
      text-transform: uppercase;
      display: flex;
      align-items: center;
      gap: 3.5px;
      border-bottom: 1px solid #000000;
      padding-bottom: 0.8mm;
      margin-bottom: 0.8mm;
      line-height: 1.1;
    }}

    .card-icon {{
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .card-list {{
      list-style: none;
      padding: 0;
      margin: 0;
    }}

    .card-list li {{
      font-size: 6pt;
      line-height: 1.2;
      color: #000;
      margin-bottom: 1.2px;
      display: flex;
      align-items: flex-start;
      gap: 2.5px;
    }}

    .card-list li::before {{
      content: "▪";
      font-size: 6.5pt;
      color: #000;
      line-height: 1.1;
    }}

    /* 5. Преимущества */
    .benefits-bar {{
      display: flex;
      justify-content: space-between;
      background: #ffffff;
      border: 1.5px solid #000000;
      border-radius: 3px;
      padding: 1.4mm 1.8mm;
      margin-bottom: 1.6mm;
      gap: 1.2mm;
    }}

    .benefit-item {{
      flex: 1;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }}

    .benefit-item:not(:last-child) {{
      border-right: 1px dashed #000000;
    }}

    .benefit-head {{
      font-size: 6.4pt;
      font-weight: 900;
      text-transform: uppercase;
      line-height: 1.1;
      display: flex;
      align-items: center;
      gap: 3px;
    }}

    .benefit-desc {{
      font-size: 5.4pt;
      font-weight: 700;
      color: #222;
      margin-top: 1px;
    }}

    /* 6. Блок заказа и QR-кода */
    .order-action-box {{
      border: 2px solid #000000;
      border-radius: 4px;
      padding: 1.8mm 2mm;
      display: flex;
      gap: 2mm;
      align-items: center;
      margin-bottom: 1.6mm;
      background: #ffffff;
    }}

    .qr-container {{
      flex-shrink: 0;
      width: 24mm;
      height: 24mm;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      border: 1.5px solid #000000;
      padding: 0.8mm;
      background: #ffffff;
    }}

    .qr-svg-wrapper {{
      width: 19mm;
      height: 19mm;
    }}

    .qr-svg-wrapper svg {{
      width: 100%;
      height: 100%;
      display: block;
    }}

    .qr-caption {{
      font-size: 4.8pt;
      font-weight: 900;
      text-transform: uppercase;
      margin-top: 1px;
      text-align: center;
      line-height: 1;
      letter-spacing: 0.3px;
    }}

    .order-instructions {{
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .order-steps-title {{
      font-size: 7pt;
      font-weight: 900;
      text-transform: uppercase;
      letter-spacing: 0.3px;
      margin-bottom: 1mm;
      display: flex;
      align-items: center;
      gap: 4px;
    }}

    .steps-list {{
      font-size: 6pt;
      line-height: 1.2;
      font-weight: 600;
      margin-bottom: 1.4mm;
    }}

    .steps-list div {{
      margin-bottom: 1.2px;
    }}

    .steps-list strong {{
      font-weight: 900;
    }}

    .contact-highlight {{
      background: #000000;
      color: #ffffff;
      padding: 1.4mm 1.8mm;
      border-radius: 3px;
      display: flex;
      flex-direction: column;
      gap: 1.2px;
    }}

    .contact-row {{
      font-size: 6.8pt;
      font-weight: 800;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .contact-label {{
      font-size: 5.8pt;
      letter-spacing: 0.3px;
    }}

    .contact-phone {{
      font-size: 8.6pt;
      font-weight: 900;
      letter-spacing: 0.3px;
    }}

    .contact-tg {{
      font-size: 7.2pt;
      font-weight: 900;
      color: #ffffff;
    }}

    /* 7. Отрывные корешки (Tear-off coupons) */
    .tear-tabs-container {{
      border-top: 1.5px dashed #000000;
      margin-top: 0.8mm;
      padding-top: 1mm;
      display: flex;
      flex-direction: column;
      position: relative;
    }}

    .tear-guide {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 5.4pt;
      font-weight: 900;
      text-transform: uppercase;
      letter-spacing: 0.4px;
      margin-bottom: 0.8mm;
    }}

    .tabs-row {{
      display: flex;
      height: 35mm;
      border-bottom: 1px solid #000000;
    }}

    .tab-coupon {{
      flex: 1;
      border-left: 1px dashed #000000;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      padding: 1.2mm 0.8mm;
      box-sizing: border-box;
      position: relative;
      text-align: center;
    }}

    .tab-coupon:last-child {{
      border-right: 1px dashed #000000;
    }}

    .tab-cut-scissors {{
      font-size: 6pt;
      line-height: 1;
      color: #000;
      margin-bottom: 0.8mm;
    }}

    .tab-text-vertical {{
      writing-mode: vertical-rl;
      transform: rotate(180deg);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 1.5mm;
      height: 100%;
      white-space: nowrap;
    }}

    .tab-title {{
      font-size: 7pt;
      font-weight: 950;
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }}

    .tab-service {{
      font-size: 5.2pt;
      font-weight: 700;
      color: #000;
    }}

    .tab-contact {{
      font-size: 6.5pt;
      font-weight: 900;
      letter-spacing: 0.2px;
      border: 1px solid #000;
      padding: 1px 3px;
      border-radius: 2px;
      background: #fff;
      color: #000;
    }}

    .tab-tg {{
      font-size: 6pt;
      font-weight: 800;
    }}

    .tab-mini-qr {{
      width: 7.2mm;
      height: 7.2mm;
      margin-top: 0.8mm;
      flex-shrink: 0;
    }}

    .tab-mini-qr svg {{
      width: 100%;
      height: 100%;
      display: block;
    }}

    /* Режим сплошной листовки */
    .prices-mode-block {{
      display: none;
      border: 1.5px solid #000000;
      border-radius: 3px;
      padding: 1.8mm 2.2mm;
      margin-top: 0.8mm;
      background: #ffffff;
    }}

    .prices-title {{
      font-size: 7pt;
      font-weight: 900;
      text-transform: uppercase;
      border-bottom: 1.5px solid #000;
      padding-bottom: 0.8mm;
      margin-bottom: 1.2mm;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .badge-mini {{
      background: #000;
      color: #fff;
      font-size: 5.8pt;
      padding: 1.2px 4px;
      border-radius: 2px;
    }}

    .prices-grid-layout {{
      display: flex;
      gap: 2mm;
      align-items: center;
    }}

    .prices-table {{
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 1.2px;
      font-size: 6pt;
    }}

    .price-row {{
      display: flex;
      justify-content: space-between;
      border-bottom: 1px dotted #888;
      padding-bottom: 1px;
    }}

    .price-val {{
      font-weight: 900;
    }}

    .catalog-link-box {{
      width: 28mm;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      border-left: 1px solid #000;
      padding-left: 2mm;
    }}

    .catalog-qr-wrap {{
      width: 17mm;
      height: 17mm;
    }}

    .catalog-qr-wrap svg {{
      width: 100%;
      height: 100%;
      display: block;
    }}

    .catalog-qr-desc {{
      margin-top: 1px;
      font-size: 4.6pt;
      line-height: 1.1;
      text-transform: uppercase;
    }}

    .catalog-qr-desc strong {{
      display: block;
      font-size: 5pt;
    }}

    /* Переключение классов через body */
    body.mode-tabs .tabs-section {{
      display: flex !important;
    }}
    body.mode-tabs .prices-section {{
      display: none !important;
    }}

    body.mode-prices .tabs-section {{
      display: none !important;
    }}
    body.mode-prices .prices-section {{
      display: block !important;
    }}

    @page {{
      size: A4 landscape;
      margin: 0;
    }}

    @media print {{
      html, body {{
        background: #ffffff !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 297mm !important;
        height: 210mm !important;
      }}

      .control-panel {{
        display: none !important;
      }}

      .sheet-wrapper {{
        box-shadow: none !important;
      }}

      .page-a4 {{
        width: 297mm !important;
        height: 210mm !important;
        page-break-after: avoid !important;
        page-break-inside: avoid !important;
      }}

      * {{
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
        color-adjust: exact !important;
      }}
    }}
  </style>
</head>
<body class="mode-tabs">

  <!-- ВЕРХНЯЯ ПАНЕЛЬ УПРАВЛЕНИЯ -->
  <div class="control-panel">
    <div class="panel-header">
      <div class="panel-title">
        <span>🖨️ Макет рекламной брошюры для подъездов (2 на А4 в Ч/Б)</span>
      </div>
      <div class="panel-actions">
        <button class="btn btn-print" onclick="window.print()">
          <span>Печать (Ctrl+P)</span>
        </button>
      </div>
    </div>

    <div class="panel-inputs">
      <div class="input-group">
        <label>Контактный телефон (впишите свой)</label>
        <input type="text" id="inputPhone" value="+7 (___) ___-__-__" placeholder="+7 (999) 123-45-67" oninput="updateContent()">
      </div>

      <div class="input-group">
        <label>Telegram (канал / контакт)</label>
        <input type="text" id="inputTg" value="@stl_garage" placeholder="@your_telegram" oninput="updateContent()">
      </div>

      <div class="input-group">
        <label>Бейдж мастера (в шапке)</label>
        <input type="text" id="inputBadge" value="ВАШ СОСЕДСКИЙ МАСТЕР" placeholder="СОСЕД ИЗ 3-ГО ПОДЪЕЗДА" oninput="updateContent()">
      </div>

      <div class="input-group">
        <label>Формат нижней части</label>
        <select id="selectMode" onchange="toggleMode()">
          <option value="tabs" selected>С отрывными талончиками (для досок объявлений)</option>
          <option value="prices">Сплошной постер с ценами (для ящиков/стендов)</option>
        </select>
      </div>
    </div>

    <div class="panel-hint">
      <strong>Рекомендации для печати:</strong> В диалоге печати выберите <strong>Альбомная (Landscape)</strong>, масштаб <strong>100%</strong> (или «Подогнать по размеру страницы»), поля — <strong>Минимальные</strong> или <strong>Отсутствуют</strong>. Включите галочку <em>«Печать фоновых изображений»</em>. После печати разрежьте лист по пунктирной линии ✂ пополам на 2 готовых флаера А5.
    </div>
  </div>

  <!-- ЛИСТ А4 -->
  <div class="sheet-wrapper">
    <div class="page-a4">

      <!-- Линия реза листа пополам -->
      <div class="sheet-cut-divider">
        <div class="cut-label">✂ ЛИНИЯ РЕЗА • РАЗРЕЗАТЬ ПОПОЛАМ НА 2 ФЛАЕРА А5 ✂</div>
      </div>

      <!-- Левый флаер -->
      <div class="flyer">
        {flyer_single_html}
      </div>

      <!-- Правый флаер -->
      <div class="flyer">
        {flyer_single_html}
      </div>

    </div>
  </div>

  <script>
    function updateContent() {{
      const phone = document.getElementById('inputPhone').value.trim() || '+7 (___) ___-__-__';
      const tg = document.getElementById('inputTg').value.trim() || '@stl_garage';
      const badge = document.getElementById('inputBadge').value.trim() || 'ВАШ СОСЕДСКИЙ МАСТЕР';

      document.querySelectorAll('.dynamic-phone').forEach(el => el.textContent = phone);
      document.querySelectorAll('.dynamic-phone-short').forEach(el => el.textContent = phone);
      document.querySelectorAll('.dynamic-tg').forEach(el => el.textContent = tg);
      document.querySelectorAll('.dynamic-badge').forEach(el => el.textContent = badge);
    }}

    function toggleMode() {{
      const mode = document.getElementById('selectMode').value;
      if (mode === 'prices') {{
        document.body.classList.remove('mode-tabs');
        document.body.classList.add('mode-prices');
      }} else {{
        document.body.classList.remove('mode-prices');
        document.body.classList.add('mode-tabs');
      }}
    }}
  </script>
</body>
</html>
'''

    with open('flyer.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Updated flyer.html written successfully.")

    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    html_path = os.path.abspath('flyer.html')
    pdf_out = os.path.abspath('flyer_2x_a4.pdf')
    preview_out = os.path.abspath('assets/flyer_preview_large.png')

    # PDF export
    cmd_pdf = [edge_path, '--headless', '--disable-gpu', f'--print-to-pdf={pdf_out}', '--no-pdf-header-footer', f'file:///{html_path}']
    subprocess.run(cmd_pdf, capture_output=True)

    # Screenshot export
    cmd_img = [edge_path, '--headless', '--disable-gpu', '--window-size=1754,1240', f'--screenshot={preview_out}', f'file:///{html_path}']
    subprocess.run(cmd_img, capture_output=True)

    # Crop previews
    im = Image.open(preview_out)
    sheet = im.crop((307, 210, 1446, 1101))
    sheet.save('assets/flyer_preview_sheet.png')
    single = sheet.crop((0, 0, sheet.width // 2, sheet.height))
    single.save('assets/flyer_preview_single.png')

    print("Rendered updated flyer_2x_a4.pdf and previews successfully.")

if __name__ == '__main__':
    generate_flyer()
