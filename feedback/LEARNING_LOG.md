## Section 10 begins (Forms)

## django-admin startproject feedback

    - New Django project "feedback" (inside django_complete/, next to mypage,
      monthly_challenges, my_site and book_store) - for learning forms.
    - Makes a folder "feedback" containing:
        manage.py          -> tool to run project commands (runserver, migrate, startapp, ...)
        feedback/          -> project settings package
            __init__.py    -> marks the folder as a Python package
            settings.py    -> project configuration (installed apps, database, etc.)
            urls.py        -> main URL routes of the site
            asgi.py        -> entry point for async web servers
            wsgi.py        -> entry point for regular web servers
    - No app yet (next: python manage.py startapp ...), no db.sqlite3 until
      the first migrate.

## App "reviews" + a first plain HTML form

    - python manage.py startapp reviews -> reviews/ (views, models, admin,
      migrations/, ...), added 'reviews' to INSTALLED_APPS in settings.py.
    - feedback/urls.py:
        from django.urls import path, include
        urlpatterns = [
            path('admin/', admin.site.urls),
            path("", include("reviews.urls"))
        ]
    - reviews/urls.py:
        urlpatterns = [
            path("", views.review)
        ]
    - reviews/views.py:
        def review(request):
            return render(request, "reviews/review.html")
    - reviews/templates/reviews/review.html:
        <form>
            <label for="username">Your name:</label>
            <input id="username" name="username" type="text">
            <button>Send</button>
        </form>
    - label for="username" <-> input id="username": clicking the label focuses
      the input. name="username" = the KEY the value is sent under.
    - A <form> with no method/action: method defaults to GET, action defaults
      to the SAME URL. Clicking Send loads:
        http://127.0.0.1:8000/?username=Sachin
      -> data in the URL as a query string. Django puts it in request.GET:
        <QueryDict: {'username': ['Sachin']}>
      The view ignores it for now, so the page just reloads.
      GET = for reading/searching; sending data to SAVE -> method="POST"
      (next step, needs {% csrf_token %}).
    - db.sqlite3 appeared (created by runserver), but it's EMPTY:
      0 migrations applied -> runserver warns about unapplied migrations
      until python manage.py migrate.

## Helpful resources

    - Course code snapshot repository (branch per lesson):
        https://github.com/academind/django-practical-guide-course-code
    - Django docs:
        https://docs.djangoproject.com/en/6.0/
    - Working with forms:
        https://docs.djangoproject.com/en/6.0/topics/forms/
