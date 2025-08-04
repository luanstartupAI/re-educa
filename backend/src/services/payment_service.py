"""
Service de pagamentos RE-EDUCA Store
"""
import logging
from typing import Dict, Any
from datetime import datetime
from config.database import get_db
from utils.helpers import generate_uuid

logger = logging.getLogger(__name__)

class PaymentService:
    """Service para operações de pagamento"""
    
    def __init__(self):
        self.supabase = get_db()
    
    def create_payment_intent(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria intent de pagamento"""
        try:
            # Em produção, integrar com Stripe ou similar
            payment_intent_data = {
                'id': generate_uuid(),
                'user_id': user_id,
                'amount': data['amount'],
                'currency': data.get('currency', 'brl'),
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('payment_intents').insert(payment_intent_data).execute()
            
            if result.data:
                return {
                    'success': True,
                    'client_secret': f"pi_{result.data[0]['id']}_secret",
                    'payment_intent_id': result.data[0]['id']
                }
            else:
                return {'success': False, 'error': 'Erro ao criar payment intent'}
                
        except Exception as e:
            logger.error(f"Erro ao criar payment intent: {str(e)}")
            return {'success': False, 'error': 'Erro interno do servidor'}
    
    def create_subscription(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria assinatura"""
        try:
            subscription_data = {
                'id': generate_uuid(),
                'user_id': user_id,
                'plan': data['plan'],
                'amount': data['amount'],
                'status': 'active',
                'start_date': datetime.now().isoformat(),
                'end_date': None,  # Assinatura ativa
                'created_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('subscriptions').insert(subscription_data).execute()
            
            if result.data:
                # Atualiza tipo de assinatura do usuário
                self.supabase.table('users').update({
                    'subscription_type': data['plan'],
                    'subscription_status': 'active'
                }).eq('id', user_id).execute()
                
                return {'success': True, 'subscription': result.data[0]}
            else:
                return {'success': False, 'error': 'Erro ao criar assinatura'}
                
        except Exception as e:
            logger.error(f"Erro ao criar assinatura: {str(e)}")
            return {'success': False, 'error': 'Erro interno do servidor'}
    
    def cancel_subscription(self, user_id: str) -> Dict[str, Any]:
        """Cancela assinatura"""
        try:
            # Atualiza status da assinatura
            result = self.supabase.table('subscriptions').update({
                'status': 'cancelled',
                'end_date': datetime.now().isoformat()
            }).eq('user_id', user_id).eq('status', 'active').execute()
            
            if result.data:
                # Atualiza tipo de assinatura do usuário
                self.supabase.table('users').update({
                    'subscription_type': 'free',
                    'subscription_status': 'cancelled'
                }).eq('id', user_id).execute()
                
                return {'success': True}
            else:
                return {'success': False, 'error': 'Assinatura não encontrada'}
                
        except Exception as e:
            logger.error(f"Erro ao cancelar assinatura: {str(e)}")
            return {'success': False, 'error': 'Erro interno do servidor'}