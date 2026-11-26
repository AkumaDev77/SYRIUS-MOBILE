from flask import (
    Blueprint, render_template, request, redirect,
    session, flash, url_for, jsonify
)
from datetime import datetime, timedelta
from database.supabase_client import supabase, criar_cliente_dinamico
from extensions import limiter
from datetime import datetime, date
import locale
import yfinance as yf
import re
from difflib import get_close_matches
from functools import wraps
from flask import make_response, send_from_directory, current_app


home_route = Blueprint('home', __name__)

# ---------- CONTROLE DE TENTATIVAS (em memória) ----------
# Estrutura: { "cliente_id:email": {"count": int, "blocked_until": datetime|None} }
tentativas_falhas = {}
MAX_TENTATIVAS = 5
TEMPO_BLOQUEIO_MINUTOS = 5
JANELA_RESET_MINUTOS = 15   # se ficar 15 min sem errar, zera a contagem





#region DICIONARIO SUPORTE BOT

#! BIBLIOTECA DE MESES EM PORTUGUÊS
MESES_PT = {
    1: {'nome': 'Janeiro', 'abrev': 'Jan'},
    2: {'nome': 'Fevereiro', 'abrev': 'Fev'},
    3: {'nome': 'Março', 'abrev': 'Mar'},
    4: {'nome': 'Abril', 'abrev': 'Abr'},
    5: {'nome': 'Maio', 'abrev': 'Mai'},
    6: {'nome': 'Junho', 'abrev': 'Jun'},
    7: {'nome': 'Julho', 'abrev': 'Jul'},
    8: {'nome': 'Agosto', 'abrev': 'Ago'},
    9: {'nome': 'Setembro', 'abrev': 'Set'},
    10: {'nome': 'Outubro', 'abrev': 'Out'},
    11: {'nome': 'Novembro', 'abrev': 'Nov'},
    12: {'nome': 'Dezembro', 'abrev': 'Dez'}
}

def get_mes_pt(numero_mes):
    """Retorna o nome do mês em português"""
    return MESES_PT.get(numero_mes, {}).get('nome', '')

def get_mes_abrev_pt(numero_mes):
    """Retorna a abreviação do mês em português"""
    return MESES_PT.get(numero_mes, {}).get('abrev', '')


#! DICIONÁRIO DE ABREVIAÇÕES
ABREVIACOES = {
    # Alimentação
    'padaria': 'Padaria',
    'pad': 'Padaria',
    'padi': 'Padaria',
    'supermercado': 'Supermercado',
    'mercado': 'Supermercado',
    'merc': 'Supermercado',
    'super': 'Supermercado',
    'restaurante': 'Restaurante',
    'rest': 'Restaurante',
    'lanches': 'Lanches por Delivery',
    'lanch': 'Lanches por Delivery',
    'lanche': 'Lanches por Delivery',
    'ifood': 'Lanches por Delivery',
    'cafe': 'Lanchonetes',
    'sorvete': 'Lanchonetes',
    'sorv': 'Lanchonetes',
    'sacolao': 'Sacolão',
    'sacol': 'Sacolão',
    'suplementos': 'Loja de Suplementos',
    'suple': 'Loja de Suplementos',
    'sup': 'Loja de Suplementos',
    
    # Transporte
    'uber': 'Uber',
    'ube': 'Uber',
    'ub': 'Uber',
    'posto': 'Posto de Gasolina',
    'gasolina': 'Posto de Gasolina',
    'gas': 'Posto de Gasolina',
    'mecanica': 'Mecânica',
    'mec': 'Mecânica',
    'mecan': 'Mecânica',
    'oficina': 'Mecânica',
    'ipva': 'IPVA',
    'seguro': 'Associação Avap',
    'consorcio': 'Consorcio',
    'consor': 'Consorcio',
    'financiamento': 'Consorcio',
    
    # Saúde e Bem-estar
    'drogaria': 'Drogaria',
    'farm': 'Drogaria',
    'farma': 'Drogaria',
    'academia': 'Mensalidade Academia',
    'acad': 'Mensalidade Academia',
    'barbearia': 'Barbearia',
    'barb': 'Barbearia',
    'cabelo': 'Barbearia',
    
    # Compras
    'inter shop': 'Inter Shop',
    'shop': 'Inter Shop',
    'shopping': 'Inter Shop',
    'roupas': 'Roupas/Calçados',
    'roupa': 'Roupas/Calçados',
    'calcado': 'Roupas/Calçados',
    'calcados': 'Roupas/Calçados',
    'pet shop': 'Pet Shop',
    'pet': 'Pet Shop',
    'vet': 'Pet Shop',
    'acessorios': 'Loja de Acessórios',
    'acess': 'Loja de Acessórios',
    'acessorio': 'Loja de Acessórios',
    'celular': 'Acessórios Celular',
    'cel': 'Acessórios Celular',
    
    # Lazer
    'bar': 'Bar/Balada',
    'balada': 'Bar/Balada',
    'show': 'Shows e Eventos',
    'evento': 'Shows e Eventos',
    'viagem': 'Viagem',
    'travel': 'Viagem',
    'jogos': 'Jogos de Video Game',
    'jogo': 'Jogos de Video Game',
    'game': 'Jogos de Video Game',
    'carnaval': 'Carnaval',
    'fest': 'Carnaval',
    'clube': 'Clube de lazer',
    
    # Educação
    'curso': 'Compra de Cursos',
    'cursos': 'Compra de Cursos',
    'livro': 'Compra de Cursos',
    'livros': 'Compra de Cursos',
    
    # Casa
    'internet': 'Internet',
    'net': 'Internet',
    'wifi': 'Internet',
    'aluguel': 'Aluguél',
    'alug': 'Aluguél',
    'luz': 'Custos de Casa',
    'agua': 'Custos de Casa',
    'condominio': 'Custos de Casa',
    'cond': 'Custos de Casa',
    
    # Rendas
    'salario': 'Remuneração Grupo Hinova',
    'lucro 031' 'Lucro 031 Assados'
    'lucro 031 assados' 'Lucro 031 Assados'
    'salário': 'Remuneração Grupo Hinova',
    'remuneracao': 'Remuneração Grupo Hinova',
    'remuneração': 'Remuneração Grupo Hinova',
    'renda extra': 'Renda Extra Web',
    'extra': 'Renda Extra Web',
    'milhas': 'Venda de milhas',
    'cashback inter': 'Cashback Inter',
    'cashback xp': 'Cashback Xp',
    'dividendos': 'Dividendos',
    'fundos imobiliarios': 'Fundos Imobiliários',
    'fundo': 'Fundos Imobiliários',
    'fii': 'Fundos Imobiliários',
    'acoes': 'Ações',
    'acao': 'Ações',
    'cdb': 'Resgate CDB',
    'fgts': 'FGTS',
    'ferias': 'Férias 1/12',
    'férias': 'Férias 1/12',
    'decimo': 'Décimo Terceiro 1/12',
    'décimo': 'Décimo Terceiro 1/12',
    '13': 'Décimo Terceiro 1/12',
    'pis': 'Pis/Pasep',
}


@home_route.route('/service-worker.js')
def service_worker():

    response = send_from_directory(
        current_app.static_folder,
        'service-worker.js',
        mimetype='application/javascript'
    )

    response.headers['Service-Worker-Allowed'] = '/'

    return response


@home_route.route('/manifest.json')
def manifest():
    return send_from_directory(
        current_app.root_path,
        'manifest.json',
        mimetype='application/manifest+json'
    )



#! CACHE DO CADASTRO
class CadastroCache:
    def __init__(self):
        self._caches = {}  # { cliente_id: {"cadastros": {}, "descricao_para_cod": {}} }

    def _get_db(self, cliente_db):
        return cliente_db  # só para clareza

    def carregar_cadastros(self, cliente_db, cliente_id):
        try:
            result = cliente_db.table('finp_cad').select('*').execute()
            cadastros = {}
            descricao_para_cod = {}
            for item in result.data:
                cod = item['cod']
                cadastros[cod] = item
                desc_normalizada = ' '.join(item['descricao'].lower().split())
                descricao_para_cod[desc_normalizada] = cod
            self._caches[cliente_id] = {
                "cadastros": cadastros,
                "descricao_para_cod": descricao_para_cod
            }
            print(f"✅ Cadastros carregados p/ {cliente_id}: {len(cadastros)} itens")
            return True
        except Exception as e:
            print(f"❌ Erro ao carregar cadastros: {e}")
            return False

    def _get_cache(self, cliente_id, cliente_db=None):
        if cliente_id not in self._caches and cliente_db:
            self.carregar_cadastros(cliente_db, cliente_id)
        return self._caches.get(cliente_id, {"cadastros": {}, "descricao_para_cod": {}})

    def buscar_por_cod(self, cliente_id, cod):
        return self._get_cache(cliente_id)["cadastros"].get(cod)

    def buscar_por_descricao_exata(self, cliente_id, descricao):
        cache = self._get_cache(cliente_id)
        desc_norm = ' '.join(descricao.lower().strip().split())
        cod = cache["descricao_para_cod"].get(desc_norm)
        return cache["cadastros"].get(cod) if cod else None

    def buscar_por_abreviacao(self, cliente_id, descricao):
        descricao_lower = descricao.lower().strip()
        for abrev, desc_completa in ABREVIACOES.items():
            if abrev in descricao_lower:
                cadastro = self.buscar_por_descricao_exata(cliente_id, desc_completa)
                if cadastro:
                    return cadastro
        return None

    def buscar_por_palavra_chave(self, cliente_id, descricao):
        cache = self._get_cache(cliente_id)
        palavras = [p for p in descricao.lower().strip().split() if len(p) >= 4]
        for cod, cadastro in cache["cadastros"].items():
            desc_item = cadastro['descricao'].lower()
            for palavra in palavras:
                if palavra in desc_item:
                    return cadastro
        return None

    def buscar_por_similaridade(self, cliente_id, descricao, cutoff=0.8):
        cache = self._get_cache(cliente_id)
        descricao_lower = descricao.lower().strip()
        if len(descricao_lower) < 4:
            return None
        descricoes = list(cache["descricao_para_cod"].keys())
        matches = get_close_matches(descricao_lower, descricoes, n=1, cutoff=cutoff)
        if matches:
            cod = cache["descricao_para_cod"].get(matches[0])
            return cache["cadastros"].get(cod) if cod else None
        return None

    def buscar_inteligente(self, cliente_id, descricao, cliente_db=None):
        self._get_cache(cliente_id, cliente_db)  # garante carregado
        r = self.buscar_por_descricao_exata(cliente_id, descricao)
        if r: return r, 'exata'
        r = self.buscar_por_abreviacao(cliente_id, descricao)
        if r: return r, 'abreviacao'
        r = self.buscar_por_palavra_chave(cliente_id, descricao)
        if r: return r, 'palavra_chave'
        r = self.buscar_por_similaridade(cliente_id, descricao, cutoff=0.85)
        if r: return r, 'similaridade'
        return None, None

    def sugerir_descricoes(self, cliente_id, descricao, limite=5):
        cache = self._get_cache(cliente_id)
        descricao_lower = descricao.lower().strip()
        if len(descricao_lower) < 3:
            return []
        descricoes = list(cache["descricao_para_cod"].keys())
        matches = get_close_matches(descricao_lower, descricoes, n=limite, cutoff=0.4)
        return matches if matches else []

    def invalidar(self, cliente_id):
        self._caches.pop(cliente_id, None)

# Instância global do cache (agora é um gerenciador de caches por cliente)
cadastro_cache = CadastroCache()


#endregion


#region FUNÇÕES DO BOT
#! HELPERS DE PARSING
def parse_mensagem_inteligente(mensagem, cliente_id, cliente_db):
    """Interpreta mensagem natural e extrai dados usando o cadastro DO CLIENTE"""
    mensagem = mensagem.strip()

    padrao_simples = r'^(.+?)\s+([\d,]+\.?\d*)(?:\s+(.+))?$'
    padrao_completo = r'^(ganho|gasto|receita|despesa|investimento)\s+(.+?)\s+([\d,]+\.?\d*)(?:\s+(.+))?$'

    descricao = None
    valor = None
    tipo_usuario = None
    observacao = None

    match = re.match(padrao_completo, mensagem, re.IGNORECASE)
    if match:
        tipo_usuario = match.group(1).lower()
        descricao = match.group(2).strip()
        valor_str = match.group(3).replace(',', '.')
        valor = float(valor_str)
        observacao = match.group(4).strip() if match.group(4) else None
    else:
        match = re.match(padrao_simples, mensagem)
        if match:
            descricao = match.group(1).strip()
            valor_str = match.group(2).replace(',', '.')
            valor = float(valor_str)
            observacao = match.group(3).strip() if match.group(3) else None

    if not descricao or not valor:
        return None

    if len(descricao.strip()) < 3:
        return {
            'valor': valor,
            'descricao_original': descricao,
            'observacao': observacao,
            'cadastro_encontrado': False,
            'sugestoes': [],
            'erro': 'descricao_muito_curta'
        }

    # Busca no cache DO CLIENTE
    cadastro, metodo = cadastro_cache.buscar_inteligente(
        cliente_id, descricao, cliente_db
    )

    if cadastro:
        return {
            'valor': valor,
            'tipo': tipo_usuario,
            'cod': cadastro['cod'],
            'descricao_cadastro': cadastro['descricao'],
            'tipo_cadastro': cadastro['tipo'],
            'categoria': cadastro['categoria'],
            'grupo': cadastro['grupo'],
            'natureza_cadastro': cadastro['natureza'],
            'cadastro_encontrado': True,
            'metodo_match': metodo,
            'descricao_original': descricao,
            'observacao': observacao
        }
    else:
        sugestoes = cadastro_cache.sugerir_descricoes(cliente_id, descricao)
        return {
            'valor': valor,
            'tipo_usuario': tipo_usuario,
            'descricao_original': descricao,
            'observacao': observacao,
            'cadastro_encontrado': False,
            'sugestoes': sugestoes,
            'erro': 'descricao_nao_encontrada'
        }


#endregion



#region FUNÇÕES LOGIN


def _chave_conta(cliente_id: str, email: str) -> str:
    return f"{cliente_id.lower()}:{email.lower()}"


def _conta_bloqueada(chave: str):
    """Retorna (bloqueado: bool, minutos_restantes: int)."""
    reg = tentativas_falhas.get(chave)
    if not reg:
        return False, 0

    agora = datetime.now()

    # Bloqueio ativo?
    if reg.get("blocked_until") and agora < reg["blocked_until"]:
        restante = int((reg["blocked_until"] - agora).total_seconds() / 60) + 1
        return True, restante

    # Bloqueio expirou → limpa
    if reg.get("blocked_until") and agora >= reg["blocked_until"]:
        tentativas_falhas.pop(chave, None)
        return False, 0

    # Sem bloqueio, mas inatividade longa → zera contagem
    if reg.get("last_attempt") and (agora - reg["last_attempt"]).total_seconds() > JANELA_RESET_MINUTOS * 60:
        tentativas_falhas.pop(chave, None)
        return False, 0

    return False, 0


def _registrar_falha(chave: str) -> int:
    """Incrementa a contagem e bloqueia se atingir o limite. Retorna a contagem atual."""
    agora = datetime.now()
    reg = tentativas_falhas.get(chave, {"count": 0, "blocked_until": None, "last_attempt": agora})
    reg["count"] += 1
    reg["last_attempt"] = agora

    if reg["count"] >= MAX_TENTATIVAS:
        reg["blocked_until"] = agora + timedelta(minutes=TEMPO_BLOQUEIO_MINUTOS)

    tentativas_falhas[chave] = reg
    return reg["count"]


def _limpar_tentativas(chave: str) -> None:
    tentativas_falhas.pop(chave, None)

def _get_cliente_db():
    if not session.get("supabase_url") or not session.get("supabase_key"):
        raise RuntimeError("Sessão sem credenciais do cliente")

    cliente_db = criar_cliente_dinamico(
        session["supabase_url"],
        session["supabase_key"]
    )

    access_token = session.get("access_token")
    refresh_token = session.get("refresh_token", "")
    if access_token:
        cliente_db.auth.set_session(access_token, refresh_token)

    return cliente_db


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        # 1 - Verifica se existe sessão mínima
        if (
            not session.get("user_id")
            or not session.get("access_token")
            or not session.get("supabase_url")
            or not session.get("supabase_key")
        ):
            session.clear()
            return _redirecionar_para_login()

        # 2 - Verifica se o token ainda é válido no banco do cliente
        try:
            cliente_db = criar_cliente_dinamico(
                session["supabase_url"],
                session["supabase_key"]
            )
            cliente_db.auth.get_user(session["access_token"])

        except Exception as e:
            print(f"⚠️ Token expirado ou inválido: {e}")
            session.clear()
            return _redirecionar_para_login()

        return f(*args, **kwargs)

    return decorated_function


def _redirecionar_para_login():
    """Resposta padronizada: JSON para AJAX, redirect para navegação normal."""
    if (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or request.is_json
    ):
        return jsonify({
            "success": False,
            "message": "Sua sessão expirou. Faça login novamente.",
            "redirect": url_for("home.login")
        }), 401

    return redirect(url_for("home.login"))





#endregion



#region API BOT

# ---------- helpers internos (recebem cliente_db explicitamente) ----------

def _listar_lancamentos_db(cliente_db, limite=None):
    """Lista lançamentos do banco do cliente."""
    try:
        query = cliente_db.table('finp_movfin').select('*').order('id', desc=True)
        if limite:
            query = query.limit(limite)

        result = query.execute()
        lancamentos = result.data

        if lancamentos:
            mensagem = "📊 <b>Últimos Lançamentos:</b><br><br>"
            for item in lancamentos[:limite or 10]:
                valor = float(item['valor'])
                natureza = item['natureza']
                emoji = '📤' if natureza == 'D' else '📥'
                sinal = '-' if natureza == 'D' else '+'
                mensagem += (
                    f"{emoji} <b>{item['descricao']}</b> - {sinal}R$ {valor:.2f}<br>"
                    f"&nbsp;&nbsp;🆔 ID: {item['id']} | 📅 {item['data']} | {item['categoria']}<br><br>"
                )
        else:
            mensagem = "📭 Nenhum lançamento encontrado"

        return jsonify({
            'type': 'mensagem',
            'conteudo': {
                'texto': mensagem,
                'tipo': 'lista',
                'dados': lancamentos[:limite or 10] if lancamentos else []
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _criar_lancamento_db(cliente_db, dados):
    """Cria lançamento no banco do cliente."""
    try:
        if not dados.get('cadastro_encontrado', False):
            return jsonify({
                'type': 'mensagem',
                'conteudo': {
                    'texto': '❌ <b>Não é possível lançar sem cadastro!</b><br><br>'
                             'Use uma descrição que exista no cadastro ou veja /ajuda',
                    'tipo': 'erro'
                }
            })

        hoje = date.today()
        mes_num = hoje.month
        cod = dados.get('cod')

        # Busca no cadastro DO CLIENTE
        response = (
            cliente_db.table("finp_cad")
            .select("tipo, categoria, grupo, natureza")
            .eq("cod", cod)
            .execute()
        )

        if not response.data:
            return jsonify({"error": "Código não encontrado na tabela Finp_cad"}), 400

        despesa = response.data[0]
        descricao_banco = dados.get('descricao_cadastro', '')
        tipo_cadastro = dados.get('tipo_cadastro', '')
        natureza_cadastro = dados.get('natureza_cadastro', '')

        novo_lancamento = {
            'data': hoje.strftime('%Y-%m-%d'),
            'mes': get_mes_pt(mes_num),
            'ano': hoje.strftime('%Y'),
            'id_mes': mes_num,
            'mes_abrev': get_mes_abrev_pt(mes_num),
            'cod': cod,
            'descricao': descricao_banco,
            'tipo': despesa["tipo"],
            'categoria': despesa["categoria"],
            'grupo': despesa["grupo"],
            'natureza': despesa["natureza"],
            'valor': float(dados.get('valor', 0)),
            'observacao': dados.get('observacao', ''),
            'data_lanc': hoje.strftime('%Y-%m-%d %H:%M:%S')
        }

        print(f"📝 Dados do lançamento (cliente em sessão):")
        print(f"  - Descrição: {descricao_banco}")
        print(f"  - Tipo (cadastro): {tipo_cadastro}")
        print(f"  - Natureza (cadastro): {natureza_cadastro}")
        print(f"  - Categoria: {dados.get('categoria')}")
        print(f"  - Grupo: {dados.get('grupo')}")
        print(f"  - Código: {cod}")
        print(f"  - Match: {dados.get('metodo_match')}")

        result = cliente_db.table('finp_movfin').insert(novo_lancamento).execute()

        if result.data:
            emoji = '📤' if tipo_cadastro == 'Saída' else '📥'
            sinal = '-' if tipo_cadastro == 'Saída' else '+'

            metodo = dados.get('metodo_match', '')
            desc_original = dados.get('descricao_original', '')
            desc_cadastro = dados.get('descricao_cadastro', '')

            if metodo == 'exata':
                msg_match = "✅ Match exato com o cadastro!"
            elif metodo == 'abreviacao':
                msg_match = f"🔍 <b>{desc_original}</b> → <b>{desc_cadastro}</b> (abreviação)"
            elif metodo == 'palavra_chave':
                msg_match = f"🔍 Palavra-chave reconhecida: <b>{desc_cadastro}</b>"
            elif metodo == 'similaridade':
                msg_match = f"🔍 Similar a: <b>{desc_cadastro}</b>"
            else:
                msg_match = f"✅ Encontrado no cadastro: <b>{desc_cadastro}</b>"

            observacao_texto = (
                f"<br>📝 Obs: {dados.get('observacao', '')}"
                if dados.get('observacao') else ''
            )

            return jsonify({
                'type': 'mensagem',
                'conteudo': {
                    'texto': f"✅ <b>Lançamento realizado com sucesso!</b><br><br>"
                             f"{emoji} <b>{descricao_banco}</b><br>"
                             f"{sinal}R$ {float(dados.get('valor', 0)):.2f}<br>"
                             f"📅 {hoje.strftime('%d/%m/%Y')}<br>"
                             f"🏷️ {dados.get('categoria')} &gt; {dados.get('grupo')}<br>"
                             f"📋 Tipo: {tipo_cadastro} | Natureza: {natureza_cadastro}<br>"
                             f"🆔 ID: {result.data[0]['id']}{observacao_texto}<br><br>"
                             f"🔎 {msg_match}",
                    'tipo': 'sucesso',
                    'dados': result.data[0]
                }
            })
        else:
            return jsonify({'error': 'Erro ao criar lançamento'}), 500

    except Exception as e:
        print(f"❌ Erro ao criar lançamento: {e}")
        return jsonify({'error': str(e)}), 500


def _calcular_saldo_db(cliente_db):
    """Calcula saldo no banco do cliente."""
    try:
        result = cliente_db.table('finp_movfin').select('tipo, valor').execute()

        if not result.data:
            return jsonify({
                'type': 'mensagem',
                'conteudo': {
                    'texto': '💰 <b>Saldo Atual</b><br><br>Nenhum lançamento encontrado. Saldo: R$ 0,00',
                    'tipo': 'saldo',
                    'dados': {'total_credito': 0, 'total_debito': 0, 'saldo': 0}
                }
            })

        # ⚠️ Ajuste 'Entrada'/'Saída' se sua coluna `tipo` guardar 'ganho'/'gasto'
        total_credito = sum(float(i['valor']) for i in result.data if i['tipo'] == 'Entrada')
        total_debito = sum(float(i['valor']) for i in result.data if i['tipo'] == 'Saída')
        saldo = total_credito - total_debito

        mensagem = (
            f"💰 <b>Saldo Atual</b><br><br>"
            f"📥 Total Receitas: R$ {total_credito:.2f}<br>"
            f"📤 Total Despesas: R$ {total_debito:.2f}<br>"
            f"──────────────────────────────<br>"
            f"📊 <b>Saldo: R$ {saldo:.2f}</b>"
        )

        return jsonify({
            'type': 'mensagem',
            'conteudo': {
                'texto': mensagem,
                'tipo': 'saldo',
                'dados': {
                    'total_credito': total_credito,
                    'total_debito': total_debito,
                    'saldo': saldo
                }
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _deletar_lancamento_db(cliente_db, id):
    """Deleta lançamento no banco do cliente."""
    try:
        busca = cliente_db.table('finp_movfin').select('*').eq('id', id).execute()

        if not busca.data:
            return jsonify({
                'type': 'mensagem',
                'conteudo': {
                    'texto': f'❌ Lançamento com ID {id} não encontrado',
                    'tipo': 'sistema'
                }
            })

        result = cliente_db.table('finp_movfin').delete().eq('id', id).execute()

        if result.data:
            return jsonify({
                'type': 'mensagem',
                'conteudo': {
                    'texto': f'🗑️ <b>Lançamento deletado com sucesso!</b><br><br>'
                             f'ID: {id}<br>'
                             f'Descrição: {busca.data[0]["descricao"]}<br>'
                             f'Valor: R$ {float(busca.data[0]["valor"]):.2f}',
                    'tipo': 'sucesso'
                }
            })
        else:
            return jsonify({'error': 'Erro ao deletar lançamento'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------- ROTAS ----------

@home_route.route('/api/mensagem', methods=['POST'])
@login_required
def processar_mensagem():
    """Processa mensagem do chat e executa ação"""
    data = request.json or {}
    mensagem = data.get('mensagem', '').strip()

    if not mensagem:
        return jsonify({'error': 'Mensagem vazia'}), 400

    cliente_id = session.get('cliente_id')
    cliente_db = _get_cliente_db()

    # Comandos especiais
    if mensagem.lower() == '/listar':
        return _listar_lancamentos_db(cliente_db)

    if mensagem.lower().startswith('/ultimos'):
        try:
            limite = int(mensagem.split()[1]) if len(mensagem.split()) > 1 else 5
        except Exception:
            limite = 5
        return _listar_lancamentos_db(cliente_db, limite)

    if mensagem.lower() == '/saldo':
        return _calcular_saldo_db(cliente_db)

    if mensagem.lower() == '/recarregar':
        cadastro_cache.carregar_cadastros(cliente_db, cliente_id)
        return jsonify({
            'type': 'mensagem',
            'conteudo': {
                'texto': '✅ Cadastro recarregado com sucesso!',
                'tipo': 'sucesso'
            }
        })

    if mensagem.lower() == '/cadastros':
        try:
            result = (
                cliente_db.table('finp_cad')
                .select('tipo, descricao')
                .order('tipo')
                .order('descricao')
                .execute()
            )

            if not result.data:
                return jsonify({
                    'type': 'mensagem',
                    'conteudo': {
                        'texto': '📭 Nenhum cadastro encontrado.',
                        'tipo': 'sistema'
                    }
                })

            entradas = []
            saidas = []

            for item in result.data:
                tipo = (item.get('tipo') or '').strip()
                descricao = (item.get('descricao') or '').strip()
                if not descricao:
                    continue
                if tipo == 'Entrada':
                    entradas.append(descricao)
                elif tipo == 'Saída':
                    saidas.append(descricao)

            entradas = sorted(set(entradas))
            saidas = sorted(set(saidas))

            texto = "📚 <b>Cadastros Disponíveis</b><br><br>"
            texto += f"📥 <b>ENTRADAS</b> ({len(entradas)})<br>"
            if entradas:
                for desc in entradas:
                    texto += f"&nbsp;&nbsp;• {desc}<br>"
            else:
                texto += "&nbsp;&nbsp;<i>Nenhuma entrada cadastrada</i><br>"

            texto += "<br>"
            texto += f"📤 <b>SAÍDAS</b> ({len(saidas)})<br>"
            if saidas:
                for desc in saidas:
                    texto += f"&nbsp;&nbsp;• {desc}<br>"
            else:
                texto += "&nbsp;&nbsp;<i>Nenhuma saída cadastrada</i><br>"

            texto += f"<br>━━━━━━━━━━━━━━━━━━<br>"
            texto += f"📊 <b>Total:</b> {len(entradas) + len(saidas)} cadastros"

            return jsonify({
                'type': 'mensagem',
                'conteudo': {'texto': texto, 'tipo': 'lista'}
            })
        except Exception as e:
            print(f"❌ Erro ao listar cadastros: {e}")
            return jsonify({
                'type': 'mensagem',
                'conteudo': {
                    'texto': f'❌ Erro ao carregar cadastros: {str(e)}',
                    'tipo': 'erro'
                }
            })

    if mensagem.lower() == '/ajuda':
        return jsonify({
            'type': 'mensagem',
            'conteudo': {
                'texto': '📋 <b>Comandos disponíveis:</b><br><br>'
                         '• <b>[descrição] [valor]</b> - Ex: "Padaria 5,50"<br>'
                         '• <b>gasto [descrição] [valor]</b> - Ex: "gasto Uber 25,00"<br>'
                         '• <b>ganho [descrição] [valor]</b> - Ex: "ganho Salário 1500"<br>'
                         '• <b>/listar</b> - Lista todos lançamentos<br>'
                         '• <b>/ultimos [n]</b> - Lista últimos N lançamentos<br>'
                         '• <b>/saldo</b> - Mostra saldo atual<br>'
                         '• <b>/deletar [id]</b> - Deleta um lançamento<br>'
                         '• <b>/recarregar</b> - Recarrega o cadastro<br>'
                         '• <b>/cadastros</b> - Mostra total de cadastros<br><br>'
                         '💡 <b>Dica:</b> O bot reconhece automaticamente<br>'
                         'abreviações como "Ube" para "Uber" ou "Merc" para "Supermercado"<br><br>'
                         '⚠️ <b>Importante:</b> Só lança se encontrar a descrição no cadastro!',
                'tipo': 'sistema'
            }
        })

    if mensagem.lower().startswith('/deletar'):
        try:
            id_lancamento = int(mensagem.split()[1])
            return _deletar_lancamento_db(cliente_db, id_lancamento)
        except Exception:
            return jsonify({
                'type': 'mensagem',
                'conteudo': {
                    'texto': '❌ Use: /deletar [id] - Ex: /deletar 5',
                    'tipo': 'sistema'
                }
            })

    # Tenta parsear mensagem natural
    dados = parse_mensagem_inteligente(mensagem, cliente_id, cliente_db)

    if dados:
        if not dados.get('cadastro_encontrado', False):
            sugestoes = dados.get('sugestoes', [])
            desc_original = dados.get('descricao_original', '')
            valor = dados.get('valor', 0)

            if dados.get('erro') == 'descricao_muito_curta':
                mensagem_erro = (
                    f"❌ <b>Descrição muito curta!</b><br><br>"
                    f"📝 Você digitou: <b>{desc_original}</b><br>"
                    f"💰 Valor: R$ {valor:.2f}<br><br>"
                    f"💡 A descrição precisa ter pelo menos 3 caracteres.<br>"
                    f"🔄 Tente uma descrição mais completa."
                )
            elif sugestoes:
                texto_sugestoes = '<br>'.join([f'&nbsp;&nbsp;• {s}' for s in sugestoes[:5]])
                mensagem_erro = (
                    f"❌ <b>Descrição não encontrada no cadastro!</b><br><br>"
                    f"📝 Você digitou: <b>{desc_original}</b><br>"
                    f"💰 Valor: R$ {valor:.2f}<br><br>"
                    f"💡 <b>Sugestões disponíveis:</b><br>{texto_sugestoes}<br><br>"
                    f"🔄 Tente novamente com uma das sugestões acima ou use /ajuda"
                )
            else:
                mensagem_erro = (
                    f"❌ <b>Descrição não encontrada no cadastro!</b><br><br>"
                    f"📝 Você digitou: <b>{desc_original}</b><br>"
                    f"💰 Valor: R$ {valor:.2f}<br><br>"
                    f"💡 Nenhuma sugestão disponível.<br>"
                    f"🔄 Tente usar uma descrição mais comum ou use /ajuda"
                )

            return jsonify({
                'type': 'mensagem',
                'conteudo': {'texto': mensagem_erro, 'tipo': 'erro'}
            })

        return _criar_lancamento_db(cliente_db, dados)

    return jsonify({
        'type': 'mensagem',
        'conteudo': {
            'texto': '❓ Não entendi. Tente: "[descrição] [valor]" ou "/ajuda" para ver comandos',
            'tipo': 'sistema'
        }
    })


@home_route.route('/api/lancamentos', methods=['GET'])
@login_required
def listar_lancamentos():
    """Lista lançamentos do cliente logado."""
    return _listar_lancamentos_db(_get_cliente_db())


@home_route.route('/api/lancamentos', methods=['POST'])
@login_required
def criar_lancamento():
    """Cria um novo lançamento no banco do cliente logado."""
    return _criar_lancamento_db(_get_cliente_db(), request.json or {})


@home_route.route('/api/saldo', methods=['GET'])
@login_required
def calcular_saldo():
    """Calcula saldo do cliente logado."""
    return _calcular_saldo_db(_get_cliente_db())


@home_route.route('/api/lancamentos/<int:id>', methods=['DELETE'])
@login_required
def deletar_lancamento(id):
    """Deleta um lançamento do banco do cliente logado."""
    return _deletar_lancamento_db(_get_cliente_db(), id)


#endregion


#region ROTAS DE TELA

#! Pagina de LOGIN
@home_route.route('/')
def login2():
    if session.get('user_id'): # Se já estiver logado
        return redirect(url_for('home.index'))
    return render_template('pages/login.html')


@home_route.route('/login')
def login():
    return render_template('pages/login.html')

#! Pagina Principal
@home_route.route('/index')
@login_required
def index():
    return render_template('pages/index.html')


#endregion



#region API HOME 






def home_getData(cliente_db, limite=None):
    try:
        # ---------- 1. Nome do usuário ----------
        nome = session.get('nome')
        if not nome:
            return jsonify({'error': 'Usuário não autenticado'}), 401

        nome = nome.strip()
        inicial = nome[0].upper() if nome else '?'

        # ---------- 2. Saudação pela hora ----------
        hora = datetime.now().hour
        if 5 <= hora < 12:
            saudacao = 'Bom dia'
        elif 12 <= hora < 18:
            saudacao = 'Boa tarde'
        else:
            saudacao = 'Boa noite'

        # ---------- 3. Mês atual (pt-BR) ----------
        meses = [
            'janeiro', 'fevereiro', 'março', 'abril',
            'maio', 'junho', 'julho', 'agosto',
            'setembro', 'outubro', 'novembro', 'dezembro'
        ]

        hoje = datetime.now()
        mes_atual = meses[hoje.month - 1]
        id_mes_atual = hoje.month
        ano_atual = str(hoje.year)

        # ---------- 4. Consulta no banco (mês atual) ----------
        query = (
            cliente_db
            .table('finp_movfin')
            .select('tipo, valor')
            .eq('id_mes', id_mes_atual)
            .eq('ano', ano_atual)
        )

        if limite:
            query = query.limit(limite)

        result = query.execute()
        lancamentos = result.data or []

        # ---------- 5. Calcula entradas e saídas ----------
        total_entrada = 0.0
        total_saida = 0.0

        for item in lancamentos:
            valor = float(item.get('valor') or 0)
            tipo = (item.get('tipo') or '').strip()

            if tipo == 'Entrada':
                total_entrada += valor
            elif tipo == 'Saida':
                total_saida += valor

        saldo_mes = total_entrada - total_saida

        # ---------- 6. Percentual gasto ----------
        # Se entrou R$ 1000 e saiu R$ 590 → gastou 59%
        percentual_gasto = 0
        if total_entrada > 0:
            percentual_gasto = round((total_saida / total_entrada) * 100)


        # ---------- 7. Retorno ----------
        return jsonify({
            'nome': nome,
            'avatar': inicial,
            'saudacao': saudacao,
            'mes': mes_atual,

            # dados financeiros do mês
            'total_entrada': round(total_entrada, 2),
            'total_saida': round(total_saida, 2),
            'saldo_mes': round(saldo_mes, 2),
            'percentual_gasto': percentual_gasto
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500





@home_route.route('/api/home', methods=['GET'])
@login_required
def api_home():
    try:
        # ajuste 'get_db' para o nome do seu cliente_db
        cliente_db = _get_cliente_db()
        return home_getData(cliente_db)
    except Exception as e:
        return jsonify({'error': str(e)}), 500










#endregion

#region REALIZAR LOGIN/LOGOUT

@home_route.route('/logrequest', methods=['POST'])
@limiter.limit("5 per minute")
def login_request():

    #* Recebe os dados do frontend
    cliente_id = (request.form.get('cliente_id') or '').strip()
    email      = (request.form.get('email') or '').strip()
    senha      = request.form.get('senha') or ''

    #* Validação básica
    if not cliente_id:
        flash('Informe o Cliente ID.', 'error')
        return redirect(url_for('home.login'))
    if not email or not senha:
        flash('Informe e-mail e senha.', 'error')
        return redirect(url_for('home.login'))

    chave = _chave_conta(cliente_id, email)

    #* 0. Conta já está bloqueada?
    bloqueado, minutos = _conta_bloqueada(chave)
    if bloqueado:
        msg = f'Muitas tentativas. Tente novamente em {minutos} minuto(s).'
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return jsonify({"success": False, "message": msg}), 401
        flash(msg, 'error')
        return redirect(url_for('home.login'))

    print(cliente_id)    

    try:
        #* 1. Consulta no banco MASTER
        resp = (
            supabase
            .table('credenciais_finp')
            .select('url, api_key, bloq_total, bloq_exctmaster')
            .eq('cliente_id', cliente_id)
            .limit(1)
            .execute()
        )

        if not resp.data:
            msg = 'Cliente ID não encontrado.'
            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                return jsonify({"success": False, "message": msg}), 401
            flash(msg, 'error')
            return redirect(url_for('home.login'))

        cred = resp.data[0]
        client_url = cred['url']
        client_key = cred['api_key']

        #* 1.1 Verifica bloqueios administrativos ANTES de qualquer auth
        if cred.get('bloq_total') or cred.get('bloq_exctmaster'):
            msg = 'Acesso bloqueado. Entre em contato com o suporte para mais informações.'
            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                return jsonify({"success": False, "message": msg}), 401
            flash(msg, 'error')
            return redirect(url_for('home.login'))

        #* 2. Cria o cliente dinâmico (banco do cliente)
        cliente_db = criar_cliente_dinamico(client_url, client_key)

        #* 3. Autentica no Supabase Auth DO CLIENTE
        try:
            auth_response = cliente_db.auth.sign_in_with_password({
                "email": email,
                "password": senha
            })
        except Exception as e:
            print("❌ AUTH ERRO:", e)
            count = _registrar_falha(chave)

            msg = ''
            if count >= MAX_TENTATIVAS:
                msg = f'Conta bloqueada por {TEMPO_BLOQUEIO_MINUTOS} minutos devido a múltiplas tentativas incorretas.'
            else:
                restantes = MAX_TENTATIVAS - count
                msg = f'E-mail ou senha inválidos. Restam {restantes} tentativa(s).'

            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                return jsonify({"success": False, "message": msg}), 401

            flash(msg, 'error')
            return redirect(url_for('home.login'))

        user = auth_response.user

        if not user:
            msg = 'Não foi possível autenticar. Verifique se o e-mail foi confirmado.'
            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                return jsonify({"success": False, "message": msg}), 401
            flash(msg, 'error')
            return redirect(url_for('home.login'))

        #* 3.1 Pegar informações de credenciais
        nome_cliente = (user.user_metadata or {}).get('user_name')

        print(nome_cliente)

        #* 4. Sucesso → limpa tentativas e salva sessão
        _limpar_tentativas(chave)

        session['supabase_url'] = client_url
        session['supabase_key'] = client_key
        session['cliente_id']   = cliente_id
        session['user_id']      = user.id
        session['user_email']   = user.email
        session['nome']         = nome_cliente
        session['access_token'] = auth_response.session.access_token
        session['refresh_token']= auth_response.session.refresh_token

        # Retorna JSON se for requisição AJAX, senão mantém o redirect padrão
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return jsonify({
                "success": True,
                "message": f"Login OK! Bem-vindo, {nome_cliente}.",
                "redirect": url_for('home.index')
            })
            
        flash(f'Login OK! Bem-vindo, {nome_cliente}.', 'success')
        return redirect(url_for('home.index'))

    # 👇 ESTE É O EXCEPT QUE ESTAVA FALTANDO
    except Exception as e:
        print("❌ ERRO GERAL:", e)
        msg = f'Erro ao validar cliente: {e}'
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return jsonify({"success": False, "message": msg}), 500
        flash(msg, 'error')
        return redirect(url_for('home.login'))




#! ---------- LOGOUT ----------
@home_route.route('/logout')
def logout():
    try:
        if session.get("access_token") and session.get("supabase_url"):
            cliente_db = criar_cliente_dinamico(
                session["supabase_url"], session["supabase_key"]
            )
            cliente_db.auth.sign_out()
    except Exception as e:
        print(f"⚠️ Erro ao encerrar sessão remota: {e}")
    finally:
        cliente_id = session.get("cliente_id")
        if cliente_id:
            cadastro_cache.invalidar(cliente_id)
        session.clear()
    return redirect(url_for('home.login'))






#endregion



