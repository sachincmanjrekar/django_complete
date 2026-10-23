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

## .gitignore (files git should not track)

    - db.sqlite3 and __pycache__/ showed up as untracked files in git status.
    - Don't delete them: Django/Python recreate them, and db.sqlite3 will hold my data.
    - Instead, list them in django_complete/.gitignore so git ignores them:
        db.sqlite3
        __pycache__/
        .gitignore
    - git status no longer shows them, so they can't be pushed by mistake.

## python manage.py startapp challenges

    - Creates a new app named "challenges" (run inside the folder with manage.py).
    - Makes a folder "challenges" containing:
        __init__.py   -> marks the folder as a Python package
        admin.py      -> register models to show in the admin site
        apps.py       -> app configuration (ChallengesConfig)
        migrations/   -> database change files for this app
        models.py     -> database tables (models) for this app
        tests.py      -> tests for this app
        views.py      -> functions that handle requests and return responses

## Virtual environment (optional)

    - Recommended for any Python project (Django or not).
    - Each project gets its own environment, so installed modules are
      project-specific instead of global.
    - Docs: https://docs.python.org/3/tutorial/venv.html

## Pylance in VS Code

    - VS Code extension that gives better code checks and code completion.
    - Enable it for the project in .vscode/settings.json:
        {
            "python.languageServer": "Pylance",
        }

## Section 2 complete

## Helpful resources (Django docs: starting a project)

    - Tutorial part 1 (startproject, project layout, runserver, first app):
        https://docs.djangoproject.com/en/6.0/intro/tutorial01/
    - django-admin and manage.py (all commands: startproject, startapp, runserver...):
        https://docs.djangoproject.com/en/6.0/ref/django-admin/
    - Settings reference (everything that can go in settings.py):
        https://docs.djangoproject.com/en/6.0/ref/settings/
    - PEP 8 (Python style guide: naming, indentation, line length, imports...):
        https://peps.python.org/pep-0008/
    - Course module slides and extra files (Academind Django practical guide):
        https://github.com/academind/django-practical-guide-course-code/tree/setup-zz-extra-files
    - Python virtual environments (venv):
        https://docs.python.org/3/tutorial/venv.html
