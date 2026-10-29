import hmac
import os

import click
from flask import Flask, abort, g, request, session
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()


def create_app(config_class=Config):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_object(config_class)
	os.makedirs(app.instance_path, exist_ok=True)
	db.init_app(app)

	from app.models import User
	from app.routes_admin import admin_bp
	from app.routes_public import public_bp

	app.register_blueprint(public_bp)
	app.register_blueprint(admin_bp)

	@app.before_request
	def protect_post_requests():
		if request.method == "POST":
			token = session.get("csrf_token", "")
			submitted = request.form.get("csrf_token", "")
			if not token or not hmac.compare_digest(token, submitted):
				abort(400)
		else:
			session.setdefault("csrf_token", os.urandom(32).hex())

		user_id = session.get("user_id")
		g.user = db.session.get(User, user_id) if user_id else None

	@app.context_processor
	def inject_csrf_token():
		return {"csrf_token": session.get("csrf_token", "")}

	@app.cli.command("init-db")
	def init_db_command():
		"""Create the database tables."""
		with app.app_context():
			db.create_all()
		click.echo("Base de datos inicializada.")

	@app.cli.command("create-admin")
	def create_admin_command():
		"""Create an administrator without a bundled default password."""
		username = click.prompt("Usuario", type=str).strip()
		if not username:
			raise click.ClickException("El usuario no puede estar vacío.")
		if User.query.filter_by(username=username).first():
			raise click.ClickException("Ese usuario ya existe.")
		password = click.prompt("Contraseña", hide_input=True, confirmation_prompt=True)
		if len(password) < 12:
			raise click.ClickException("La contraseña debe tener al menos 12 caracteres.")
		user = User(username=username)
		user.set_password(password)
		db.session.add(user)
		db.session.commit()
		click.echo("Administrador creado.")

	return app
