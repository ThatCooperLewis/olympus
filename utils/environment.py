import os


class env_meta(type):

    def __init__(cls, *args, **kwargs):
        return

    @property
    def service_name(cls) -> str:
        return os.getenv('OLYMPUS_SERVICE')

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
        return os.getenv('POSTGRES_USER')

    @property
    def postgres_password(cls) -> str:
        return os.getenv('POSTGRES_PASSWORD')

    @property
    def postgres_host(cls) -> str:
        return os.getenv('POSTGRES_HOST')

    @property
    def postgres_port(cls) -> str:
        return os.getenv('POSTGRES_PORT')

    @property
    def postgres_database(cls) -> str:
        return os.getenv('POSTGRES_DB')

    @property
    def keras_model_path(cls) -> str:
        return os.getenv('KERAS_MODEL_PATH')
    
    @property
    def keras_params_path(cls) -> str:
        return os.getenv('KERAS_PARAMS_PATH')
    
    @property
    def google_sheet_id(cls) -> str:
        return os.getenv('GOOGLE_SHEET_ID')

    @property
    def github_access_token(cls) -> str:
        return os.getenv('GITHUB_ACCESS_TOKEN')

    @property
    def robinhood_email(cls) -> str:
        return os.getenv('RH_EMAIL')

    @property
    def robinhood_password(cls) -> str:
        return os.getenv('RH_PASSWORD')

    @property
    def robinhood_mfa(cls) -> str:
        return os.getenv('RH_MFA')

class env(metaclass=env_meta):
    pass
