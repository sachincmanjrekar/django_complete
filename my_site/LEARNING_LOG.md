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

## python manage.py startapp blog

    - Creates the "blog" app (admin.py, apps.py, migrations/, models.py,
      tests.py, views.py). Registered in my_site/settings.py:
        INSTALLED_APPS = [
            ...
            'blog',
        ]

## Blog URLs (blog/urls.py) and the slug converter

    - blog/urls.py (new file):
        urlpatterns = [
            path('', views.starting_page, name="starting-page"),
            path("posts/", views.posts, name="posts-page"),
            path("posts/<slug:slug>/", views.post_detail, name="post_detail-page"),
        ]
    - <slug:slug> -> slug converter: letters, numbers, hyphens, underscores
      (e.g. "mountain-hiking"); passed to the view as slug.
    - Views first only had pass -> returning None = error when the page opens.
      Now each renders a template:
        def starting_page(request):
            return render(request, "blog/index.html")
        def posts(request):
            return render(request, "blog/posts.html")
        def post_detail(request, slug):
            return render(request, "blog/post_detail.html", {"slug": slug})

## Page not found at / (and making the blog the home page)

    - my_site/urls.py first had:
        path('blog/', include('blog.urls'))
      -> every URL had to start with blog/; http://127.0.0.1:8000/ -> 404.
    - Changed to an empty prefix:
        path('', include('blog.urls'))
      Now:  /                  -> starting_page
            /posts/            -> posts
            /posts/<slug>/     -> post_detail

## Project-level templates and static files (settings.py)

    - 'DIRS': [BASE_DIR / 'templates'] -> templates/base.html (shared layout)
    - STATICFILES_DIRS = [BASE_DIR / "static"] -> static/app.css (global CSS)
    - App files are found automatically (blog is in INSTALLED_APPS):
        blog/templates/blog/index.html
        blog/static/blog/index.css

## base.html, index.html and the starting page

    - templates/base.html: {% load static %}, global app.css,
      empty {% block css_files %} in <head>, {% block content %} in <body>.
    - blog/templates/blog/index.html extends it: navigation, welcome section,
      "The Latest Thoughts" post list, "What I do" section.
    - Issues found and fixed:
        'app.cs' typo in {% static %} -> app.css never loaded -> 'app.css'
        {% block css_files %} was INSIDE {% block content %} -> index.css was
          linked twice (in <head> AND in <body>) -> moved above content
        <section> had no id, but index.css styles #latest-posts
          -> <section id="latest-posts">
        href="" links just reload the page -> {% url %} tags:
            {% url 'starting-page' %}                       -> /
            {% url 'posts-page' %}                          -> /posts/
            {% url 'post_detail-page' 'mountain-hiking' %}  -> /posts/mountain-hiking/
        rel="Stylesheet" -> rel="stylesheet" (lowercase is standard)
        text: "Sachin's blog", "SACHIN MANJREKAR'S BLOG", "Hi, this is Sachin"
    - Lesson: Django finds child blocks by NAME, even when nested, so a block
      nested in the wrong place still fills the parent's gap - and also prints
      where it sits.

## Placeholder posts.html and post_detail.html

    - /posts/ and /posts/<slug>/ crashed with TemplateDoesNotExist.
    - Added simple templates extending base.html:
        posts.html       -> "All My Posts" + link to the Mountain Hiking post
        post_detail.html -> <h1>Post: {{ slug }}</h1> + link to All Posts

## Images as static files

    - Images in blog/static/images/ (sachin.jpg, mountains.jpg, coding.jpg, woods.jpg).
    - Used with the static tag, like CSS:
        <img src="{% static 'images/sachin.jpg' %}" alt="Sachin - The Author of This Blog" />
        <img src="{% static 'images/mountains.jpg' %}" alt="Mountain Hiking" />
      -> /static/images/sachin.jpg
    - Path in {% static %} is relative to the static/ folder.
    - Safer (namespaced) location: blog/static/blog/images/ -> 'blog/images/...'
    - coding.jpg and woods.jpg not used yet (only one post so far).

## Helpful resources

    - Course code snapshot repository (branch per lesson):
        https://github.com/academind/django-practical-guide-course-code
    - Django docs:
        https://docs.djangoproject.com/en/6.0/
    - Path converters (str, int, slug, uuid, path) in URLs:
        https://docs.djangoproject.com/en/3.1/topics/http/urls/#path-converters
    - PEP 8 (Python style guide):
        https://peps.python.org/pep-0008/
