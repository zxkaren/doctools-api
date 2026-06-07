from flask import Flask
from flasgger import Swagger

from app.config import Config
from app.core.exceptions import register_error_handlers
from app.features.compare import compare_blueprint


SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "DocTools API",
        "description": "API para ferramentas de documentos criada por zxkaren",
        "version": "1.0.0",
        "contact": {
            "name": "zxkaren",
        },
    },
    "tags": [
        {
            "name": "Compare",
            "description": "Funcionalidade para comparação de documentos",
        },
    ],
}

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/",
}


def create_app() -> Flask:
    """
    Resumo:
        Cria e configura a aplicação Flask.

    Parâmetros:
        Nenhum.

    Retorno:
        Flask: aplicação configurada com Swagger, blueprints e tratamento de erros.
    """
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    Swagger(flask_app, template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)

    flask_app.register_blueprint(compare_blueprint, url_prefix="/compare")
    register_error_handlers(flask_app)

    return flask_app