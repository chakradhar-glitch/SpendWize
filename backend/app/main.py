import logging

from pydantic import ValidationError
from pydantic_settings import SettingsError

from app.factory import create_app

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
try:
    app = create_app()
except (ValidationError, SettingsError):
    raise SystemExit(
        "Invalid SpendWise configuration. Check backend/.env.example; "
        "SPENDWISE_DATABASE_URL must use postgresql+psycopg."
    ) from None
