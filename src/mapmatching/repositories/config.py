import os
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Settings:
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    @classmethod
    def load_env_info(cls) -> "Settings":
        password = os.environ.get("DB_PASSWORD")
        if password is None:
            raise RuntimeError("Environment variable DB_PASSWORD is not set.")

        return cls(
            db_host=os.environ.get("DB_HOST", "localhost"),
            db_port=int(os.environ.get("DB_PORT","5432")),
            db_name=os.environ.get("DB_NAME", "data"),
            db_user=os.environ.get("DB_USER", "postgres"),
            db_password=password,
        )