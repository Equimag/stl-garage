// TELEGRAM INTEGRATION & ORDER DISPATCH
const TG_CONFIG = {
  botUsername: 'STLGarage_bot',
  botToken: '7860903769:AAFIQQr8Mx8Ld5Sb5saiZ0nhfqR7B7txgkc',
  channelUsername: 'stl_garage',
  channelUrl: 'https://t.me/stl_garage',
  channelChatId: '-1002753288392'
};

const TelegramService = {
  init() {
    // Check if running inside Telegram Mini App
    if (window.Telegram && window.Telegram.WebApp) {
      this.tg = window.Telegram.WebApp;
      this.tg.ready();
      this.tg.expand();
      
      // Auto-set theme accent if inside Telegram
      if (this.tg.themeParams && this.tg.themeParams.button_color) {
        document.documentElement.style.setProperty('--color-primary', this.tg.themeParams.button_color);
      }
      
      console.log('Running inside Telegram Mini App, User:', this.tg.initDataUnsafe?.user?.username || 'Guest');
    }
  },

  isMiniApp() {
    return Boolean(this.tg && this.tg.initDataUnsafe && Object.keys(this.tg.initDataUnsafe).length > 0);
  },

  getUserData() {
    if (this.isMiniApp() && this.tg.initDataUnsafe?.user) {
      const u = this.tg.initDataUnsafe.user;
      return {
        username: u.username ? `@${u.username}` : '',
        name: [u.first_name, u.last_name].filter(Boolean).join(' '),
        id: u.id
      };
    }
    return null;
  },

  async sendOrder(orderData) {
    const message = this.formatOrderMessage(orderData);

    // Option 1: If in Telegram Mini App and MainButton / sendData is available
    if (this.isMiniApp()) {
      try {
        this.tg.sendData(JSON.stringify(orderData));
        this.tg.HapticFeedback?.notificationOccurred('success');
      } catch (e) {
        console.warn('sendData failed, falling back to direct message:', e);
      }
    }

    // Option 2: Post notification to Telegram Bot API (or channel/admin)
    try {
      const encodedMsg = encodeURIComponent(message);
      
      // Direct call to Telegram Bot API to notify owner/channel
      await fetch(`https://api.telegram.org/bot${TG_CONFIG.botToken}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: TG_CONFIG.channelChatId,
          text: message,
          parse_mode: 'HTML'
        })
      });
    } catch (err) {
      console.warn('Telegram direct fetch error (normal if CORS restriction in browser):', err);
    }

    // Option 3: Fallback / 1-tap direct Telegram chat redirection with prefilled order
    const directUrl = `https://t.me/${TG_CONFIG.botUsername}?text=${encodeURIComponent(message)}`;
    
    return {
      success: true,
      directUrl: directUrl
    };
  },

  formatOrderMessage(order) {
    let text = `📦 <b>НОВЫЙ ЗАКАЗ — STL GARAGE</b>\n\n`;
    text += `👤 <b>Клиент:</b> ${order.name}\n`;
    text += `📱 <b>Контакт:</b> ${order.contact}\n`;
    if (order.delivery) {
      text += `🚚 <b>Доставка:</b> ${order.delivery} (${order.city || 'Город не указан'})\n`;
    }
    if (order.comment) {
      text += `💬 <b>Комментарий:</b> ${order.comment}\n`;
    }
    text += `\n📋 <b>Состав заказа:</b>\n`;
    
    order.items.forEach((item, idx) => {
      text += `${idx + 1}. <b>${item.title}</b>\n`;
      text += `   ↳ ${item.material || 'Стандарт'} × ${item.quantity} шт. = ${item.price * item.quantity} ₽\n`;
    });

    text += `\n💰 <b>ИТОГО К ОПЛАТЕ:</b> ${order.total} ₽\n`;
    text += `⏱ <i>Дата: ${new Date().toLocaleString('ru-RU')}</i>`;

    return text;
  }
};

window.TelegramService = TelegramService;
