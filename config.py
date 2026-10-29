import os
from datetime import timedelta


class Config:
	SECRET_KEY = os.environ.get("SECRET_KEY", "development-key-change-before-deploying")
	SQLALCHEMY_DATABASE_URI = os.environ.get(
		"DATABASE_URL", "sqlite:///centro_estudiantes.db"
	)
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
	PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
	MAX_CONTENT_LENGTH = 1024 * 1024
	POSTS_PER_PAGE = 12
	ADMIN_ITEMS_PER_PAGE = 25


class TestConfig(Config):
	TESTING = True
	SECRET_KEY = "test-key"
	SQLALCHEMY_DATABASE_URI = "sqlite://"
	WTF_CSRF_ENABLED = False
