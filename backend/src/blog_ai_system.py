"""
🤖 Blog Inteligente Backend - RE-EDUCA Store v2.0.0
Sistema de geração de conteúdo com IA usando Google Gemini e Perplexity AI
"""

import os
import json
import requests
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dataclasses import dataclass
import logging

# ================================
# CONFIGURAÇÃO
# ================================

# Configurar APIs
GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY', 'AIzaSyDUS4HxE4WTN7QZGWBtq_GRrRtcCZIVjhQ')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY', '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')
INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')

# Configurar Gemini
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================
# MODELOS DE DADOS
# ================================

@dataclass
class BlogPost:
    id: str
    title: str
    excerpt: str
    content: str
    category: str
    tags: List[str]
    author: Dict[str, str]
    published_at: str
    read_time: int
    ai_generated: bool
    instagram_source: Optional[str] = None
    image_url: Optional[str] = None
    views: int = 0
    likes: int = 0
    comments: int = 0

@dataclass
class ContentRequest:
    topic: str
    category: str
    target_audience: str
    tone: str
    length: str
    include_instagram: bool = True

# ================================
# SISTEMA DE IA PARA BLOG
# ================================

class IntelligentBlogSystem:
    def __init__(self):
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
        self.instagram_posts_cache = []
        
    async def generate_blog_post(self, content_request: ContentRequest) -> BlogPost:
        """Gera um post de blog completo usando IA"""
        try:
            # 1. Pesquisar tendências com Perplexity AI
            trends_data = await self._research_trends(content_request.topic)
            
            # 2. Buscar conteúdo do Instagram relacionado
            instagram_data = await self._fetch_instagram_content(content_request.topic)
            
            # 3. Gerar conteúdo com Google Gemini
            blog_content = await self._generate_content_with_gemini(
                content_request, trends_data, instagram_data
            )
            
            # 4. Criar post estruturado
            post = BlogPost(
                id=f"ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title=blog_content['title'],
                excerpt=blog_content['excerpt'],
                content=blog_content['content'],
                category=content_request.category,
                tags=blog_content['tags'],
                author={
                    'name': 'IA Assistant RE-EDUCA',
                    'avatar': '/api/placeholder/40/40',
                    'bio': 'Assistente de IA especializado em saúde e bem-estar'
                },
                published_at=datetime.now().isoformat(),
                read_time=self._calculate_read_time(blog_content['content']),
                ai_generated=True,
                instagram_source=instagram_data.get('source', 'Múltiplas fontes'),
                image_url=blog_content.get('image_url', '/api/placeholder/600/300')
            )
            
            logger.info(f"Post gerado com sucesso: {post.title}")
            return post
            
        except Exception as e:
            logger.error(f"Erro ao gerar post: {str(e)}")
            raise

    async def _research_trends(self, topic: str) -> Dict:
        """Pesquisa tendências usando Perplexity AI"""
        try:
            headers = {
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""
            Pesquise as últimas tendências, estudos científicos e novidades sobre {topic} 
            na área de saúde e bem-estar. Foque em:
            - Descobertas científicas recentes
            - Tendências populares nas redes sociais
            - Recomendações de especialistas
            - Dados estatísticos relevantes
            
            Forneça informações atualizadas e confiáveis.
            """
            
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "Você é um pesquisador especializado em saúde e bem-estar. Forneça informações precisas e atualizadas."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.3
            }
            
            response = requests.post(self.perplexity_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'trends': result['choices'][0]['message']['content'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.warning(f"Erro na API Perplexity: {response.status_code}")
                return {'trends': 'Dados de tendências não disponíveis', 'timestamp': datetime.now().isoformat()}
                
        except Exception as e:
            logger.error(f"Erro ao pesquisar tendências: {str(e)}")
            return {'trends': 'Erro ao buscar tendências', 'timestamp': datetime.now().isoformat()}

    async def _fetch_instagram_content(self, topic: str) -> Dict:
        """Busca conteúdo relacionado do Instagram"""
        try:
            # Simular busca no Instagram (em produção usaria a API real)
            # Por enquanto, retorna dados simulados baseados no tópico
            
            instagram_insights = {
                'nutrição': {
                    'hashtags': ['#alimentacaosaudavel', '#nutricao', '#superalimentos'],
                    'influencers': ['@dra.ana.nutricao', '@nutri.funcional', '@alimentacao.consciente'],
                    'trending_content': 'Jejum intermitente e alimentos anti-inflamatórios'
                },
                'fitness': {
                    'hashtags': ['#treino', '#fitness', '#hiit'],
                    'influencers': ['@coach.marcus.fit', '@treino.funcional', '@fitness.brasil'],
                    'trending_content': 'Treinos funcionais e HIIT para queima de gordura'
                },
                'bem-estar': {
                    'hashtags': ['#bemestar', '#mindfulness', '#saudemental'],
                    'influencers': ['@mestre.zen.silva', '@mindfulness.br', '@equilibrio.mental'],
                    'trending_content': 'Meditação e técnicas de respiração para ansiedade'
                }
            }
            
            # Determinar categoria baseada no tópico
            category_key = 'bem-estar'  # default
            if any(word in topic.lower() for word in ['nutrição', 'alimentação', 'dieta', 'comida']):
                category_key = 'nutrição'
            elif any(word in topic.lower() for word in ['treino', 'exercício', 'fitness', 'musculação']):
                category_key = 'fitness'
            
            return {
                'source': instagram_insights[category_key]['influencers'][0],
                'hashtags': instagram_insights[category_key]['hashtags'],
                'trending': instagram_insights[category_key]['trending_content'],
                'engagement_data': {
                    'avg_likes': 1250,
                    'avg_comments': 89,
                    'reach': 15000
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar conteúdo Instagram: {str(e)}")
            return {'source': 'Instagram', 'hashtags': [], 'trending': ''}

    async def _generate_content_with_gemini(self, request: ContentRequest, trends: Dict, instagram: Dict) -> Dict:
        """Gera conteúdo usando Google Gemini"""
        try:
            prompt = f"""
            Crie um artigo de blog completo sobre {request.topic} para o público {request.target_audience}.
            
            CONTEXTO E DADOS:
            - Categoria: {request.category}
            - Tom: {request.tone}
            - Tamanho: {request.length}
            - Tendências atuais: {trends.get('trends', '')}
            - Insights do Instagram: {instagram.get('trending', '')}
            - Hashtags populares: {', '.join(instagram.get('hashtags', []))}
            
            ESTRUTURA REQUERIDA:
            1. Título atrativo e otimizado para SEO
            2. Resumo/excerpt de 2-3 frases
            3. Conteúdo completo em HTML com:
               - Introdução envolvente
               - Seções bem estruturadas com subtítulos
               - Listas e bullet points quando apropriado
               - Dados científicos e estatísticas
               - Dicas práticas e acionáveis
               - Conclusão inspiradora
            4. 5-8 tags relevantes
            
            DIRETRIZES:
            - Use linguagem clara e acessível
            - Inclua dados científicos quando relevante
            - Mantenha o tom {request.tone}
            - Foque em valor prático para o leitor
            - Otimize para SEO sem comprometer a qualidade
            - Inclua call-to-actions sutis
            
            FORMATO DE RESPOSTA (JSON):
            {{
                "title": "Título do artigo",
                "excerpt": "Resumo atrativo do artigo",
                "content": "Conteúdo completo em HTML",
                "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
                "seo_keywords": ["palavra1", "palavra2", "palavra3"],
                "estimated_read_time": 8
            }}
            """
            
            response = self.gemini_model.generate_content(prompt)
            
            # Processar resposta
            content_text = response.text
            
            # Tentar extrair JSON da resposta
            try:
                # Remover markdown code blocks se existirem
                if '```json' in content_text:
                    content_text = content_text.split('```json')[1].split('```')[0]
                elif '```' in content_text:
                    content_text = content_text.split('```')[1].split('```')[0]
                
                content_data = json.loads(content_text.strip())
                
                # Validar e completar dados
                if 'title' not in content_data:
                    content_data['title'] = f"Guia Completo: {request.topic}"
                if 'excerpt' not in content_data:
                    content_data['excerpt'] = f"Descubra tudo sobre {request.topic} e transforme sua saúde."
                if 'tags' not in content_data:
                    content_data['tags'] = [request.topic.lower(), request.category.lower(), 'saúde', 'bem-estar']
                
                return content_data
                
            except json.JSONDecodeError:
                # Fallback: criar estrutura manualmente
                logger.warning("Erro ao parsear JSON do Gemini, usando fallback")
                return self._create_fallback_content(request, content_text)
                
        except Exception as e:
            logger.error(f"Erro ao gerar conteúdo com Gemini: {str(e)}")
            return self._create_fallback_content(request, "")

    def _create_fallback_content(self, request: ContentRequest, raw_content: str) -> Dict:
        """Cria conteúdo de fallback quando a IA falha"""
        return {
            'title': f"Guia Completo: {request.topic}",
            'excerpt': f"Descubra as melhores práticas e dicas sobre {request.topic} para transformar sua saúde e bem-estar.",
            'content': f"""
                <h2>Introdução</h2>
                <p>Bem-vindo ao nosso guia completo sobre {request.topic}. Este artigo foi criado especialmente para {request.target_audience} que desejam melhorar sua qualidade de vida.</p>
                
                <h2>O que você vai aprender</h2>
                <ul>
                    <li>Fundamentos essenciais sobre {request.topic}</li>
                    <li>Dicas práticas para implementar no dia a dia</li>
                    <li>Benefícios científicamente comprovados</li>
                    <li>Erros comuns a evitar</li>
                </ul>
                
                <h2>Conteúdo Principal</h2>
                <p>{raw_content if raw_content else f'Conteúdo detalhado sobre {request.topic} será desenvolvido com base nas suas necessidades específicas.'}</p>
                
                <h2>Conclusão</h2>
                <p>Implementar essas práticas em sua rotina pode trazer benefícios significativos para sua saúde e bem-estar. Comece gradualmente e seja consistente.</p>
            """,
            'tags': [request.topic.lower(), request.category.lower(), 'saúde', 'bem-estar', 'dicas'],
            'seo_keywords': [request.topic, 'saúde', 'bem-estar'],
            'estimated_read_time': 5
        }

    def _calculate_read_time(self, content: str) -> int:
        """Calcula tempo estimado de leitura"""
        # Remove HTML tags para contar palavras
        import re
        text = re.sub('<[^<]+?>', '', content)
        word_count = len(text.split())
        # Média de 200 palavras por minuto
        return max(1, round(word_count / 200))

    async def get_trending_topics(self) -> List[Dict]:
        """Busca tópicos em alta"""
        try:
            # Simular busca de trending topics
            trending = [
                {
                    'topic': 'Jejum Intermitente',
                    'category': 'Nutrição',
                    'growth': '+45%',
                    'hashtag': '#jejumintermitente'
                },
                {
                    'topic': 'Treino HIIT',
                    'category': 'Fitness',
                    'growth': '+32%',
                    'hashtag': '#hiit'
                },
                {
                    'topic': 'Mindfulness',
                    'category': 'Bem-estar Mental',
                    'growth': '+28%',
                    'hashtag': '#mindfulness'
                },
                {
                    'topic': 'Suplementação Natural',
                    'category': 'Nutrição',
                    'growth': '+25%',
                    'hashtag': '#suplementos'
                },
                {
                    'topic': 'Sono Reparador',
                    'category': 'Bem-estar',
                    'growth': '+22%',
                    'hashtag': '#sono'
                }
            ]
            
            return trending
            
        except Exception as e:
            logger.error(f"Erro ao buscar trending topics: {str(e)}")
            return []

    async def analyze_instagram_engagement(self, hashtag: str) -> Dict:
        """Analisa engajamento de hashtags no Instagram"""
        try:
            # Simular análise de engajamento
            return {
                'hashtag': hashtag,
                'total_posts': 125000,
                'avg_likes': 1250,
                'avg_comments': 89,
                'engagement_rate': 4.2,
                'top_influencers': [
                    '@influencer1',
                    '@influencer2',
                    '@influencer3'
                ],
                'trending_content_types': [
                    'Receitas saudáveis',
                    'Dicas de treino',
                    'Transformações'
                ]
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar engajamento: {str(e)}")
            return {}

# ================================
# API ENDPOINTS
# ================================

app = Flask(__name__)
CORS(app)

blog_system = IntelligentBlogSystem()

@app.route('/api/blog/generate', methods=['POST'])
async def generate_blog_post():
    """Endpoint para gerar novo post de blog"""
    try:
        data = request.get_json()
        
        content_request = ContentRequest(
            topic=data.get('topic', 'Saúde e Bem-estar'),
            category=data.get('category', 'Geral'),
            target_audience=data.get('target_audience', 'pessoas interessadas em saúde'),
            tone=data.get('tone', 'informativo e amigável'),
            length=data.get('length', 'médio'),
            include_instagram=data.get('include_instagram', True)
        )
        
        post = await blog_system.generate_blog_post(content_request)
        
        return jsonify({
            'success': True,
            'post': {
                'id': post.id,
                'title': post.title,
                'excerpt': post.excerpt,
                'content': post.content,
                'category': post.category,
                'tags': post.tags,
                'author': post.author,
                'published_at': post.published_at,
                'read_time': post.read_time,
                'ai_generated': post.ai_generated,
                'instagram_source': post.instagram_source,
                'image_url': post.image_url
            }
        })
        
    except Exception as e:
        logger.error(f"Erro no endpoint generate: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/blog/trending', methods=['GET'])
async def get_trending_topics():
    """Endpoint para buscar tópicos em alta"""
    try:
        topics = await blog_system.get_trending_topics()
        return jsonify({
            'success': True,
            'trending_topics': topics
        })
        
    except Exception as e:
        logger.error(f"Erro no endpoint trending: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/blog/instagram/analyze', methods=['POST'])
async def analyze_instagram():
    """Endpoint para analisar engajamento no Instagram"""
    try:
        data = request.get_json()
        hashtag = data.get('hashtag', '#saude')
        
        analysis = await blog_system.analyze_instagram_engagement(hashtag)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Erro no endpoint analyze_instagram: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/blog/health', methods=['GET'])
def health_check():
    """Health check do sistema"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'gemini_api': bool(GOOGLE_GEMINI_API_KEY),
            'perplexity_api': bool(PERPLEXITY_API_KEY),
            'instagram_api': bool(INSTAGRAM_ACCESS_TOKEN)
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

