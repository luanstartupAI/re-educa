"""
Rotas de ferramentas de saúde RE-EDUCA Store
"""
from flask import Blueprint, request, jsonify
from services.health_service import HealthService
from utils.decorators import token_required, log_activity, rate_limit, premium_required
from utils.validators import health_data_validator
from utils.helpers import calculate_imc, calculate_calories, calculate_macros
from middleware.logging import log_user_activity
import requests

health_tools_bp = Blueprint('health_tools', __name__)
health_service = HealthService()

@health_tools_bp.route('/imc/calculate', methods=['POST'])
@token_required
@rate_limit("20 per hour")
@log_activity('imc_calculation')
def calculate_imc_route():
    """Calcula IMC do usuário"""
    try:
        data = request.get_json()
        user_id = request.current_user['id']
        
        # Valida dados
        if not health_data_validator.validate_imc_data(data):
            return jsonify({
                'error': 'Dados inválidos',
                'details': health_data_validator.get_errors()
            }), 400
        
        # Calcula IMC
        result = calculate_imc(data['weight'], data['height'])
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        # Salva cálculo no banco
        health_service.save_imc_calculation(user_id, result)
        
        log_user_activity(user_id, 'imc_calculated', {
            'weight': data['weight'],
            'height': data['height'],
            'imc': result['imc']
        })
        
        return jsonify({
            'imc': result['imc'],
            'classification': result['classification'],
            'color': result['color'],
            'recommendations': result['recommendations'],
            'weight_range': result['weight_range']
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@health_tools_bp.route('/imc/history', methods=['GET'])
@token_required
def get_imc_history():
    """Retorna histórico de cálculos de IMC"""
    try:
        user_id = request.current_user['id']
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        history = health_service.get_imc_history(user_id, page, per_page)
        
        return jsonify(history), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@health_tools_bp.route('/calories/calculate', methods=['POST'])
@token_required
@rate_limit("10 per hour")
@log_activity('calories_calculation')
def calculate_calories_route():
    """Calcula necessidade calórica"""
    try:
        data = request.get_json()
        user_id = request.current_user['id']
        
        required_fields = ['age', 'weight', 'height', 'gender', 'activity_level']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Calcula calorias
        result = calculate_calories(
            data['age'],
            data['weight'],
            data['height'],
            data['gender'],
            data['activity_level']
        )
        
        # Calcula macronutrientes
        macros = calculate_macros(result['daily_calories'])
        
        log_user_activity(user_id, 'calories_calculated', {
            'age': data['age'],
            'weight': data['weight'],
            'height': data['height'],
            'daily_calories': result['daily_calories']
        })
        
        return jsonify({
            'bmr': result['bmr'],
            'daily_calories': result['daily_calories'],
            'activity_multiplier': result['activity_multiplier'],
            'macros': macros
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@health_tools_bp.route('/nutrition/search', methods=['GET'])
@token_required
@rate_limit("50 per hour")
def search_foods():
    """Busca alimentos na API USDA"""
    try:
        query = request.args.get('query', '')
        if not query:
            return jsonify({'error': 'Query é obrigatória'}), 400
        
        # Busca na API USDA
        foods = health_service.search_foods(query)
        
        return jsonify({
            'foods': foods,
            'query': query
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@health_tools_bp.route('/nutrition/food/<int:fdc_id>', methods=['GET'])
@token_required
@rate_limit("100 per hour")
def get_food_details(fdc_id):
    """Retorna detalhes nutricionais de um alimento"""
    try:
        food_details = health_service.get_food_details(fdc_id)
        
        if not food_details:
            return jsonify({'error': 'Alimento não encontrado'}), 404
        
        return jsonify(food_details), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@health_tools_bp.route('/food-diary/entries', methods=['POST'])
@token_required
@rate_limit("100 per hour")
@log_activity('food_entry_added')
def add_food_entry():
    """Adiciona entrada no diário alimentar"""
    try:
        data = request.get_json()
        user_id = request.current_user['id']
        
        # Valida dados
        if not health_data_validator.validate_food_entry(data):
            return jsonify({
                'error': 'Dados inválidos',
                'details': health_data_validator.get_errors()
            }), 400
        
        # Adiciona entrada
        result = health_service.add_food_entry(user_id, data)
        
        if result.get('success'):
            log_user_activity(user_id, 'food_entry_added', {
                'food_name': data['food_name'],
                'quantity': data['quantity']
            })
            
            return jsonify({
                'message': 'Entrada adicionada com sucesso',
                'entry': result['entry']
            }), 201
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@health_tools_bp.route('/food-diary/entries', methods=['GET'])
@token_required
def get_food_entries():
    """Retorna entradas do diário alimentar"""
    try:
        user_id = request.current_user['id']
        date = request.args.get('date')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        entries = health_service.get_food_entries(user_id, date, page, per_page)
        
        return jsonify(entries), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@health_tools_bp.route('/exercise/entries', methods=['POST'])
@token_required
@rate_limit("50 per hour")
@log_activity('exercise_entry_added')
def add_exercise_entry():
    """Adiciona entrada de exercício"""
    try:
        data = request.get_json()
        user_id = request.current_user['id']
        
        # Valida dados
        if not health_data_validator.validate_exercise_entry(data):
            return jsonify({
                'error': 'Dados inválidos',
                'details': health_data_validator.get_errors()
            }), 400
        
        # Adiciona entrada
        result = health_service.add_exercise_entry(user_id, data)
        
        if result.get('success'):
            log_user_activity(user_id, 'exercise_entry_added', {
                'exercise_name': data['exercise_name'],
                'duration': data['duration']
            })
            
            return jsonify({
                'message': 'Exercício adicionado com sucesso',
                'entry': result['entry']
            }), 201
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@health_tools_bp.route('/exercise/entries', methods=['GET'])
@token_required
def get_exercise_entries():
    """Retorna entradas de exercícios"""
    try:
        user_id = request.current_user['id']
        date = request.args.get('date')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        entries = health_service.get_exercise_entries(user_id, date, page, per_page)
        
        return jsonify(entries), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@health_tools_bp.route('/analytics/summary', methods=['GET'])
@token_required
@premium_required
def get_health_analytics():
    """Retorna resumo de analytics de saúde"""
    try:
        user_id = request.current_user['id']
        period = request.args.get('period', '30')  # dias
        
        analytics = health_service.get_health_analytics(user_id, int(period))
        
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@health_tools_bp.route('/goals', methods=['GET'])
@token_required
def get_health_goals():
    """Retorna metas de saúde do usuário"""
    try:
        user_id = request.current_user['id']
        goals = health_service.get_health_goals(user_id)
        
        return jsonify({'goals': goals}), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@health_tools_bp.route('/goals', methods=['POST'])
@token_required
@log_activity('goal_created')
def create_health_goal():
    """Cria nova meta de saúde"""
    try:
        data = request.get_json()
        user_id = request.current_user['id']
        
        result = health_service.create_health_goal(user_id, data)
        
        if result.get('success'):
            log_user_activity(user_id, 'goal_created', {
                'goal_type': data.get('type'),
                'target_value': data.get('target_value')
            })
            
            return jsonify({
                'message': 'Meta criada com sucesso',
                'goal': result['goal']
            }), 201
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500