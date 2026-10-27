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

## Handling the POST in the view + redirect to a thank-you page

    - reviews/views.py:
        from django.shortcuts import render
        from django.http import HttpResponseRedirect

        def review(request):
            if request.method == "POST":
                username = request.POST.get("username")
                print(username)
                return HttpResponseRedirect("/thank-you")

            return render(request, "reviews/review.html")

        def thank_you(request):
            return render(request, "reviews/thank_you.html")
    - reviews/urls.py:
        urlpatterns = [
            path("", views.review),
            path("thank-you", views.thank_you)
        ]
    - review.html: <form action="/" method="POST">  (action = WHERE to send;
      "/" is the same URL it would use anyway without action)
    - thank_you.html: <title>Thank you!</title> ... <body>Thank you!</body>
    - request.POST.get("username") vs request.POST["username"]:
      .get() returns None if the field is missing, [] raises an error.

## How a view runs: if first, return ends it

    - EVERY request calls the view function ONCE, top to bottom. The if is
      checked FIRST; the first return reached ends the function.
        GET  -> if is False -> skip block -> return render(review.html)
        POST -> if is True  -> return redirect -> render line never reached
    - Loading the page and clicking Send are TWO separate requests -> the
      function runs twice. The form page stays on screen from the first
      (GET) request until the browser loads the next page.

## The chain: URL / -> the "Your name" form (GET)

    1. feedback/urls.py:  path("", include("reviews.urls"))
       "" = nothing after 127.0.0.1:8000/ -> hand over to reviews/urls.py
    2. reviews/urls.py:   path("", views.review) -> call review()
    3. views.review: GET -> if skipped -> render(request, "reviews/review.html")
    4. APP_DIRS: True + 'reviews' in INSTALLED_APPS ->
       Django finds reviews/templates/reviews/review.html,
       fills in {% csrf_token %}, sends the HTML -> browser shows the form.

## The chain: after clicking Send (POST -> redirect -> GET)

    Round 1 - POST (sending the name)
    1. Browser reads <form action="/" method="POST">, collects every input
       as name=value: username=Sachin + csrfmiddlewaretoken=...
    2. Browser sends POST / with that data in the request BODY.
    3. Django's CSRF check runs BEFORE the view: token in form == token in
       cookie? yes -> continue (no -> 403, the view never runs).
    4. Same URL chain: / -> feedback/urls.py -> reviews/urls.py -> views.review
    5. review(): request.method == "POST" -> True
         username = request.POST.get("username")   # "Sachin" (by name=)
         print(username)                           # shows in runserver terminal
         return HttpResponseRedirect("/thank-you") # status 302, no page
       302 = "go to /thank-you instead".

    Round 2 - GET (the thank-you page)
    6. Browser AUTOMATICALLY sends GET /thank-you (address bar changes).
    7. /thank-you -> feedback/urls.py -> reviews/urls.py
       path("thank-you", views.thank_you)
    8. thank_you() -> render(request, "reviews/thank_you.html")
    9. Browser shows "Thank you!".

    runserver terminal for ONE click on Send:
        Sachin                              <- print(), step 5
        "POST / HTTP/1.1" 302               <- round 1
        "GET /thank-you HTTP/1.1" 200       <- round 2

## Why redirect instead of render after a POST? (Post/Redirect/Get)

    - If the POST returned a page directly, pressing F5 on it would make the
      browser SEND THE FORM AGAIN ("Confirm form resubmission?") -> later
      that would save the same review twice.
    - After a redirect, the page on screen came from a plain GET ->
      refreshing is safe. This pattern is called Post/Redirect/Get (PRG).

## Manual validation: empty name -> show the form again with an error

    - views.py:
        def review(request):
            if request.method == "POST":
                username = request.POST.get("username")
                print(username)

                if username == "":
                    return render(request, "reviews/review.html", {"has_error": True})
                return HttpResponseRedirect("/thank-you")

            return render(request, "reviews/review.html")
    - review.html (inside the form):
        {% if has_error %}
           <p>This form is invalid - please enter a valid username</p>
        {% endif %}
    - Invalid input -> NO redirect: render the same form again (200) with the
      error message. Valid -> redirect (302) to /thank-you.
      On the normal GET, has_error isn't passed at all -> {% if %} treats a
      missing variable as False -> no message.
    - Tested:
        username=""        -> 200, error message shown
        username="Sachin"  -> 302 /thank-you
        username="   "     -> 302 /thank-you  (spaces pass the == "" check!)
        no username field  -> 302 /thank-you  (.get() gives None, not "")
      Better check: if not username or not username.strip():
    - Problems with doing it by hand: the typed name is LOST when the form
      re-renders (input comes back empty), one if per rule per field, and
      the HTML must be kept in sync with the view. -> Django's Form class
      does all of this (next).
    - thank_you() passes {"has_error": False}, but thank_you.html never
      uses has_error -> not needed there.

## Helpful resources

    - Course code snapshot repository (branch per lesson):
        https://github.com/academind/django-practical-guide-course-code
    - Django docs:
        https://docs.djangoproject.com/en/6.0/
    - Working with forms:
        https://docs.djangoproject.com/en/6.0/topics/forms/
