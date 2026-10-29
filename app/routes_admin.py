from functools import wraps

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from app import db
from app.models import Event, Feedback, Post, Project, User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view):
	@wraps(view)
	def wrapped(*args, **kwargs):
		if not session.get("user_id"):
			flash("Inicia sesión para acceder a administración.", "warning")
			return redirect(url_for("admin.login"))
		return view(*args, **kwargs)
	return wrapped


def required_text(name, label, maximum):
	value = request.form.get(name, "").strip()
	if not value or len(value) > maximum:
		flash(f"{label}: completa este campo (máximo {maximum} caracteres).", "error")
		return None
	return value


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		username = request.form.get("username", "").strip()
		password = request.form.get("password", "")
		user = User.query.filter_by(username=username).first()
		if user and user.check_password(password):
			session.clear()
			session["user_id"] = user.id
			flash("Sesión iniciada.", "success")
			return redirect(url_for("admin.dashboard"))
		flash("Usuario o contraseña incorrectos.", "error")
	return render_template("admin/login.html")


@admin_bp.post("/logout")
@admin_required
def logout():
	session.clear()
	flash("Sesión cerrada.", "info")
	return redirect(url_for("public.index"))


@admin_bp.get("")
@admin_required
def dashboard():
	counts = {
		"posts": Post.query.count(),
		"projects": Project.query.count(),
		"events": Event.query.count(),
		"feedback": Feedback.query.count(),
	}
	return render_template("admin/dashboard.html", counts=counts)


@admin_bp.get("/posts")
@admin_required
def posts():
	items = Post.query.order_by(Post.created_at.desc()).paginate(
		page=request.args.get("pagina", 1, type=int),
		per_page=current_app.config["ADMIN_ITEMS_PER_PAGE"], error_out=False,
	)
	return render_template("admin/posts.html", items=items)


@admin_bp.route("/posts/nuevo", methods=["GET", "POST"])
@admin_required
def post_create():
	if request.method == "POST":
		title = required_text("title", "Título", 150)
		content = required_text("content", "Contenido", 20000)
		category = required_text("category", "Categoría", 50)
		if title and content and category:
			db.session.add(Post(title=title, content=content, category=category,
								is_priority=bool(request.form.get("is_priority")),
								image_url=request.form.get("image_url", "").strip()[:500] or None))
			db.session.commit()
			flash("Publicación creada.", "success")
			return redirect(url_for("admin.posts"))
	return render_template("admin/post_form.html", post=None)


@admin_bp.route("/posts/<int:post_id>/editar", methods=["GET", "POST"])
@admin_required
def post_edit(post_id):
	post = db.get_or_404(Post, post_id)
	if request.method == "POST":
		title = required_text("title", "Título", 150)
		content = required_text("content", "Contenido", 20000)
		category = required_text("category", "Categoría", 50)
		if title and content and category:
			post.title, post.content, post.category = title, content, category
			post.is_priority = bool(request.form.get("is_priority"))
			post.image_url = request.form.get("image_url", "").strip()[:500] or None
			db.session.commit()
			flash("Publicación actualizada.", "success")
			return redirect(url_for("admin.posts"))
	return render_template("admin/post_form.html", post=post)


@admin_bp.post("/posts/<int:post_id>/eliminar")
@admin_required
def post_delete(post_id):
	db.session.delete(db.get_or_404(Post, post_id))
	db.session.commit()
	flash("Publicación eliminada.", "info")
	return redirect(url_for("admin.posts"))


@admin_bp.get("/proyectos")
@admin_required
def projects():
	items = Project.query.order_by(Project.updated_at.desc()).all()
	return render_template("admin/projects.html", items=items)


@admin_bp.route("/proyectos/nuevo", methods=["GET", "POST"])
@admin_required
def project_create():
	if request.method == "POST":
		title = required_text("title", "Título", 150)
		description = required_text("description", "Descripción", 20000)
		if title and description:
			db.session.add(Project(title=title, description=description,
								   status=request.form.get("status", "En propuesta")[:50],
								   category=request.form.get("category", "General").strip()[:50] or "General"))
			db.session.commit()
			flash("Proyecto registrado.", "success")
			return redirect(url_for("admin.projects"))
	return render_template("admin/project_form.html", project=None)


@admin_bp.route("/proyectos/<int:project_id>/editar", methods=["GET", "POST"])
@admin_required
def project_edit(project_id):
	project = db.get_or_404(Project, project_id)
	if request.method == "POST":
		title = required_text("title", "Título", 150)
		description = required_text("description", "Descripción", 20000)
		if title and description:
			project.title, project.description = title, description
			project.status = request.form.get("status", "En propuesta")[:50]
			project.category = request.form.get("category", "General").strip()[:50] or "General"
			db.session.commit()
			flash("Proyecto actualizado.", "success")
			return redirect(url_for("admin.projects"))
	return render_template("admin/project_form.html", project=project)


@admin_bp.post("/proyectos/<int:project_id>/eliminar")
@admin_required
def project_delete(project_id):
	db.session.delete(db.get_or_404(Project, project_id))
	db.session.commit()
	flash("Proyecto eliminado.", "info")
	return redirect(url_for("admin.projects"))


@admin_bp.get("/eventos")
@admin_required
def events():
	items = Event.query.order_by(Event.event_date.asc()).all()
	return render_template("admin/events.html", items=items)


@admin_bp.route("/eventos/nuevo", methods=["GET", "POST"])
@admin_required
def event_create():
	if request.method == "POST":
		title = required_text("title", "Título", 150)
		event_date = required_text("event_date", "Fecha", 50)
		if title and event_date:
			db.session.add(Event(title=title, event_date=event_date,
								 description=request.form.get("description", "").strip()[:20000] or None,
								 location=request.form.get("location", "Colegio CTPAM").strip()[:100] or "Colegio CTPAM"))
			db.session.commit()
			flash("Evento guardado.", "success")
			return redirect(url_for("admin.events"))
	return render_template("admin/event_form.html", event=None)


@admin_bp.route("/eventos/<int:event_id>/editar", methods=["GET", "POST"])
@admin_required
def event_edit(event_id):
	event = db.get_or_404(Event, event_id)
	if request.method == "POST":
		title = required_text("title", "Título", 150)
		event_date = required_text("event_date", "Fecha", 50)
		if title and event_date:
			event.title, event.event_date = title, event_date
			event.description = request.form.get("description", "").strip()[:20000] or None
			event.location = request.form.get("location", "Colegio CTPAM").strip()[:100] or "Colegio CTPAM"
			db.session.commit()
			flash("Evento actualizado.", "success")
			return redirect(url_for("admin.events"))
	return render_template("admin/event_form.html", event=event)


@admin_bp.post("/eventos/<int:event_id>/eliminar")
@admin_required
def event_delete(event_id):
	db.session.delete(db.get_or_404(Event, event_id))
	db.session.commit()
	flash("Evento eliminado.", "info")
	return redirect(url_for("admin.events"))


@admin_bp.get("/mensajes")
@admin_required
def feedback():
	items = Feedback.query.order_by(Feedback.created_at.desc()).all()
	return render_template("admin/feedback.html", items=items)


@admin_bp.post("/mensajes/<int:feedback_id>/eliminar")
@admin_required
def feedback_delete(feedback_id):
	db.session.delete(db.get_or_404(Feedback, feedback_id))
	db.session.commit()
	flash("Mensaje eliminado.", "info")
	return redirect(url_for("admin.feedback"))
