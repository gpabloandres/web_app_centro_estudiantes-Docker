# Despliegue en PythonAnywhere gratuito

La aplicación está organizada directamente en la raíz del proyecto: `app/`, `config.py`, `wsgi.py` y `requirements.txt`. Sube esa estructura a `/home/TU_USUARIO/centro_estudiantes`. El plan gratuito puede ejecutarla con SQLite local; no depende de servicios externos de base de datos.

## Preparación

Sube el contenido de la raíz del proyecto (`app/`, `config.py`, `wsgi.py` y `requirements.txt`) a `/home/TU_USUARIO/centro_estudiantes` en PythonAnywhere. En una Bash Console:

```bash
cd ~/centro_estudiantes
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
flask --app 'app:create_app' init-db
flask --app 'app:create_app' create-admin
```

El segundo comando CLI solicitará usuario y contraseña; exige al menos 12 caracteres. No existe una cuenta ni una contraseña predeterminada.

## Configuración Web

1. En **Web**, crea una aplicación nueva con **Manual configuration** y una versión de Python soportada por tu cuenta.
2. Configura el código y el directorio de trabajo como `/home/TU_USUARIO/centro_estudiantes`.
3. Configura el virtualenv `/home/TU_USUARIO/centro_estudiantes/venv`.
4. Abre el archivo WSGI que indica el panel y reemplaza su contenido por:

   ```python
   import os
   import sys

    project_folder = "/home/TU_USUARIO/centro_estudiantes"
   if project_folder not in sys.path:
       sys.path.insert(0, project_folder)

   os.environ["SECRET_KEY"] = "REEMPLAZA_CON_UN_SECRETO_ALEATORIO_ESTABLE"

    from wsgi import application
   ```

   Genera el secreto una vez con `python -c 'import secrets; print(secrets.token_hex(32))'` en la consola y mantenlo estable entre recargas. No lo publiques ni lo guardes en el repositorio.
5. Añade el mapeo de estáticos `/static/` a `/home/TU_USUARIO/centro_estudiantes/app/static/`.
6. Guarda y recarga la aplicación web.

La base de datos se crea en `instance/centro_estudiantes.db`; haz copias periódicas desde **Files**. No elimines `instance` al actualizar el código. Comprueba `/`, `/novedades`, `/calendario`, `/pantalla` y `/admin/login` tras la recarga.

El plan gratuito de PythonAnywhere puede suspender sitios con poca actividad y limita algunas funciones de red saliente; esta aplicación no necesita llamadas salientes para funcionar salvo la descarga opcional de fuentes e imagen de portada.
