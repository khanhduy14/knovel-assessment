import os
import re
from pathlib import PurePath, PurePosixPath
from typing import Any, cast

import yaml
from yaml import SafeLoader

_ENV_TAG = "!ENV"
_ENV_PATTERN = re.compile(r".*?\$\{(\w+)\}.*?")

_CONTENT_TAG = "!CONTENT"
_CONTENT_PATTERN = re.compile(r"\s+(\S+)\s*")


def parse_config(path: os.PathLike[str] | str) -> dict[str, Any]:
    """
    Load a yaml configuration file and resolve any environment variables and read file contents.
    The environment variables must have !ENV before them and be in this format
    to be parsed: !ENV ${VAR_NAME}.
    The path variables must have !CONTENT before them and be in this format
    to be parsed: !CONTENT ${VAR_NAME}.
    E.g.:

    database:
        host: !ENV ${HOST}
        port: !ENV ${PORT}
        password: !CONTENT /tmp/secrets/database-password
    app:
        log_path: !ENV '/var/${LOG_PATH}'
        something_else: !ENV '${AWESOME_ENV_VAR}/var/${A_SECOND_AWESOME_VAR}'

    :param str path: the path to the yaml file
    :return: the dict configuration
    """
    loader = cast(Any, type("YAMLLoader", (SafeLoader, ), {}))

    # the tag will be used to mark where to start searching for the pattern
    # e.g. somekey: !ENV somestring${MYENVVAR}blah blah blah
    loader.add_implicit_resolver(_ENV_TAG, _ENV_PATTERN, None)

    def constructor_env_variables(loader: Any, node: Any):
        """
        Extracts the environment variable from the node's value
        :param yaml.Loader loader: the yaml loader
        :param node: the current node in the yaml
        :return: the parsed string that contains the value of the environment
        variable
        """
        value = loader.construct_scalar(node)
        match = _ENV_PATTERN.findall(value)  # to find all env variables in line
        if match:
            full_value = value
            for next_match in match:
                env_value = os.environ.get(next_match, next_match)
                full_value = full_value.replace(f"${{{next_match}}}", env_value)
            return full_value
        return value

    loader.add_constructor(_ENV_TAG, constructor_env_variables)

    # the tag will be used to mark where to start searching for the pattern
    # e.g. somekey: !CONTENT ./asd/data
    loader.add_implicit_resolver(_CONTENT_TAG, _CONTENT_PATTERN, None)

    def constructor_content_variables(loader: Any, node: Any):
        """
        Extracts the file path variable from the node's value
        :param yaml.Loader loader: the yaml loader
        :param node: the current node in the yaml
        :return: the parsed string that contains the value of the file
        """
        value = loader.construct_scalar(node)
        with open(value, encoding="utf-8") as f:
            return f.read()

    loader.add_constructor(_CONTENT_TAG, constructor_content_variables)

    os_path = PurePath(PurePosixPath(path))
    with open(os_path, encoding="utf-8") as conf_data:
        return yaml.load(conf_data, Loader=loader)
