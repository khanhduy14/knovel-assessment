from argparse import ArgumentParser
from typing import Any

from pydantic_settings import BaseSettings

from utils.base_app_settings import BaseAppSettings
from utils.postgresql_dbconnection import PostgresqlDbConnectionFactory


class WebserverConfig(BaseSettings):
    host: str = 'localhost'
    port: int = 8080


class JwtConfig(BaseSettings):
    secret_key: str
    algorithm: str = 'HS256'
    token_expire_mins: int = 30


class AppSettings(BaseAppSettings):
    webserver: WebserverConfig
    debug: bool = False
    db: PostgresqlDbConnectionFactory
    jwt: JwtConfig
    logging: dict[str, Any]

    @classmethod
    def get_config(cls) -> "AppSettings":
        parser = ArgumentParser()
        parser.add_argument(
            "-c",
            "--conf",
            action="store",
            dest="conf_file",
            help="Path to config file.",
            default="./config.yml",
        )
        args = parser.parse_args()

        return cls.from_yaml(args.conf_file)
