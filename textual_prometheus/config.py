import os.path
import sys
from pathlib import Path
from typing import Any

if sys.version_info < (3, 11):
    # compatibility for python <3.11
    import tomli as tomllib
else:
    import tomllib

from pydantic import BaseSettings, HttpUrl


class ConfigNotFound(Exception):
    ...


def toml_config_settings_source(settings: BaseSettings) -> dict[str, Any]:
    """
    Settings source that loads variables from a TOML file
    at the project's root.

    Using `env_file_encoding` from Config when reading `config.toml`
    """

    conf_paths = ("./config.toml", "~/.config/tprom/config.toml", "/etc/tprom/config.toml")
    for conf_path in conf_paths:
        conf_file = Path(os.path.expanduser(conf_path))
        if conf_file.is_file():
            encoding = settings.__config__.env_file_encoding
            return tomllib.loads(conf_file.read_text(encoding))
    raise ConfigNotFound(f"Couldn't find config file in {conf_paths}")


class Settings(BaseSettings):
    endpoints: list[HttpUrl]
    instance_whitelist: list[str]
    instance_blacklist: list[str]
    endpoint: HttpUrl | None
    verify_cert: bool = True

    class Config:
        env_file_encoding = 'utf-8'

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                toml_config_settings_source,
                env_settings,
                file_secret_settings,
            )


SETTINGS = Settings()
if SETTINGS.endpoints and not SETTINGS.endpoint:
    SETTINGS.endpoint = SETTINGS.endpoints[0]


if __name__ == "__main__":
    print(SETTINGS)
