import os
import sys
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from supabase import create_client, Client
import requests
import logging
from typing import Dict, Any, Optional

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da aplicação Flask
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-super-secret-key-change-in-production')

# Configuração CORS para permitir requisições do frontend
CORS(app, origins=['http://localhost:5174', 'http://localhost:3000'])

# Configuração Supabase
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'your-supabase-url')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'your-supabase-anon-key')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuração API USDA para dados nutricionais
USDA_API_KEY = os.environ.get('USDA_API_KEY', 'your-usda-api-key')
USDA_BASE_URL = 'https://api.nal.usda.gov/fdc/v1'

# ================================
# MIDDLEWARE E DECORADORES
# ================================

def token_required(f):
    """Decorator para rotas que requerem autenticação"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token de acesso requerido'}), 401
        
        try:
            # Remove 'Bearer ' do token
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decodifica o token JWT
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            
            # Verifica se o usuário existe no Supabase
            user_response = supabase.table('users').select('*').eq('id', current_user_id).execute()
            
            if not user_response.data:
                return jsonify({'error': 'Usuário não encontrado'}), 401
            
            request.current_user = user_response.data[0]
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        except Exception as e:
            logger.error(f"Erro na autenticação: {str(e)}")
            return jsonify({'error': 'Erro interno de autenticação'}), 500
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator para rotas que requerem privilégios de administrador"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, 'current_user') or request.current_user.get('role') != 'admin':
            return jsonify({'error': 'Acesso negado. Privilégios de administrador requeridos.'}), 403
        return f(*args, **kwargs)
    
    return decorated

# ================================
# UTILITÁRIOS
# ================================

def generate_token(user_id: str) -> str:
    """Gera token JWT para o usuário"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)  # Token válido por 7 dias
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def hash_password(password: str) -> str:
    """Gera hash da senha usando bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def log_user_activity(user_id: str, activity_type: str, details: Dict[str, Any] = None):
    """Registra atividade do usuário para analytics"""
    try:
        activity_data = {
            'user_id': user_id,
            'activity_type': activity_type,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')
        }
        
        supabase.table('user_activities').insert(activity_data).execute()
    except Exception as e:
        logger.error(f"Erro ao registrar atividade: {str(e)}")

# ================================
# ROTAS DE AUTENTICAÇÃO
# ================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Registro de novo usuário"""
    try:
        data = request.get_json()
        
        # Validação dos dados
        required_fields = ['email', 'password', 'name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        name = data['name'].strip()
        
        # Validações adicionais
        if len(password) < 8:
            return jsonify({'error': 'Senha deve ter pelo menos 8 caracteres'}), 400
        
        # Verifica se o usuário já existe
        existing_user = supabase.table('users').select('id').eq('email', email).execute()
        if existing_user.data:
            return jsonify({'error': 'Email já cadastrado'}), 409
        
        # Cria novo usuário
        user_data = {
            'email': email,
            'password_hash': hash_password(password),
            'name': name,
            'role': 'user',
            'is_active': True,
            'created_at': datetime.utcnow().isoformat(),
            'subscription_plan': 'free'
        }
        
        user_response = supabase.table('users').insert(user_data).execute()
        
        if not user_response.data:
            return jsonify({'error': 'Erro ao criar usuário'}), 500
        
        user = user_response.data[0]
        token = generate_token(user['id'])
        
        # Log da atividade
        log_user_activity(user['id'], 'user_registered')
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'role': user['role'],
                'subscription_plan': user['subscription_plan']
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Erro no registro: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login do usuário"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        # Busca o usuário
        user_response = supabase.table('users').select('*').eq('email', email).execute()
        
        if not user_response.data:
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        user = user_response.data[0]
        
        # Verifica se o usuário está ativo
        if not user.get('is_active', True):
            return jsonify({'error': 'Conta desativada'}), 401
        
        # Verifica a senha
        if not verify_password(password, user['password_hash']):
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        # Atualiza último login
        supabase.table('users').update({
            'last_login': datetime.utcnow().isoformat()
        }).eq('id', user['id']).execute()
        
        token = generate_token(user['id'])
        
        # Log da atividade
        log_user_activity(user['id'], 'user_login')
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'role': user['role'],
                'subscription_plan': user['subscription_plan']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# ================================
# ROTAS DE PERFIL DO USUÁRIO
# ================================

@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_profile():
    """Obtém perfil do usuário"""
    try:
        user = request.current_user
        
        # Busca dados adicionais do perfil
        profile_response = supabase.table('user_profiles').select('*').eq('user_id', user['id']).execute()
        profile = profile_response.data[0] if profile_response.data else {}
        
        return jsonify({
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'role': user['role'],
                'subscription_plan': user['subscription_plan'],
                'created_at': user['created_at'],
                'last_login': user.get('last_login')
            },
            'profile': profile
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar perfil: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/user/profile', methods=['PUT'])
@token_required
def update_profile():
    """Atualiza perfil do usuário"""
    try:
        data = request.get_json()
        user_id = request.current_user['id']
        
        # Campos permitidos para atualização
        allowed_fields = ['name', 'birth_date', 'gender', 'height', 'weight', 'activity_level', 'health_goals']
        
        # Atualiza dados do usuário
        user_updates = {}
        if 'name' in data:
            user_updates['name'] = data['name'].strip()
        
        if user_updates:
            supabase.table('users').update(user_updates).eq('id', user_id).execute()
        
        # Atualiza perfil estendido
        profile_updates = {k: v for k, v in data.items() if k in allowed_fields and k != 'name'}
        profile_updates['updated_at'] = datetime.utcnow().isoformat()
        
        # Verifica se já existe perfil
        existing_profile = supabase.table('user_profiles').select('id').eq('user_id', user_id).execute()
        
        if existing_profile.data:
            supabase.table('user_profiles').update(profile_updates).eq('user_id', user_id).execute()
        else:
            profile_updates['user_id'] = user_id
            profile_updates['created_at'] = datetime.utcnow().isoformat()
            supabase.table('user_profiles').insert(profile_updates).execute()
        
        # Log da atividade
        log_user_activity(user_id, 'profile_updated', {'fields': list(data.keys())})
        
        return jsonify({'message': 'Perfil atualizado com sucesso'}), 200
        
    except Exception as e:
        logger.error(f"Erro ao atualizar perfil: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# ================================
# ROTAS DE FERRAMENTAS DE SAÚDE
# ================================

@app.route('/api/tools/imc/calculate', methods=['POST'])
@token_required
def calculate_imc():
    """Calcula IMC e salva no histórico"""
    try:
        data = request.get_json()
        user_id = request.current_user['id']
        
        weight = float(data.get('weight', 0))
        height = float(data.get('height', 0))
        
        if weight <= 0 or height <= 0:
            return jsonify({'error': 'Peso e altura devem ser maiores que zero'}), 400
        
        # Calcula IMC
        height_m = height / 100  # Converte cm para metros
        imc = weight / (height_m ** 2)
        
        # Classifica IMC
        if imc < 18.5:
            classification = 'Abaixo do peso'
            risk = 'Baixo'
        elif imc < 25:
            classification = 'Peso normal'
            risk = 'Muito baixo'
        elif imc < 30:
            classification = 'Sobrepeso'
            risk = 'Baixo'
        elif imc < 35:
            classification = 'Obesidade grau I'
            risk = 'Moderado'
        elif imc < 40:
            classification = 'Obesidade grau II'
            risk = 'Alto'
        else:
            classification = 'Obesidade grau III'
            risk = 'Muito alto'
        
        # Salva no histórico
        imc_data = {
            'user_id': user_id,
            'weight': weight,
            'height': height,
            'imc_value': round(imc, 2),
            'classification': classification,
            'risk_level': risk,
            'calculated_at': datetime.utcnow().isoformat()
        }
        
        supabase.table('imc_history').insert(imc_data).execute()
        
        # Log da atividade
        log_user_activity(user_id, 'imc_calculated', {'imc': round(imc, 2)})
        
        return jsonify({
            'imc': round(imc, 2),
            'classification': classification,
            'risk_level': risk,
            'recommendations': get_imc_recommendations(imc)
        }), 200
        
    except ValueError:
        return jsonify({'error': 'Valores inválidos para peso ou altura'}), 400
    except Exception as e:
        logger.error(f"Erro ao calcular IMC: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

def get_imc_recommendations(imc: float) -> list:
    """Retorna recomendações baseadas no IMC"""
    if imc < 18.5:
        return [
            "Consulte um nutricionista para ganho de peso saudável",
            "Inclua mais proteínas e carboidratos complexos na dieta",
            "Pratique exercícios de fortalecimento muscular"
        ]
    elif imc < 25:
        return [
            "Mantenha uma alimentação equilibrada",
            "Continue praticando exercícios regulares",
            "Monitore seu peso periodicamente"
        ]
    elif imc < 30:
        return [
            "Reduza o consumo de açúcares e gorduras saturadas",
            "Aumente a prática de exercícios aeróbicos",
            "Considere acompanhamento nutricional"
        ]
    else:
        return [
            "Procure orientação médica especializada",
            "Implemente mudanças graduais na alimentação",
            "Inicie atividade física com supervisão profissional"
        ]

@app.route('/api/tools/imc/history', methods=['GET'])
@token_required
def get_imc_history():
    """Obtém histórico de IMC do usuário"""
    try:
        user_id = request.current_user['id']
        
        history_response = supabase.table('imc_history').select('*').eq('user_id', user_id).order('calculated_at', desc=True).limit(50).execute()
        
        return jsonify({'history': history_response.data}), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico IMC: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# ================================
# ROTAS DE ALIMENTOS E NUTRIÇÃO
# ================================

@app.route('/api/nutrition/search', methods=['GET'])
@token_required
def search_foods():
    """Busca alimentos na API USDA"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'error': 'Termo de busca é obrigatório'}), 400
        
        # Busca na API USDA
        url = f"{USDA_BASE_URL}/foods/search"
        params = {
            'api_key': USDA_API_KEY,
            'query': query,
            'pageSize': 20,
            'dataType': ['Foundation', 'SR Legacy']
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return jsonify({'error': 'Erro ao buscar alimentos'}), 500
        
        data = response.json()
        
        # Processa os resultados
        foods = []
        for food in data.get('foods', []):
            foods.append({
                'fdc_id': food.get('fdcId'),
                'description': food.get('description'),
                'brand_owner': food.get('brandOwner'),
                'ingredients': food.get('ingredients'),
                'nutrients': process_nutrients(food.get('foodNutrients', []))
            })
        
        # Log da atividade
        log_user_activity(request.current_user['id'], 'food_search', {'query': query})
        
        return jsonify({'foods': foods}), 200
        
    except Exception as e:
        logger.error(f"Erro na busca de alimentos: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

def process_nutrients(nutrients: list) -> dict:
    """Processa nutrientes do USDA para formato padronizado"""
    processed = {}
    
    nutrient_map = {
        'Energy': 'calories',
        'Protein': 'protein',
        'Total lipid (fat)': 'fat',
        'Carbohydrate, by difference': 'carbohydrates',
        'Fiber, total dietary': 'fiber',
        'Sugars, total including NLEA': 'sugars',
        'Sodium, Na': 'sodium',
        'Calcium, Ca': 'calcium',
        'Iron, Fe': 'iron',
        'Vitamin C, total ascorbic acid': 'vitamin_c'
    }
    
    for nutrient in nutrients:
        name = nutrient.get('nutrientName', '')
        if name in nutrient_map:
            processed[nutrient_map[name]] = {
                'value': nutrient.get('value', 0),
                'unit': nutrient.get('unitName', '')
            }
    
    return processed

@app.route('/api/nutrition/food/<int:fdc_id>', methods=['GET'])
@token_required
def get_food_details(fdc_id):
    """Obtém detalhes completos de um alimento"""
    try:
        url = f"{USDA_BASE_URL}/food/{fdc_id}"
        params = {'api_key': USDA_API_KEY}
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return jsonify({'error': 'Alimento não encontrado'}), 404
        
        data = response.json()
        
        food_details = {
            'fdc_id': data.get('fdcId'),
            'description': data.get('description'),
            'brand_owner': data.get('brandOwner'),
            'ingredients': data.get('ingredients'),
            'nutrients': process_nutrients(data.get('foodNutrients', [])),
            'portions': data.get('foodPortions', [])
        }
        
        return jsonify({'food': food_details}), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar detalhes do alimento: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# ================================
# ROTAS DE CALENDÁRIO ALIMENTAR
# ================================

@app.route('/api/food-diary/entries', methods=['POST'])
@token_required
def add_food_entry():
    """Adiciona entrada no diário alimentar"""
    try:
        data = request.get_json()
        user_id = request.current_user['id']
        
        required_fields = ['fdc_id', 'description', 'quantity', 'unit', 'meal_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        entry_data = {
            'user_id': user_id,
            'fdc_id': data['fdc_id'],
            'description': data['description'],
            'quantity': float(data['quantity']),
            'unit': data['unit'],
            'meal_type': data['meal_type'],
            'nutrients': data.get('nutrients', {}),
            'consumed_at': data.get('consumed_at', datetime.utcnow().isoformat()),
            'created_at': datetime.utcnow().isoformat()
        }
        
        supabase.table('food_diary_entries').insert(entry_data).execute()
        
        # Log da atividade
        log_user_activity(user_id, 'food_entry_added', {
            'meal_type': data['meal_type'],
            'food': data['description']
        })
        
        return jsonify({'message': 'Entrada adicionada com sucesso'}), 201
        
    except ValueError:
        return jsonify({'error': 'Quantidade deve ser um número válido'}), 400
    except Exception as e:
        logger.error(f"Erro ao adicionar entrada: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/food-diary/entries', methods=['GET'])
@token_required
def get_food_entries():
    """Obtém entradas do diário alimentar"""
    try:
        user_id = request.current_user['id']
        date = request.args.get('date', datetime.utcnow().date().isoformat())
        
        # Busca entradas do dia
        entries_response = supabase.table('food_diary_entries').select('*').eq('user_id', user_id).gte('consumed_at', f"{date}T00:00:00").lt('consumed_at', f"{date}T23:59:59").order('consumed_at').execute()
        
        # Agrupa por tipo de refeição
        meals = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snacks': []
        }
        
        total_nutrients = {
            'calories': 0,
            'protein': 0,
            'carbohydrates': 0,
            'fat': 0,
            'fiber': 0
        }
        
        for entry in entries_response.data:
            meal_type = entry['meal_type']
            if meal_type in meals:
                meals[meal_type].append(entry)
                
                # Soma nutrientes
                nutrients = entry.get('nutrients', {})
                for nutrient in total_nutrients:
                    if nutrient in nutrients:
                        total_nutrients[nutrient] += nutrients[nutrient].get('value', 0) * entry['quantity']
        
        return jsonify({
            'date': date,
            'meals': meals,
            'total_nutrients': total_nutrients
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar entradas: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# ================================
# ROTAS ADMINISTRATIVAS
# ================================

@app.route('/api/admin/users', methods=['GET'])
@token_required
@admin_required
def get_all_users():
    """Lista todos os usuários (admin only)"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        offset = (page - 1) * per_page
        
        users_response = supabase.table('users').select('id, email, name, role, subscription_plan, is_active, created_at, last_login').range(offset, offset + per_page - 1).execute()
        
        return jsonify({
            'users': users_response.data,
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/admin/analytics', methods=['GET'])
@token_required
@admin_required
def get_analytics():
    """Obtém dados de analytics (admin only)"""
    try:
        # Contadores básicos
        users_count = supabase.table('users').select('id', count='exact').execute()
        active_users = supabase.table('users').select('id', count='exact').eq('is_active', True).execute()
        
        # Atividades recentes
        recent_activities = supabase.table('user_activities').select('*').order('timestamp', desc=True).limit(100).execute()
        
        # Estatísticas por tipo de atividade
        activity_stats = {}
        for activity in recent_activities.data:
            activity_type = activity['activity_type']
            activity_stats[activity_type] = activity_stats.get(activity_type, 0) + 1
        
        return jsonify({
            'total_users': users_count.count,
            'active_users': active_users.count,
            'activity_stats': activity_stats,
            'recent_activities': recent_activities.data[:20]
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar analytics: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# ================================
# ROTAS DE SAÚDE E STATUS
# ================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica saúde da API"""
    try:
        # Testa conexão com Supabase
        supabase.table('users').select('id').limit(1).execute()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.0'
        }), 200
        
    except Exception as e:
        logger.error(f"Health check falhou: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# ================================
# ROTAS DE ARQUIVOS ESTÁTICOS
# ================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    """Serve arquivos estáticos"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({'message': 'RE-EDUCA Store API v2.0.0'}), 200

# ================================
# TRATAMENTO DE ERROS
# ================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erro interno: {str(error)}")
    return jsonify({'error': 'Erro interno do servidor'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Requisição inválida'}), 400

# ================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Iniciando RE-EDUCA Store API v2.0.0 na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

