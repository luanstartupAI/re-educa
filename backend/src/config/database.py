"""
Configuração do banco de dados RE-EDUCA Store
"""
import os
from supabase import create_client, Client
from typing import Optional
from .settings import get_config

class DatabaseConfig:
    """Configuração do banco de dados"""
    
    def __init__(self):
        self.config = get_config()
        self.supabase: Optional[Client] = None
        self._initialize_supabase()
    
    def _initialize_supabase(self):
        """Inicializa a conexão com o Supabase"""
        try:
            self.supabase = create_client(
                self.config.SUPABASE_URL,
                self.config.SUPABASE_KEY
            )
        except Exception as e:
            print(f"Erro ao conectar com Supabase: {e}")
            self.supabase = None
    
    def get_supabase(self) -> Optional[Client]:
        """Retorna a instância do Supabase"""
        return self.supabase
    
    def test_connection(self) -> bool:
        """Testa a conexão com o banco de dados"""
        try:
            if self.supabase:
                # Testa uma query simples
                response = self.supabase.table('users').select('count').limit(1).execute()
                return True
        except Exception as e:
            print(f"Erro ao testar conexão: {e}")
            return False
        return False

# Instância global do banco de dados
db_config = DatabaseConfig()

def get_db() -> Optional[Client]:
    """Retorna a instância do banco de dados"""
    return db_config.get_supabase()

def test_db_connection() -> bool:
    """Testa a conexão com o banco de dados"""
    return db_config.test_connection()