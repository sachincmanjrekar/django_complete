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

## GET vs POST requests

    - Changed the form to POST:
        <form method="POST">
            ...
            <button type="submit">Send</button>
        </form>
      (type="submit" is already the default for a <button> inside a form,
       writing it just makes it clear.)
    - GET vs POST:

| | GET | POST |
|---|---|---|
| Used for | loading/reading a page, search, filters | sending data to SAVE or change something |
| Data goes | in the URL: `/?username=Sachin` | in the request BODY (not visible in the URL) |
| In Django | `request.GET["username"]` | `request.POST["username"]` |
| Bookmark / share / back button | yes | no (browser asks "resubmit form?") |
| Size limit | URL length | practically none (files too) |
| CSRF token needed | no | yes, `{% csrf_token %}` |
| Default for `<form>` | yes | `method="POST"` |

    - In the view: request.method is "GET" or "POST" - the same view handles
      both (show the empty form on GET, process the data on POST):
        def review(request):
            if request.method == "POST":
                entered_username = request.POST["username"]
                ...
            return render(request, "reviews/review.html")
    - Submitting the POST form WITHOUT a token ->
        403 Forbidden
        CSRF verification failed. Request aborted.
        (terminal: Forbidden (CSRF cookie not set.): /)
      CSRF = Cross-Site Request Forgery: another website could make YOUR
      browser send a POST to this site while you're logged in. Django blocks
      every POST that doesn't carry the secret token it gave the page.
      Fix - inside the form:
        <form method="POST">
            {% csrf_token %}
            ...
      -> renders <input type="hidden" name="csrfmiddlewaretoken" value="...">.

## Added {% csrf_token %} -> POST works

    - review.html:
        <form method="POST">
            {% csrf_token %}
            <label for="username">Your name:</label>
            <input id="username" name="username" type="text">
            <button type="submit">Send</button>
        </form>
    - Page now contains (see it with right-click > View page source):
        <input type="hidden" name="csrfmiddlewaretoken" value="6NZqCg2AKjGfwb2E...">
      hidden = not shown on the page, but sent along with the form.
    - Flow:
        GET  /  -> Django sets a csrftoken COOKIE + puts the token in the form
        POST /  -> browser sends cookie + csrfmiddlewaretoken field
                -> Django compares them -> match -> 200 (no more 403)
      Another site can't read the token, so it can't fake the POST.
    - Rule: EVERY <form method="POST"> in a Django template needs
      {% csrf_token %} inside the <form> tag. GET forms don't.
    - The view still doesn't read request.POST, so after Send the same page
      just shows again (next: handle the data in the view).

## Helpful resources

    - Course code snapshot repository (branch per lesson):
        https://github.com/academind/django-practical-guide-course-code
    - Django docs:
        https://docs.djangoproject.com/en/6.0/
    - Working with forms:
        https://docs.djangoproject.com/en/6.0/topics/forms/
