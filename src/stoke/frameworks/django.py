"""Django 프로젝트 스캐폴딩."""
import sys
from pathlib import Path

from stoke.python_versions import detect_all
from stoke.init import _prompt, _select_python_version, _select_env_type

def cmd_init_django():
    """stoke init django 명령어."""
    print("Creating Django project\n")

    project_name = _prompt("Project name", "myapp")

    installs = detect_all()
    python_version = _select_python_version(installs)
    env_type = _select_env_type()

    project_path = Path.cwd() / project_name
    if project_path.exists():
        print(f"Error: directory '{project_name}' already exists", file=sys.stderr)
        sys.exit(1)

    project_path.mkdir()
    src = project_path / "src"
    src.mkdir()
    (src / project_name).mkdir()
    (src / "hello").mkdir()
    (src / "hello" / "templates").mkdir()
    (src / "hello" / "templates" / "hello").mkdir()
    (src / "static").mkdir()

    _write_stoke_toml(project_path, project_name, python_version, env_type)
    _write_main(src / "main.py", project_name)
    _write_manage_py(src / "manage.py", project_name)

    _write_project_init(src / project_name / "__init__.py")
    _write_settings(src / project_name / "settings.py", project_name)
    _write_urls(src / project_name / "urls.py")
    _write_wsgi(src / project_name / "wsgi.py", project_name)
    _write_asgi(src / project_name / "asgi.py", project_name)

    _write_app_init(src / "hello" / "__init__.py")
    _write_app_apps(src / "hello" / "apps.py")
    _write_app_views(src / "hello" / "views.py")
    _write_app_urls(src / "hello" / "urls.py")
    _write_app_template(src / "hello" / "templates" / "hello" / "index.html")
    _write_static_css(src / "static" / "style.css")

    print(f"\nDjango project created at: {project_path}")
    print()
    print("Next steps:")
    print(f"  cd {project_name}")
    print(f"  stoke build")
    print(f"  stoke run")
    print()
    print(f"After running, open: http://localhost:8000/")

def _write_stoke_toml(project_path: Path, project_name: str, python_version: str, env_type: str) -> None:
    env_line = f'env_type = "{env_type}"\n' if env_type != "venv" else ""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "local"

[targets.{project_name}]
language = "python"
python_version = "{python_version}"
{env_line}sources = ["src/**/*.py"]
entry = "src/main.py"

[targets.{project_name}.deps]
django = "*"
'''
    (project_path / "stoke.toml").write_text(content, encoding="utf-8")

def _write_main(path: Path, project_name: str) -> None:
    content = '''"""stoke run으로 실행 시 manage.py runserver 호출."""
import os
import sys
import subprocess

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    manage_py = os.path.join(script_dir, "manage.py")
    try:
        subprocess.run([sys.executable, manage_py, "runserver"])
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
'''
    path.write_text(content, encoding="utf-8")

def _write_manage_py(path: Path, project_name: str) -> None:
    content = f'''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{project_name}.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
'''
    path.write_text(content, encoding="utf-8")

def _write_project_init(path: Path) -> None:
    path.write_text("", encoding="utf-8")

def _write_settings(path: Path, project_name: str) -> None:
    content = f'''"""Django settings for {project_name} project."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-change-this-in-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "hello",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "{project_name}.urls"

TEMPLATES = [
    {{
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {{
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        }},
    }},
]

WSGI_APPLICATION = "{project_name}.wsgi.application"

DATABASES = {{
    "default": {{
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }}
}}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
'''
    path.write_text(content, encoding="utf-8")

def _write_urls(path: Path) -> None:
    content = '''"""Project URL Configuration."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("hello.urls")),
]
'''
    path.write_text(content, encoding="utf-8")

def _write_wsgi(path: Path, project_name: str) -> None:
    content = f'''"""WSGI config."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{project_name}.settings")
application = get_wsgi_application()
'''
    path.write_text(content, encoding="utf-8")

def _write_asgi(path: Path, project_name: str) -> None:
    content = f'''"""ASGI config."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{project_name}.settings")
application = get_asgi_application()
'''
    path.write_text(content, encoding="utf-8")

def _write_app_init(path: Path) -> None:
    path.write_text("", encoding="utf-8")

def _write_app_apps(path: Path) -> None:
    content = '''from django.apps import AppConfig

class HelloConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hello"
'''
    path.write_text(content, encoding="utf-8")

def _write_app_views(path: Path) -> None:
    content = '''from django.http import JsonResponse
from django.shortcuts import render

def home(request):
    return render(request, "hello/index.html", {"title": "Django + stoke"})

def api_hello(request, name):
    return JsonResponse({"message": f"Hello, {name}!"})
'''
    path.write_text(content, encoding="utf-8")

def _write_app_urls(path: Path) -> None:
    content = '''from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("api/hello/<str:name>/", views.api_hello),
]
'''
    path.write_text(content, encoding="utf-8")

def _write_app_template(path: Path) -> None:
    content = '''{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="{% static 'style.css' %}">
</head>
<body>
    <h1>{{ title }}</h1>
    <p>Hello from Django + stoke!</p>
    <p>Try: <a href="/api/hello/world/">/api/hello/world/</a></p>
</body>
</html>
'''
    path.write_text(content, encoding="utf-8")

def _write_static_css(path: Path) -> None:
    content = '''body {
    font-family: sans-serif;
    max-width: 720px;
    margin: 4rem auto;
    padding: 0 1rem;
    color: #333;
}

h1 {
    color: #0284c7;
}
'''
    path.write_text(content, encoding="utf-8")