# database/supabase_client.py — versão ajustada
import os
from dotenv import load_dotenv
from supabase import create_client
import httpx

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

url = os.getenv("SUPABASE_URL")
# Usa service_role se existir, senão cai para anon (ok p/ teste com RLS off)
key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("⚠ ERRO: SUPABASE_URL ou SUPABASE_KEY não definidas no .env!")

supabase = create_client(url, key)
supabase.postgrest.session.timeout = httpx.Timeout(60.0)


def criar_cliente_dinamico(client_url: str, client_key: str):
    if not client_url or not client_key:
        raise ValueError("⚠ ERRO: url ou key do cliente não informadas.")
    cliente = create_client(client_url, client_key)
    cliente.postgrest.session.timeout = httpx.Timeout(60.0)
    return cliente