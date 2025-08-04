"""
🤖 Sistema de Agentes IA Avançado - RE-EDUCA Store
Sistema completo de IA conversacional com agentes especializados
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

import openai
import google.generativeai as genai
import requests
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import stripe
import mercadopago

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
CORS(app, origins=['*'])
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuração das APIs
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
MERCADOPAGO_ACCESS_TOKEN = os.environ.get('MERCADOPAGO_ACCESS_TOKEN')

# Inicialização das APIs
genai.configure(api_key=GOOGLE_API_KEY)
openai.api_key = OPENAI_API_KEY
stripe.api_key = STRIPE_SECRET_KEY
mp = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)

# ================================
# MODELOS E ENUMS
# ================================

class AgentType(Enum):
    DR_NUTRI = "dr_nutri"
    COACH_FIT = "coach_fit"
    SAGE_RESEARCH = "sage_research"
    MOTI_GAME = "moti_game"
    MIND_WELLNESS = "mind_wellness"
    SALES_ASSISTANT = "sales_assistant"
    PLATFORM_CONCIERGE = "platform_concierge"

class MessageType(Enum):
    TEXT = "text"
    PRODUCT_CARD = "product_card"
    TOOL_INTEGRATION = "tool_integration"
    PAYMENT_LINK = "payment_link"
    GAMIFICATION = "gamification"
    CHART = "chart"
    RECOMMENDATION = "recommendation"

@dataclass
class UserContext:
    user_id: str
    profile: Dict[str, Any]
    health_data: Dict[str, Any]
    preferences: Dict[str, Any]
    current_tool: Optional[str] = None
    conversation_history: List[Dict] = None
    gamification_data: Dict[str, Any] = None

@dataclass
class AgentResponse:
    agent_type: AgentType
    message: str
    message_type: MessageType
    metadata: Dict[str, Any]
    suggested_actions: List[Dict] = None
    products: List[Dict] = None
    tools_integration: Dict = None

# ================================
# SISTEMA DE AGENTES IA
# ================================

class AIAgentSystem:
    def __init__(self):
        self.agents = {
            AgentType.DR_NUTRI: DrNutriAgent(),
            AgentType.COACH_FIT: CoachFitAgent(),
            AgentType.SAGE_RESEARCH: SageResearchAgent(),
            AgentType.MOTI_GAME: MotiGameAgent(),
            AgentType.MIND_WELLNESS: MindWellnessAgent(),
            AgentType.SALES_ASSISTANT: SalesAssistantAgent(),
            AgentType.PLATFORM_CONCIERGE: PlatformConciergeAgent()
        }
        
    async def process_message(self, user_context: UserContext, message: str, agent_type: AgentType) -> AgentResponse:
        """Processa mensagem com o agente apropriado"""
        try:
            agent = self.agents[agent_type]
            response = await agent.process_message(user_context, message)
            
            # Log da interação
            self._log_interaction(user_context.user_id, agent_type, message, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            return self._create_error_response(agent_type, str(e))
    
    def _log_interaction(self, user_id: str, agent_type: AgentType, message: str, response: AgentResponse):
        """Log das interações para analytics"""
        interaction_data = {
            'user_id': user_id,
            'agent_type': agent_type.value,
            'message': message,
            'response_type': response.message_type.value,
            'timestamp': datetime.utcnow().isoformat()
        }
        # Aqui você salvaria no banco de dados
        logger.info(f"Interação registrada: {interaction_data}")
    
    def _create_error_response(self, agent_type: AgentType, error: str) -> AgentResponse:
        """Cria resposta de erro padronizada"""
        return AgentResponse(
            agent_type=agent_type,
            message=f"Desculpe, ocorreu um erro. Nossa equipe foi notificada. Erro: {error}",
            message_type=MessageType.TEXT,
            metadata={'error': True, 'error_message': error}
        )

# ================================
# AGENTES ESPECIALIZADOS
# ================================

class DrNutriAgent:
    """Agente especializado em nutrição"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.context_prompt = """
        Você é Dr. Nutri, um nutricionista virtual especializado e empático da plataforma RE-EDUCA Store.
        
        PERSONALIDADE:
        - Empático e motivador
        - Linguagem acessível e didática
        - Baseado em evidências científicas
        - Foco em mudanças graduais e sustentáveis
        
        CAPACIDADES:
        - Análise nutricional personalizada
        - Criação de planos alimentares
        - Recomendações baseadas em objetivos
        - Interpretação de dados do calendário alimentar
        - Sugestões de produtos nutricionais
        
        DADOS DISPONÍVEIS:
        - Perfil completo do usuário
        - Histórico alimentar (USDA database)
        - Metas de saúde
        - Preferências e restrições
        - Dados de IMC e progresso
        
        INSTRUÇÕES:
        - Sempre personalize baseado no contexto do usuário
        - Sugira produtos relevantes quando apropriado
        - Integre com as ferramentas da plataforma
        - Mantenha tom motivador e positivo
        - Cite evidências quando necessário
        """
    
    async def process_message(self, user_context: UserContext, message: str) -> AgentResponse:
        """Processa mensagem nutricional"""
        try:
            # Prepara contexto personalizado
            context = self._prepare_context(user_context)
            
            # Gera resposta com Gemini
            full_prompt = f"{self.context_prompt}\n\nCONTEXTO DO USUÁRIO:\n{context}\n\nMENSAGEM: {message}\n\nRESPOSTA:"
            
            response = await self.model.generate_content_async(full_prompt)
            
            # Processa resposta e identifica ações
            processed_response = self._process_response(response.text, user_context)
            
            return processed_response
            
        except Exception as e:
            logger.error(f"Erro no Dr. Nutri: {str(e)}")
            raise
    
    def _prepare_context(self, user_context: UserContext) -> str:
        """Prepara contexto personalizado para o usuário"""
        context_parts = []
        
        # Dados do perfil
        if user_context.profile:
            context_parts.append(f"Perfil: {json.dumps(user_context.profile, indent=2)}")
        
        # Dados de saúde
        if user_context.health_data:
            context_parts.append(f"Dados de Saúde: {json.dumps(user_context.health_data, indent=2)}")
        
        # Ferramenta atual
        if user_context.current_tool:
            context_parts.append(f"Ferramenta Atual: {user_context.current_tool}")
        
        return "\n".join(context_parts)
    
    def _process_response(self, response_text: str, user_context: UserContext) -> AgentResponse:
        """Processa resposta e identifica produtos/ações"""
        
        # Identifica se deve sugerir produtos
        products = self._identify_product_suggestions(response_text, user_context)
        
        # Identifica integrações com ferramentas
        tools_integration = self._identify_tool_integrations(response_text, user_context)
        
        # Identifica ações sugeridas
        suggested_actions = self._identify_suggested_actions(response_text)
        
        message_type = MessageType.TEXT
        if products:
            message_type = MessageType.PRODUCT_CARD
        elif tools_integration:
            message_type = MessageType.TOOL_INTEGRATION
        
        return AgentResponse(
            agent_type=AgentType.DR_NUTRI,
            message=response_text,
            message_type=message_type,
            metadata={
                'personalized': True,
                'evidence_based': True,
                'tool_context': user_context.current_tool
            },
            suggested_actions=suggested_actions,
            products=products,
            tools_integration=tools_integration
        )
    
    def _identify_product_suggestions(self, response: str, user_context: UserContext) -> List[Dict]:
        """Identifica produtos nutricionais relevantes"""
        # Aqui você implementaria lógica para sugerir produtos baseado na resposta
        # Por exemplo, se mencionar "proteína", sugerir whey protein
        products = []
        
        keywords_products = {
            'proteína': {'category': 'suplementos', 'type': 'protein'},
            'vitamina': {'category': 'suplementos', 'type': 'vitamins'},
            'omega': {'category': 'suplementos', 'type': 'omega3'},
            'probiótico': {'category': 'suplementos', 'type': 'probiotics'}
        }
        
        for keyword, product_info in keywords_products.items():
            if keyword.lower() in response.lower():
                # Buscar produtos reais do banco de dados
                products.append({
                    'id': f'prod_{keyword}',
                    'name': f'Suplemento de {keyword.title()}',
                    'category': product_info['category'],
                    'price': 89.90,
                    'currency': 'BRL',
                    'description': f'Suplemento premium de {keyword}',
                    'relevance_score': 0.9
                })
        
        return products[:3]  # Máximo 3 produtos
    
    def _identify_tool_integrations(self, response: str, user_context: UserContext) -> Dict:
        """Identifica integrações com ferramentas"""
        integrations = {}
        
        # Calendário alimentar
        if any(word in response.lower() for word in ['registrar', 'anotar', 'adicionar', 'alimento']):
            integrations['food_diary'] = {
                'action': 'open_food_search',
                'context': 'nutrition_recommendation'
            }
        
        # Calculadora IMC
        if any(word in response.lower() for word in ['imc', 'peso', 'altura', 'calcular']):
            integrations['imc_calculator'] = {
                'action': 'open_calculator',
                'context': 'nutrition_assessment'
            }
        
        return integrations
    
    def _identify_suggested_actions(self, response: str) -> List[Dict]:
        """Identifica ações sugeridas"""
        actions = []
        
        if 'plano alimentar' in response.lower():
            actions.append({
                'type': 'create_meal_plan',
                'label': 'Criar Plano Alimentar',
                'icon': '🍽️'
            })
        
        if 'receita' in response.lower():
            actions.append({
                'type': 'search_recipes',
                'label': 'Buscar Receitas',
                'icon': '👨‍🍳'
            })
        
        return actions

class CoachFitAgent:
    """Agente especializado em exercícios e fitness"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.context_prompt = """
        Você é Coach Fit, um personal trainer virtual motivador e especializado da plataforma RE-EDUCA Store.
        
        PERSONALIDADE:
        - Motivador e encorajador
        - Adaptável a diferentes níveis
        - Foco na progressão gradual
        - Considera limitações físicas
        
        CAPACIDADES:
        - Criação de planos de treino personalizados
        - Análise de progresso físico
        - Recomendações baseadas em IMC e objetivos
        - Motivação e coaching comportamental
        - Sugestões de equipamentos e produtos fitness
        
        DADOS DISPONÍVEIS:
        - Nível de condicionamento físico
        - Histórico de exercícios
        - Limitações e preferências
        - Equipamentos disponíveis
        - Metas fitness
        
        INSTRUÇÕES:
        - Sempre adapte treinos ao nível do usuário
        - Sugira produtos fitness quando relevante
        - Integre com ferramentas de exercício
        - Mantenha tom motivador e positivo
        - Foque na segurança e progressão gradual
        """
    
    async def process_message(self, user_context: UserContext, message: str) -> AgentResponse:
        """Processa mensagem de fitness"""
        try:
            context = self._prepare_fitness_context(user_context)
            full_prompt = f"{self.context_prompt}\n\nCONTEXTO DO USUÁRIO:\n{context}\n\nMENSAGEM: {message}\n\nRESPOSTA:"
            
            response = await self.model.generate_content_async(full_prompt)
            processed_response = self._process_fitness_response(response.text, user_context)
            
            return processed_response
            
        except Exception as e:
            logger.error(f"Erro no Coach Fit: {str(e)}")
            raise
    
    def _prepare_fitness_context(self, user_context: UserContext) -> str:
        """Prepara contexto específico para fitness"""
        context_parts = []
        
        # Dados físicos
        if user_context.health_data:
            imc = user_context.health_data.get('imc')
            if imc:
                context_parts.append(f"IMC atual: {imc}")
        
        # Nível de atividade
        activity_level = user_context.profile.get('activity_level', 'beginner')
        context_parts.append(f"Nível de atividade: {activity_level}")
        
        # Objetivos fitness
        goals = user_context.profile.get('fitness_goals', [])
        if goals:
            context_parts.append(f"Objetivos: {', '.join(goals)}")
        
        return "\n".join(context_parts)
    
    def _process_fitness_response(self, response_text: str, user_context: UserContext) -> AgentResponse:
        """Processa resposta de fitness"""
        
        # Identifica produtos fitness
        products = self._identify_fitness_products(response_text)
        
        # Identifica integrações com ferramentas
        tools_integration = self._identify_fitness_tools(response_text)
        
        # Ações sugeridas
        suggested_actions = self._identify_fitness_actions(response_text)
        
        return AgentResponse(
            agent_type=AgentType.COACH_FIT,
            message=response_text,
            message_type=MessageType.TOOL_INTEGRATION if tools_integration else MessageType.TEXT,
            metadata={
                'fitness_focused': True,
                'safety_checked': True,
                'progressive': True
            },
            suggested_actions=suggested_actions,
            products=products,
            tools_integration=tools_integration
        )
    
    def _identify_fitness_products(self, response: str) -> List[Dict]:
        """Identifica produtos fitness relevantes"""
        products = []
        
        fitness_keywords = {
            'halteres': {'category': 'equipamentos', 'price': 199.90},
            'whey': {'category': 'suplementos', 'price': 89.90},
            'creatina': {'category': 'suplementos', 'price': 59.90},
            'tênis': {'category': 'vestuario', 'price': 299.90},
            'corda': {'category': 'equipamentos', 'price': 29.90}
        }
        
        for keyword, info in fitness_keywords.items():
            if keyword in response.lower():
                products.append({
                    'id': f'fitness_{keyword}',
                    'name': f'{keyword.title()} Premium',
                    'category': info['category'],
                    'price': info['price'],
                    'currency': 'BRL',
                    'relevance_score': 0.8
                })
        
        return products[:3]
    
    def _identify_fitness_tools(self, response: str) -> Dict:
        """Identifica integrações com ferramentas fitness"""
        integrations = {}
        
        if any(word in response.lower() for word in ['treino', 'exercício', 'plano']):
            integrations['workout_planner'] = {
                'action': 'create_workout',
                'context': 'personalized_training'
            }
        
        if 'progresso' in response.lower():
            integrations['progress_tracker'] = {
                'action': 'view_progress',
                'context': 'fitness_tracking'
            }
        
        return integrations
    
    def _identify_fitness_actions(self, response: str) -> List[Dict]:
        """Identifica ações fitness sugeridas"""
        actions = []
        
        if 'treino' in response.lower():
            actions.append({
                'type': 'start_workout',
                'label': 'Iniciar Treino',
                'icon': '💪'
            })
        
        if 'cronômetro' in response.lower():
            actions.append({
                'type': 'start_timer',
                'label': 'Cronômetro',
                'icon': '⏱️'
            })
        
        return actions

class SageResearchAgent:
    """Agente especializado em pesquisa científica"""
    
    def __init__(self):
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
        self.context_prompt = """
        Você é Sage Research, um pesquisador especializado em saúde e bem-estar da plataforma RE-EDUCA Store.
        
        PERSONALIDADE:
        - Rigoroso cientificamente
        - Sempre cita fontes confiáveis
        - Linguagem técnica mas acessível
        - Imparcial e baseado em evidências
        
        CAPACIDADES:
        - Pesquisa de estudos científicos recentes
        - Verificação de informações de saúde
        - Análise de tendências em nutrição e fitness
        - Informações sobre ingredientes e suplementos
        - Guidelines médicas atualizadas
        
        INSTRUÇÕES:
        - Sempre cite fontes científicas
        - Mantenha-se atualizado com pesquisas recentes
        - Seja imparcial e baseado em evidências
        - Traduza informações técnicas para linguagem acessível
        - Sugira produtos apenas se cientificamente comprovados
        """
    
    async def process_message(self, user_context: UserContext, message: str) -> AgentResponse:
        """Processa mensagem de pesquisa"""
        try:
            # Usa Perplexity para pesquisa em tempo real
            research_query = f"{self.context_prompt}\n\nPergunta do usuário: {message}\n\nPor favor, forneça uma resposta baseada em evidências científicas recentes, citando fontes confiáveis."
            
            headers = {
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": [
                    {"role": "system", "content": self.context_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.2,
                "max_tokens": 1000
            }
            
            response = requests.post(self.perplexity_url, json=payload, headers=headers)
            response_data = response.json()
            
            research_result = response_data['choices'][0]['message']['content']
            
            processed_response = self._process_research_response(research_result, user_context)
            
            return processed_response
            
        except Exception as e:
            logger.error(f"Erro no Sage Research: {str(e)}")
            raise
    
    def _process_research_response(self, response_text: str, user_context: UserContext) -> AgentResponse:
        """Processa resposta de pesquisa"""
        
        # Identifica produtos baseados em evidências
        products = self._identify_evidence_based_products(response_text)
        
        # Extrai fontes citadas
        sources = self._extract_sources(response_text)
        
        return AgentResponse(
            agent_type=AgentType.SAGE_RESEARCH,
            message=response_text,
            message_type=MessageType.TEXT,
            metadata={
                'evidence_based': True,
                'sources_cited': len(sources) > 0,
                'research_quality': 'high',
                'sources': sources
            },
            products=products
        )
    
    def _identify_evidence_based_products(self, response: str) -> List[Dict]:
        """Identifica produtos com base científica"""
        # Lógica para identificar produtos mencionados na pesquisa
        return []
    
    def _extract_sources(self, response: str) -> List[str]:
        """Extrai fontes citadas da resposta"""
        # Lógica para extrair URLs e citações
        sources = []
        # Implementar regex para encontrar URLs e citações
        return sources

class MotiGameAgent:
    """Agente especializado em gamificação e motivação"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.context_prompt = """
        Você é Moti Game, o especialista em gamificação da plataforma RE-EDUCA Store.
        
        PERSONALIDADE:
        - Entusiasta e energético
        - Criativo com elementos de jogo
        - Celebra cada pequena vitória
        - Cria senso de progressão e conquista
        
        CAPACIDADES:
        - Criação de desafios personalizados
        - Sistema de pontuação e badges
        - Narrativas motivacionais épicas
        - Celebração de conquistas
        - Histórias de progresso personalizadas
        
        ELEMENTOS DE JOGO:
        - Health Points (HP)
        - Badges e conquistas
        - Níveis de usuário
        - Desafios diários/semanais
        - Narrativas épicas de transformação
        
        INSTRUÇÕES:
        - Sempre gamifique a experiência
        - Crie narrativas épicas onde o usuário é o herói
        - Celebre conquistas com entusiasmo
        - Ofereça desafios alcançáveis
        - Mantenha o usuário motivado e engajado
        """
    
    async def process_message(self, user_context: UserContext, message: str) -> AgentResponse:
        """Processa mensagem de gamificação"""
        try:
            # Prepara contexto de gamificação
            game_context = self._prepare_game_context(user_context)
            
            full_prompt = f"{self.context_prompt}\n\nCONTEXTO DE JOGO:\n{game_context}\n\nMENSAGEM: {message}\n\nRESPOSTA GAMIFICADA:"
            
            response = await self.model.generate_content_async(full_prompt)
            processed_response = self._process_game_response(response.text, user_context)
            
            return processed_response
            
        except Exception as e:
            logger.error(f"Erro no Moti Game: {str(e)}")
            raise
    
    def _prepare_game_context(self, user_context: UserContext) -> str:
        """Prepara contexto de gamificação"""
        game_data = user_context.gamification_data or {}
        
        context_parts = [
            f"Nível atual: {game_data.get('level', 1)}",
            f"Health Points: {game_data.get('hp', 0)}",
            f"Badges conquistadas: {len(game_data.get('badges', []))}",
            f"Streak atual: {game_data.get('streak', 0)} dias",
            f"Desafios ativos: {len(game_data.get('active_challenges', []))}"
        ]
        
        return "\n".join(context_parts)
    
    def _process_game_response(self, response_text: str, user_context: UserContext) -> AgentResponse:
        """Processa resposta de gamificação"""
        
        # Identifica elementos de jogo na resposta
        game_elements = self._identify_game_elements(response_text)
        
        # Cria desafios personalizados
        challenges = self._create_challenges(user_context)
        
        return AgentResponse(
            agent_type=AgentType.MOTI_GAME,
            message=response_text,
            message_type=MessageType.GAMIFICATION,
            metadata={
                'gamified': True,
                'motivational': True,
                'game_elements': game_elements,
                'challenges': challenges
            }
        )
    
    def _identify_game_elements(self, response: str) -> Dict:
        """Identifica elementos de jogo na resposta"""
        elements = {}
        
        if 'parabéns' in response.lower():
            elements['celebration'] = True
        
        if 'desafio' in response.lower():
            elements['challenge'] = True
        
        if 'nível' in response.lower():
            elements['level_up'] = True
        
        return elements
    
    def _create_challenges(self, user_context: UserContext) -> List[Dict]:
        """Cria desafios personalizados"""
        challenges = []
        
        # Desafio baseado no perfil do usuário
        if user_context.current_tool == 'imc_calculator':
            challenges.append({
                'id': 'imc_weekly',
                'title': 'Guerreiro do IMC',
                'description': 'Calcule seu IMC 3 vezes esta semana',
                'reward': 150,
                'type': 'weekly'
            })
        
        return challenges

class SalesAssistantAgent:
    """Agente especializado em vendas e produtos"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.context_prompt = """
        Você é Sales Assistant, o consultor de vendas especializado da plataforma RE-EDUCA Store.
        
        PERSONALIDADE:
        - Consultivo e não invasivo
        - Foca no valor para o cliente
        - Conhece todos os produtos da plataforma
        - Personaliza recomendações
        
        CAPACIDADES:
        - Recomendações de produtos personalizadas
        - Processamento de pagamentos via chat
        - Informações sobre produtos próprios e afiliados
        - Comparação de produtos
        - Ofertas e promoções personalizadas
        
        PRODUTOS DISPONÍVEIS:
        - Produtos próprios (suplementos, equipamentos)
        - Produtos afiliados (Hotmart, Kiwify, Logs, Braip)
        - Planos de assinatura (Basic, Premium, Enterprise)
        
        INSTRUÇÕES:
        - Sempre personalize baseado no perfil do usuário
        - Ofereça produtos relevantes para os objetivos
        - Facilite o processo de compra via chat
        - Seja transparente sobre preços e benefícios
        - Processe pagamentos de forma segura
        """
    
    async def process_message(self, user_context: UserContext, message: str) -> AgentResponse:
        """Processa mensagem de vendas"""
        try:
            # Prepara contexto de produtos
            product_context = await self._prepare_product_context(user_context)
            
            full_prompt = f"{self.context_prompt}\n\nCONTEXTO DE PRODUTOS:\n{product_context}\n\nMENSAGEM: {message}\n\nRESPOSTA DE VENDAS:"
            
            response = await self.model.generate_content_async(full_prompt)
            processed_response = await self._process_sales_response(response.text, user_context)
            
            return processed_response
            
        except Exception as e:
            logger.error(f"Erro no Sales Assistant: {str(e)}")
            raise
    
    async def _prepare_product_context(self, user_context: UserContext) -> str:
        """Prepara contexto de produtos personalizados"""
        # Aqui você buscaria produtos do banco de dados baseado no perfil
        context_parts = [
            "Produtos recomendados baseados no perfil:",
            "- Whey Protein Premium (R$ 89,90)",
            "- Plano Premium (R$ 29,90/mês)",
            "- Kit Exercícios Casa (R$ 199,90)"
        ]
        
        return "\n".join(context_parts)
    
    async def _process_sales_response(self, response_text: str, user_context: UserContext) -> AgentResponse:
        """Processa resposta de vendas"""
        
        # Identifica intenção de compra
        purchase_intent = self._identify_purchase_intent(response_text)
        
        # Busca produtos mencionados
        products = await self._get_mentioned_products(response_text)
        
        # Cria links de pagamento se necessário
        payment_links = []
        if purchase_intent and products:
            payment_links = await self._create_payment_links(products, user_context)
        
        message_type = MessageType.PRODUCT_CARD if products else MessageType.TEXT
        if payment_links:
            message_type = MessageType.PAYMENT_LINK
        
        return AgentResponse(
            agent_type=AgentType.SALES_ASSISTANT,
            message=response_text,
            message_type=message_type,
            metadata={
                'sales_focused': True,
                'purchase_intent': purchase_intent,
                'payment_ready': len(payment_links) > 0
            },
            products=products,
            suggested_actions=[{
                'type': 'view_cart',
                'label': 'Ver Carrinho',
                'icon': '🛒'
            }] if products else []
        )
    
    def _identify_purchase_intent(self, response: str) -> bool:
        """Identifica intenção de compra"""
        purchase_keywords = ['comprar', 'adquirir', 'preço', 'quanto custa', 'onde compro']
        return any(keyword in response.lower() for keyword in purchase_keywords)
    
    async def _get_mentioned_products(self, response: str) -> List[Dict]:
        """Busca produtos mencionados na resposta"""
        # Aqui você implementaria busca real no banco de dados
        products = []
        
        if 'whey' in response.lower():
            products.append({
                'id': 'whey_premium',
                'name': 'Whey Protein Premium',
                'price': 89.90,
                'currency': 'BRL',
                'category': 'suplementos',
                'image': '/images/whey-premium.jpg'
            })
        
        return products
    
    async def _create_payment_links(self, products: List[Dict], user_context: UserContext) -> List[Dict]:
        """Cria links de pagamento para produtos"""
        payment_links = []
        
        for product in products:
            # Cria sessão de checkout no Stripe
            checkout_session = await self._create_stripe_session(product, user_context)
            
            payment_links.append({
                'product_id': product['id'],
                'checkout_url': checkout_session['url'],
                'session_id': checkout_session['id']
            })
        
        return payment_links
    
    async def _create_stripe_session(self, product: Dict, user_context: UserContext) -> Dict:
        """Cria sessão de checkout no Stripe"""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': product['currency'].lower(),
                        'product_data': {
                            'name': product['name'],
                        },
                        'unit_amount': int(product['price'] * 100),  # Stripe usa centavos
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='https://your-domain.com/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='https://your-domain.com/cancel',
                metadata={
                    'user_id': user_context.user_id,
                    'product_id': product['id']
                }
            )
            
            return {
                'id': session.id,
                'url': session.url
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar sessão Stripe: {str(e)}")
            raise

class PlatformConciergeAgent:
    """Agente concierge da plataforma - atendimento geral"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.context_prompt = """
        Você é Platform Concierge, o concierge virtual da plataforma RE-EDUCA Store.
        
        PERSONALIDADE:
        - Acolhedor e prestativo
        - Conhece toda a plataforma
        - Direciona para agentes especializados
        - Resolve dúvidas gerais
        
        CAPACIDADES:
        - Orientação sobre uso da plataforma
        - Direcionamento para agentes especializados
        - Suporte técnico básico
        - Informações sobre funcionalidades
        - Onboarding de novos usuários
        
        AGENTES DISPONÍVEIS:
        - Dr. Nutri: Nutrição e alimentação
        - Coach Fit: Exercícios e fitness
        - Sage Research: Pesquisa científica
        - Moti Game: Gamificação e motivação
        - Mind Wellness: Bem-estar mental
        - Sales Assistant: Produtos e vendas
        
        INSTRUÇÕES:
        - Seja o primeiro ponto de contato
        - Direcione para agentes especializados quando apropriado
        - Forneça orientações gerais sobre a plataforma
        - Mantenha tom acolhedor e prestativo
        - Ajude no onboarding de novos usuários
        """
    
    async def process_message(self, user_context: UserContext, message: str) -> AgentResponse:
        """Processa mensagem geral da plataforma"""
        try:
            # Analisa intenção do usuário
            intent = self._analyze_intent(message)
            
            # Prepara contexto da plataforma
            platform_context = self._prepare_platform_context(user_context)
            
            full_prompt = f"{self.context_prompt}\n\nCONTEXTO DA PLATAFORMA:\n{platform_context}\n\nINTENÇÃO DETECTADA: {intent}\n\nMENSAGEM: {message}\n\nRESPOSTA:"
            
            response = await self.model.generate_content_async(full_prompt)
            processed_response = self._process_concierge_response(response.text, intent, user_context)
            
            return processed_response
            
        except Exception as e:
            logger.error(f"Erro no Platform Concierge: {str(e)}")
            raise
    
    def _analyze_intent(self, message: str) -> str:
        """Analisa intenção do usuário"""
        intents = {
            'nutrition': ['nutrição', 'alimentação', 'dieta', 'comida', 'calorias'],
            'fitness': ['exercício', 'treino', 'academia', 'musculação', 'cardio'],
            'research': ['pesquisa', 'estudo', 'científico', 'evidência'],
            'motivation': ['motivação', 'desafio', 'meta', 'objetivo'],
            'wellness': ['bem-estar', 'mental', 'ansiedade', 'estresse'],
            'sales': ['comprar', 'produto', 'preço', 'venda'],
            'support': ['ajuda', 'como', 'dúvida', 'problema']
        }
        
        message_lower = message.lower()
        for intent, keywords in intents.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent
        
        return 'general'
    
    def _prepare_platform_context(self, user_context: UserContext) -> str:
        """Prepara contexto da plataforma"""
        context_parts = [
            f"Usuário: {user_context.profile.get('name', 'Usuário')}",
            f"Nível: {user_context.gamification_data.get('level', 1) if user_context.gamification_data else 1}",
            f"Ferramenta atual: {user_context.current_tool or 'Nenhuma'}"
        ]
        
        return "\n".join(context_parts)
    
    def _process_concierge_response(self, response_text: str, intent: str, user_context: UserContext) -> AgentResponse:
        """Processa resposta do concierge"""
        
        # Sugere agente especializado baseado na intenção
        suggested_agent = self._suggest_specialized_agent(intent)
        
        # Cria ações sugeridas
        suggested_actions = self._create_platform_actions(intent)
        
        return AgentResponse(
            agent_type=AgentType.PLATFORM_CONCIERGE,
            message=response_text,
            message_type=MessageType.TEXT,
            metadata={
                'intent': intent,
                'suggested_agent': suggested_agent,
                'platform_guidance': True
            },
            suggested_actions=suggested_actions
        )
    
    def _suggest_specialized_agent(self, intent: str) -> Optional[str]:
        """Sugere agente especializado baseado na intenção"""
        agent_mapping = {
            'nutrition': 'dr_nutri',
            'fitness': 'coach_fit',
            'research': 'sage_research',
            'motivation': 'moti_game',
            'wellness': 'mind_wellness',
            'sales': 'sales_assistant'
        }
        
        return agent_mapping.get(intent)
    
    def _create_platform_actions(self, intent: str) -> List[Dict]:
        """Cria ações da plataforma baseadas na intenção"""
        actions = []
        
        if intent == 'nutrition':
            actions.append({
                'type': 'switch_agent',
                'agent': 'dr_nutri',
                'label': 'Falar com Dr. Nutri',
                'icon': '🥗'
            })
        
        elif intent == 'fitness':
            actions.append({
                'type': 'switch_agent',
                'agent': 'coach_fit',
                'label': 'Falar com Coach Fit',
                'icon': '💪'
            })
        
        # Sempre oferece tour da plataforma
        actions.append({
            'type': 'platform_tour',
            'label': 'Tour da Plataforma',
            'icon': '🗺️'
        })
        
        return actions

# ================================
# SISTEMA DE PAGAMENTOS GLOBAL
# ================================

class GlobalPaymentSystem:
    """Sistema de pagamentos global com Stripe e PIX"""
    
    def __init__(self):
        self.stripe = stripe
        self.mp = mp
        self.supported_currencies = [
            'BRL', 'USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CHF', 'SEK', 'NOK'
        ]
    
    async def create_payment_session(self, product: Dict, user_context: UserContext, payment_method: str = 'auto') -> Dict:
        """Cria sessão de pagamento baseada na localização do usuário"""
        
        user_country = user_context.profile.get('country', 'BR')
        user_currency = user_context.profile.get('currency', 'BRL')
        
        if user_country == 'BR' and payment_method in ['pix', 'auto']:
            # Usar Mercado Pago para PIX
            return await self._create_mercadopago_session(product, user_context)
        else:
            # Usar Stripe para outros países
            return await self._create_stripe_session(product, user_context, user_currency)
    
    async def _create_mercadopago_session(self, product: Dict, user_context: UserContext) -> Dict:
        """Cria sessão de pagamento no Mercado Pago com PIX"""
        try:
            preference_data = {
                "items": [
                    {
                        "title": product['name'],
                        "quantity": 1,
                        "unit_price": product['price'],
                        "currency_id": "BRL"
                    }
                ],
                "payment_methods": {
                    "excluded_payment_types": [],
                    "installments": 12
                },
                "back_urls": {
                    "success": "https://your-domain.com/success",
                    "failure": "https://your-domain.com/failure",
                    "pending": "https://your-domain.com/pending"
                },
                "auto_return": "approved",
                "metadata": {
                    "user_id": user_context.user_id,
                    "product_id": product['id']
                }
            }
            
            preference_response = self.mp.preference().create(preference_data)
            preference = preference_response["response"]
            
            return {
                'provider': 'mercadopago',
                'preference_id': preference['id'],
                'init_point': preference['init_point'],
                'sandbox_init_point': preference['sandbox_init_point'],
                'qr_code': preference.get('qr_code'),
                'qr_code_base64': preference.get('qr_code_base64')
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar sessão Mercado Pago: {str(e)}")
            raise
    
    async def _create_stripe_session(self, product: Dict, user_context: UserContext, currency: str) -> Dict:
        """Cria sessão de pagamento no Stripe"""
        try:
            # Converte preço para a moeda do usuário
            converted_price = await self._convert_currency(product['price'], 'BRL', currency)
            
            session = self.stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency.lower(),
                        'product_data': {
                            'name': product['name'],
                            'description': product.get('description', ''),
                        },
                        'unit_amount': int(converted_price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='https://your-domain.com/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='https://your-domain.com/cancel',
                metadata={
                    'user_id': user_context.user_id,
                    'product_id': product['id'],
                    'original_currency': 'BRL',
                    'original_price': str(product['price'])
                },
                customer_email=user_context.profile.get('email'),
                billing_address_collection='required'
            )
            
            return {
                'provider': 'stripe',
                'session_id': session.id,
                'checkout_url': session.url,
                'currency': currency,
                'amount': converted_price
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar sessão Stripe: {str(e)}")
            raise
    
    async def _convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Converte moeda usando API de câmbio"""
        if from_currency == to_currency:
            return amount
        
        try:
            # Usar API de câmbio (exemplo: exchangerate-api.com)
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            response = requests.get(url)
            rates = response.json()['rates']
            
            converted_amount = amount * rates[to_currency]
            return round(converted_amount, 2)
            
        except Exception as e:
            logger.error(f"Erro na conversão de moeda: {str(e)}")
            # Fallback: retorna valor original
            return amount
    
    async def process_webhook(self, provider: str, payload: Dict) -> Dict:
        """Processa webhooks de pagamento"""
        if provider == 'stripe':
            return await self._process_stripe_webhook(payload)
        elif provider == 'mercadopago':
            return await self._process_mercadopago_webhook(payload)
        else:
            raise ValueError(f"Provider não suportado: {provider}")
    
    async def _process_stripe_webhook(self, payload: Dict) -> Dict:
        """Processa webhook do Stripe"""
        try:
            event = payload
            
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                
                # Atualizar status do pedido
                await self._update_order_status(
                    session['metadata']['user_id'],
                    session['metadata']['product_id'],
                    'completed'
                )
                
                return {'status': 'success', 'message': 'Pagamento processado'}
            
        except Exception as e:
            logger.error(f"Erro no webhook Stripe: {str(e)}")
            raise
    
    async def _process_mercadopago_webhook(self, payload: Dict) -> Dict:
        """Processa webhook do Mercado Pago"""
        try:
            # Implementar lógica do webhook do Mercado Pago
            return {'status': 'success', 'message': 'Webhook processado'}
            
        except Exception as e:
            logger.error(f"Erro no webhook Mercado Pago: {str(e)}")
            raise
    
    async def _update_order_status(self, user_id: str, product_id: str, status: str):
        """Atualiza status do pedido no banco de dados"""
        # Implementar atualização no banco de dados
        logger.info(f"Pedido atualizado: {user_id}, {product_id}, {status}")

# ================================
# ROTAS DA API
# ================================

# Instância global do sistema de agentes
ai_system = AIAgentSystem()
payment_system = GlobalPaymentSystem()

@app.route('/api/ai/chat', methods=['POST'])
async def chat_with_agent():
    """Endpoint principal para chat com agentes"""
    try:
        data = request.get_json()
        
        # Extrai dados da requisição
        user_id = data.get('user_id')
        message = data.get('message')
        agent_type = AgentType(data.get('agent_type', 'platform_concierge'))
        
        # Busca contexto do usuário (implementar busca real no banco)
        user_context = await _get_user_context(user_id)
        
        # Processa mensagem com o agente
        response = await ai_system.process_message(user_context, message, agent_type)
        
        # Converte resposta para JSON
        response_data = {
            'agent_type': response.agent_type.value,
            'message': response.message,
            'message_type': response.message_type.value,
            'metadata': response.metadata,
            'suggested_actions': response.suggested_actions,
            'products': response.products,
            'tools_integration': response.tools_integration,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Erro no chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/agents', methods=['GET'])
def get_available_agents():
    """Lista agentes disponíveis"""
    agents = [
        {
            'type': 'dr_nutri',
            'name': 'Dr. Nutri',
            'specialty': 'Nutrição e Alimentação',
            'description': 'Especialista em nutrição personalizada',
            'icon': '🥗',
            'available': True
        },
        {
            'type': 'coach_fit',
            'name': 'Coach Fit',
            'specialty': 'Exercícios e Fitness',
            'description': 'Personal trainer virtual motivador',
            'icon': '💪',
            'available': True
        },
        {
            'type': 'sage_research',
            'name': 'Sage Research',
            'specialty': 'Pesquisa Científica',
            'description': 'Pesquisador de evidências científicas',
            'icon': '🔬',
            'available': True
        },
        {
            'type': 'moti_game',
            'name': 'Moti Game',
            'specialty': 'Gamificação',
            'description': 'Especialista em motivação e jogos',
            'icon': '🎮',
            'available': True
        },
        {
            'type': 'mind_wellness',
            'name': 'Mind Wellness',
            'specialty': 'Bem-estar Mental',
            'description': 'Suporte para bem-estar emocional',
            'icon': '🧘',
            'available': True
        },
        {
            'type': 'sales_assistant',
            'name': 'Sales Assistant',
            'specialty': 'Vendas e Produtos',
            'description': 'Consultor de vendas especializado',
            'icon': '🛒',
            'available': True
        },
        {
            'type': 'platform_concierge',
            'name': 'Platform Concierge',
            'specialty': 'Atendimento Geral',
            'description': 'Concierge da plataforma',
            'icon': '🤖',
            'available': True
        }
    ]
    
    return jsonify({'agents': agents}), 200

@app.route('/api/payments/create-session', methods=['POST'])
async def create_payment_session():
    """Cria sessão de pagamento"""
    try:
        data = request.get_json()
        
        product = data.get('product')
        user_id = data.get('user_id')
        payment_method = data.get('payment_method', 'auto')
        
        # Busca contexto do usuário
        user_context = await _get_user_context(user_id)
        
        # Cria sessão de pagamento
        session = await payment_system.create_payment_session(product, user_context, payment_method)
        
        return jsonify(session), 200
        
    except Exception as e:
        logger.error(f"Erro ao criar sessão de pagamento: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/payments/webhook/stripe', methods=['POST'])
async def stripe_webhook():
    """Webhook do Stripe"""
    try:
        payload = request.get_json()
        result = await payment_system.process_webhook('stripe', payload)
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

# ================================
# WEBSOCKET PARA CHAT EM TEMPO REAL
# ================================

@socketio.on('connect')
def handle_connect():
    """Usuário conectou ao chat"""
    print(f'Usuário conectado: {request.sid}')
    emit('connected', {'message': 'Conectado ao sistema de IA'})

@socketio.on('disconnect')
def handle_disconnect():
    """Usuário desconectou do chat"""
    print(f'Usuário desconectado: {request.sid}')

@socketio.on('join_chat')
def handle_join_chat(data):
    """Usuário entrou no chat"""
    user_id = data.get('user_id')
    join_room(user_id)
    emit('joined_chat', {'message': f'Entrou no chat: {user_id}'})

@socketio.on('send_message')
async def handle_message(data):
    """Processa mensagem em tempo real"""
    try:
        user_id = data.get('user_id')
        message = data.get('message')
        agent_type = AgentType(data.get('agent_type', 'platform_concierge'))
        
        # Busca contexto do usuário
        user_context = await _get_user_context(user_id)
        
        # Processa mensagem
        response = await ai_system.process_message(user_context, message, agent_type)
        
        # Envia resposta em tempo real
        emit('ai_response', {
            'agent_type': response.agent_type.value,
            'message': response.message,
            'message_type': response.message_type.value,
            'metadata': response.metadata,
            'suggested_actions': response.suggested_actions,
            'products': response.products,
            'tools_integration': response.tools_integration,
            'timestamp': datetime.utcnow().isoformat()
        }, room=user_id)
        
    except Exception as e:
        logger.error(f"Erro no WebSocket: {str(e)}")
        emit('error', {'message': str(e)})

# ================================
# FUNÇÕES AUXILIARES
# ================================

async def _get_user_context(user_id: str) -> UserContext:
    """Busca contexto completo do usuário"""
    # Implementar busca real no banco de dados
    # Por enquanto, retorna contexto mock
    
    return UserContext(
        user_id=user_id,
        profile={
            'name': 'Usuário Teste',
            'age': 30,
            'country': 'BR',
            'currency': 'BRL',
            'email': 'usuario@teste.com',
            'fitness_goals': ['perder_peso', 'ganhar_musculo'],
            'activity_level': 'intermediate'
        },
        health_data={
            'imc': 25.5,
            'weight': 75.0,
            'height': 175.0
        },
        preferences={
            'language': 'pt-BR',
            'notifications': True,
            'ai_interactions': True
        },
        conversation_history=[],
        gamification_data={
            'level': 3,
            'hp': 1250,
            'badges': ['first_login', 'week_warrior'],
            'streak': 7,
            'active_challenges': []
        }
    )

# ================================
# INICIALIZAÇÃO
# ================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)

