"""
Service de produtos RE-EDUCA Store
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from config.database import get_db
from utils.helpers import generate_uuid

logger = logging.getLogger(__name__)

class ProductService:
    """Service para operações de produtos"""
    
    def __init__(self):
        self.supabase = get_db()
    
    def get_products(self, page: int = 1, per_page: int = 20, category: Optional[str] = None, search: Optional[str] = None) -> Dict[str, Any]:
        """Retorna lista de produtos"""
        try:
            query = self.supabase.table('products').select('*').eq('status', 'active')
            
            if category:
                query = query.eq('category', category)
            
            if search:
                query = query.ilike('name', f'%{search}%')
            
            result = query.order('created_at', desc=True).execute()
            
            if result.data:
                # Paginação manual
                start = (page - 1) * per_page
                end = start + per_page
                paginated_data = result.data[start:end]
                
                return {
                    'products': paginated_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': len(result.data),
                        'pages': (len(result.data) + per_page - 1) // per_page
                    }
                }
            else:
                return {
                    'products': [],
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': 0,
                        'pages': 0
                    }
                }
                
        except Exception as e:
            logger.error(f"Erro ao buscar produtos: {str(e)}")
            return {'error': 'Erro interno do servidor'}
    
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Retorna detalhes de um produto"""
        try:
            result = self.supabase.table('products').select('*').eq('id', product_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar produto: {str(e)}")
            return None
    
    def create_product(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria novo produto"""
        try:
            product_data = {
                'id': generate_uuid(),
                'name': data['name'],
                'description': data.get('description', ''),
                'price': data['price'],
                'category': data.get('category', 'other'),
                'status': data.get('status', 'active'),
                'stock': data.get('stock', 0),
                'images': data.get('images', []),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('products').insert(product_data).execute()
            
            if result.data:
                return {'success': True, 'product': result.data[0]}
            else:
                return {'success': False, 'error': 'Erro ao criar produto'}
                
        except Exception as e:
            logger.error(f"Erro ao criar produto: {str(e)}")
            return {'success': False, 'error': 'Erro interno do servidor'}
    
    def update_product(self, product_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza produto"""
        try:
            data['updated_at'] = datetime.now().isoformat()
            
            result = self.supabase.table('products').update(data).eq('id', product_id).execute()
            
            if result.data:
                return {'success': True, 'product': result.data[0]}
            else:
                return {'success': False, 'error': 'Produto não encontrado'}
                
        except Exception as e:
            logger.error(f"Erro ao atualizar produto: {str(e)}")
            return {'success': False, 'error': 'Erro interno do servidor'}
    
    def delete_product(self, product_id: str) -> Dict[str, Any]:
        """Remove produto (soft delete)"""
        try:
            result = self.supabase.table('products').update({
                'status': 'archived',
                'updated_at': datetime.now().isoformat()
            }).eq('id', product_id).execute()
            
            if result.data:
                return {'success': True}
            else:
                return {'success': False, 'error': 'Produto não encontrado'}
                
        except Exception as e:
            logger.error(f"Erro ao remover produto: {str(e)}")
            return {'success': False, 'error': 'Erro interno do servidor'}
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Retorna categorias de produtos"""
        try:
            result = self.supabase.table('products').select('category').execute()
            
            categories = list(set(item['category'] for item in result.data if item.get('category')))
            
            return [{'id': cat, 'name': cat.title()} for cat in categories]
            
        except Exception as e:
            logger.error(f"Erro ao buscar categorias: {str(e)}")
            return []
    
    def get_product_reviews(self, product_id: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Retorna avaliações de um produto"""
        try:
            result = self.supabase.table('product_reviews')\
                .select('*, users(name, avatar)')\
                .eq('product_id', product_id)\
                .eq('status', 'approved')\
                .order('created_at', desc=True)\
                .execute()
            
            if result.data:
                # Paginação manual
                start = (page - 1) * per_page
                end = start + per_page
                paginated_data = result.data[start:end]
                
                return {
                    'reviews': paginated_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': len(result.data),
                        'pages': (len(result.data) + per_page - 1) // per_page
                    }
                }
            else:
                return {
                    'reviews': [],
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': 0,
                        'pages': 0
                    }
                }
                
        except Exception as e:
            logger.error(f"Erro ao buscar avaliações: {str(e)}")
            return {'error': 'Erro interno do servidor'}
    
    def create_review(self, product_id: str, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria avaliação de produto"""
        try:
            review_data = {
                'id': generate_uuid(),
                'product_id': product_id,
                'user_id': user_id,
                'rating': data['rating'],
                'comment': data['comment'],
                'status': 'pending',  # Aguarda aprovação
                'created_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('product_reviews').insert(review_data).execute()
            
            if result.data:
                return {'success': True, 'review': result.data[0]}
            else:
                return {'success': False, 'error': 'Erro ao criar avaliação'}
                
        except Exception as e:
            logger.error(f"Erro ao criar avaliação: {str(e)}")
            return {'success': False, 'error': 'Erro interno do servidor'}
    
    def get_featured_products(self) -> List[Dict[str, Any]]:
        """Retorna produtos em destaque"""
        try:
            result = self.supabase.table('products')\
                .select('*')\
                .eq('status', 'active')\
                .eq('featured', True)\
                .order('created_at', desc=True)\
                .limit(10)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Erro ao buscar produtos em destaque: {str(e)}")
            return []
    
    def get_recommended_products(self, user_id: str) -> List[Dict[str, Any]]:
        """Retorna produtos recomendados para o usuário"""
        try:
            # Implementação básica - em produção usar ML
            result = self.supabase.table('products')\
                .select('*')\
                .eq('status', 'active')\
                .order('created_at', desc=True)\
                .limit(10)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Erro ao buscar produtos recomendados: {str(e)}")
            return []