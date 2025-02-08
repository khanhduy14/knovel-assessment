from abc import ABC
from typing import Tuple, Type, TypeVar

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from utils.config import parse_config

_T = TypeVar('_T', bound='BaseAppSettings')


class BaseAppSettings(ABC, BaseSettings):

    model_config = SettingsConfigDict(env_prefix='app_', env_nested_delimiter='__')

    @classmethod
    def from_yaml(cls: Type[_T], path: str) -> _T:
        """
        Values from the config file can be overwritten by environment variables.
        E.g.:
        os.environ['app_db_connection'] = '{"password": "asd"}'
        os.environ['app_db_connection__password'] = 'asd'
        """
        config_dict = parse_config(path)
        return cls(**config_dict)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return env_settings, init_settings
