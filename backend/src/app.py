"""
Aplicação principal RE-EDUCA Store
"""
import os
import logging
from flask import Flask
from flask_cors import CORS
from config.settings import get_config
from config.database import test_db_connection
from middleware.cors import setup_cors
from middleware.logging import setup_logging
from middleware.rate_limit import setup_rate_limiting

def create_app(config_name=None):
    """Factory function para criar a aplicação Flask"""
    
    # Cria a aplicação Flask
    app = Flask(__name__, static_folder='static')
    
    # Carrega configurações
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Configura logging
    setup_logging(app)
    logger = logging.getLogger(__name__)
    
    # Configura CORS
    setup_cors(app)
    
    # Configura rate limiting
    setup_rate_limiting(app)
    
    # Testa conexão com banco de dados
    if not test_db_connection():
        logger.warning("Conexão com banco de dados falhou")
    
    # Registra blueprints
    register_blueprints(app)
    
    # Registra handlers de erro
    register_error_handlers(app)
    
    logger.info("Aplicação RE-EDUCA Store inicializada com sucesso")
    
    return app

def register_blueprints(app):
    """Registra os blueprints da aplicação"""
    from routes.auth import auth_bp
    from routes.users import users_bp
    from routes.products import products_bp
    from routes.orders import orders_bp
    from routes.health_tools import health_tools_bp
    from routes.admin import admin_bp
    from routes.payments import payments_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(health_tools_bp, url_prefix='/api/health')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')

def register_error_handlers(app):
    """Registra handlers de erro"""
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Recurso não encontrado'}, 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return {'error': 'Método não permitido'}, 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Erro interno do servidor'}, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Requisição inválida'}, 400

def main():
    """Função principal para executar a aplicação"""
    app = create_app()
    
    # Configurações de desenvolvimento
    debug = app.config.get('DEBUG', False)
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🚀 RE-EDUCA Store iniciando...")
    print(f"📍 Host: {host}")
    print(f"🔌 Porta: {port}")
    print(f"🐛 Debug: {debug}")
    print(f"🌐 Ambiente: {os.environ.get('FLASK_ENV', 'development')}")
    
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()