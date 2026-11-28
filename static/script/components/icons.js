/* ============================================
   ÍCONES POR CATEGORIA
   ============================================ */

const iconsCategoria = {
    'Academia':                  `<i class="fa-solid fa-dumbbell"></i>`,
    'Alimentação e Dieta':       `<i class="fa-solid fa-utensils"></i>`,
    'Aplicação em RV':           `<i class="fa-solid fa-chart-line"></i>`,
    'Assinatura e Streaming':    `<i class="fa-solid fa-tv"></i>`,
    'Combustível':               `<i class="fa-solid fa-gas-pump"></i>`,
    'Compras E-commerce':        `<i class="fa-solid fa-cart-shopping"></i>`,
    'Conhecimento':              `<i class="fa-solid fa-graduation-cap"></i>`,
    'Cuidados Pessoais':         `<i class="fa-solid fa-user"></i>`,
    'Custos de Casa':            `<i class="fa-solid fa-house"></i>`,
    'Diversos':                  `<i class="fa-solid fa-ellipsis"></i>`,
    'Financiamento de CP':       `<i class="fa-solid fa-credit-card"></i>`,
    'Financiamento de LP':       `<i class="fa-solid fa-file-invoice-dollar"></i>`,
    'Gastos com Pet':            `<i class="fa-solid fa-paw"></i>`,
    'Higiêne e Medicamentos':    `<i class="fa-solid fa-kit-medical"></i>`,
    'Impostos':                  `<i class="fa-solid fa-file-invoice"></i>`,
    'Lazer e Diversão':          `<i class="fa-solid fa-gamepad"></i>`,
    'Manutenção Carro':          `<i class="fa-solid fa-screwdriver-wrench"></i>`,
    'Outras aquisições':         `<i class="fa-solid fa-bag-shopping"></i>`,
    'Peças e Acessórios':        `<i class="fa-solid fa-gears"></i>`,
    'Provisões':                 `<i class="fa-solid fa-piggy-bank"></i>`,
    'Remuneração':               `<i class="fa-solid fa-money-bill-wave"></i>`,
    'Renda Extra':               `<i class="fa-solid fa-sack-dollar"></i>`,
    'Resgate RF':                `<i class="fa-solid fa-building-columns"></i>`,
    'Resgate RV':                `<i class="fa-solid fa-arrow-trend-up"></i>`,
    'Rendimentos':               `<i class="fa-solid fa-coins"></i>`,
    'Transportes':               `<i class="fa-solid fa-car"></i>`,
    'Outros':                    `<i class="fa-solid fa-shapes"></i>`,
    'Seguro Veicular':           `<i class="fa-solid fa-shield-halved"></i>`,
    'Venda de Ativos':           `<i class="fa-solid fa-money-bill-transfer"></i>`,
    'Vestimenta':                `<i class="fa-solid fa-shirt"></i>`,
};

const ICON_FALLBACK = iconsCategoria['Outros'];

/** Retorna o HTML do <i> da categoria, com fallback pra "Outros". */
function getIcon(categoria) {
    return iconsCategoria[categoria] ?? ICON_FALLBACK;
}