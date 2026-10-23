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

## django-admin startproject monthly_challenges

    - New project for section 3, next to mypage in django_complete/.
    - Same layout as before:
        manage.py
        monthly_challenges/  -> settings.py, urls.py, asgi.py, wsgi.py, __init__.py

## python manage.py startapp challenges (inside monthly_challenges)

    - Creates the "challenges" app in the monthly_challenges project
      (admin.py, apps.py, migrations/, models.py, tests.py, views.py).
    - Files are still the defaults; no views or URLs written yet.

## First view and URL (challenges/views.py + challenges/urls.py)

    - challenges/views.py:
        from django.http import HttpResponse

        def index(request):
            return HttpResponse("Hello, World!")
    - challenges/urls.py (new file, made by me - startapp does not create it):
        from django.urls import path
        from . import views

        urlpatterns = [
            path("january", views.index),
        ]
    - monthly_challenges/urls.py connects the app URLs with include():
        from django.urls import path, include

        urlpatterns = [
            path('admin/', admin.site.urls),
            path("challenges/", include("challenges.urls")),
        ]
    - Result: challenges/ + january = http://127.0.0.1:8000/challenges/january
      -> "Hello, World!"

## Error: view without the request parameter

    - First wrote def index(): (no parameter).
    - Opening /challenges/january gave:
        TypeError: index() takes 0 positional arguments but 1 was given
    - Django always passes the request object to a view as the first argument.
    - Fix: def index(request):

## Trailing slash in the route

    - path("january", ...) matches only /challenges/january
    - /challenges/january/ (with slash) -> 404 Page not found.
    - Common Django style is path("january/", ...) so the URL ends with a slash.

## Dynamic URL segment (<month>)

    - One route for all months instead of one path() per month:
        path("<month>", views.monthly_challenge),
    - <month> captures that part of the URL and passes it to the view
      as a keyword argument with the same name:
        def monthly_challenge(request, month):
    - challenges dict + challenges.get(month):
        found     -> HttpResponse(f"Monthly Challenge for {month}: {challenge_text}")
        not found -> HttpResponseNotFound(f"No challenge found for {month}")  (404)
    - "december": None -> if challenge_text: is False -> also 404.

## Error: dynamic route pointing to the wrong view

    - Wrote path("<month>", views.index) by mistake.
    - Django calls index(request, month="february") but index() only takes request:
        TypeError: index() got an unexpected keyword argument 'month'
    - Fix: point the route to the view that accepts month -> views.monthly_challenge
    - The view's parameter name must match the name inside < >.

## Path converters (int, str) and why ORDER matters

    - challenges/urls.py:
        urlpatterns = [
            path("<int:month>", views.monthly_challenge_by_number),
            path("<str:month>", views.monthly_challenge),
        ]
    - <int:month> -> matches only digits, and month arrives as an int (1, not "1").
    - <str:month> -> matches ANY text without "/" (also "1"); month arrives as a str.
      (<month> with no converter = str by default.)
    - Django checks urlpatterns top to bottom and uses the FIRST match.
    - int first (correct):
        /challenges/1       -> int matches   -> monthly_challenge_by_number
        /challenges/january -> int fails, str matches -> monthly_challenge
    - str first (wrong): str also matches "1", so the int route is never reached;
      /challenges/1 goes to monthly_challenge and gives 404 "No challenge found for 1".
    - Rule: put the more specific converter (int) before the general one (str).

## Global dictionary (monthly_challenges)

    - Moved the challenges dict out of monthly_challenge() to the top of
      challenges/views.py and renamed it monthly_challenges:
        monthly_challenges = {
            "january": "Eat no meat for the entire month!",
            ...
            "december": None,
        }

        def monthly_challenge(request, month):
            challenge_text = monthly_challenges.get(month)
    - Why global (module level):
        every view in views.py can use it (e.g. monthly_challenge_by_number)
        the dict is built once when the file loads, not on every request

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
    - URL dispatcher (path(), include(), path converters int/str/slug...):
        https://docs.djangoproject.com/en/6.0/topics/http/urls/
