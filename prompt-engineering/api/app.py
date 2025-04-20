from flask import Flask
from flask_cors import CORS
from routes.generate import generate_bp
from routes.tokens import tokens_bp
from config import DEBUG, HOST, PORT, TEMPLATES_AUTO_RELOAD, SEND_FILE_MAX_AGE_DEFAULT, CORS_ORIGINS

def create_app():
    app = Flask(__name__)
    
    # Configuración de la aplicación
    app.config['DEBUG'] = DEBUG
    app.config['TEMPLATES_AUTO_RELOAD'] = TEMPLATES_AUTO_RELOAD
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = SEND_FILE_MAX_AGE_DEFAULT
    
    # Configuración de CORS
    CORS(app, resources={r"/*": {"origins": CORS_ORIGINS}})
    
    # Registro de blueprints
    app.register_blueprint(generate_bp)
    app.register_blueprint(tokens_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=DEBUG, host=HOST, port=PORT, use_reloader=True, extra_files=None)