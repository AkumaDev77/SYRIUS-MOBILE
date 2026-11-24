// static/script/pages/bot.js
(function () {
    const messagesArea = document.getElementById('messagesArea');
    const messageInput = document.getElementById('messageInput');
    if (!messagesArea || !messageInput) return; // não está na página do bot

    async function sendMessage(message = null) {
        const text = message || messageInput.value.trim();
        if (!text) return;

        addMessage(text, 'sent');
        messageInput.value = '';
        messageInput.focus();
        showTyping();

        try {
            const response = await fetch(`/api/mensagem`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mensagem: text })
            });

            // Sessão expirada → login_required devolve 401 JSON com redirect
            if (response.status === 401) {
                const data = await response.json().catch(() => ({}));
                hideTyping();
                addMessage('🔒 Sessão expirada. Redirecionando para o login...', 'received', 'error');
                setTimeout(() => { window.location = data.redirect || '/login'; }, 1200);
                return;
            }

            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Resposta não é JSON');
            }

            const data = await response.json();
            hideTyping();

            if (data.error) {
                addMessage('❌ ' + data.error, 'received', 'error');
            } else if (data.type === 'mensagem') {
                addMessage(data.conteudo.texto, 'received', data.conteudo.tipo || '');
            } else {
                addMessage('✅ Operação realizada com sucesso!', 'received', 'success');
            }
        } catch (error) {
            hideTyping();
            console.error('Erro detalhado:', error);
            addMessage('❌ Erro ao conectar com o servidor.', 'received', 'error');
        }
    }

    function addMessage(text, type, customClass = '') {
        const wrapper = document.createElement('div');
        wrapper.className = `message-wrapper ${type}`;

        const bubble = document.createElement('div');
        bubble.className = `message-bubble ${customClass}`;

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.innerHTML = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
        bubble.appendChild(textDiv);

        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
        bubble.appendChild(time);

        wrapper.appendChild(bubble);
        messagesArea.appendChild(wrapper);

        setTimeout(() => { messagesArea.scrollTop = messagesArea.scrollHeight; }, 50);
    }

    function showTyping() {
        let indicator = messagesArea.querySelector('.typing-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'typing-indicator';
            indicator.innerHTML = '<span></span><span></span><span></span>';
            messagesArea.appendChild(indicator);
        }
        indicator.classList.add('active');
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }

    function hideTyping() {
        const indicator = messagesArea.querySelector('.typing-indicator');
        if (indicator) indicator.classList.remove('active');
    }

    // Expõe para os onclick="" do HTML
    window.sendMessage = sendMessage;

    messageInput.focus();
    console.log('Bot Financeiro carregado! 🚀');

    // ---------- TOGGLE DA NAVBAR ----------
    // Guarda o estado por página: { "bot-page": true (escondida), ... }
    const navbar = document.getElementById('navbarMobile');
    const btnToggleNavbar = document.getElementById('btnToggleNavbar');

    function setNavbarVisible(visible) {
        if (!navbar) return;
        navbar.classList.toggle('navbar-hidden', !visible);

        // Ajusta o padding-bottom do #content para o bot ocupar o espaço
        const content = document.getElementById('content');
        if (content) {
            content.classList.toggle('no-navbar-padding', !visible);
        }

        // Atualiza ícone do botão (barras ↔ fechar)
        if (btnToggleNavbar) {
            const icon = btnToggleNavbar.querySelector('i');
            if (icon) {
                icon.className = visible ? 'fas fa-bars' : 'fas fa-xmark';
            }
            btnToggleNavbar.setAttribute(
                'aria-label',
                visible ? 'Esconder menu' : 'Mostrar menu'
            );
        }
    }

    if (btnToggleNavbar) {
    btnToggleNavbar.addEventListener('click', () => {
        const escondida = navbar.classList.contains('navbar-hidden');
        setNavbarVisible(escondida); // se estava escondida → mostra
    });
    }

    window.setNavbarVisible = setNavbarVisible;

    // Ao entrar na página do bot, esconde a navbar (opcional).
    // Remova este bloco se quiser que o botão comece mostrando a navbar.

})();