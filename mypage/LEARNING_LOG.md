## django-admin startproject mypage

    - Creates a new Django project named "mypage".
    - Makes a folder "mypage" containing:
        manage.py        -> tool to run project commands (runserver, migrate, startapp, ...)
        mypage/          -> project settings package
            __init__.py  -> marks the folder as a Python package
            settings.py  -> project configuration (installed apps, database, etc.)
            urls.py      -> main URL routes of the site
            asgi.py      -> entry point for async web servers
            wsgi.py      -> entry point for regular web servers

## python manage.py runserver

    - Starts the development server at http://127.0.0.1:8000/
    - Shows the Django welcome page (rocket) because no URLs are added yet.
    - Running it created two new things:
        db.sqlite3   -> empty SQLite database file (no tables yet)
        __pycache__/ -> compiled Python files, made automatically
    - Warning "You have 18 unapplied migration(s)" -> built-in apps (admin, auth,
      sessions...) need their tables; python manage.py migrate creates them.
    - Stop the server with Ctrl + C.

## Helpful resources (Django docs: starting a project)

    - Tutorial part 1 (startproject, project layout, runserver, first app):
        https://docs.djangoproject.com/en/6.0/intro/tutorial01/
    - django-admin and manage.py (all commands: startproject, startapp, runserver...):
        https://docs.djangoproject.com/en/6.0/ref/django-admin/
    - Settings reference (everything that can go in settings.py):
        https://docs.djangoproject.com/en/6.0/ref/settings/
    - PEP 8 (Python style guide: naming, indentation, line length, imports...):
        https://peps.python.org/pep-0008/
