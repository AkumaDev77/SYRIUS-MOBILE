
# database/supabase_client.py

import os
import httpx
from dotenv import load_dotenv
from supabase import create_client

# Carrega .env localmente.
# Na Vercel, utiliza as Environment Variables configuradas no painel.
dotenv_path = os.path.join(
    os.path.dirname(__file__), "..", ".env"
)
load_dotenv(dotenv_path)

url = os.getenv("SUPABASE_URL", "").strip()
# Usa service_role se existir, senão cai para anon (ok p/ teste com RLS off)
key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError(
        "ERRO: SUPABASE_URL ou SUPABASE_KEY não configuradas."
    )

if not url.startswith("https://"):
    raise ValueError("ERRO: SUPABASE_URL inválida.")

# Cliente principal
supabase = create_client(url, key)
supabase.postgrest.session.timeout = httpx.Timeout(60.0)


def criar_cliente_dinamico(client_url: str, client_key: str):

    if not client_url or not client_key:
        raise ValueError("URL ou chave do cliente não informadas.")

    cliente = create_client(
        client_url.strip(),
        client_key.strip()
    )

    cliente.postgrest.session.timeout = httpx.Timeout(60.0)

    return cliente


# Cliente administrativo separado, quando necessário
def criar_cliente_admin():

    secret_key = os.getenv("SUPABASE_SECRET_KEY", "").strip()

    if not secret_key:
        raise ValueError("SUPABASE_SECRET_KEY não configurada.")

    cliente = create_client(url, secret_key)
    cliente.postgrest.session.timeout = httpx.Timeout(60.0)

    return cliente
