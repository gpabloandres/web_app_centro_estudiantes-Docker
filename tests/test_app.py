import unittest

from app import create_app, db
from app.models import Event, Feedback, Post, Project, User
from config import TestConfig


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        admin = User(username="test-admin")
        admin.set_password("test-password-123")
        db.session.add(admin)
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def csrf_token(self):
        with self.client.session_transaction() as session:
            return session["csrf_token"]

    def login(self):
        self.client.get("/admin/login")
        response = self.client.post(
            "/admin/login",
            data={
                "csrf_token": self.csrf_token(),
                "username": "test-admin",
                "password": "test-password-123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.client.get("/admin")

    def test_public_routes_and_static_assets_render(self):
        paths = (
            "/",
            "/quienes-somos",
            "/novedades",
            "/calendario",
            "/contacto",
            "/pantalla",
            "/api/pantalla-data",
            "/admin/login",
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)
        response = self.client.get("/static/css/site.css")
        self.assertEqual(response.status_code, 200)
        response.close()

    def test_public_navigation_marks_current_page(self):
        pages = (
            ("/", 'aria-label="Centro de Estudiantes, inicio" aria-current="page"'),
            ("/quienes-somos", 'href="/quienes-somos" aria-current="page"'),
            ("/novedades", 'href="/novedades" aria-current="page"'),
            ("/calendario", 'href="/calendario" aria-current="page"'),
            ("/contacto", 'href="/contacto" aria-current="page"'),
        )
        for path, current_link in pages:
            with self.subTest(path=path):
                response = self.client.get(path)
                html = response.get_data(as_text=True)
                self.assertIn(current_link, html)
                self.assertEqual(html.count('aria-current="page"'), 1)
                response.close()

    def test_home_has_student_shortcuts_and_clear_actions(self):
        response = self.client.get("/")
        html = response.get_data(as_text=True)
        for link in (
            'href="/novedades"',
            'href="/contacto"',
            'href="#novedades"',
            'href="#agenda"',
            'href="#proyectos"',
        ):
            with self.subTest(link=link):
                self.assertIn(link, html)
        response.close()

    def test_post_requests_require_csrf_and_contact_is_saved(self):
        self.assertEqual(
            self.client.post("/contacto", data={"message": "Sin token"}).status_code,
            400,
        )
        self.client.get("/contacto")
        response = self.client.post(
            "/contacto",
            data={
                "csrf_token": self.csrf_token(),
                "message": "Una idea para la comunidad",
                "type": "Sugerencia",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Feedback.query.count(), 1)

    def test_admin_requires_login_and_post_crud_works(self):
        self.assertEqual(self.client.get("/admin").status_code, 302)
        self.login()
        token = self.csrf_token()
        response = self.client.post(
            "/admin/posts/nuevo",
            data={"csrf_token": token, "title": "Aviso", "content": "Texto", "category": "Noticia"},
        )
        self.assertEqual(response.status_code, 302)
        post = Post.query.one()
        response = self.client.post(
            f"/admin/posts/{post.id}/editar",
            data={"csrf_token": token, "title": "Aviso actualizado", "content": "Texto", "category": "Noticia"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(post.title, "Aviso actualizado")
        response = self.client.post(f"/admin/posts/{post.id}/eliminar", data={"csrf_token": token})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.query.count(), 0)

    def test_project_and_event_crud_work(self):
        self.login()
        token = self.csrf_token()
        for path, form, model, name, edit_form in (
            (
                "/admin/proyectos/nuevo",
                {"title": "Proyecto", "description": "Descripción"},
                Project,
                "proyectos",
                {"title": "Proyecto actualizado", "description": "Descripción"},
            ),
            (
                "/admin/eventos/nuevo",
                {"title": "Encuentro", "event_date": "2026-12-01"},
                Event,
                "eventos",
                {"title": "Encuentro actualizado", "event_date": "2026-12-01"},
            ),
        ):
            with self.subTest(model=model.__name__):
                response = self.client.post(path, data={"csrf_token": token, **form})
                self.assertEqual(response.status_code, 302)
                item = model.query.one()
                item_id = item.id
                response = self.client.post(
                    f"/admin/{name}/{item_id}/editar",
                    data={"csrf_token": token, **edit_form},
                )
                self.assertEqual(response.status_code, 302)
                self.assertTrue(item.title.endswith("actualizado"))
                response = self.client.post(
                    f"/admin/{name}/{item_id}/eliminar", data={"csrf_token": token}
                )
                self.assertEqual(response.status_code, 302)
                self.assertEqual(model.query.count(), 0)


if __name__ == "__main__":
    unittest.main()