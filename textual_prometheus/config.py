import sys
from pathlib import Path
from typing import Any

if sys.version_info < (3, 11):
    # compatibility for python <3.11
    import tomli as tomllib
else:
    import tomllib

from pydantic import BaseSettings, HttpUrl


def toml_config_settings_source(settings: BaseSettings) -> dict[str, Any]:
    """
    Settings source that loads variables from a TOML file
    at the project's root.

    Using `env_file_encoding` from Config when reading `config.toml`
    """
    encoding = settings.__config__.env_file_encoding
    return tomllib.loads(Path('config.toml').read_text(encoding))


class Settings(BaseSettings):
    endpoints: list[HttpUrl]
    instance_whitelist: list[str]
    instance_blacklist: list[str]
    endpoint: HttpUrl | None

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
