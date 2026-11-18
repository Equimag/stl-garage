// 3D PRINT ESTIMATION CALCULATOR
const MATERIAL_RATES = {
  'petg': { name: 'PETG (Инженерный)', pricePerGram: 4.0, speedFactor: 1.0 },
  'pla': { name: 'PLA Matte / Basic', pricePerGram: 4.5, speedFactor: 1.0 },
  'abs': { name: 'ABS / ASA (Авто-термостойкий)', pricePerGram: 5.5, speedFactor: 1.2 },
  'tpu': { name: 'TPU 95A (Гибкий эластомер)', pricePerGram: 7.5, speedFactor: 1.8 },
  'carbon': { name: 'Carbon CF (Углеволокно)', pricePerGram: 9.5, speedFactor: 1.3 }
};

const Calculator = {
  init() {
    this.materialSelect = document.getElementById('calc-material');
    this.weightInput = document.getElementById('calc-weight');
    this.weightValDisplay = document.getElementById('calc-weight-val');
    this.infillInput = document.getElementById('calc-infill');
    this.infillValDisplay = document.getElementById('calc-infill-val');
    this.layerSelect = document.getElementById('calc-layer');
    this.qtyInput = document.getElementById('calc-qty');
    
    this.resultPriceDisplay = document.getElementById('calc-total-price');
    this.resultWeightDisplay = document.getElementById('calc-res-weight');
    this.resultTimeDisplay = document.getElementById('calc-res-time');
    this.btnOrderCustom = document.getElementById('btn-order-custom');

    if (!this.weightInput) return;

    this.bindEvents();
    this.calculate();
  },

  bindEvents() {
    const triggerCalc = () => this.calculate();
    
    this.materialSelect.addEventListener('change', triggerCalc);
    this.layerSelect.addEventListener('change', triggerCalc);
    
    this.weightInput.addEventListener('input', (e) => {
      this.weightValDisplay.textContent = `${e.target.value} г`;
      this.calculate();
    });

    this.infillInput.addEventListener('input', (e) => {
      this.infillValDisplay.textContent = `${e.target.value}%`;
      this.calculate();
    });

    this.qtyInput.addEventListener('input', triggerCalc);

    if (this.btnOrderCustom) {
      this.btnOrderCustom.addEventListener('click', () => this.handleCustomOrder());
    }
  },

  calculate() {
    const matKey = this.materialSelect.value;
    const material = MATERIAL_RATES[matKey] || MATERIAL_RATES['petg'];
    const baseWeight = parseFloat(this.weightInput.value) || 50;
    const infill = parseFloat(this.infillInput.value) || 25;
    const layerHeight = parseFloat(this.layerSelect.value) || 0.16;
    const qty = parseInt(this.qtyInput.value, 10) || 1;

    // Infill weight factor (normalized to 20% base)
    const infillFactor = 0.8 + (infill / 100) * 0.8;
    const totalWeightPerUnit = Math.round(baseWeight * infillFactor);

    // Speed / layer height factor (lower layer = longer print)
    const layerSpeedFactor = 0.20 / layerHeight;
    const estimatedHoursPerUnit = (totalWeightPerUnit / 25) * material.speedFactor * (layerSpeedFactor * 0.7);
    const roundedHours = Math.max(0.5, Math.round(estimatedHoursPerUnit * 10) / 10);

    // Pricing calculation
    const materialCost = totalWeightPerUnit * material.pricePerGram;
    const machineHourCost = roundedHours * 60; // 60 rub per printer hour
    const setupFee = 100; // prep & slicing
    
    let singlePrice = Math.round(materialCost + machineHourCost + setupFee);
    // Round to pleasant tens
    singlePrice = Math.ceil(singlePrice / 10) * 10;
    
    const totalPrice = singlePrice * qty;

    // Update UI
    this.resultPriceDisplay.textContent = `${totalPrice.toLocaleString('ru-RU')} ₽`;
    this.resultWeightDisplay.textContent = `${totalWeightPerUnit * qty} г`;
    this.resultTimeDisplay.textContent = `~${Math.round(roundedHours * qty * 10) / 10} ч`;

    this.currentCalculation = {
      material: material.name,
      weightPerUnit: totalWeightPerUnit,
      infill: infill,
      layerHeight: layerHeight,
      hours: roundedHours,
      qty: qty,
      singlePrice: singlePrice,
      totalPrice: totalPrice
    };
  },

  handleCustomOrder() {
    const calc = this.currentCalculation;
    if (!calc) return;

    const customItem = {
      id: 'custom-' + Date.now(),
      title: `Индивидуальная печать (${calc.material})`,
      price: calc.singlePrice,
      quantity: calc.qty,
      material: `${calc.material}, ${calc.infill}% заполнение, слой ${calc.layerHeight}мм`,
      weight_g: calc.weightPerUnit
    };

    if (window.Cart) {
      window.Cart.addItem(customItem);
      window.Cart.openModal();
    }
  }
};

window.Calculator = Calculator;
