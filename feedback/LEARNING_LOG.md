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

## Django Form class (forms.py) + {{ form }}

    - New file reviews/forms.py (convention: forms live next to views/models):
        from django import forms

        class ReviewForm(forms.Form):
            user_name = forms.CharField()
      Like a model: a class with fields - but it describes a FORM (inputs +
      validation), not a database table. No migration.
    - views.py (old manual POST code commented out for now):
        from .forms import ReviewForm

        def review(request):
            form = ReviewForm()
            return render(request, "reviews/review.html", {"form": form})
    - review.html - the hand-written label/input/error replaced by one tag:
        <form action="/" method="POST">
            {% csrf_token %}
            {{ form }}
            <button type="submit">Submit</button>
        </form>
    - {{ form }} renders:
        <div>
            <label for="id_user_name">User name:</label>
            <input type="text" name="user_name" required id="id_user_name">
        </div>
      Generated from the field:
        label        "User name:"   <- field name, _ -> space, capitalised
        name=        "user_name"    <- field name (so request.POST["user_name"],
                                       not "username" like before)
        id / for     "id_user_name" <- "id_" + field name, linked automatically
        required                    <- CharField is required by default ->
                                       browser blocks an empty Submit itself
    - Not handled yet: the view ignores request.method -> submitting just
      shows an empty form again (200, no redirect). Next step below.

## Validating with the Form: is_valid() and cleaned_data

    - views.py:
        def review(request):
            if request.method == "POST":
                form = ReviewForm(request.POST)       # "bound" form: has data

                if form.is_valid():
                    print("clean data received:", form.cleaned_data)
                    return HttpResponseRedirect("/thank-you")
                else:
                    print("clean data not received")
            else:
                form = ReviewForm()                   # "unbound" form: empty

            return render(request, "reviews/review.html", {"form": form})
    - form.is_valid()   runs every field's checks (required, max_length, ...)
      form.cleaned_data dict of checked + converted values, ONLY after is_valid():
                          {'user_name': 'Sachin'}
      form.errors        what went wrong, per field
    - Invalid POST -> render the SAME bound form -> {{ form }} shows the error
      AND keeps the typed value:
        <ul class="errorlist" id="id_user_name_error"><li>This field is required.</li></ul>
    - My first version - BUG:
        if request.method == "POST":
            form = ReviewForm(request.POST)
            if form.is_valid():
                ...
                return HttpResponseRedirect("/thank-you")

        form = ReviewForm()        # ran after an INVALID POST too
        # print(form.cleaned_data)
      -> the bound form (with errors) was overwritten by an empty one:
         no error message, input empty. Fix = create the empty form only
         in the else (GET) branch.
      (print(form.cleaned_data) on an empty form -> AttributeError:
       cleaned_data only exists after is_valid().)
    - Spaces only "   " -> CharField strips it -> "" -> "This field is
      required." (the browser's `required` check doesn't catch spaces).

## Spaces stay in the input after an error -> strip before binding

    - Problem: after typing "   " the error showed, but the box came back as
      value="   " -> had to backspace. A re-rendered form shows the RAW
      submitted data, not cleaned_data (normally good: you don't retype a
      long value because of one mistake).
    - Fix in views.py - strip before creating the form:
        if request.method == "POST":
            data = request.POST.copy()                              # request.POST can't be edited
            data["user_name"] = data.get("user_name", "").strip()   # "   " -> ""
            form = ReviewForm(data)
    - Tested:
        "   "         -> 200, "This field is required.", input EMPTY
        "  Sachin  "  -> {'user_name': 'Sachin'} -> 302 /thank-you
        "Sachin"      -> 302 /thank-you
    - Downside: one line per field. For many fields, strip everything once
      in a base form class instead:
        class StrippedForm(forms.Form):
            def __init__(self, data=None, *args, **kwargs):
                if data is not None:
                    data = data.copy()
                    for key in data:
                        data.setlist(key, [value.strip() for value in data.getlist(key)])
                super().__init__(data, *args, **kwargs)

        class ReviewForm(StrippedForm):
            user_name = forms.CharField()
      (getlist/setlist keep multi-value fields like checkboxes working)

## Field options: label, max_length, error_messages

    - forms.py:
        class ReviewForm(forms.Form):
            user_name = forms.CharField(label="Your Name",
                                        max_length=10,
                                        error_messages={"required": "Please enter your name.",
                                                        "max_length": "Your name is too long."})
    - label="Your Name"   replaces the automatic "User name:" -> "Your Name:"
      max_length=10       server check in is_valid() + Django adds
                          maxlength="10" to the <input>
      error_messages      own text per error type, keys = error codes
                          ("required", "max_length", "invalid", ...)
    - Rendered input: <input type="text" name="user_name" maxlength="10" required id="id_user_name">
    - Tested:
        "   "               -> 200, "Please enter your name."
        "Sachin"            -> 302 /thank-you
        "Sachin Manjrekar"  -> 200, "Your name is too long." (16 chars, value kept)
    - In the browser I can't even type an 11th character (maxlength). The
      server message only shows when someone sends the POST directly
      (DevTools: delete maxlength, curl/Postman/script).
    - Three layers:

| Layer | Stops | Can be bypassed? |
|---|---|---|
| Browser `maxlength="10"` / `required` | normal users typing | yes: DevTools, scripts |
| CSRF check | POSTs not coming from my own page | only with a valid token |
| `form.is_valid()` on the server | everything: too long, empty, ... | no |

      -> browser checks = convenience, server checks = real protection.
      A direct POST with a valid CSRF token but a 16-char name gets 200 +
      "Your name is too long.", no redirect, nothing used/saved.
      Without a valid token -> 403 before the view even runs.

## Rendering form fields by hand (instead of {{ form }})

    - review.html:
        <form action="/" method="POST">
            {% csrf_token %}
            <div class="form-control {% if form.user_name.errors %} errors {% endif %}">
                {{ form.user_name.label_tag }}
                {{ form.user_name }}
                {{ form.user_name.errors }}
            </div>
            <br>
            <button type="submit">Submit</button>
        </form>
    - Each piece of one field:
        form.user_name.label_tag  -> <label for="id_user_name">Your Name:</label>
        form.user_name            -> <input type="text" name="user_name" ...>
        form.user_name.errors     -> <ul class="errorlist">...</ul> (empty if none)
      -> full control over the HTML around each field (wrapper div, classes,
         order) - {{ form }} decides all of that itself.
    - {% if form.user_name.errors %} errors {% endif %} adds a CSS class ONLY
      when the field has an error -> lets CSS style the invalid field.
    - forms.py: required message changed to "Please enter your valid name."
    - Rendered on GET:
        <div class="form-control ">
            <label for="id_user_name">Your Name:</label>
            <input type="text" name="user_name" maxlength="10" required id="id_user_name">
        </div>
      Rendered after an invalid POST ("   "):
        <div class="form-control  errors ">
            <label for="id_user_name">Your Name:</label>
            <input type="text" name="user_name" maxlength="10" required
                   aria-invalid="true" aria-describedby="id_user_name_error" id="id_user_name">
            <ul class="errorlist" id="id_user_name_error"><li>Please enter your valid name.</li></ul>
        </div>
      Differences: "errors" class on the div, aria-invalid / aria-describedby
      on the input (for screen readers), and the errorlist <ul>.
    - No CSS linked yet -> the errors class has no visible effect so far.
    - Spaces inside {% if %} ... {% endif %} -> double spaces in class="".
      Harmless; {% if form.user_name.errors %}errors{% endif %} is tidier.

## Inspecting the rendered HTML in the browser

    - Django sends plain HTML - template tags are gone by then. To see what
      it actually produced:
        Right-click the page > View page source (Ctrl+U)
          -> the HTML exactly as the server sent it (read-only).
        Right-click an element > Inspect (F12 / Ctrl+Shift+I) > Elements tab
          -> the live page; hover a line to highlight it, can edit to try
             things out (changes vanish on reload).
    - To compare the two states:
        1) open http://127.0.0.1:8000/, Inspect the input -> div is
           class="form-control", no errorlist
        2) submit only spaces -> Inspect again -> div is
           class="form-control errors", errorlist <ul> below the input,
           input has aria-invalid="true"
    - Network tab (F12 > Network) shows the requests:
        POST /            -> 200 (invalid, form shown again)
        POST / -> 302 + GET /thank-you   (valid)
      Click the POST -> Payload tab shows what was sent:
        csrfmiddlewaretoken, user_name
    - Elements tab is also where I can delete maxlength="10" to test the
      server-side "Your name is too long." message.

## Styling the form + error state (static CSS)

    - New file reviews/static/reviews/styles.css (app static folder,
      namespaced with the app name like templates).
    - review.html:
        {% load static %}
        ...
        <title>Your Review</title>
        <link rel="stylesheet" href="{% static 'reviews/styles.css' %}">
      -> renders href="/static/reviews/styles.css"
      (python manage.py findstatic reviews/styles.css -> shows where
       Django finds it; DEBUG = True -> runserver serves it)
    - Main CSS rules:
        form                       white card, centered, rounded, shadow
        button / button:hover      purple #1f0050 -> #320777, pointer cursor
        .form-control label        bold, on its own line (display: block)
        .form-control input:focus  purple border, light purple background
        .errorlist                 no bullets, dark red text
        .errors input              red border, pink background
        .errors label              red
      .errors only matches when the div got the "errors" class from
        {% if form.user_name.errors %} errors {% endif %}
      -> invalid submit = whole field turns red, valid = normal.
    - Mistake: <link rel="stylesheet" href="{% static 'reviews/styles.css' %}"
      had no closing > -> the browser read "</head" as part of the link tag.
      CSS may still load (browsers are forgiving) but the HTML is broken.
      Fixed: ...styles.css' %}">
    - After CSS changes: Ctrl+F5 / Empty Cache and Hard Reload.

## More fields: Textarea widget + IntegerField

    - forms.py:
        review_text = forms.CharField(label="your Feedback",
                                      widget=forms.Textarea,
                                      max_length=200)
        rating = forms.IntegerField(label="Your Rating", min_value=1, max_value=5)
    - review.html: same block per field (wrapper div + label_tag + field + errors):
        <div class="form-control {% if form.review_text.errors %} errors {% endif %}">
            {{ form.review_text.label_tag }}
            {{ form.review_text }}
            {{ form.review_text.errors }}
        </div>
        (and the same for rating)
    - widget = which HTML element draws the field. Field type = how the value
      is validated/converted; widget = how it LOOKS:
        CharField()                         -> <input type="text">
        CharField(widget=forms.Textarea)    -> <textarea cols="40" rows="10" maxlength="200">
        IntegerField(min_value=1, max_value=5)
                                            -> <input type="number" min="1" max="5">
                                               (browser arrows, blocks outside 1-5)
    - Tested:
        Sachin / "Great" / 4  -> 302 /thank-you
            cleaned_data = {'user_name': 'Sachin', 'review_text': 'Great', 'rating': 4}
            -> rating sent as text "4", comes out as the NUMBER 4
        review "   ", rating 9 -> "This field is required."
                                  "Ensure this value is less than or equal to 5."
        rating "abc"           -> "Enter a whole number."
        only the name          -> "This field is required." x2
    - To tidy:
        - CSS targets only "input" (.form-control input, .errors input) ->
          the <textarea> isn't styled and doesn't turn red on error. Use
          ".form-control input, .form-control textarea" etc.
        - views.py strips only user_name -> spaces stay in the textarea after
          an error (the "one line per field" problem) -> StrippedForm idea.
        - label "your Feedback" - lowercase y vs "Your Name" / "Your Rating".

## Looping over the form's fields ({% for field in form %})

    - review.html - the 3 copied blocks replaced by one loop:
        {% for field in form %}
        <div class="form-control {% if field.errors %} errors {% endif %}">
            {{ field.label_tag }}
            {{ field }}
            {{ field.errors }}
        </div>
        {% endfor %}
    - Looping over a form gives each field ("bound field") in the ORDER they
      are defined in forms.py: user_name, review_text, rating.
      field.label_tag / field / field.errors = same parts as
      form.user_name.label_tag etc., just generic.
    - New fields added to ReviewForm show up automatically - no template change.
      Still my own wrapper HTML (unlike {{ form }}), so styling stays in my hands.
    - Tested:
        GET                -> 3 form-control blocks: Your Name / your Feedback / Your Rating
        POST rating = 9    -> only the rating div gets "errors":
                              "Ensure this value is less than or equal to 5."
        valid POST         -> 302 /thank-you
    - Same to-dos as before: textarea CSS, strip spaces in all fields,
      "your Feedback" capital Y.

## Saving the form data to the database (Review model)

    - models.py:
        class Review(models.Model):
            user_name = models.CharField(max_length=10)
            review_text = models.TextField()
            rating = models.IntegerField()
    - makemigrations -> reviews/migrations/0001_initial.py (CreateModel Review),
      migrate -> table reviews_review. This was the project's first migrate,
      so Django's built-in apps (auth, admin, sessions, ...) were applied too
      (19 migrations in total).
    - views.py:
        from .models import Review
        ...
        if form.is_valid():
            review = Review(user_name=form.cleaned_data['user_name'],
                            review_text=form.cleaned_data['review_text'],
                            rating=form.cleaned_data['rating'])
            review.save()
            return HttpResponseRedirect("/thank-you")
    - Flow: form checks the input -> cleaned_data (already stripped, rating
      already an int) -> copied into a model object -> save() = INSERT.
    - DB after my test submit:
        reviews_review: (1, 'Sachin', 'good mate', 3)
    - Checked: a valid POST -> 302 /thank-you + exactly 1 new row, rating
      stored as the number 5. (Tested inside a transaction and rolled back,
      so my data stayed at 1 review.)
    - Duplication: form and model both describe the same 3 fields and limits
      (max_length=10 twice). The 1-5 rating rule is ONLY in the form - the
      model's IntegerField has no MinValueValidator/MaxValueValidator, so a
      review made in the shell/admin could have any rating.
      -> ModelForm: build the form FROM the model, define fields once (next).

## ModelForm: the form built from the model

    - forms.py (old forms.Form version kept as comments):
        from django import forms
        from .models import Review

        class ReviewForm(forms.ModelForm):
            class Meta:
                model = Review
                fields = '__all__'          # or ['user_name', 'rating'], or exclude = [...]
                labels = {"user_name": "Your Name",
                          "review_text": "Your Feedback",
                          "rating": "Your Rating"}
                error_messages = {"user_name": {"required": "Please enter your valid name.",
                                                "max_length": "Your name is too long."}}
    - class Meta = settings for the form (like Meta on a model). Fields are
      NOT written again - Django creates them from the model fields:
        CharField(max_length=10)  -> <input type="text" maxlength="10">
        TextField()               -> <textarea>  (no widget= needed)
        IntegerField()            -> <input type="number">
    - labels / error_messages / widgets in Meta are dicts keyed by field name.
    - views.py - the form saves itself:
        if form.is_valid():
            form.save()             # creates the Review from cleaned_data + INSERT
            return HttpResponseRedirect("/thank-you")
      and `from .models import Review` is no longer needed in views.py.
    - Mistake on the way: deleted the Review(...) lines but kept review.save() ->
        AttributeError: 'function' object has no attribute 'save'
      "review" was now the VIEW FUNCTION itself (def review(request)) - the
      only thing left with that name. Fixed with form.save().
    - Tested: valid POST -> 1 new row ('Test', 'Nice', 5) + 302 /thank-you
      (rolled back afterwards); empty name -> "Please enter your valid name.".
    - LOST in the switch - a ModelForm only knows the model's rules:
        rating 1-5      (was min_value/max_value on the form) -> 9 accepted!
        feedback <=200  (was max_length=200 on the form)      -> no limit
      Fix = put the rules on the MODEL (also protects admin/shell), then
      makemigrations + migrate:
        review_text = models.TextField(max_length=200)
        rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

## Class-based view: ReviewView(View) with get() and post()

    - views.py - the review function became a class:
        from django.views import View

        class ReviewView(View):
            def get(self, request):
                form = ReviewForm()
                return render(request, "reviews/review.html", {"form": form})

            def post(self, request):
                data = request.POST.copy()
                data["user_name"] = data.get("user_name", "").strip()
                form = ReviewForm(data)

                if form.is_valid():
                    form.save()
                    return HttpResponseRedirect("/thank-you")
                else:
                    print("clean data not received")
                    return render(request, "reviews/review.html", {"form": form})
    - urls.py:
        path("", views.ReviewView.as_view()),
      URLs need a FUNCTION -> .as_view() turns the class into one.
    - No more `if request.method == "POST":` - Django calls the method named
      after the request: GET -> get(), POST -> post(). Any other method
      (PUT, DELETE, ...) -> 405 Method Not Allowed automatically.
      self = the view object, request is passed in like before.
    - Mistake: post() had no return in the else branch ->
        ValueError: The view reviews.views.view didn't return an HttpResponse
        object. It returned None instead.
      In the old function, an invalid form fell through to the shared
      `return render(...)` at the bottom - in the class each method needs its
      OWN return. Every Django view must return a response.
      Fixed: render the bound form (with its errors) in the else branch.
    - Tested: GET 200 / valid POST saved + 302 /thank-you /
      invalid POST 200 "Please enter your valid name."
    - This is the BASE View class. Generic class-based views come next:
      TemplateView, FormView, CreateView, ListView, DetailView... - they do
      the common steps (render template, validate form, save, redirect) for you.

## Section 10 complete (Forms)

## Section 11 begins (Class-based views in detail)

    - Same feedback project. Starting point: ReviewView(View) with get()/post()
      and a function view thank_you. Next: generic class-based views
      (TemplateView, ListView, DetailView, FormView, CreateView) that do the
      usual steps for you.

## Base template: base.html + {% extends %}

    - New reviews/templates/reviews/base.html - the shared page skeleton:
        {% load static %}
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{% block title %}{% endblock %}</title>
            <link rel="stylesheet" href="{% static 'reviews/styles.css' %}">
        </head>
        <body>
            {% block content %}{% endblock %}
        </body>
        </html>
    - review.html / thank_you.html now only fill the blocks:
        {% extends "reviews/base.html" %}
        {% block title %}Your Review{% endblock %}       (thank_you: Form submitted)
        {% block content %} ...form... {% endblock %}    (thank_you: Thank you!)
    - Both pages get the stylesheet from base.html -> thank-you page is
      styled now too. {% load static %} is needed in base.html (where
      {% static %} is used), not in the child templates.
    - Mistakes - the CSS disappeared after the move:
        <link rel="stylesheet" href="{% static 'reviews/style.css'}">
        1) "}" instead of "%}" -> not a template tag at all, Django sent the
           text unchanged: href="{% static 'reviews/style.css'}"
        2) style.css instead of styles.css -> after fixing 1) the page asked
           for /static/reviews/style.css -> 404
      Fixed: href="{% static 'reviews/styles.css' %}"
      Tip: python manage.py findstatic reviews/styles.css shows whether a
      static path exists; view page source shows what the link became.

## Thank-you page as a class: ThankYouView(View)

    - views.py: function view thank_you replaced by a class (same idea as
      ReviewView, only a get() because the page is never POSTed to):
        class ThankYouView(View):
            def get(self, request):
                return render(request, "reviews/thank_you.html")
    - urls.py: path("thank-you", views.ThankYouView.as_view())
    - The unused {"has_error": False} context is gone.
    - Checked: GET /thank-you -> 200 "Thank you!", GET / -> 200.
    - Next step (import already there, commented out):
        # from django.views.generic.base import TemplateView
      TemplateView only renders a template, so get() isn't needed at all:
        class ThankYouView(TemplateView):
            template_name = "reviews/thank_you.html"

## TemplateView + get_context_data()

    - ThankYouView now inherits TemplateView - no get() needed, Django renders
      template_name on GET by itself:
        from django.views.generic.base import TemplateView

        class ThankYouView(TemplateView):
            template_name = "reviews/thank_you.html"

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context["message"] = "Thank you for your feedback!"
                return context
    - get_context_data() = the place to add template variables (what used to
      be the {...} dict in render()). super() gives the base context, add
      keys, then RETURN it.
    - thank_you.html: <p>{{ message }}</p> inside the content block.
    - Mistake: return context was missing -> the method returned None, the
      template got no "message" and rendered an empty <p></p> (no error,
      a missing variable just becomes "").
    - Checked: GET /thank-you -> 200 with "Thank you for your feedback!".

## Helpful resources

    - Course code snapshot repository (branch per lesson):
        https://github.com/academind/django-practical-guide-course-code
    - Section 10 code snapshots = branches starting with "forms-...", e.g.:
        https://github.com/academind/django-practical-guide-course-code/tree/forms-00-starting-setup
    - Section 10 module slides:
        https://github.com/academind/django-practical-guide-course-code/tree/forms-zz-extra-files/slides
    - ModelForm docs (Meta: model, fields, exclude, labels, widgets, error_messages):
        https://docs.djangoproject.com/en/6.0/topics/forms/modelforms/
    - Form fields reference (CharField, IntegerField, options, error codes):
        https://docs.djangoproject.com/en/6.0/ref/forms/fields/
    - CSRF protection:
        https://docs.djangoproject.com/en/6.0/ref/csrf/
    - Class-based views intro:
        https://docs.djangoproject.com/en/6.0/topics/class-based-views/intro/
    - Django docs:
        https://docs.djangoproject.com/en/6.0/
    - Working with forms:
        https://docs.djangoproject.com/en/6.0/topics/forms/
