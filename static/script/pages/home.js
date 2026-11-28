
const elements = {

    //? Header
    userAvatar:   document.getElementById('user-avatar'),
    userGreeting: document.getElementById('user-greeting'),
    userName:     document.getElementById('user-name'),

    //? Toggle
    togglePessoal: document.getElementById('toggle-pessoal'),
    toggleInvest:  document.getElementById('toggle-veiculo'), // ID no HTML é 'toggle-veiculo'

    //? Saldo principal
    balanceMonthLabel: document.getElementById('balance-month-label'),
    balanceTotal:      document.getElementById('balance-total'),
    balanceIncome:     document.getElementById('balance-income'),
    balanceCurrent:    document.getElementById('balance-current'),
    spentProgressBar:  document.getElementById('spent-progress-bar'),
    spentProgressText: document.getElementById('spent-progress-text'),

    //? Orçamento
    budgetMonthLabel:  document.getElementById('budget-month-label'),
    budgetSpentValue:  document.getElementById('budget-spent-value'),
    budgetTotalValue:  document.getElementById('budget-total-value'),
    budgetPercentValue:document.getElementById('budget-percent-value'),
    budgetProgressBar: document.getElementById('budget-progress-bar'),
    categ_estouradas: document.getElementById('categ_estouradas'),
    categ_sobras: document.getElementById('categ_sobras'),
    budgetwarningcount: document.getElementById('budget-warning-count')

    
};





/* ============================================
   SKELETON — helpers
   ============================================ */

// Elementos que entram em modo skeleton no carregamento
const skeletonTargets = [
    { el: elements.userName,           cls: 'skeleton--text' },
    { el: elements.userGreeting,       cls: 'skeleton--text' },
    { el: elements.userAvatar,         cls: 'skeleton--avatar' },
    { el: elements.balanceMonthLabel,  cls: 'skeleton--text-md' },
    { el: elements.balanceTotal,       cls: 'skeleton--title' },
    { el: elements.balanceIncome,      cls: 'skeleton--value' },
    { el: elements.balanceCurrent,     cls: 'skeleton--value' },
    { el: elements.spentProgressBar,   cls: 'skeleton--bar' },
    { el: elements.spentProgressText,  cls: 'skeleton--text-md' },
    { el: elements.budgetMonthLabel,   cls: 'skeleton--text-md' },
];

function ativarSkeleton() {
    skeletonTargets.forEach(({ el, cls }) => {
        if (!el) return;
        el.classList.add('skeleton', cls);
    });
}

function desativarSkeleton() {
    skeletonTargets.forEach(({ el, cls }) => {
        if (!el) return;
        el.classList.remove('skeleton', cls);
    });
}


const fmtBRL = (v) =>
    new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(v || 0);



// Cor determinística por nome de categoria (sempre a mesma pra mesma string).
function corDaCategoria(nome) {
    let hash = 0;
    for (let i = 0; i < nome.length; i++) {
        hash = nome.charCodeAt(i) + ((hash << 5) - hash);
    }
    const hue = Math.abs(hash) % 360;
    return `hsl(${hue}, 65%, 60%)`;
}

/* ============================================
   ORÇADO × REALIZADO — donut, agrupamento, render
   ============================================ */

/**
 * Donut fininho em SVG.
 * @param {number} percent  0..∞ (clampa em 100 no anel)
 * @returns {string} SVG string
 */



function donutSVG(percent) {
    const pct    = Math.min(Math.max(percent, 0), 100);
    const size   = 44;
    const stroke = 3;
    const r      = (size - stroke) / 2;
    const c      = 2 * Math.PI * r;
    const dash   = (pct / 100) * c;
    const estourou = percent > 100;
    const cor    = estourou ? 'var(--accent-red)' : 'var(--accent-yellow)';

    return `
        <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
            <circle cx="${size/2}" cy="${size/2}" r="${r}"
                    fill="none" stroke="var(--border-color)" stroke-width="${stroke}"/>
            <circle cx="${size/2}" cy="${size/2}" r="${r}"
                    fill="none" stroke="${cor}" stroke-width="${stroke}"
                    stroke-linecap="round"
                    stroke-dasharray="${dash} ${c}"
                    transform="rotate(-90 ${size/2} ${size/2})"/>
        </svg>`;
}

/**
 * Agrupa a lista plana (por descrição) em grupos por categoria.
 * Entrada: [{ categoria, descricao, valor_orcado, valor_realizado }, ...]
 * Saída:   [{ categoria, valor_orcado, valor_realizado, saldo, percentual, descricoes: [...] }]
 */
function agruparPorCategoria(itens) {
    const mapa = new Map();

    for (const item of itens) {
        const cat = item.categoria ?? 'Sem categoria';

        if (!mapa.has(cat)) {
            mapa.set(cat, {
                categoria:       cat,
                valor_orcado:    0,
                valor_realizado: 0,
                descricoes:      [],
            });
        }

        const g = mapa.get(cat);
        g.valor_orcado    += Number(item.valor_orcado)    || 0;
        g.valor_realizado += Number(item.valor_realizado) || 0;
        g.descricoes.push(item);
    }

    for (const g of mapa.values()) {
        g.saldo = g.valor_orcado - g.valor_realizado;
        g.percentual = g.valor_orcado > 0
            ? (g.valor_realizado / g.valor_orcado) * 100
            : (g.valor_realizado > 0 ? 999 : 0);

        g.descricoes.sort((a, b) => b.valor_realizado - a.valor_realizado);
    }

    return [...mapa.values()].sort((a, b) => b.percentual - a.percentual);
}

/** Renderiza o accordion de categorias dentro de .budget-section. */
function renderCategorias(itens) {
    const section = document.querySelector('.budget-section');
    if (!section) return;

    let lista = section.querySelector('.categorias-list');
    if (!lista) {
        lista = document.createElement('div');
        lista.className = 'categorias-list';
        section.appendChild(lista);
    }

    if (!Array.isArray(itens) || itens.length === 0) {
        lista.innerHTML = `<p class="categorias-empty">Nenhum orçamento cadastrado.</p>`;
        return;
    }

    const grupos = agruparPorCategoria(itens);

    lista.innerHTML = grupos.map((g) => {
        const pctLabel = g.valor_orcado > 0
            ? `${Math.round(g.percentual)}%`
            : '—';

        const descricoesHTML = g.descricoes.map((d) => `
            <div class="descricao">
                <span class="descricao__nome">${d.descricao}</span>
                <span class="descricao__valores">
                    ${fmtBRL(d.valor_realizado)}
                    <span class="descricao__de">de ${fmtBRL(d.valor_orcado)}</span>
                </span>
            </div>
        `).join('');

        return `
        <details class="categoria" data-categoria="${g.categoria}">
            <summary class="categoria__summary">
                <div class="categoria__donut">
                    ${donutSVG(g.percentual)}
                    <span class="categoria__icon">${getIcon(g.categoria)}</span>
                </div>

                <div class="categoria__info">
                    <span class="categoria__nome">${g.categoria}</span>
                    <span class="categoria__valores">
                        ${fmtBRL(g.valor_realizado)}
                        <span class="categoria__de">de ${fmtBRL(g.valor_orcado)}</span>
                    </span>
                </div>

                <span class="categoria__pct ${g.percentual > 100 ? 'is-over' : ''}">
                    ${pctLabel}
                </span>
            </summary>

            <div class="categoria__descricoes">${descricoesHTML}</div>
        </details>`;
    }).join('');
}

/* ============================================
   CARREGAMENTO
   ============================================ */


async function carregarHome() {
    ativarSkeleton();

    try {
        const resp = await fetch('/api/home');
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

        const data = await resp.json();

        // ... (todo o preenchimento que já fizemos) ...

        elements.userName.textContent     = data.nome;
        elements.userAvatar.textContent   = data.avatar;
        elements.userGreeting.textContent = data.saudacao;

        elements.balanceMonthLabel.textContent = `Sobrou em ${data.mes}`;
        elements.budgetMonthLabel.textContent  = `Orçamento de ${data.mes}`;

        elements.balanceTotal.textContent   = fmtBRL(data.saldo_mes);
        elements.balanceIncome.textContent  = fmtBRL(data.total_entrada);
        elements.balanceCurrent.textContent = fmtBRL(data.total_saida);
        elements.budgetTotalValue.textContent = fmtBRL(data.total_saidaPlan);

        const pct = Math.min(Math.max(data.percentual_gasto, 0), 100);
        const qtd_estourou = data.categorias_estouraram;
        const qtd_sobras = data.categorias_com_sobra;


        elements.spentProgressBar.style.width = `${pct}%`;
        elements.spentProgressText.textContent = `Você gastou ${pct}% do que entrou`;
        elements.categ_estouradas.textContent = `⚠️ ${qtd_estourou} categoria(s) estourada(s)`;
        elements.categ_sobras.textContent = `✅ ${qtd_sobras} categoria(s) dentro do orçamento(s)`;

         //! Orçado × Realizado (accordion)
        renderCategorias(data.orcado_realizado || []);


    } catch (err) {
        console.error('Erro ao carregar home:', err);

    } finally {
        desativarSkeleton();   // roda SEMPRE — sucesso ou erro
    }
}

// roda quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', carregarHome);