"""
Service administrativo RE-EDUCA Store
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from config.database import get_db

logger = logging.getLogger(__name__)

class AdminService:
    """Service para operações administrativas"""
    
    def __init__(self):
        self.supabase = get_db()
    
    def get_all_users(self, page: int = 1, per_page: int = 20, search: str = None) -> Dict[str, Any]:
        """Retorna todos os usuários"""
        try:
            query = self.supabase.table('users').select('*')
            
            if search:
                query = query.or_(f'name.ilike.%{search}%,email.ilike.%{search}%')
            
            result = query.order('created_at', desc=True).execute()
            
            if result.data:
                # Paginação manual
                start = (page - 1) * per_page
                end = start + per_page
                paginated_data = result.data[start:end]
                
                return {
                    'users': paginated_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': len(result.data),
                        'pages': (len(result.data) + per_page - 1) // per_page
                    }
                }
            else:
                return {
                    'users': [],
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': 0,
                        'pages': 0
                    }
                }
                
        except Exception as e:
            logger.error(f"Erro ao buscar usuários: {str(e)}")
            return {'error': 'Erro interno do servidor'}
    
    def get_analytics(self, period_days: int = 30) -> Dict[str, Any]:
        """Retorna analytics gerais"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Busca dados do período
            users_result = self.supabase.table('users')\
                .select('created_at')\
                .gte('created_at', start_date.isoformat())\
                .lte('created_at', end_date.isoformat())\
                .execute()
            
            orders_result = self.supabase.table('orders')\
                .select('total, status')\
                .gte('created_at', start_date.isoformat())\
                .lte('created_at', end_date.isoformat())\
                .execute()
            
            # Calcula métricas
            total_users = len(users_result.data)
            total_orders = len(orders_result.data)
            total_revenue = sum(order.get('total', 0) for order in orders_result.data if order.get('status') == 'paid')
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': period_days
                },
                'metrics': {
                    'total_users': total_users,
                    'total_orders': total_orders,
                    'total_revenue': total_revenue,
                    'average_order_value': total_revenue / total_orders if total_orders > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar analytics: {str(e)}")
            return {'error': 'Erro interno do servidor'}
    
    def get_all_orders(self, page: int = 1, per_page: int = 20, status: str = None) -> Dict[str, Any]:
        """Retorna todos os pedidos"""
        try:
            query = self.supabase.table('orders').select('*, users(name, email)')
            
            if status:
                query = query.eq('status', status)
            
            result = query.order('created_at', desc=True).execute()
            
            if result.data:
                # Paginação manual
                start = (page - 1) * per_page
                end = start + per_page
                paginated_data = result.data[start:end]
                
                return {
                    'orders': paginated_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': len(result.data),
                        'pages': (len(result.data) + per_page - 1) // per_page
                    }
                }
            else:
                return {
                    'orders': [],
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': 0,
                        'pages': 0
                    }
                }
                
        except Exception as e:
            logger.error(f"Erro ao buscar pedidos: {str(e)}")
            return {'error': 'Erro interno do servidor'}