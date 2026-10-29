"""WSGI entry point for local and PythonAnywhere deployments."""

from app import create_app

application = create_app()