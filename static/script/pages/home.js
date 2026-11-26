/* ============================================
   HOME — carrega dados iniciais do usuário
   ============================================ */





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
    budgetWarningText: document.getElementById('budget-warning-text'),
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
        elements.spentProgressBar.style.width = `${pct}%`;
        elements.spentProgressText.textContent = `Você gastou ${pct}% do que entrou`;

    } catch (err) {
        console.error('Erro ao carregar home:', err);

    } finally {
        desativarSkeleton();   // roda SEMPRE — sucesso ou erro
    }
}

// roda quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', carregarHome);