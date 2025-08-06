"""
Middleware CORS para RE-EDUCA Store
"""
from flask import Flask
from flask_cors import CORS

def setup_cors(app: Flask):
    """Configura CORS para a aplicação"""
    
    # Configuração CORS
    CORS(app, 
         origins=app.config.get('CORS_ORIGINS', ['http://localhost:5174', 'http://localhost:3000']),
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         supports_credentials=True,
         max_age=3600)
    
    # Headers de segurança adicionais
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response