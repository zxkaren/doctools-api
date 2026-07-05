from flask import Flask
from flasgger import Swagger

from app.config import Config
from app.core.exceptions import register_error_handlers
from app.features.compare import compare_blueprint
from app.features.extract_text import extract_text_blueprint


def load_project_version() -> str:
    version_file_path = Config.PROJECT_ROOT / "VERSION"

    if not version_file_path.exists():
        return "0.0.0"

    project_version = version_file_path.read_text(encoding="utf-8").strip()

    return project_version or "0.0.0"


def include_all_swagger_items(swagger_item: object) -> bool:
    # O Flasgger exige um callable com parâmetro, mas aqui queremos documentar tudo.
    return isinstance(swagger_item, object)


SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "DocTools API",
        "description": "API para ferramentas de documentos criada por zxkaren",
        "version": load_project_version(),
        "contact": {
            "name": "zxkaren",
        },
    },
    "tags": [
        {
            "name": "Compare",
            "description": "Funcionalidade para comparação de documentos",
        },
        {
            "name": "Extração de Texto",
            "description": "Funcionalidade para extração de texto limpo de documentos",
        },
    ],
}


SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": include_all_swagger_items,
            "model_filter": include_all_swagger_items,
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
    flask_app.register_blueprint(extract_text_blueprint, url_prefix="/extract-text")

    register_error_handlers(flask_app)

    return flask_app