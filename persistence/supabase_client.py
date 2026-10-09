import os
from typing import Any

def _load_env_file():
    """Load variables from .env if present."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

_load_env_file()

_supabase_client = None

def is_supabase_configured() -> bool:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return bool(url and key and url.startswith("http"))

def get_supabase_client() -> Any | None:
    """
    Returns an active Supabase Client, or None if credentials are not configured.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not is_supabase_configured():
        return None

    try:
        from supabase import create_client
        url = os.environ["SUPABASE_URL"].strip()
        key = os.environ["SUPABASE_KEY"].strip()
        _supabase_client = create_client(url, key)
        return _supabase_client
    except Exception as e:
        print(f"[Supabase Init Warning] Could not connect: {e}")
        return None
