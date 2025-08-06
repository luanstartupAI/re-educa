"""
Rotas de pagamentos RE-EDUCA Store
"""
from flask import Blueprint, request, jsonify
from services.payment_service import PaymentService
from utils.decorators import token_required, log_activity, rate_limit
from middleware.logging import log_user_activity

payments_bp = Blueprint('payments', __name__)
payment_service = PaymentService()

@payments_bp.route('/create-payment-intent', methods=['POST'])
@token_required
@rate_limit("20 per hour")
@log_activity('payment_intent_created')
def create_payment_intent():
    """Cria intent de pagamento"""
    try:
        data = request.get_json()
        user_id = request.current_user['id']
        
        result = payment_service.create_payment_intent(user_id, data)
        
        if result.get('success'):
            log_user_activity(user_id, 'payment_intent_created', {
                'amount': data.get('amount'),
                'currency': data.get('currency', 'brl')
            })
            
            return jsonify({
                'client_secret': result['client_secret'],
                'payment_intent_id': result['payment_intent_id']
            }), 200
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@payments_bp.route('/subscription/create', methods=['POST'])
@token_required
@log_activity('subscription_created')
def create_subscription():
    """Cria assinatura"""
    try:
        data = request.get_json()
        user_id = request.current_user['id']
        
        result = payment_service.create_subscription(user_id, data)
        
        if result.get('success'):
            log_user_activity(user_id, 'subscription_created', {
                'plan': data.get('plan'),
                'amount': data.get('amount')
            })
            
            return jsonify({
                'message': 'Assinatura criada com sucesso',
                'subscription': result['subscription']
            }), 201
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@payments_bp.route('/subscription/cancel', methods=['POST'])
@token_required
@log_activity('subscription_cancelled')
def cancel_subscription():
    """Cancela assinatura"""
    try:
        user_id = request.current_user['id']
        
        result = payment_service.cancel_subscription(user_id)
        
        if result.get('success'):
            log_user_activity(user_id, 'subscription_cancelled')
            return jsonify({'message': 'Assinatura cancelada com sucesso'}), 200
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500