"""
💳 Sistema de Pagamentos Global - RE-EDUCA Store
Sistema completo de pagamentos com Stripe, PIX e suporte mundial
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal
import hashlib
import hmac

import stripe
import mercadopago
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================
# CONFIGURAÇÕES DE PAGAMENTO
# ================================

class PaymentConfig:
    """Configurações globais de pagamento"""
    
    # Stripe
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Mercado Pago
    MP_ACCESS_TOKEN = os.environ.get('MERCADOPAGO_ACCESS_TOKEN')
    MP_PUBLIC_KEY = os.environ.get('MERCADOPAGO_PUBLIC_KEY')
    MP_WEBHOOK_SECRET = os.environ.get('MERCADOPAGO_WEBHOOK_SECRET')
    
    # Moedas suportadas
    SUPPORTED_CURRENCIES = {
        'BRL': {'symbol': 'R$', 'name': 'Real Brasileiro', 'decimal_places': 2},
        'USD': {'symbol': '$', 'name': 'Dólar Americano', 'decimal_places': 2},
        'EUR': {'symbol': '€', 'name': 'Euro', 'decimal_places': 2},
        'GBP': {'symbol': '£', 'name': 'Libra Esterlina', 'decimal_places': 2},
        'CAD': {'symbol': 'C$', 'name': 'Dólar Canadense', 'decimal_places': 2},
        'AUD': {'symbol': 'A$', 'name': 'Dólar Australiano', 'decimal_places': 2},
        'JPY': {'symbol': '¥', 'name': 'Iene Japonês', 'decimal_places': 0},
        'CHF': {'symbol': 'CHF', 'name': 'Franco Suíço', 'decimal_places': 2},
        'SEK': {'symbol': 'kr', 'name': 'Coroa Sueca', 'decimal_places': 2},
        'NOK': {'symbol': 'kr', 'name': 'Coroa Norueguesa', 'decimal_places': 2}
    }
    
    # Países e suas configurações
    COUNTRY_CONFIGS = {
        'BR': {
            'currency': 'BRL',
            'payment_methods': ['pix', 'credit_card', 'debit_card', 'boleto'],
            'tax_rate': 0.0,  # Configurar conforme legislação
            'provider': 'mercadopago'
        },
        'US': {
            'currency': 'USD',
            'payment_methods': ['credit_card', 'debit_card', 'apple_pay', 'google_pay'],
            'tax_rate': 0.0875,  # Exemplo NY
            'provider': 'stripe'
        },
        'GB': {
            'currency': 'GBP',
            'payment_methods': ['credit_card', 'debit_card', 'apple_pay', 'google_pay'],
            'tax_rate': 0.20,  # VAT
            'provider': 'stripe'
        },
        'DE': {
            'currency': 'EUR',
            'payment_methods': ['credit_card', 'debit_card', 'sepa_debit', 'sofort'],
            'tax_rate': 0.19,  # VAT
            'provider': 'stripe'
        }
    }

# ================================
# SISTEMA DE CONVERSÃO DE MOEDAS
# ================================

class CurrencyConverter:
    """Sistema de conversão de moedas em tempo real"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 3600  # 1 hora
        self.api_key = os.environ.get('EXCHANGE_API_KEY')
    
    async def convert(self, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        """Converte valor entre moedas"""
        if from_currency == to_currency:
            return amount
        
        rate = await self._get_exchange_rate(from_currency, to_currency)
        converted = amount * Decimal(str(rate))
        
        # Arredonda baseado na moeda de destino
        decimal_places = PaymentConfig.SUPPORTED_CURRENCIES[to_currency]['decimal_places']
        return converted.quantize(Decimal('0.1') ** decimal_places)
    
    async def _get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """Busca taxa de câmbio"""
        cache_key = f"{from_currency}_{to_currency}"
        
        # Verifica cache
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < timedelta(seconds=self.cache_duration):
                return cached_data['rate']
        
        try:
            # API de câmbio (exemplo: exchangerate-api.com)
            url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/pair/{from_currency}/{to_currency}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data['result'] == 'success':
                rate = data['conversion_rate']
                
                # Atualiza cache
                self.cache[cache_key] = {
                    'rate': rate,
                    'timestamp': datetime.now()
                }
                
                return rate
            else:
                raise Exception(f"Erro na API de câmbio: {data.get('error-type', 'Unknown')}")
                
        except Exception as e:
            logger.error(f"Erro ao buscar taxa de câmbio: {str(e)}")
            # Fallback: usar taxa fixa ou última conhecida
            return self._get_fallback_rate(from_currency, to_currency)
    
    def _get_fallback_rate(self, from_currency: str, to_currency: str) -> float:
        """Taxa de fallback quando API falha"""
        # Taxas aproximadas para fallback
        fallback_rates = {
            'BRL_USD': 0.20,
            'USD_BRL': 5.00,
            'BRL_EUR': 0.18,
            'EUR_BRL': 5.55,
            'USD_EUR': 0.90,
            'EUR_USD': 1.11
        }
        
        key = f"{from_currency}_{to_currency}"
        return fallback_rates.get(key, 1.0)

# ================================
# SISTEMA PIX AVANÇADO
# ================================

class PixPaymentSystem:
    """Sistema PIX completo com QR Code e pagamento instantâneo"""
    
    def __init__(self, mp_access_token: str):
        self.mp = mercadopago.SDK(mp_access_token)
    
    async def create_pix_payment(self, amount: Decimal, description: str, user_data: Dict) -> Dict:
        """Cria pagamento PIX com QR Code"""
        try:
            payment_data = {
                "transaction_amount": float(amount),
                "description": description,
                "payment_method_id": "pix",
                "payer": {
                    "email": user_data.get('email'),
                    "first_name": user_data.get('first_name', ''),
                    "last_name": user_data.get('last_name', ''),
                    "identification": {
                        "type": user_data.get('doc_type', 'CPF'),
                        "number": user_data.get('doc_number', '')
                    }
                },
                "notification_url": "https://your-domain.com/api/payments/webhook/mercadopago",
                "metadata": {
                    "user_id": user_data.get('user_id'),
                    "product_id": user_data.get('product_id'),
                    "payment_type": "pix"
                }
            }
            
            payment_response = self.mp.payment().create(payment_data)
            payment = payment_response["response"]
            
            if payment_response["status"] == 201:
                return {
                    'payment_id': payment['id'],
                    'status': payment['status'],
                    'qr_code': payment['point_of_interaction']['transaction_data']['qr_code'],
                    'qr_code_base64': payment['point_of_interaction']['transaction_data']['qr_code_base64'],
                    'ticket_url': payment['point_of_interaction']['transaction_data']['ticket_url'],
                    'expires_at': payment['date_of_expiration'],
                    'amount': payment['transaction_amount'],
                    'currency': 'BRL'
                }
            else:
                raise Exception(f"Erro ao criar pagamento PIX: {payment_response}")
                
        except Exception as e:
            logger.error(f"Erro no PIX: {str(e)}")
            raise
    
    async def check_pix_status(self, payment_id: str) -> Dict:
        """Verifica status do pagamento PIX"""
        try:
            payment_response = self.mp.payment().get(payment_id)
            payment = payment_response["response"]
            
            return {
                'payment_id': payment['id'],
                'status': payment['status'],
                'status_detail': payment['status_detail'],
                'amount': payment['transaction_amount'],
                'paid_at': payment.get('date_approved'),
                'metadata': payment.get('metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar status PIX: {str(e)}")
            raise

# ================================
# SISTEMA STRIPE AVANÇADO
# ================================

class StripePaymentSystem:
    """Sistema Stripe com suporte global"""
    
    def __init__(self, secret_key: str):
        stripe.api_key = secret_key
    
    async def create_payment_intent(self, amount: Decimal, currency: str, user_data: Dict, metadata: Dict) -> Dict:
        """Cria Payment Intent do Stripe"""
        try:
            # Converte para centavos (exceto JPY)
            if currency.upper() != 'JPY':
                amount_cents = int(amount * 100)
            else:
                amount_cents = int(amount)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                customer=await self._get_or_create_customer(user_data),
                metadata=metadata,
                automatic_payment_methods={'enabled': True},
                receipt_email=user_data.get('email')
            )
            
            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': amount,
                'currency': currency,
                'status': intent.status
            }
            
        except Exception as e:
            logger.error(f"Erro no Stripe Payment Intent: {str(e)}")
            raise
    
    async def create_checkout_session(self, line_items: List[Dict], user_data: Dict, metadata: Dict) -> Dict:
        """Cria sessão de checkout do Stripe"""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url='https://your-domain.com/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='https://your-domain.com/cancel',
                customer_email=user_data.get('email'),
                metadata=metadata,
                billing_address_collection='required',
                shipping_address_collection={
                    'allowed_countries': ['US', 'CA', 'GB', 'DE', 'FR', 'IT', 'ES', 'AU', 'JP']
                } if metadata.get('requires_shipping') else None,
                tax_id_collection={'enabled': True},
                automatic_tax={'enabled': True}
            )
            
            return {
                'session_id': session.id,
                'checkout_url': session.url,
                'expires_at': session.expires_at
            }
            
        except Exception as e:
            logger.error(f"Erro no Stripe Checkout: {str(e)}")
            raise
    
    async def _get_or_create_customer(self, user_data: Dict) -> str:
        """Busca ou cria cliente no Stripe"""
        try:
            email = user_data.get('email')
            
            # Busca cliente existente
            customers = stripe.Customer.list(email=email, limit=1)
            
            if customers.data:
                return customers.data[0].id
            
            # Cria novo cliente
            customer = stripe.Customer.create(
                email=email,
                name=f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
                metadata={
                    'user_id': user_data.get('user_id'),
                    'country': user_data.get('country', ''),
                    'created_via': 're_educa_store'
                }
            )
            
            return customer.id
            
        except Exception as e:
            logger.error(f"Erro ao gerenciar cliente Stripe: {str(e)}")
            raise

# ================================
# SISTEMA DE PAGAMENTOS UNIFICADO
# ================================

class UnifiedPaymentSystem:
    """Sistema unificado que gerencia todos os provedores"""
    
    def __init__(self):
        self.currency_converter = CurrencyConverter()
        self.pix_system = PixPaymentSystem(PaymentConfig.MP_ACCESS_TOKEN)
        self.stripe_system = StripePaymentSystem(PaymentConfig.STRIPE_SECRET_KEY)
    
    async def create_payment(self, payment_request: Dict) -> Dict:
        """Cria pagamento baseado na localização e preferências do usuário"""
        try:
            user_country = payment_request.get('user_country', 'BR')
            payment_method = payment_request.get('payment_method', 'auto')
            amount = Decimal(str(payment_request['amount']))
            original_currency = payment_request.get('currency', 'BRL')
            
            # Determina configuração do país
            country_config = PaymentConfig.COUNTRY_CONFIGS.get(user_country, PaymentConfig.COUNTRY_CONFIGS['BR'])
            target_currency = country_config['currency']
            
            # Converte moeda se necessário
            if original_currency != target_currency:
                amount = await self.currency_converter.convert(amount, original_currency, target_currency)
            
            # Determina provedor baseado no país e método de pagamento
            if user_country == 'BR' and payment_method in ['pix', 'auto']:
                return await self._create_brazil_payment(payment_request, amount, payment_method)
            else:
                return await self._create_international_payment(payment_request, amount, target_currency, country_config)
                
        except Exception as e:
            logger.error(f"Erro ao criar pagamento: {str(e)}")
            raise
    
    async def _create_brazil_payment(self, payment_request: Dict, amount: Decimal, payment_method: str) -> Dict:
        """Cria pagamento para o Brasil (Mercado Pago)"""
        
        if payment_method == 'pix':
            # Pagamento PIX
            pix_result = await self.pix_system.create_pix_payment(
                amount=amount,
                description=payment_request['description'],
                user_data=payment_request['user_data']
            )
            
            return {
                'provider': 'mercadopago',
                'payment_type': 'pix',
                'payment_data': pix_result,
                'amount': amount,
                'currency': 'BRL'
            }
        
        else:
            # Checkout completo do Mercado Pago
            preference_data = {
                "items": [{
                    "title": payment_request['description'],
                    "quantity": 1,
                    "unit_price": float(amount),
                    "currency_id": "BRL"
                }],
                "payment_methods": {
                    "excluded_payment_types": [],
                    "installments": 12
                },
                "back_urls": {
                    "success": payment_request.get('success_url', 'https://your-domain.com/success'),
                    "failure": payment_request.get('failure_url', 'https://your-domain.com/failure'),
                    "pending": payment_request.get('pending_url', 'https://your-domain.com/pending')
                },
                "auto_return": "approved",
                "metadata": payment_request.get('metadata', {})
            }
            
            mp = mercadopago.SDK(PaymentConfig.MP_ACCESS_TOKEN)
            preference_response = mp.preference().create(preference_data)
            preference = preference_response["response"]
            
            return {
                'provider': 'mercadopago',
                'payment_type': 'checkout',
                'payment_data': {
                    'preference_id': preference['id'],
                    'init_point': preference['init_point'],
                    'sandbox_init_point': preference['sandbox_init_point']
                },
                'amount': amount,
                'currency': 'BRL'
            }
    
    async def _create_international_payment(self, payment_request: Dict, amount: Decimal, currency: str, country_config: Dict) -> Dict:
        """Cria pagamento internacional (Stripe)"""
        
        # Calcula taxa se aplicável
        tax_rate = country_config.get('tax_rate', 0)
        tax_amount = amount * Decimal(str(tax_rate))
        total_amount = amount + tax_amount
        
        # Cria linha de item para o Stripe
        line_items = [{
            'price_data': {
                'currency': currency.lower(),
                'product_data': {
                    'name': payment_request['description'],
                },
                'unit_amount': int(total_amount * 100) if currency != 'JPY' else int(total_amount),
            },
            'quantity': 1,
        }]
        
        # Adiciona taxa separadamente se aplicável
        if tax_amount > 0:
            line_items.append({
                'price_data': {
                    'currency': currency.lower(),
                    'product_data': {
                        'name': f'Tax ({tax_rate*100}%)',
                    },
                    'unit_amount': int(tax_amount * 100) if currency != 'JPY' else int(tax_amount),
                },
                'quantity': 1,
            })
        
        checkout_result = await self.stripe_system.create_checkout_session(
            line_items=line_items,
            user_data=payment_request['user_data'],
            metadata=payment_request.get('metadata', {})
        )
        
        return {
            'provider': 'stripe',
            'payment_type': 'checkout',
            'payment_data': checkout_result,
            'amount': total_amount,
            'currency': currency,
            'tax_amount': tax_amount
        }
    
    async def process_webhook(self, provider: str, payload: Dict, signature: str = None) -> Dict:
        """Processa webhooks de pagamento"""
        
        if provider == 'stripe':
            return await self._process_stripe_webhook(payload, signature)
        elif provider == 'mercadopago':
            return await self._process_mercadopago_webhook(payload)
        else:
            raise ValueError(f"Provider não suportado: {provider}")
    
    async def _process_stripe_webhook(self, payload: Dict, signature: str) -> Dict:
        """Processa webhook do Stripe"""
        try:
            # Verifica assinatura
            event = stripe.Webhook.construct_event(
                payload, signature, PaymentConfig.STRIPE_WEBHOOK_SECRET
            )
            
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                
                # Processa pagamento aprovado
                await self._handle_payment_success({
                    'provider': 'stripe',
                    'payment_id': session['payment_intent'],
                    'session_id': session['id'],
                    'amount': session['amount_total'] / 100,
                    'currency': session['currency'].upper(),
                    'metadata': session.get('metadata', {}),
                    'customer_email': session.get('customer_email')
                })
                
            elif event['type'] == 'payment_intent.payment_failed':
                payment_intent = event['data']['object']
                
                # Processa pagamento falhado
                await self._handle_payment_failure({
                    'provider': 'stripe',
                    'payment_id': payment_intent['id'],
                    'error': payment_intent.get('last_payment_error', {}),
                    'metadata': payment_intent.get('metadata', {})
                })
            
            return {'status': 'success', 'processed': True}
            
        except Exception as e:
            logger.error(f"Erro no webhook Stripe: {str(e)}")
            raise
    
    async def _process_mercadopago_webhook(self, payload: Dict) -> Dict:
        """Processa webhook do Mercado Pago"""
        try:
            # Mercado Pago envia notificações de diferentes tipos
            if payload.get('type') == 'payment':
                payment_id = payload['data']['id']
                
                # Busca detalhes do pagamento
                mp = mercadopago.SDK(PaymentConfig.MP_ACCESS_TOKEN)
                payment_response = mp.payment().get(payment_id)
                payment = payment_response["response"]
                
                if payment['status'] == 'approved':
                    # Pagamento aprovado
                    await self._handle_payment_success({
                        'provider': 'mercadopago',
                        'payment_id': payment['id'],
                        'amount': payment['transaction_amount'],
                        'currency': 'BRL',
                        'payment_method': payment['payment_method_id'],
                        'metadata': payment.get('metadata', {}),
                        'payer_email': payment['payer']['email']
                    })
                    
                elif payment['status'] in ['rejected', 'cancelled']:
                    # Pagamento rejeitado/cancelado
                    await self._handle_payment_failure({
                        'provider': 'mercadopago',
                        'payment_id': payment['id'],
                        'status': payment['status'],
                        'status_detail': payment['status_detail'],
                        'metadata': payment.get('metadata', {})
                    })
            
            return {'status': 'success', 'processed': True}
            
        except Exception as e:
            logger.error(f"Erro no webhook Mercado Pago: {str(e)}")
            raise
    
    async def _handle_payment_success(self, payment_data: Dict):
        """Processa pagamento bem-sucedido"""
        logger.info(f"Pagamento aprovado: {payment_data}")
        
        # Aqui você implementaria:
        # 1. Atualizar status do pedido no banco
        # 2. Liberar acesso ao produto/serviço
        # 3. Enviar email de confirmação
        # 4. Atualizar gamificação do usuário
        # 5. Notificar sistemas externos
        
        metadata = payment_data.get('metadata', {})
        user_id = metadata.get('user_id')
        product_id = metadata.get('product_id')
        
        if user_id and product_id:
            # Implementar lógica de negócio
            pass
    
    async def _handle_payment_failure(self, payment_data: Dict):
        """Processa pagamento falhado"""
        logger.warning(f"Pagamento falhado: {payment_data}")
        
        # Aqui você implementaria:
        # 1. Notificar usuário sobre falha
        # 2. Sugerir métodos alternativos
        # 3. Log para análise
        # 4. Retry automático se aplicável

# ================================
# API FLASK PARA PAGAMENTOS
# ================================

app = Flask(__name__)
CORS(app, origins=['*'])

# Instância global do sistema de pagamentos
payment_system = UnifiedPaymentSystem()

@app.route('/api/payments/currencies', methods=['GET'])
def get_supported_currencies():
    """Lista moedas suportadas"""
    return jsonify({
        'currencies': PaymentConfig.SUPPORTED_CURRENCIES,
        'default_currency': 'BRL'
    }), 200

@app.route('/api/payments/countries', methods=['GET'])
def get_country_configs():
    """Lista configurações por país"""
    return jsonify({
        'countries': PaymentConfig.COUNTRY_CONFIGS
    }), 200

@app.route('/api/payments/convert', methods=['POST'])
async def convert_currency():
    """Converte entre moedas"""
    try:
        data = request.get_json()
        
        amount = Decimal(str(data['amount']))
        from_currency = data['from_currency']
        to_currency = data['to_currency']
        
        converted_amount = await payment_system.currency_converter.convert(
            amount, from_currency, to_currency
        )
        
        return jsonify({
            'original_amount': float(amount),
            'original_currency': from_currency,
            'converted_amount': float(converted_amount),
            'converted_currency': to_currency,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na conversão: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/payments/create', methods=['POST'])
async def create_payment():
    """Cria pagamento unificado"""
    try:
        payment_request = request.get_json()
        
        # Validação básica
        required_fields = ['amount', 'description', 'user_data']
        for field in required_fields:
            if field not in payment_request:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        # Cria pagamento
        payment_result = await payment_system.create_payment(payment_request)
        
        return jsonify(payment_result), 200
        
    except Exception as e:
        logger.error(f"Erro ao criar pagamento: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/payments/pix/create', methods=['POST'])
async def create_pix_payment():
    """Cria pagamento PIX específico"""
    try:
        data = request.get_json()
        
        amount = Decimal(str(data['amount']))
        description = data['description']
        user_data = data['user_data']
        
        pix_result = await payment_system.pix_system.create_pix_payment(
            amount, description, user_data
        )
        
        return jsonify(pix_result), 200
        
    except Exception as e:
        logger.error(f"Erro no PIX: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/payments/pix/status/<payment_id>', methods=['GET'])
async def check_pix_status(payment_id):
    """Verifica status do PIX"""
    try:
        status = await payment_system.pix_system.check_pix_status(payment_id)
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Erro ao verificar PIX: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/payments/webhook/stripe', methods=['POST'])
async def stripe_webhook():
    """Webhook do Stripe"""
    try:
        payload = request.data
        signature = request.headers.get('Stripe-Signature')
        
        result = await payment_system.process_webhook('stripe', payload, signature)
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Erro no webhook Stripe: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/payments/webhook/mercadopago', methods=['POST'])
async def mercadopago_webhook():
    """Webhook do Mercado Pago"""
    try:
        payload = request.get_json()
        
        result = await payment_system.process_webhook('mercadopago', payload)
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Erro no webhook Mercado Pago: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)

