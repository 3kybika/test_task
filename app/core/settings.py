from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    This class gots settings form os variables
    """

    # Base
    debug: bool = False
    project_name: str = "app"

    # Database
    # db_async_connection_str = "postgresql+asyncpg://postgres:postgres@localhost/asyncalchemy"
    # db_async_connection_str: str = "sqlite+aiosqlite:///data.db"
    # db_async_test_connection_str: str = ""

    # Logger
    logger_cfg: str = "app/core/logger_cfg.yaml"

    # api
    templates_dir: str = "app/templates"
    static_dir: str = "app/templates/static"

    # auth service
    auth_service_jwt_secret: str = "a4dlkgjnp9ujdd7tf98e89jhre9pja89rpy8jmj89pa0f"
    auth_service_jwt_algo: str = "HS256"
    auth_service_expire_time: int = 30 * 60  # minutes
    auth_service_cookie_name: str = "access_token"
