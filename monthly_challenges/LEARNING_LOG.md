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

## Redirect (HttpResponseRedirect): /challenges/1 -> /challenges/january

    - challenges/views.py:
        from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect

        def monthly_challenge_by_number(request, month):
            months = list(monthly_challenges.keys())
            if month > len(months):
                return HttpResponseNotFound("Invalid month")
            else:
                month = months[month - 1]
                return HttpResponseRedirect(f"/challenges/{month}")
    - list(monthly_challenges.keys()) -> ["january", "february", ..., "december"]
    - month - 1 because list index starts at 0 (month 1 -> months[0] -> "january").
    - Open http://127.0.0.1:8000/challenges/1
        -> browser is sent to /challenges/january -> January challenge.
    - /challenges/13 -> 13 > 12 -> 404 "Invalid month".
    - A redirect means TWO requests:
        1) /challenges/1        -> server answers 302 + Location: /challenges/january
        2) /challenges/january  -> server answers 200 + the challenge text
    - Watch out: /challenges/0 -> months[-1] = "december" (negative index = last item),
      so 0 is not caught by month > len(months).

## reverse() and named URLs (no hard-coded paths)

    - Problem: HttpResponseRedirect(f"/challenges/{month}") hard-codes "/challenges/".
      If "challenges/" changes in monthly_challenges/urls.py (e.g. to "challenge/"),
      the redirect breaks.
    - Step 1: give the URL a name in challenges/urls.py:
        path("<str:month>", views.monthly_challenge, name="month-challenge"),
    - Step 2: build the URL from that name in challenges/views.py:
        from django.urls import reverse

        redirect_path = reverse("month-challenge", args=[month])
        return HttpResponseRedirect(redirect_path)
    - reverse("month-challenge", args=["january"]) -> "/challenges/january"
      (args fills the <month> part; Django adds the "challenges/" prefix from include()).
    - Now the prefix can change in one place and every reverse() follows it.

## Returning HTML from a view (h1 + p)

    - HttpResponse can send HTML, not only plain text:
        def monthly_challenge(request, month):
            challenge_text = monthly_challenges.get(month)
            if challenge_text:
                response_data = f'<h1>{month.capitalize()}</h1><p>{challenge_text}</p>'
                return HttpResponse(response_data)
    - month.capitalize() -> "january" becomes "January".
    - /challenges/january -> big heading "January" + challenge text below it.

## Index page: list of month links (built with reverse())

    - challenges/urls.py -> empty path "" = /challenges/ itself:
        path("", views.index, name="index"),
    - challenges/views.py:
        def index(request):
            list_items = ""
            months = list(monthly_challenges.keys())
            for month in months:
                capitalized_month = month.capitalize()
                month_path = reverse("month-challenge", args=[month])
                list_items += f'<li><a href="{month_path}">{capitalized_month}</a></li>'
            return HttpResponse(f"<ul>{list_items}</ul>")
    - The loop builds one <li><a href="/challenges/january">January</a></li> per month,
      then wraps them all in <ul> ... </ul>.
    - reverse() makes each link, so no "/challenges/" is hard-coded.
    - Open http://127.0.0.1:8000/challenges/ -> bullet list of 12 clickable months.
    - Building HTML in Python strings gets messy fast -> templates solve this later.

## Section 3 complete (URLs and views)

## Section 4: Templates

## First template (challenges/templates/challenges/challenge.html)

    - HTML goes in a separate .html file instead of Python strings.
    - Folder: challenges/templates/challenges/challenge.html
      (the extra "challenges" folder inside templates = namespacing, so the
       template is loaded as "challenges/challenge.html" and won't clash
       with same-named templates from other apps).
    - challenge.html is a normal HTML page:
        <h1>This is the monthly challenge</h1>
        <h2> Go for walk</h2>

## render_to_string (template -> HTML string)

    - challenges/views.py:
        from django.template.loader import render_to_string

        def monthly_challenge(request, month):
            try:
                response_data = render_to_string("challenges/challenge.html")
                return HttpResponse(response_data)
            except:
                return HttpResponseNotFound(f"No challenge found for {month}")
    - render_to_string() finds the template, turns it into an HTML string,
      and HttpResponse sends it to the browser.
    - Right now every month shows the same page (no data passed in yet);
      even /challenges/hello shows it, because the dict is not checked.
    - Bare except: hides every error (e.g. a missing template also shows
      "No challenge found"), so real problems are harder to see.

## Error: TemplateDoesNotExist (how Django finds templates)

    - Got: TemplateDoesNotExist: challenges/challenge.html
    - settings.py -> TEMPLATES:
        'DIRS': []        -> extra folders to search (none at first)
        'APP_DIRS': True  -> search the templates/ folder of every app
                             listed in INSTALLED_APPS
    - "challenges" was NOT in INSTALLED_APPS, so its templates/ folder was skipped.
      (URLs/views still worked because include("challenges.urls") imports
       the code directly; templates are found a different way.)
    - Two fixes:
        1) Add the folder to DIRS (what I did):
             'DIRS': [BASE_DIR / "challenges" / "templates"],
        2) Register the app (the usual way):
             INSTALLED_APPS = [
                 'challenges',
                 ...
             ]
    - BASE_DIR = the folder with manage.py; "/" joins path parts (pathlib).

## Template variables ({{ }}) must match the context keys

    - View passes data as a dict (the "context"):
        render_to_string("challenges/challenge.html", {
            "text": challenge_text,
            "month_name": month,
        })
    - Template showed nothing for:
        This is the monthly challenge for {{ month }}
      because the key is "month_name", not "month".
    - Django renders an unknown variable as an EMPTY string - no error.
    - Fix: use {{ month_name }} in the template, or rename the key to "month".

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
    - Course code snapshot repository (branch per lesson):
        https://github.com/academind/django-practical-guide-course-code
    - Section 3 code snapshots = branches starting with "urls-views-...", e.g.:
        https://github.com/academind/django-practical-guide-course-code/tree/urls-views-01-adding-a-first-url-and-view
    - Section 3 module slides:
        https://github.com/academind/django-practical-guide-course-code/tree/urls-views-zz-extra-files
