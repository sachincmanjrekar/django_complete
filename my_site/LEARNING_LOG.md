## django-admin startproject my_site

    - Creates a new Django project named "my_site" (inside django_complete/,
      next to mypage and monthly_challenges).
    - Makes a folder "my_site" containing:
        manage.py        -> tool to run project commands (runserver, migrate, startapp, ...)
        my_site/         -> project settings package
            __init__.py  -> marks the folder as a Python package
            settings.py  -> project configuration (installed apps, database, etc.)
            urls.py      -> main URL routes of the site
            asgi.py      -> entry point for async web servers
            wsgi.py      -> entry point for regular web servers

## Helpful resources

    - Course code snapshot repository (branch per lesson):
        https://github.com/academind/django-practical-guide-course-code
    - Django docs:
        https://docs.djangoproject.com/en/6.0/
    - Path converters (str, int, slug, uuid, path) in URLs:
        https://docs.djangoproject.com/en/3.1/topics/http/urls/#path-converters
    - PEP 8 (Python style guide):
        https://peps.python.org/pep-0008/
