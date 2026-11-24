document.addEventListener('DOMContentLoaded', () => {

    const navbar  = document.getElementById('navbarMobile');
    const content = document.getElementById('content');
    const buttons = document.querySelectorAll('.navbar-mobile .nav-item');
    const pages   = document.querySelectorAll('.page');

    // ---------- Troca de página ----------
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const target = button.dataset.page;

            buttons.forEach(btn => btn.classList.remove('active'));
            pages.forEach(page => page.classList.remove('active'));

            button.classList.add('active');
            document.getElementById(target)?.classList.add('active');

            // Esconde se entrou no bot; mostra em qualquer outra aba
            if (typeof window.setNavbarVisible === 'function') {
                window.setNavbarVisible(target !== 'bot-page');
            }
        });
    });

    // ---------- Compactar navbar ao rolar ----------
    let lastScroll = 0;
    content.addEventListener('scroll', () => {
        const current = content.scrollTop;
        if (current > lastScroll + 8) {
            navbar.classList.add('compact');
        } else if (current < lastScroll - 8) {
            navbar.classList.remove('compact');
        }
        lastScroll = current;
    });

    // ---------- Swipe entre páginas ----------
    let startX = 0;
    let endX = 0;

    content.addEventListener('touchstart', e => {
        startX = e.changedTouches[0].clientX;
    });

    content.addEventListener('touchend', e => {
        endX = e.changedTouches[0].clientX;
        trocarPaginaSwipe();
    });

    function trocarPaginaSwipe() {
        const limite = 70;
        if (Math.abs(endX - startX) < limite) return;

        const botoes = [...document.querySelectorAll('.nav-item')];
        const atual = botoes.findIndex(btn => btn.classList.contains('active'));

        if (endX < startX) {
            // swipe p/ esquerda → próxima
            if (atual < botoes.length - 1) botoes[atual + 1].click();
        } else {
            // swipe p/ direita → anterior
            if (atual > 0) botoes[atual - 1].click();
        }
    }
});