from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for

from app import db
from app.models import Event, Feedback, Post, Project

public_bp = Blueprint("public", __name__)


@public_bp.get("/")
def index():
	priority_news = Post.query.filter_by(is_priority=True).order_by(Post.created_at.desc()).first()
	recent_posts = Post.query.order_by(Post.created_at.desc()).limit(3).all()
	upcoming_events = Event.query.order_by(Event.event_date.asc()).limit(3).all()
	active_projects = Project.query.order_by(Project.updated_at.desc()).limit(3).all()
	return render_template(
		"public/index.html",
		priority_news=priority_news,
		recent_posts=recent_posts,
		upcoming_events=upcoming_events,
		active_projects=active_projects,
	)


@public_bp.get("/quienes-somos")
def quienes_somos():
	projects = Project.query.order_by(Project.updated_at.desc()).all()
	return render_template("public/quienes_somos.html", projects=projects)


@public_bp.get("/novedades")
def novedades():
	category_filter = request.args.get("categoria", "").strip()
	query = Post.query
	if category_filter:
		query = query.filter_by(category=category_filter)
	posts = query.order_by(Post.created_at.desc()).paginate(
		page=request.args.get("pagina", 1, type=int),
		per_page=current_app.config["POSTS_PER_PAGE"],
		error_out=False,
	)
	categories = [row[0] for row in db.session.query(Post.category).distinct().order_by(Post.category).all()]
	return render_template(
		"public/novedades.html", posts=posts, categories=categories, category_filter=category_filter
	)


@public_bp.get("/calendario")
def calendario():
	events = Event.query.order_by(Event.event_date.asc()).all()
	return render_template("public/calendario.html", events=events)


@public_bp.route("/contacto", methods=["GET", "POST"])
def contacto():
	if request.method == "POST":
		message = request.form.get("message", "").strip()
		kind = request.form.get("type", "Sugerencia")
		contact_info = request.form.get("contact_info", "").strip()
		if not message or len(message) > 3000:
			flash("Escribe un mensaje de hasta 3000 caracteres.", "error")
		elif kind not in {"Consulta", "Sugerencia"}:
			flash("Selecciona un tipo de mensaje válido.", "error")
		else:
			db.session.add(
				Feedback(
					type=kind,
					message=message,
					contact_info=contact_info[:120] or None,
				)
			)
			db.session.commit()
			flash("Gracias. Tu mensaje fue enviado.", "success")
			return redirect(url_for("public.contacto"))
	return render_template("public/contacto.html")


@public_bp.get("/pantalla")
def pantalla():
	priority_news = Post.query.filter_by(is_priority=True).order_by(Post.created_at.desc()).limit(5).all()
	recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
	events = Event.query.order_by(Event.event_date.asc()).limit(5).all()
	return render_template(
		"pantalla.html", priority_news=priority_news, recent_posts=recent_posts, events=events
	)


@public_bp.get("/api/pantalla-data")
def api_pantalla_data():
	posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
	events = Event.query.order_by(Event.event_date.asc()).limit(5).all()
	return jsonify(
		{
			"posts": [
				{"title": post.title, "content": post.content, "category": post.category,
				 "is_priority": post.is_priority}
				for post in posts
			],
			"events": [
				{"title": event.title, "date": event.event_date, "location": event.location}
				for event in events
			],
		}
	)
