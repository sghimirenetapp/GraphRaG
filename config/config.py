from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["setting.toml", "prompt.toml", "schema.toml", ".secrets.toml"],
)