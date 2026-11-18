// STL GARAGE — MAIN APPLICATION LOGIC

// Embedded fallback products catalog for local file:// previews
const FALLBACK_PRODUCTS = [
  {
    "id": "esp32-cam-case",
    "title": "Корпус для платы ESP32-CAM с креплением и вентиляцией",
    "category": "enclosures",
    "category_name": "РЭА и Корпуса",
    "price": 450,
    "old_price": 550,
    "material": "PETG",
    "layer_height": "0.16 мм",
    "infill": "30% (Gyroid)",
    "weight_g": 38,
    "print_time_h": "1.5 ч",
    "dimensions": "42 x 32 x 28 мм",
    "in_stock": true,
    "badge": "ХИТ",
    "description": "Инженерный корпус для модуля ESP32-CAM с объективом OV2640. Сквозные вентиляционные прорези над стабилизатором питания, технологический карман под MicroSD слот, разгрузка разъема питания и монтажные ушки под винты М3.",
    "features": [
      "Гарантированная посадка в четверть с термозазором 0.2 мм",
      "Стойкость к УФ и нагреву до 75°C (PETG)",
      "Латунные резьбовые втулки М3 горячей запрессовки",
      "Отверстие для индикаторного светодиода и сброса"
    ],
    "image_color": "#00AE42"
  },
  {
    "id": "magnetic-tool-rail",
    "title": "Магнитная планка-держатель инструмента в гараж",
    "category": "auto",
    "category_name": "Авто & Мастерская",
    "price": 850,
    "old_price": null,
    "material": "PETG / Neodymium",
    "layer_height": "0.20 мм",
    "infill": "40% (Tri-Hexagonal)",
    "weight_g": 95,
    "print_time_h": "3.0 ч",
    "dimensions": "250 x 35 x 18 мм",
    "in_stock": true,
    "badge": "НАДЕЖНО",
    "description": "Сверхпрочный модульный держатель для гаечных ключей, бит и пассатижей. Внутренние карманы под неодимовые магниты 20х10х3 мм с защитой от сколов и влаги.",
    "features": [
      "Впрессованные 6 неодимовых магнитов N52",
      "Удержание ключей до 32 мм и тяжелых пассатижей",
      "Скрытый крепеж к верстаку, стене или перфопанели"
    ],
    "image_color": "#FF6B00"
  },
  {
    "id": "car-clip-set-reinforced",
    "title": "Комплект усиленных клипс обшивки салона (10 шт)",
    "category": "auto",
    "category_name": "Авто & Мастерская",
    "price": 390,
    "old_price": 500,
    "material": "ABS / ASA",
    "layer_height": "0.12 мм",
    "infill": "100% (Solid)",
    "weight_g": 24,
    "print_time_h": "1.2 ч",
    "dimensions": "22 x 14 x 14 мм",
    "in_stock": true,
    "badge": "В НАЛИЧИИ",
    "description": "Усиленные пистоны-клипсы взамен ломких заводских. Напечатаны с монолитным 100% заполнением из конструкционного ударопрочного пластика ABS с термостойкостью до 105°C.",
    "features": [
      "Эластичный замок с памятью формы",
      "Не дубеют на морозе до -40°C",
      "Химическая стойкость к маслу и омывателю"
    ],
    "image_color": "#FF6B00"
  },
  {
    "id": "drill-bit-organizer-48",
    "title": "Органайзер бит и свёрел на 48 позиций с замком",
    "category": "organizers",
    "category_name": "Органайзеры & Инструмент",
    "price": 690,
    "old_price": 850,
    "material": "PETG",
    "layer_height": "0.20 мм",
    "infill": "25% (Gyroid)",
    "weight_g": 115,
    "print_time_h": "4.2 ч",
    "dimensions": "140 x 95 x 30 мм",
    "in_stock": true,
    "badge": "ТОП",
    "description": "Компактный кейс для шестигранных бит 1/4\" и сверл от 1 до 10 мм. Каждый колодец промаркирован рельефным шрифтом. Крышка на надежных печатных петлях с замком-защелкой.",
    "features": [
      "Четкая рельефная маркировка калибров",
      "Плотная посадка бит — не выпадают при тряске",
      "Ударопрочный корпус для переноски в сумке"
    ],
    "image_color": "#00AE42"
  },
  {
    "id": "headphone-gamepad-stand",
    "title": "Настольная подставка под наушники и геймпад «Stealth»",
    "category": "gadgets",
    "category_name": "Гаджеты & Стенды",
    "price": 1190,
    "old_price": 1400,
    "material": "PLA Matte",
    "layer_height": "0.16 мм",
    "infill": "20% (Grid)",
    "weight_g": 160,
    "print_time_h": "5.5 ч",
    "dimensions": "110 x 130 x 240 мм",
    "in_stock": true,
    "badge": "ДИЗАЙН",
    "description": "Минималистичный стенд в граненом лоу-поли стиле для рабочего стола. Одновременное размещение полноразмерных наушников и геймпада (Xbox / DualSense). Скрытый органайзер для кабеля зарядки.",
    "features": [
      "Широкое утяжеленное основание с противоскользящими ножками",
      "Шелковистая матовая текстура без бликов",
      "Радиус оголовья спроектирован без деформации амбушюр"
    ],
    "image_color": "#00D2FF"
  },
  {
    "id": "tpu-vibration-dampers",
    "title": "Виброопоры-демпферы для оборудования и акустики (4 шт)",
    "category": "gadgets",
    "category_name": "Гаджеты & Стенды",
    "price": 550,
    "old_price": null,
    "material": "TPU 95A",
    "layer_height": "0.20 мм",
    "infill": "15% (Concentric)",
    "weight_g": 48,
    "print_time_h": "2.0 ч",
    "dimensions": "Ø38 x 20 мм",
    "in_stock": true,
    "badge": "FLEX",
    "description": "Эластичные демпфирующие ножки из гибкого полиуретана TPU 95A. Эффективно гасят резонансные частоты 3D-принтеров, сабвуферов, насосов и системных блоков.",
    "features": [
      "Специальная сотовая структура для поглощения вибраций",
      "Не скользят и не царапают лакированные поверхности",
      "Стойкость к истиранию и деформации под весом до 40 кг"
    ],
    "image_color": "#FF6B00"
  },
  {
    "id": "cable-drop-clips-tpu",
    "title": "Кабель-органайзеры под столешницу гибкие (набор 6 шт)",
    "category": "organizers",
    "category_name": "Органайзеры & Инструмент",
    "price": 320,
    "old_price": 400,
    "material": "TPU 95A",
    "layer_height": "0.20 мм",
    "infill": "100%",
    "weight_g": 22,
    "print_time_h": "1.0 ч",
    "dimensions": "28 x 16 x 14 мм",
    "in_stock": true,
    "badge": "ПОЛЕЗНО",
    "description": "Эластичные фиксаторы проводов под двусторонний скотч 3M VHB. Провод легко защелкивается и вынимается, не перетираясь об острые грани.",
    "features": [
      "Мягкий охват кабелей сечением от 3 до 8 мм",
      "Монтаж на саморез или скотч",
      "Незаметны под столом, на верстаке или в автомобиле"
    ],
    "image_color": "#00AE42"
  },
  {
    "id": "custom-engineering-part",
    "title": "Печать ваших 3D-моделей под заказ (STL / STEP / Эскиз)",
    "category": "custom",
    "category_name": "Индивидуальный заказ",
    "price": 350,
    "old_price": null,
    "material": "По выбору: PETG / ABS / PLA / TPU / Carbon",
    "layer_height": "от 0.08 мм",
    "infill": "Индивидуально",
    "weight_g": 0,
    "print_time_h": "от 2 часов",
    "dimensions": "До 256 x 256 x 256 мм",
    "in_stock": true,
    "badge": "КАСТОМ",
    "description": "Профессиональное изготовление прототипов, шестерен, кронштейнов, переходников и декоративных моделей по вашим файлам или чертежам. Помощь в доработке геометрии и подборе пластика.",
    "features": [
      "Высокоскоростная печать на оборудовании Bambu Lab",
      "Расчет стоимости по граммам и времени печати без скрытых наценок",
      "Техническая консультация инженера перед запуском"
    ],
    "image_color": "#00D2FF"
  }
];

// App State
const AppState = {
  products: [],
  currentCategory: 'all',
  searchQuery: '',
  cart: []
};

// Toast Notification Manager
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `
    <span style="color: var(--color-primary)">●</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-10px)';
    setTimeout(() => toast.remove(), 250);
  }, 2800);
}

// Cart Manager
const Cart = {
  init() {
    try {
      const saved = localStorage.getItem('stl_garage_cart');
      if (saved) AppState.cart = JSON.parse(saved);
    } catch (e) {
      console.warn('LocalStorage error:', e);
    }
    this.updateUI();
    this.bindEvents();
  },

  save() {
    try {
      localStorage.setItem('stl_garage_cart', JSON.stringify(AppState.cart));
    } catch (e) {}
    this.updateUI();
  },

  addItem(product) {
    const existing = AppState.cart.find(item => item.id === product.id);
    if (existing) {
      existing.quantity += (product.quantity || 1);
    } else {
      AppState.cart.push({
        id: product.id,
        title: product.title,
        price: product.price,
        material: product.material,
        quantity: product.quantity || 1
      });
    }
    this.save();
    showToast(`«${product.title}» добавлен в корзину`);
  },

  removeItem(id) {
    AppState.cart = AppState.cart.filter(item => item.id !== id);
    this.save();
  },

  updateQuantity(id, delta) {
    const item = AppState.cart.find(it => it.id === id);
    if (item) {
      item.quantity += delta;
      if (item.quantity <= 0) {
        this.removeItem(id);
        return;
      }
    }
    this.save();
  },

  getTotal() {
    return AppState.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  },

  getItemCount() {
    return AppState.cart.reduce((sum, item) => sum + item.quantity, 0);
  },

  clear() {
    AppState.cart = [];
    this.save();
  },

  updateUI() {
    const badge = document.getElementById('cart-badge');
    const count = this.getItemCount();
    if (badge) {
      badge.textContent = count;
      badge.style.display = count > 0 ? 'flex' : 'none';
    }

    const cartList = document.getElementById('cart-items-container');
    const cartTotalDisplay = document.getElementById('cart-total-price');
    const emptyNotice = document.getElementById('cart-empty-notice');
    const checkoutBtn = document.getElementById('btn-checkout');

    if (!cartList) return;

    if (AppState.cart.length === 0) {
      cartList.innerHTML = '';
      if (emptyNotice) emptyNotice.style.display = 'block';
      if (checkoutBtn) checkoutBtn.disabled = true;
      if (cartTotalDisplay) cartTotalDisplay.textContent = '0 ₽';
      return;
    }

    if (emptyNotice) emptyNotice.style.display = 'none';
    if (checkoutBtn) checkoutBtn.disabled = false;

    cartList.innerHTML = AppState.cart.map(item => `
      <div class="cart-item-row">
        <div class="cart-item-info">
          <strong>${item.title}</strong>
          <span>${item.material || ''} — ${item.price} ₽</span>
        </div>
        <div style="display:flex; align-items:center; gap:12px;">
          <div class="qty-control">
            <button class="qty-btn" onclick="Cart.updateQuantity('${item.id}', -1)">−</button>
            <span style="font-weight:700; font-size:0.85rem; min-width:18px; text-align:center;">${item.quantity}</span>
            <button class="qty-btn" onclick="Cart.updateQuantity('${item.id}', 1)">+</button>
          </div>
          <button style="background:transparent; border:none; color:var(--text-tertiary); cursor:pointer; font-size:1.1rem;" onclick="Cart.removeItem('${item.id}')" title="Удалить">✕</button>
        </div>
      </div>
    `).join('');

    if (cartTotalDisplay) {
      cartTotalDisplay.textContent = `${this.getTotal().toLocaleString('ru-RU')} ₽`;
    }
  },

  openModal() {
    const modal = document.getElementById('cart-modal');
    if (modal) {
      modal.classList.add('open');
      this.updateUI();
    }
  },

  closeModal() {
    const modal = document.getElementById('cart-modal');
    if (modal) modal.classList.remove('open');
  },

  bindEvents() {
    const cartBtn = document.getElementById('btn-open-cart');
    const closeBtn = document.getElementById('btn-close-cart');
    const backdrop = document.getElementById('cart-modal');
    const checkoutBtn = document.getElementById('btn-checkout');

    if (cartBtn) cartBtn.addEventListener('click', () => this.openModal());
    if (closeBtn) closeBtn.addEventListener('click', () => this.closeModal());
    if (backdrop) {
      backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) this.closeModal();
      });
    }

    if (checkoutBtn) {
      checkoutBtn.addEventListener('click', () => {
        this.closeModal();
        OrderModal.open();
      });
    }
  }
};

// Order Form Modal
const OrderModal = {
  open() {
    const modal = document.getElementById('order-modal');
    if (!modal) return;
    
    // Auto-fill client telegram if in Mini App
    const tgUser = window.TelegramService?.getUserData();
    if (tgUser) {
      const contactInput = document.getElementById('order-contact');
      const nameInput = document.getElementById('order-name');
      if (contactInput && !contactInput.value) contactInput.value = tgUser.username || `ID: ${tgUser.id}`;
      if (nameInput && !nameInput.value) nameInput.value = tgUser.name;
    }

    modal.classList.add('open');
  },

  close() {
    const modal = document.getElementById('order-modal');
    if (modal) modal.classList.remove('open');
  },

  init() {
    const modal = document.getElementById('order-modal');
    const closeBtn = document.getElementById('btn-close-order');
    const form = document.getElementById('order-form');

    if (closeBtn) closeBtn.addEventListener('click', () => this.close());
    if (modal) {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) this.close();
      });
    }

    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const orderData = {
          name: document.getElementById('order-name').value.trim(),
          contact: document.getElementById('order-contact').value.trim(),
          city: document.getElementById('order-city')?.value.trim() || '',
          delivery: document.getElementById('order-delivery')?.value || 'СДЭК',
          comment: document.getElementById('order-comment')?.value.trim() || '',
          items: AppState.cart,
          total: Cart.getTotal()
        };

        if (orderData.items.length === 0) {
          alert('Корзина пуста');
          return;
        }

        const submitBtn = document.getElementById('btn-submit-order');
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.textContent = 'Отправка заказа...';
        }

        const res = await window.TelegramService.sendOrder(orderData);
        
        Cart.clear();
        this.close();

        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Подтвердить заказ';
        }

        // Show success confirmation
        showToast('Заказ принят! Переходим в диалог с мастером...');
        
        // Open direct chat in Telegram
        setTimeout(() => {
          if (res.directUrl) {
            window.open(res.directUrl, '_blank');
          }
        }, 800);
      });
    }
  }
};

// Product Detail Modal
const ProductModal = {
  open(productId) {
    const p = AppState.products.find(it => it.id === productId);
    if (!p) return;

    const modal = document.getElementById('product-detail-modal');
    if (!modal) return;

    document.getElementById('modal-product-title').textContent = p.title;
    document.getElementById('modal-product-cat').textContent = p.category_name;
    document.getElementById('modal-product-desc').textContent = p.description;
    document.getElementById('modal-product-price').textContent = `${p.price.toLocaleString('ru-RU')} ₽`;
    
    // Tech specs
    document.getElementById('modal-spec-mat').textContent = p.material;
    document.getElementById('modal-spec-layer').textContent = p.layer_height;
    document.getElementById('modal-spec-infill').textContent = p.infill;
    document.getElementById('modal-spec-dim').textContent = p.dimensions;
    document.getElementById('modal-spec-weight').textContent = `${p.weight_g} г`;
    document.getElementById('modal-spec-time').textContent = p.print_time_h;

    // Features list
    const featuresList = document.getElementById('modal-features-list');
    if (featuresList) {
      featuresList.innerHTML = (p.features || []).map(f => `
        <li style="display:flex; align-items:center; gap:8px; margin-bottom:6px; font-size:0.88rem; color:var(--text-secondary);">
          <span style="color:var(--color-primary);">✓</span>
          <span>${f}</span>
        </li>
      `).join('');
    }

    const addBtn = document.getElementById('modal-btn-add-cart');
    if (addBtn) {
      addBtn.onclick = () => {
        Cart.addItem(p);
        modal.classList.remove('open');
      };
    }

    modal.classList.add('open');
  },

  close() {
    const modal = document.getElementById('product-detail-modal');
    if (modal) modal.classList.remove('open');
  },

  init() {
    const modal = document.getElementById('product-detail-modal');
    const closeBtn = document.getElementById('btn-close-product-modal');
    if (closeBtn) closeBtn.addEventListener('click', () => this.close());
    if (modal) {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) this.close();
      });
    }
  }
};

// Catalog Renderer
function renderProducts() {
  const container = document.getElementById('products-container');
  if (!container) return;

  const filtered = AppState.products.filter(p => {
    const matchCat = AppState.currentCategory === 'all' || p.category === AppState.currentCategory;
    const matchQuery = !AppState.searchQuery || 
      p.title.toLowerCase().includes(AppState.searchQuery) ||
      p.material.toLowerCase().includes(AppState.searchQuery) ||
      p.description.toLowerCase().includes(AppState.searchQuery);
    return matchCat && matchQuery;
  });

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 48px 20px; color: var(--text-tertiary);">
        <p style="font-size: 1.2rem; margin-bottom: 8px;">Ничего не найдено</p>
        <span style="font-size: 0.85rem;">Попробуйте изменить категорию или поисковый запрос</span>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(p => {
    // Generate technical SVG wireframe based on category
    const accentColor = p.image_color || 'var(--color-primary)';
    return `
      <div class="product-card">
        <div class="product-thumb">
          <div class="product-badge">${p.badge || '3D'}</div>
          <div class="product-material-tag">${p.material}</div>
          <div class="product-visual">
            <svg class="blueprint-svg" viewBox="0 0 160 120" fill="none" stroke="${accentColor}" stroke-width="1.5">
              <rect x="25" y="25" width="110" height="70" rx="8" stroke-dasharray="2 2" stroke-opacity="0.4"/>
              <path d="M40 85 L80 35 L120 85 Z" fill="${accentColor}" fill-opacity="0.12" stroke="${accentColor}" stroke-width="2"/>
              <circle cx="80" cy="60" r="14" stroke="${accentColor}" stroke-width="1.8"/>
              <circle cx="80" cy="60" r="4" fill="${accentColor}"/>
              <line x1="25" y1="60" x2="135" y2="60" stroke="${accentColor}" stroke-opacity="0.3" stroke-dasharray="4 2"/>
              <line x1="80" y1="25" x2="80" y2="95" stroke="${accentColor}" stroke-opacity="0.3" stroke-dasharray="4 2"/>
            </svg>
          </div>
        </div>
        <div class="product-content">
          <div class="product-category-sub">${p.category_name}</div>
          <h3 class="product-title">${p.title}</h3>
          <p class="product-desc">${p.description}</p>
          <div class="product-specs-pills">
            <span class="spec-pill">Слой: ${p.layer_height}</span>
            <span class="spec-pill">Заполнение: ${p.infill}</span>
            <span class="spec-pill">${p.weight_g ? p.weight_g + ' г' : 'По ТЗ'}</span>
          </div>
          <div class="product-footer">
            <div class="product-price-box">
              <span class="price-main">${p.price.toLocaleString('ru-RU')} ₽</span>
              ${p.old_price ? `<span class="price-old">${p.old_price} ₽</span>` : ''}
            </div>
            <div class="card-actions">
              <button class="btn btn-secondary" style="padding: 8px 12px; font-size: 0.8rem;" onclick="ProductModal.open('${p.id}')">Детали</button>
              <button class="btn btn-primary" style="padding: 8px 12px; font-size: 0.8rem;" onclick="Cart.addItem(AppState.products.find(x => x.id === '${p.id}'))">+ В корзину</button>
            </div>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// Category Tabs & Search Listeners
function setupFilters() {
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      AppState.currentCategory = tab.dataset.category;
      renderProducts();
    });
  });

  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      AppState.searchQuery = e.target.value.toLowerCase().trim();
      renderProducts();
    });
  }
}

// Theme Switcher
function setupThemes() {
  const themeDots = document.querySelectorAll('.theme-dot');
  themeDots.forEach(dot => {
    dot.addEventListener('click', () => {
      document.body.classList.remove('theme-orange', 'theme-cyan');
      const theme = dot.dataset.theme;
      if (theme === 'orange') document.body.classList.add('theme-orange');
      if (theme === 'cyan') document.body.classList.add('theme-cyan');
      try {
        localStorage.setItem('stl_garage_theme', theme);
      } catch (e) {}
    });
  });

  try {
    const saved = localStorage.getItem('stl_garage_theme');
    if (saved === 'orange') document.body.classList.add('theme-orange');
    if (saved === 'cyan') document.body.classList.add('theme-cyan');
  } catch (e) {}
}

// Load Catalog
async function loadProducts() {
  try {
    const res = await fetch('data/products.json');
    if (res.ok) {
      AppState.products = await res.json();
    } else {
      AppState.products = FALLBACK_PRODUCTS;
    }
  } catch (err) {
    console.log('Fetching products.json via HTTP failed (likely local file://), using fallback:', err);
    AppState.products = FALLBACK_PRODUCTS;
  }
  renderProducts();
}

// App Initialization
document.addEventListener('DOMContentLoaded', () => {
  window.TelegramService?.init();
  Cart.init();
  OrderModal.init();
  ProductModal.init();
  window.Calculator?.init();
  setupFilters();
  setupThemes();
  loadProducts();
});

window.Cart = Cart;
window.ProductModal = ProductModal;
