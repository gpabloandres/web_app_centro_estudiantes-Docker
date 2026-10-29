from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from app import db


def utc_now():
	return datetime.now(timezone.utc)


class User(db.Model):
	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False, index=True)
	password_hash = db.Column(db.String(255), nullable=False)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)


class Post(db.Model):
	__tablename__ = "posts"

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(150), nullable=False)
	content = db.Column(db.Text, nullable=False)
	category = db.Column(db.String(50), nullable=False, default="Noticia", index=True)
	is_priority = db.Column(db.Boolean, nullable=False, default=False, index=True)
	image_url = db.Column(db.String(500))
	created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now, index=True)


class Project(db.Model):
	__tablename__ = "projects"

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(150), nullable=False)
	description = db.Column(db.Text, nullable=False)
	status = db.Column(db.String(50), nullable=False, default="En propuesta", index=True)
	category = db.Column(db.String(50), nullable=False, default="General")
	updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)


class Event(db.Model):
	__tablename__ = "events"

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(150), nullable=False)
	description = db.Column(db.Text)
	event_date = db.Column(db.String(50), nullable=False, index=True)
	location = db.Column(db.String(100), nullable=False, default="Colegio CTPAM")


class Feedback(db.Model):
	__tablename__ = "feedbacks"

	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.String(20), nullable=False, default="Sugerencia")
	message = db.Column(db.Text, nullable=False)
	contact_info = db.Column(db.String(120))
	created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now, index=True)
