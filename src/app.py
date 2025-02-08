from logging.config import dictConfig

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from backend.api.exeptions import register_exception_handlers
from backend.api.task import register_task_api
from backend.api.user import register_user_api
from backend.auth.authenticator import JwtAuthenticator
from backend.model.app_managed_tables import create_app_managed_tables
from backend.viewdata.task import ViewTask
from backend.viewdata.user import ViewUser
from settings import AppSettings
from utils.jwt_token import JWTUtils


def create_app(config: AppSettings) -> FastAPI:

    # Setting up logger absed on the configuration
    dictConfig(config.logging)

    db_connection = config.db.create()
    authenticator = JwtAuthenticator(config.jwt.secret_key, db_connection)
    jwt_utils = JWTUtils(config.jwt.secret_key, config.jwt.algorithm)

    # Creating all tables if they do not exist
    create_app_managed_tables(db_connection)

    task_view = ViewTask(db_connection)
    user_view = ViewUser(db_connection, jwt_utils, config.jwt.token_expire_mins)

    app = FastAPI()

    register_user_api(app, user_view)
    register_task_api(app, task_view, authenticator)

    register_exception_handlers(app)

    if config.debug:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    return app


def main():
    config = AppSettings.get_config()
    app = create_app(config)
    uvicorn.run(
        app,
        host=config.webserver.host,
        port=config.webserver.port,
        log_config=None,
    )


if __name__ == "__main__":
    main()
