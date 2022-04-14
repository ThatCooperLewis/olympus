import os


class env_meta(type):

    def __init__(cls, *args, **kwargs):
        return

    @property
    def crosstower_api_key(cls) -> str:
        return os.getenv('CT_API_KEY')

    @property
    def crosstower_secret_key(cls) -> str:
        return os.getenv('CT_SECRET_KEY')

    @property
    def discord_alert_webhook(cls) -> str:
        return os.getenv('DISCORD_WEBHOOK')

    @property
    def discord_status_webhook(cls) -> str:
        return os.getenv('DISCORD_STATUS_WEBHOOK')

    @property
    def postgres_user(cls) -> str:
        return os.getenv('PSQL_USER')

    @property
    def postgres_password(cls) -> str:
        return os.getenv('PSQL_PW')

    @property
    def postgres_host(cls) -> str:
        return os.getenv('PSQL_HOST')

    @property
    def postgres_port(cls) -> str:
        return os.getenv('PSQL_PORT')

    @property
    def postgres_database(cls) -> str:
        return os.getenv('PSQL_DB')

    @property
    def keras_model_path(cls) -> str:
        return os.getenv('KERAS_MODEL_PATH')
    
    @property
    def keras_params_path(cls) -> str:
        return os.getenv('KERAS_PARAMS_PATH')

class env(metaclass=env_meta):
    pass
