import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///tengai.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")

    AMZ_ACCESS_KEY = os.getenv("AMZ_ACCESS_KEY", "")
    AMZ_SECRET_KEY = os.getenv("AMZ_SECRET_KEY", "")
    AMZ_PARTNER_TAG = os.getenv("AMZ_PARTNER_TAG", "")
    AMZ_PARTNER_TYPE = os.getenv("AMZ_PARTNER_TYPE", "Associates")
    AMZ_MARKETPLACE = os.getenv("AMZ_MARKETPLACE", "www.amazon.ae")
    AMZ_REGION = os.getenv("AMZ_REGION", "eu-west-1")
    AMZ_HOST = os.getenv("AMZ_HOST", "webservices.amazon.ae")

    SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

    OXYLABS_USERNAME = os.getenv("OXYLABS_USERNAME", "")
    OXYLABS_PASSWORD = os.getenv("OXYLABS_PASSWORD", "")
    OXYLABS_SOURCE = os.getenv("OXYLABS_SOURCE", "amazon_product")
    OXYLABS_AMAZON_DOMAIN = os.getenv("OXYLABS_AMAZON_DOMAIN", "ae")
