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

## Template namespacing - why "challenges/challenge.html" (best practice)

    - Django does NOT look for templates per app. All templates/ folders
      (DIRS + every installed app) act like ONE shared space, searched in
      order; the FIRST match wins.
    - Without namespacing, same file names clash:
        challenges/templates/index.html
        blog/templates/index.html
      render_to_string("index.html") -> picks whichever app is first in
      INSTALLED_APPS, so one app can silently show the other app's page.
    - With namespacing (extra folder named after the app):
        challenges/templates/challenges/index.html  ->  "challenges/index.html"
        blog/templates/blog/index.html              ->  "blog/index.html"
      The app name is part of the template name, so no clash is possible.
    - Bonus: "challenges/challenge.html" in a view shows which app it belongs to.
    - challenges/templates/challenges/ looks doubled, but it's the standard layout
      (Django's own tutorial uses polls/templates/polls/).

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
        1) Add the folder to DIRS (first try):
             'DIRS': [BASE_DIR / "challenges" / "templates"],
        2) Register the app (the usual way):
             INSTALLED_APPS = [
                 'challenges',
                 ...
             ]
    - BASE_DIR = the folder with manage.py; "/" joins path parts (pathlib).

## Another way: register the app in INSTALLED_APPS (APP_DIRS)

    - Switched from fix 1 to fix 2 in monthly_challenges/settings.py:
        INSTALLED_APPS = [
            ...
            'django.contrib.staticfiles',
            "challenges",
        ]

        TEMPLATES = [
            {
                'DIRS': [
                    # BASE_DIR / "challenges" / "templates"
                ],
                'APP_DIRS': True,
                ...
    - Now APP_DIRS finds challenges/templates/ automatically, so DIRS isn't needed.
    - Why this way is better:
        every new app's templates/ folder is found without editing DIRS
        registering the app is also needed later for models, migrations, admin
    - DIRS is still useful for project-level templates that belong to no app
      (e.g. a shared base.html in a top-level templates/ folder).

## render() shortcut (instead of render_to_string + HttpResponse)

    - challenges/views.py:
        from django.shortcuts import render

        def monthly_challenge(request, month):
            try:
                challenge_text = monthly_challenges.get(month)
                if challenge_text:
                    return render(request, "challenges/challenge.html")
                else:
                    return HttpResponseNotFound(f"No challenge found for {month}")
            except:
                return HttpResponseNotFound(f"No challenge found for {month}")
    - Before (2 steps):
        response_data = render_to_string("challenges/challenge.html")
        return HttpResponse(response_data)
    - After (1 step):
        return render(request, "challenges/challenge.html")
    - render() = render_to_string() + HttpResponse() in one call.
      It also takes the request (needed later, e.g. for {% csrf_token %} in forms).
    - render was already imported at the top by startapp
      ("from django.shortcuts import render"); the render_to_string import was removed.
    - The dict is checked again: unknown months (e.g. /challenges/hello) -> 404.

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

## Passing context with render() and showing it in the template

    - challenges/views.py -> 3rd argument of render() is the context dict:
        return render(request, "challenges/challenge.html", {
            "text": challenge_text,
            "month_name": month,
        })
    - challenge.html uses the keys inside {{ }}:
        <h1>This is the monthly challenge</h1>
        <h2>{{ month_name.capitalize }}</h2>
        <p>{{ text }}</p>
    - /challenges/january -> h2 "January" + p "Eat no meat for the entire month!"
    - {{ month_name.capitalize }} calls the Python string method
      WITHOUT () - in templates, methods are called automatically
      (writing .capitalize() would be an error).
    - The page now changes per month (before, every month showed "Go for walk").

## Template filters ({{ value|filter }})

    - A filter changes how a value is SHOWN in the template (the data itself
      is not changed). Syntax: variable | filter name, no spaces needed.
    - challenge.html, replaced the method call with a filter:
        before: <h2>{{ month_name.capitalize }}</h2>
        after:  <h2>{{ month_name|title }}</h2>
      Both show "January"; filters are the Django-template way to do it.
    - Some built-in filters:
        {{ name|title }}        -> "hello world" -> "Hello World"
        {{ name|upper }}        -> "HELLO WORLD"
        {{ name|lower }}        -> "hello world"
        {{ name|capfirst }}     -> "Hello world"  (first letter only)
        {{ text|length }}       -> number of characters / items
        {{ text|truncatewords:3 }} -> first 3 words + "..."
        {{ value|default:"none" }} -> "none" if value is empty/False
    - Filters can take an argument after ":" and can be chained:
        {{ text|lower|truncatewords:3 }}
    - Full list: https://docs.djangoproject.com/en/6.0/ref/templates/builtins/#built-in-filter-reference

## Index page with a template: {% for %} tag

    - challenges/views.py -> index() no longer builds HTML strings:
        def index(request):
            months = list(monthly_challenges.keys())
            return render(request, "challenges/index.html", {"months": months})
    - challenges/templates/challenges/index.html:
        <ul>{% for month in months %}
            <li>
                <a href="{% url 'month-challenge' month %}">{{ month|title }}</a>
            </li>{% endfor %}
        </ul>
    - {{ }}  -> OUTPUT a value          ({{ month|title }})
      {% %}  -> a TAG = logic/command   ({% for %}, {% url %}, {% if %} ...)
    - {% for month in months %} ... {% endfor %} repeats the HTML once per month.
      Like a Python for loop, but it MUST be closed with {% endfor %}.
    - Before (Python string building in index()):
        list_items += f'<li><a href="{month_path}">{capitalized_month}</a></li>'
        return HttpResponse(f"<ul>{list_items}</ul>")
      After: the view only passes data; the template does the HTML.
    - Leftovers in index() that are no longer used: list_items = "" and
      the reverse import (still used by monthly_challenge_by_number though).

## {% url %} tag = reverse() inside templates

    - In the view (Python):
        reverse("month-challenge", args=[month])        -> "/challenges/january"
    - In the template:
        {% url 'month-challenge' month %}               -> "/challenges/january"
    - Same idea: build the URL from the route NAME, never hard-code "/challenges/".
    - 'month-challenge' = name="month-challenge" in challenges/urls.py;
      month = the value for <str:month> (more values -> more args, space-separated).
    - If the "challenges/" prefix changes in monthly_challenges/urls.py,
      every {% url %} link updates automatically.

## {% if %} tag (conditions in templates)

    - challenge.html:
        <h2>{{ month_name|title }}</h2>
        {% if text %}
            <p>{{ text }}</p>
        {% else %}
            <p>No challenge found for {{ month_name|title }}.</p>
        {% endif %}
    - Like Python if/else, but MUST be closed with {% endif %}.
      ({% elif ... %} also exists.)
    - {% if text %} is False for None, "", 0, empty list - same as Python.
    - challenges/views.py -> the view no longer checks; it always renders
      and lets the template decide:
        challenge_text = monthly_challenges.get(month)
        return render(request, "challenges/challenge.html", {
            "text": challenge_text,
            "month_name": month,
        })
    - /challenges/january  -> "Eat no meat for the entire month!"
      /challenges/december -> text is None -> "No challenge found for December."
    - Note: unknown months (e.g. /challenges/hello) now also get this page with
      status 200 instead of a 404 - the page says "not found" but the HTTP
      status says OK.

## Template inheritance ({% extends %} and {% block %})

    - Problem: challenge.html and index.html both repeated the same
      <!DOCTYPE html>, <head>, <meta>, <title>, <body> ... boilerplate.
    - Solution: write it ONCE in a parent template, children fill in the gaps.
    - Parent: monthly_challenges/templates/base.html (project level, no app):
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{% block title %}My Hcallenges Challenge{% endblock %}</title>
        </head>
        <body>
        {% block content %}
        {% endblock %}
        </body>
        </html>
    - {% block name %} ... {% endblock %} = a named gap a child can replace.
      Text inside the parent's block = DEFAULT, used if the child doesn't override it.
    - Child: challenges/templates/challenges/index.html:
        {% extends "base.html" %}
        {% block title %}All extended challenges{% endblock %}
        {% block content %}
            <ul>{% for month in months %} ... {% endfor %}</ul>
        {% endblock %}
    - Child: challenge.html:
        {% extends "base.html" %}
        {% block title %}All extended individual challenges{% endblock %}
        {% block content %}
            <h1>This is the monthly challenge</h1>
            ...
        {% endblock %}
    - Rules:
        {% extends %} must be the FIRST tag in the child template
        only content inside {% block %} tags is used from the child
        block names must match the parent's (title, content)
    - Change base.html once -> every page that extends it changes.

## Project-level templates folder (DIRS)

    - base.html belongs to no single app -> lives in monthly_challenges/templates/
      (next to manage.py), not inside challenges/.
    - APP_DIRS only searches apps, so the folder is added to DIRS in settings.py:
        'DIRS': [
            # BASE_DIR / "challenges" / "templates"
            BASE_DIR / "templates"
        ],
    - {% extends "base.html" %} -> Django finds it in BASE_DIR / "templates".
    - This is the "DIRS is still useful for project-level templates" case
      noted earlier.

## {% include %} tag (reusable template pieces)

    - A small HTML snippet used in several pages -> own file, pulled in with include.
    - challenges/templates/challenges/includes/header.html (not a full page,
      just the piece):
        <header>
            <nav>
                <a href="{% url 'index' %}">All challenges</a>
            </nav>
        </header>
    - Used in BOTH index.html and challenge.html, inside {% block content %}:
        {% include "challenges/includes/header.html" %}
    - {% url 'index' %} -> name="index" in challenges/urls.py -> /challenges/
      (a link back to the list from every page).
    - includes/ subfolder = just a convention to keep snippets apart from pages.
    - The included file sees the same variables as the page that includes it
      (e.g. month_name). Extra ones can be passed:
        {% include "challenges/includes/header.html" with active_page="index" %}
    - extends vs include:
        {% extends %}  -> my page fits INTO a parent layout (one per template, first tag)
        {% include %}  -> a piece is put INTO my page (as many as needed, anywhere)

## More on DTL (Django Template Language) - it is NOT Python

    - DTL looks like Python but is a separate language parsed by Django,
      so some syntax is different.
    - Dictionary fields -> dot notation, NOT square brackets:
        wrong:  {{ myDictionary['some_key'] }}
        right:  {{ myDictionary.some_key }}
    - Calling functions -> NO parentheses, use them like a variable:
        wrong:  {{ result_from_a_function() }}
        right:  {{ result_from_a_function }}
      (Same as {{ month_name.capitalize }} earlier - Django calls it for me.
       Because of this, functions that need arguments can't be called in
       templates; do that work in the view or use a filter.)
    - The dot does all lookups: for {{ a.b }} Django tries, in order,
        dictionary key   a["b"]
        attribute/method a.b   (called if it's a method)
        list index       a[b]  (e.g. {{ months.0 }} -> "january")

## Custom 404 page (404.html + HttpResponseNotFound)

    - monthly_challenges/templates/404.html (project level, extends base.html):
        {% extends "base.html" %}
        {% block title %}Page Not Found{% endblock %}
        {% block content %}
            <h1>Page Not Found</h1>
            <p>The requested page could not be found.</p>
        {% endblock %}
    - challenges/views.py:
        from django.template.loader import render_to_string

        def monthly_challenge(request, month):
            try:
                challenge_text = monthly_challenges[month]
                return render(request, "challenges/challenge.html", {
                    "text": challenge_text,
                    "month_name": month,
                })
            except:
                rendered_string = render_to_string("404.html")
                return HttpResponseNotFound(rendered_string)
    - .get(month) -> returns None for an unknown key (no error)
      [month]     -> raises KeyError for an unknown key -> goes to except
      So the switch to [month] is what makes try/except work now.
    - /challenges/hello   -> KeyError -> 404.html with status 404 (fixes the
                             200-for-unknown-month issue from the if-tag entry)
      /challenges/december -> key exists (value None) -> challenge.html,
                             {% if text %} shows "No challenge found for December."
    - render_to_string() gives just the HTML string, which goes into
      HttpResponseNotFound to send status 404 (render() alone sends 200).
      Same result in one line: render(request, "404.html", status=404)
    - Better: catch only the expected error, so other bugs aren't hidden:
        except KeyError:

## raise Http404 (Django's built-in 404) and DEBUG

    - challenges/views.py:
        from django.http import Http404

        def monthly_challenge(request, month):
            try:
                challenge_text = monthly_challenges[month]
                return render(request, "challenges/challenge.html", {...})
            except:
                raise Http404()
    - raise (not return): Http404 is an exception; Django catches it and
      builds the 404 response itself.
    - Which page is shown depends on DEBUG in settings.py:
        DEBUG = True  (development, now):
            Django's yellow debug "Page not found (404)" page with details
            (URL patterns tried, etc.) - my 404.html is NOT used.
        DEBUG = False (real deployment):
            Django automatically renders a template named 404.html
            (found in templates/ via DIRS) -> my custom page shows up.
    - So 404.html only needs the exact name "404.html" in a templates folder;
      no view code has to load it (render_to_string version not needed).
    - DEBUG = False also needs ALLOWED_HOSTS set, otherwise runserver fails:
        CommandError: You must set settings.ALLOWED_HOSTS if DEBUG is False.
      To test locally: ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
    - Never deploy with DEBUG = True: the debug page shows code, settings and
      URL lists to anyone.

## Adding static files (CSS) to an app

    - Static files = files sent as-is to the browser (CSS, JS, images).
    - Folder: challenges/static/challenges/challenges.css
      (same namespacing idea as templates: static/<app name>/...)
        ul {
            list-style: none;
        }
    - Found automatically because:
        'django.contrib.staticfiles' is in INSTALLED_APPS (default)
        "challenges" is in INSTALLED_APPS -> its static/ folder is searched
        STATIC_URL = 'static/' -> files are served under /static/...
    - base.html gets a new EMPTY block in <head> for page-specific CSS:
        <title>{% block title %}...{% endblock %}</title>
        {% block css_files %}
        {% endblock %}
    - index.html fills that block:
        {% extends "base.html" %}
        {% load static %}

        {% block css_files %}
            <link rel="stylesheet" href="{% static 'challenges/challenges.css' %}">
        {% endblock %}
    - {% load static %} -> makes the static tag available in THIS template
      (needed in every template that uses it, even if base.html loads it;
       goes after {% extends %}, which must stay first).
    - {% static 'challenges/challenges.css' %} -> "/static/challenges/challenges.css"
      (like {% url %} for static files: never hard-code "/static/").
    - Result: /challenges/ list has no bullet points.
    - Static files are served by runserver only while DEBUG = True;
      in deployment the web server serves them (collectstatic, later).

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
    - Built-in template tags and filters (title, upper, length, default, for, if...):
        https://docs.djangoproject.com/en/6.0/ref/templates/builtins/
