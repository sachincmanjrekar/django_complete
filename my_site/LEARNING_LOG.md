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
                            (later replaced by all-posts.html)
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

## Moving shared pieces to base.html / app.css (navigation)

    - The <header id="main-navigation"> was only in index.html, but every
      page needs it -> moved into templates/base.html, above {% block content %}:
        <body>
            <header id="main-navigation">
                <h1><a href="{% url 'starting-page' %}">Sachin's blog</a></h1>
                <nav>
                    <a href="{% url 'posts-page' %}">All Posts</a>
                </nav>
            </header>
            {% block content %}{% endblock %}
        </body>
    - Its CSS moved with it: #main-navigation rules from blog/index.css -> static/app.css
      (app.css is loaded on every page by base.html).
    - Rule: markup used on every page -> base.html; its CSS -> global CSS.

## Post card as an include (blog/includes/post.html)

    - One post card (li > article.post > a > img + h3 + p) in its own file:
        blog/templates/blog/includes/post.html
      It has its own {% load static %} because it uses {% static %} itself.
    - index.html (latest posts):
        <ul>
            {% include "blog/includes/post.html" %}
        </ul>
    - Card CSS moved to blog/static/blog/post.css, linked by every page that
      shows posts (index.html and all-posts.html), before the page's own CSS:
        <link rel="stylesheet" href="{% static 'blog/post.css' %}"/>
        <link rel="stylesheet" href="{% static 'blog/index.css' %}"/>

## All posts page (all-posts.html + all-posts.css)

    - views.py -> posts() now renders the new template:
        return render(request, "blog/all-posts.html")
    - blog/templates/blog/all-posts.html:
        {% block title %}All My Posts{% endblock %}
        {% block css_files %}
            post.css + all-posts.css
        {% endblock %}
        <section id="all-posts">
            <h2>My collected Posts</h2>
            <ul>
                {% include "blog/includes/post.html" %}   (x6)
            </ul>
        </section>
    - all-posts.css: light background, purple nav bar, cards in a CSS grid,
      bigger images; it overrides some post.css rules because it loads AFTER it.
    - All 6 cards are the same Mountain Hiking post for now (hard-coded in
      post.html) - real data comes later.

## Cleanup after the refactor

    - index.css still had copies of the #main-navigation and .post rules
      (now in app.css and post.css) -> deleted, so each style lives in ONE place.
      index.css now only styles the home page: #welcome, #latest-posts, #about.
    - "My colleced Posts" typo -> "My collected Posts".
    - all-posts.html title "My Blog" (same as home) -> "All My Posts".
    - Deleted the placeholder posts.html (view uses all-posts.html now).

## Single post page (post_detail.html + post-detail.css)

    - blog/templates/blog/post_detail.html:
        {% extends "base.html" %}
        {% load static %}
        {% block title %}This Post Title{% endblock %}
        {% block css_files %}
            <link rel="stylesheet" href="{% static 'blog/post-detail.css' %}" />
        {% endblock %}
        {% block content %}
            <section id="summary">
                <h2>Post Title</h2>
                <article>
                    <img src="{% static 'blog/images/mountains.jpg' %}" alt="Post Title" />
                    <address>By Sachin</address>
                    <div>Last updated on <time>August 10</time></div>
                </article>
            </section>
            <main>
                <p>Lorem ipsum ...</p>
            </main>
        {% endblock %}
    - <address> = author info, <time> = a date, <main> = the page's main content
      (semantic HTML tags).
    - blog/static/blog/post-detail.css = course file (from the
      prj-urls-views-templates-zz-extra-files branch): purple #summary box,
      tilted image, white main card.
    - Content is placeholder for now; the slug from the URL isn't shown yet.

## Error: block tag appears more than once

    - Had two title blocks in post_detail.html:
        {% block title %}Thid Post Title{% endblock %}
        {% block title %}All My Posts{% endblock %}
    - Opening /posts/mountain-hiking/ gave:
        TemplateSyntaxError: 'block' tag with name 'title' appears more than once
    - Each block name may appear only ONCE per template -> kept one:
        {% block title %}This Post Title{% endblock %}

## Moving images to the namespaced static folder

    - post_detail.html used {% static 'blog/images/mountains.jpg' %}, but the
      images were in blog/static/images/ -> image not found.
    - Moved them (git mv keeps history):
        blog/static/images/       ->  blog/static/blog/images/
    - Updated index.html and includes/post.html to match:
        {% static 'images/sachin.jpg' %}  ->  {% static 'blog/images/sachin.jpg' %}
    - Same namespacing rule as templates: static/<app name>/... so files from
      different apps can't clash.
    - A missing static file gives NO template error - the image/CSS just
      silently doesn't load (check the browser's network tab for 404s).

## Dummy data in views.py (list of post dicts)

    - blog/views.py -> module-level list, one dict per post:
        from datetime import date

        all_posts = [
            {
                "slug": "hike-in-the-mountains",
                "image": "mountains.jpg",
                "author": "Maximilian",
                "date": date(2021, 7, 21),
                "title": "Mountain Hiking",
                "excerpt": "There's nothing like the views ...",
                "content": """ Lorem ipsum ... """,
            },
            ... "programming-is-fun" (coding.jpg), "into-the-woods" (woods.jpg)
        ]
    - date(2021, 7, 21) = Python date object, so posts can be sorted by date.
    - Later this data comes from a database (models).

## Latest 3 posts: sorted() + slicing

    - views.py:
        def get_date(post):
            return post['date']

        def starting_page(request):
            sorted_posts = sorted(all_posts, key=get_date)
            latest_posts = sorted_posts[-3:]
            return render(request, "blog/index.html", {"posts": latest_posts})
    - sorted(list, key=function) -> new list; key tells WHAT to compare
      (here each post's date). Oldest first.
    - Bug: wrote sorted_posts[-3:0] -> always EMPTY (end index 0 is before
      the start), so the for loop ran zero times and no posts showed.
        [-3:0] -> []
        [-3:]  -> last 3 items (no end = up to the end of the list)
    - Newest first instead: sorted(all_posts, key=get_date, reverse=True)[:3]

## Looping over posts and using post data in the include

    - index.html:
        <ul>
            {% for post in posts %}
                {% include "blog/includes/post.html" %}
            {% endfor %}
        </ul>
    - The include sees the loop variable post, so includes/post.html uses its fields:
        <a href="{% url 'post_detail-page' post.slug %}">
            <img src="{% static 'blog/images/'|add:post.image %}" alt="{{ post.title }}" />
            <div class="post__content">
                <h3>{{ post.title }}</h3>
                <p>{{ post.excerpt }}</p>
            </div>
        </a>
    - post.title = dict key lookup with a dot (DTL, not post['title']).
    - 'blog/images/'|add:post.image -> "blog/images/woods.jpg" (add filter
      builds the static path dynamically).

## Errors on the way (template syntax)

    - Space after the pipe:
        {% static 'blog/images/'| add:post.image %}
        TemplateSyntaxError: Could not parse the remainder: '|' from ''blog/images/'|'
      -> no spaces around | in filters: 'blog/images/'|add:post.image
    - Stray quote after a variable:
        {% url 'post_detail-page' post.slug' %}
        TemplateSyntaxError: Could not parse the remainder: ''' from 'post.slug''
      -> quotes = fixed text ('mountain-hiking'); variables get NO quotes (post.slug)
    - Empty slug in {% url %}:
        NoReverseMatch: Reverse for 'post_detail-page' with arguments '('',)' not found.
      all-posts.html used the include without any post variable -> post.slug = ""
      -> <slug:slug> needs at least 1 character, so the URL can't be built.

## All posts page with real data

    - views.py:
        def posts(request):
            return render(request, "blog/all-posts.html", {"all_posts": all_posts})
    - all-posts.html: six hard-coded includes -> one loop:
        <ul>
            {% for post in all_posts %}
                {% include "blog/includes/post.html" %}
            {% endfor %}
        </ul>
    - / shows the latest 3 (sorted by date); /posts/ shows all posts in list order.
    - post_detail still shows placeholder content for every slug.

## Helpful resources

    - Course code snapshot repository (branch per lesson):
        https://github.com/academind/django-practical-guide-course-code
    - Django docs:
        https://docs.djangoproject.com/en/6.0/
    - Blog project course files (CSS + images), and lesson snapshots in the
      branches starting with "prj-urls-views-templates-...":
        https://github.com/academind/django-practical-guide-course-code/tree/prj-urls-views-templates-zz-extra-files
    - Path converters (str, int, slug, uuid, path) in URLs:
        https://docs.djangoproject.com/en/3.1/topics/http/urls/#path-converters
    - PEP 8 (Python style guide):
        https://peps.python.org/pep-0008/
