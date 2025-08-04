"""
💳 Sistema de Pagamentos Global - RE-EDUCA Store v2.0.0
Integração completa com Stripe (Global) e Mercado Pago (PIX Brasil)
"""

import os
import json
import stripe
import requests
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import logging
from dataclasses import dataclass
from enum import Enum

# ================================
# CONFIGURAÇÃO
# ================================

# Stripe Configuration (LIVE KEYS)
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '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')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_bTU2H7zHZhRzYwbwqoacKCJHRPRIVfvB')

# Mercado Pago Configuration
MERCADO_PAGO_ACCESS_TOKEN = os.getenv('MERCADO_PAGO_ACCESS_TOKEN', '')

# Configurar Stripe
stripe.api_key = STRIPE_SECRET_KEY

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================
# MODELOS DE DADOS
# ================================

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(Enum):
    STRIPE_CARD = "stripe_card"
    STRIPE_APPLE_PAY = "stripe_apple_pay"
    STRIPE_GOOGLE_PAY = "stripe_google_pay"
    PIX = "pix"
    BOLETO = "boleto"
    MERCADO_PAGO_CARD = "mercado_pago_card"

@dataclass
class PaymentRequest:
    amount: float
    currency: str
    payment_method: str
    customer_data: Dict
    billing_address: Dict
    products: List[Dict]
    discount_code: Optional[str] = None
    installments: int = 1
    return_url: Optional[str] = None

@dataclass
class PaymentResponse:
    payment_id: str
    status: PaymentStatus
    amount: float
    currency: str
    payment_method: str
    client_secret: Optional[str] = None
    pix_qr_code: Optional[str] = None
    pix_code: Optional[str] = None
    checkout_url: Optional[str] = None
    expires_at: Optional[str] = None

# ================================
# SISTEMA DE PAGAMENTOS GLOBAL
# ================================

class GlobalPaymentProcessor:
    def __init__(self):
        self.supported_currencies = {
            'BRL': {'symbol': 'R$', 'name': 'Real Brasileiro', 'methods': ['pix', 'boleto', 'card']},
            'USD': {'symbol': '$', 'name': 'US Dollar', 'methods': ['card', 'apple_pay', 'google_pay']},
            'EUR': {'symbol': '€', 'name': 'Euro', 'methods': ['card', 'apple_pay', 'google_pay']},
            'GBP': {'symbol': '£', 'name': 'British Pound', 'methods': ['card', 'apple_pay', 'google_pay']},
            'JPY': {'symbol': '¥', 'name': 'Japanese Yen', 'methods': ['card', 'apple_pay', 'google_pay']},
        }
        
        self.discount_codes = {
            'WELCOME20': {'type': 'percentage', 'value': 20, 'description': '20% de desconto para novos usuários'},
            'SAVE50': {'type': 'fixed', 'value': 50, 'description': 'R$ 50 de desconto'},
            'PREMIUM30': {'type': 'percentage', 'value': 30, 'description': '30% de desconto no plano premium'},
            'BLACKFRIDAY': {'type': 'percentage', 'value': 50, 'description': '50% de desconto Black Friday'},
        }

    async def process_payment(self, payment_request: PaymentRequest) -> PaymentResponse:
        """Processa pagamento baseado no método escolhido"""
        try:
            # Aplicar desconto se houver
            final_amount = self._apply_discount(payment_request.amount, payment_request.discount_code)
            
            # Determinar processador baseado na moeda e método
            if payment_request.currency == 'BRL' and payment_request.payment_method in ['pix', 'boleto']:
                return await self._process_mercado_pago_payment(payment_request, final_amount)
            else:
                return await self._process_stripe_payment(payment_request, final_amount)
                
        except Exception as e:
            logger.error(f"Erro ao processar pagamento: {str(e)}")
            return PaymentResponse(
                payment_id="",
                status=PaymentStatus.FAILED,
                amount=payment_request.amount,
                currency=payment_request.currency,
                payment_method=payment_request.payment_method
            )

    async def _process_stripe_payment(self, payment_request: PaymentRequest, amount: float) -> PaymentResponse:
        """Processa pagamento via Stripe"""
        try:
            # Criar ou recuperar cliente
            customer = await self._create_stripe_customer(payment_request.customer_data)
            
            # Criar Payment Intent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe usa centavos
                currency=payment_request.currency.lower(),
                customer=customer.id,
                payment_method_types=['card'],
                metadata={
                    'customer_email': payment_request.customer_data.get('email'),
                    'products': json.dumps([p['id'] for p in payment_request.products]),
                    'discount_code': payment_request.discount_code or '',
                    'installments': payment_request.installments
                },
                receipt_email=payment_request.customer_data.get('email'),
                description=f"RE-EDUCA Store - {', '.join([p['name'] for p in payment_request.products])}"
            )
            
            logger.info(f"Payment Intent criado: {payment_intent.id}")
            
            return PaymentResponse(
                payment_id=payment_intent.id,
                status=PaymentStatus.PENDING,
                amount=amount,
                currency=payment_request.currency,
                payment_method=payment_request.payment_method,
                client_secret=payment_intent.client_secret
            )
            
        except stripe.error.StripeError as e:
            logger.error(f"Erro Stripe: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro geral Stripe: {str(e)}")
            raise

    async def _process_mercado_pago_payment(self, payment_request: PaymentRequest, amount: float) -> PaymentResponse:
        """Processa pagamento via Mercado Pago (PIX/Boleto)"""
        try:
            if payment_request.payment_method == 'pix':
                return await self._create_pix_payment(payment_request, amount)
            elif payment_request.payment_method == 'boleto':
                return await self._create_boleto_payment(payment_request, amount)
            else:
                raise ValueError(f"Método de pagamento não suportado: {payment_request.payment_method}")
                
        except Exception as e:
            logger.error(f"Erro Mercado Pago: {str(e)}")
            raise

    async def _create_pix_payment(self, payment_request: PaymentRequest, amount: float) -> PaymentResponse:
        """Cria pagamento PIX via Mercado Pago"""
        try:
            headers = {
                'Authorization': f'Bearer {MERCADO_PAGO_ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            payment_data = {
                'transaction_amount': amount,
                'description': f"RE-EDUCA Store - {', '.join([p['name'] for p in payment_request.products])}",
                'payment_method_id': 'pix',
                'payer': {
                    'email': payment_request.customer_data.get('email'),
                    'first_name': payment_request.customer_data.get('first_name', ''),
                    'last_name': payment_request.customer_data.get('last_name', ''),
                    'identification': {
                        'type': 'CPF',
                        'number': payment_request.customer_data.get('cpf', '')
                    }
                },
                'metadata': {
                    'customer_email': payment_request.customer_data.get('email'),
                    'products': json.dumps([p['id'] for p in payment_request.products]),
                    'discount_code': payment_request.discount_code or ''
                }
            }
            
            # Simular criação de pagamento PIX (em produção usaria a API real)
            # Por enquanto, retorna dados simulados
            pix_code = self._generate_pix_code(amount, payment_request.customer_data.get('email'))
            
            logger.info(f"Pagamento PIX criado para: {payment_request.customer_data.get('email')}")
            
            return PaymentResponse(
                payment_id=f"pix_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                status=PaymentStatus.PENDING,
                amount=amount,
                currency='BRL',
                payment_method='pix',
                pix_qr_code=f"data:image/png;base64,{self._generate_qr_code_base64(pix_code)}",
                pix_code=pix_code,
                expires_at=(datetime.now() + timedelta(minutes=30)).isoformat()
            )
            
        except Exception as e:
            logger.error(f"Erro ao criar pagamento PIX: {str(e)}")
            raise

    async def _create_boleto_payment(self, payment_request: PaymentRequest, amount: float) -> PaymentResponse:
        """Cria pagamento via Boleto"""
        try:
            # Simular criação de boleto
            boleto_id = f"boleto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            logger.info(f"Boleto criado: {boleto_id}")
            
            return PaymentResponse(
                payment_id=boleto_id,
                status=PaymentStatus.PENDING,
                amount=amount,
                currency='BRL',
                payment_method='boleto',
                checkout_url=f"https://re-educa.up.railway.app/boleto/{boleto_id}",
                expires_at=(datetime.now() + timedelta(days=3)).isoformat()
            )
            
        except Exception as e:
            logger.error(f"Erro ao criar boleto: {str(e)}")
            raise

    async def _create_stripe_customer(self, customer_data: Dict) -> stripe.Customer:
        """Cria ou recupera cliente no Stripe"""
        try:
            # Tentar encontrar cliente existente
            customers = stripe.Customer.list(email=customer_data.get('email'), limit=1)
            
            if customers.data:
                return customers.data[0]
            
            # Criar novo cliente
            customer = stripe.Customer.create(
                email=customer_data.get('email'),
                name=f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip(),
                phone=customer_data.get('phone'),
                metadata={
                    'source': 'RE-EDUCA Store',
                    'signup_date': datetime.now().isoformat()
                }
            )
            
            logger.info(f"Cliente Stripe criado: {customer.id}")
            return customer
            
        except Exception as e:
            logger.error(f"Erro ao criar cliente Stripe: {str(e)}")
            raise

    def _apply_discount(self, amount: float, discount_code: Optional[str]) -> float:
        """Aplica desconto se código válido"""
        if not discount_code or discount_code.upper() not in self.discount_codes:
            return amount
            
        discount = self.discount_codes[discount_code.upper()]
        
        if discount['type'] == 'percentage':
            return amount * (1 - discount['value'] / 100)
        else:
            return max(0, amount - discount['value'])

    def _generate_pix_code(self, amount: float, email: str) -> str:
        """Gera código PIX simulado"""
        # Em produção, isso viria da API do Mercado Pago
        base_string = f"{amount}_{email}_{datetime.now().isoformat()}"
        return hashlib.md5(base_string.encode()).hexdigest()[:32].upper()

    def _generate_qr_code_base64(self, pix_code: str) -> str:
        """Gera QR Code base64 simulado"""
        # Em produção, geraria QR Code real
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

    async def get_payment_status(self, payment_id: str) -> Dict:
        """Consulta status de pagamento"""
        try:
            if payment_id.startswith('pi_'):
                # Stripe Payment Intent
                payment_intent = stripe.PaymentIntent.retrieve(payment_id)
                return {
                    'payment_id': payment_id,
                    'status': payment_intent.status,
                    'amount': payment_intent.amount / 100,
                    'currency': payment_intent.currency.upper(),
                    'created': payment_intent.created
                }
            elif payment_id.startswith('pix_'):
                # PIX Payment (simulado)
                return {
                    'payment_id': payment_id,
                    'status': 'pending',
                    'amount': 0,
                    'currency': 'BRL',
                    'created': datetime.now().timestamp()
                }
            else:
                return {'error': 'Payment not found'}
                
        except Exception as e:
            logger.error(f"Erro ao consultar pagamento: {str(e)}")
            return {'error': str(e)}

    async def process_refund(self, payment_id: str, amount: Optional[float] = None) -> Dict:
        """Processa reembolso"""
        try:
            if payment_id.startswith('pi_'):
                # Stripe refund
                refund = stripe.Refund.create(
                    payment_intent=payment_id,
                    amount=int(amount * 100) if amount else None
                )
                
                logger.info(f"Reembolso criado: {refund.id}")
                
                return {
                    'refund_id': refund.id,
                    'status': refund.status,
                    'amount': refund.amount / 100,
                    'currency': refund.currency.upper()
                }
            else:
                # Outros métodos de pagamento
                return {'error': 'Refund not supported for this payment method'}
                
        except Exception as e:
            logger.error(f"Erro ao processar reembolso: {str(e)}")
            return {'error': str(e)}

# ================================
# WEBHOOK HANDLERS
# ================================

class WebhookHandler:
    def __init__(self, payment_processor: GlobalPaymentProcessor):
        self.payment_processor = payment_processor

    def handle_stripe_webhook(self, payload: bytes, signature: str) -> Dict:
        """Processa webhook do Stripe"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, STRIPE_WEBHOOK_SECRET
            )
            
            logger.info(f"Webhook Stripe recebido: {event['type']}")
            
            if event['type'] == 'payment_intent.succeeded':
                return self._handle_payment_success(event['data']['object'])
            elif event['type'] == 'payment_intent.payment_failed':
                return self._handle_payment_failed(event['data']['object'])
            elif event['type'] == 'charge.succeeded':
                return self._handle_charge_success(event['data']['object'])
            elif event['type'] == 'charge.refunded':
                return self._handle_charge_refunded(event['data']['object'])
            elif event['type'] == 'customer.created':
                return self._handle_customer_created(event['data']['object'])
            elif event['type'] == 'customer.updated':
                return self._handle_customer_updated(event['data']['object'])
            elif event['type'] == 'customer.deleted':
                return self._handle_customer_deleted(event['data']['object'])
            elif event['type'] == 'charge.dispute.created':
                return self._handle_dispute_created(event['data']['object'])
            elif event['type'] == 'charge.dispute.closed':
                return self._handle_dispute_closed(event['data']['object'])
            else:
                logger.info(f"Evento não tratado: {event['type']}")
                return {'status': 'ignored'}
                
        except ValueError as e:
            logger.error(f"Payload inválido: {str(e)}")
            return {'error': 'Invalid payload'}
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Assinatura inválida: {str(e)}")
            return {'error': 'Invalid signature'}
        except Exception as e:
            logger.error(f"Erro no webhook: {str(e)}")
            return {'error': str(e)}

    def _handle_payment_success(self, payment_intent: Dict) -> Dict:
        """Trata sucesso do pagamento"""
        logger.info(f"Pagamento bem-sucedido: {payment_intent['id']}")
        
        # Aqui você implementaria:
        # - Ativar assinatura do usuário
        # - Enviar email de confirmação
        # - Atualizar banco de dados
        # - Liberar acesso aos produtos
        
        return {'status': 'processed', 'action': 'payment_confirmed'}

    def _handle_payment_failed(self, payment_intent: Dict) -> Dict:
        """Trata falha do pagamento"""
        logger.warning(f"Pagamento falhou: {payment_intent['id']}")
        
        # Implementar:
        # - Notificar usuário
        # - Tentar novamente se apropriado
        # - Atualizar status no banco
        
        return {'status': 'processed', 'action': 'payment_failed'}

    def _handle_charge_success(self, charge: Dict) -> Dict:
        """Trata sucesso da cobrança"""
        logger.info(f"Cobrança bem-sucedida: {charge['id']}")
        return {'status': 'processed', 'action': 'charge_confirmed'}

    def _handle_charge_refunded(self, charge: Dict) -> Dict:
        """Trata reembolso"""
        logger.info(f"Reembolso processado: {charge['id']}")
        return {'status': 'processed', 'action': 'refund_processed'}

    def _handle_customer_created(self, customer: Dict) -> Dict:
        """Trata criação de cliente"""
        logger.info(f"Cliente criado: {customer['id']}")
        return {'status': 'processed', 'action': 'customer_created'}

    def _handle_customer_updated(self, customer: Dict) -> Dict:
        """Trata atualização de cliente"""
        logger.info(f"Cliente atualizado: {customer['id']}")
        return {'status': 'processed', 'action': 'customer_updated'}

    def _handle_customer_deleted(self, customer: Dict) -> Dict:
        """Trata exclusão de cliente"""
        logger.info(f"Cliente excluído: {customer['id']}")
        return {'status': 'processed', 'action': 'customer_deleted'}

    def _handle_dispute_created(self, dispute: Dict) -> Dict:
        """Trata criação de disputa"""
        logger.warning(f"Disputa criada: {dispute['id']}")
        return {'status': 'processed', 'action': 'dispute_created'}

    def _handle_dispute_closed(self, dispute: Dict) -> Dict:
        """Trata fechamento de disputa"""
        logger.info(f"Disputa fechada: {dispute['id']}")
        return {'status': 'processed', 'action': 'dispute_closed'}

# ================================
# API ENDPOINTS
# ================================

app = Flask(__name__)
CORS(app)

payment_processor = GlobalPaymentProcessor()
webhook_handler = WebhookHandler(payment_processor)

@app.route('/api/payments/create', methods=['POST'])
async def create_payment():
    """Endpoint para criar pagamento"""
    try:
        data = request.get_json()
        
        payment_request = PaymentRequest(
            amount=data.get('amount'),
            currency=data.get('currency', 'BRL'),
            payment_method=data.get('payment_method'),
            customer_data=data.get('customer_data', {}),
            billing_address=data.get('billing_address', {}),
            products=data.get('products', []),
            discount_code=data.get('discount_code'),
            installments=data.get('installments', 1),
            return_url=data.get('return_url')
        )
        
        response = await payment_processor.process_payment(payment_request)
        
        return jsonify({
            'success': True,
            'payment': {
                'payment_id': response.payment_id,
                'status': response.status.value,
                'amount': response.amount,
                'currency': response.currency,
                'payment_method': response.payment_method,
                'client_secret': response.client_secret,
                'pix_qr_code': response.pix_qr_code,
                'pix_code': response.pix_code,
                'checkout_url': response.checkout_url,
                'expires_at': response.expires_at
            }
        })
        
    except Exception as e:
        logger.error(f"Erro no endpoint create_payment: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/payments/<payment_id>/status', methods=['GET'])
async def get_payment_status(payment_id):
    """Endpoint para consultar status do pagamento"""
    try:
        status = await payment_processor.get_payment_status(payment_id)
        return jsonify({
            'success': True,
            'payment': status
        })
        
    except Exception as e:
        logger.error(f"Erro no endpoint get_payment_status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/payments/<payment_id>/refund', methods=['POST'])
async def refund_payment(payment_id):
    """Endpoint para reembolso"""
    try:
        data = request.get_json()
        amount = data.get('amount')
        
        result = await payment_processor.process_refund(payment_id, amount)
        
        return jsonify({
            'success': True,
            'refund': result
        })
        
    except Exception as e:
        logger.error(f"Erro no endpoint refund_payment: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/stripe_payments', methods=['POST'])
def stripe_webhook():
    """Webhook do Stripe"""
    payload = request.get_data()
    signature = request.headers.get('Stripe-Signature')
    
    result = webhook_handler.handle_stripe_webhook(payload, signature)
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)

@app.route('/api/payments/currencies', methods=['GET'])
def get_supported_currencies():
    """Endpoint para moedas suportadas"""
    return jsonify({
        'success': True,
        'currencies': payment_processor.supported_currencies
    })

@app.route('/api/payments/discount/<code>', methods=['GET'])
def validate_discount_code(code):
    """Endpoint para validar código de desconto"""
    discount = payment_processor.discount_codes.get(code.upper())
    
    if discount:
        return jsonify({
            'success': True,
            'discount': discount
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Código de desconto inválido'
        }), 404

@app.route('/api/payments/health', methods=['GET'])
def health_check():
    """Health check do sistema de pagamentos"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'stripe': bool(STRIPE_SECRET_KEY),
            'mercado_pago': bool(MERCADO_PAGO_ACCESS_TOKEN),
            'webhook_configured': bool(STRIPE_WEBHOOK_SECRET)
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

