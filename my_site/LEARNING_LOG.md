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

## Single post page with real data (find the post by slug)

    - views.py:
        from django.http import Http404

        def post_detail(request, slug):
            identified_post = next((post for post in all_posts if post['slug'] == slug), None)
            if identified_post is None:
                raise Http404()
            return render(request, "blog/post_detail.html", {"post": identified_post})
    - (post for post in all_posts if post['slug'] == slug) = generator expression:
      goes through the posts and yields only the ones with a matching slug.
    - next(generator, None) -> the FIRST match, or None if there is none.
    - post_detail.html uses the post's fields:
        {% block title %}{{ post.title }}{% endblock %}
        <h2>{{ post.title }}</h2>
        <img src="{% static 'blog/images/'|add:post.image %}" alt="{{ post.title }}" />
        <address>By {{ post.author }}</address>
        Last updated on <time>{{ post.date|date:'d M Y' }}</time>
        <p>{{ post.content }}</p>
    - |date:'d M Y' formats a date object -> date(2020, 8, 5) -> "05 Aug 2020"
      (d = day with 0, M = short month name, Y = 4-digit year).
    - Results:
        /posts/into-the-woods/        -> Nature At Its Best, woods.jpg, 05 Aug 2020
        /posts/hike-in-the-mountains/ -> Mountain Hiking, mountains.jpg, 21 Jul 2021
        /posts/programming-is-fun/    -> Programming Is Great!, coding.jpg, 10 Mar 2022
        /posts/nope/                  -> 404 Page not found

## Errors on the way (post_detail)

    - Looped over the wrong name:
        next(post for post in posts if ...)
        TypeError: 'function' object is not iterable
      posts is the VIEW FUNCTION def posts(request); the data list is all_posts.
      Lesson: a variable and a function with the same name -> easy mix-up.
    - Unknown slug without a default:
        next(post for post in all_posts if ...)    /posts/nope/ -> StopIteration
      next() with nothing to return raises StopIteration -> 500 server error.
      Fix: next((...), None) + raise Http404() -> proper 404.
      The extra ( ) around the generator are needed once there's a 2nd argument.
    - Edits not saved in VS Code -> Django still runs the old file
      (dot on the editor tab = unsaved; Ctrl + S).

## Custom 404 page (templates/404.html)

    - Project-level templates/404.html, extends base.html:
        {% extends "base.html" %}
        {% block title %}We didn't find that page{% endblock %}
        {% block content %}
            <h2>Sorry</h2>
            <p>Coud not find that page</p>
        {% endblock %}
    - Shown automatically when a view raises Http404 (e.g. /posts/nope/),
      but ONLY with DEBUG = False (+ ALLOWED_HOSTS set). With DEBUG = True
      Django shows its yellow debug 404 page instead.
    - The name must be exactly 404.html in a templates folder; no view code needed.
    - Typo to fix: "Coud" -> "Could".

## Section 5 complete (Blog project: URLs, views, templates, static files)

## Section 9 begins (Blog project: data & models)

    - Back in my_site after sections 6-8 in book_store (models, admin,
      relationships). Goal: replace the hard-coded posts list in
      blog/views.py with real models + database.

## Blog models: Post, Author, Tag (all 3 relationship ideas together)

    - blog/models.py:
        from django.db import models
        from django.core.validators import MinLengthValidator

        class Tag(models.Model):
            caption = models.CharField(max_length=20)

        class Author(models.Model):
            first_name = models.CharField(max_length=100)
            last_name = models.CharField(max_length=100)
            email_address = models.EmailField()

        class Post(models.Model):
            title = models.CharField(max_length=200)
            excerpt = models.CharField(max_length=200)
            image_name = models.CharField(max_length=200)
            date = models.DateField(auto_now=True)
            slug = models.SlugField(unique=True, db_index=True)
            content = models.TextField(validators=[MinLengthValidator(10)])
            author = models.ForeignKey(Author, on_delete=models.SET_NULL, related_name="posts")
            tags = models.ManyToManyField(Tag)
    - New field types / options:
        EmailField          CharField that validates "x@y.z" format in forms/admin
        TextField           long text, no max_length (post body)
        DateField(auto_now=True)      set to TODAY on every save()
                                      (auto_now_add=True -> only when created)
        SlugField(unique=True)        no two posts with the same slug
                                      (unique already creates an index ->
                                       db_index=True is extra, harmless)
        MinLengthValidator(10)        content must be at least 10 chars
                                      (form/admin validation, like MinValueValidator)
        image_name          just the file NAME (e.g. "mountains.jpg"), the
                            image itself stays in static/blog/images
    - Relationships:
        Post -> Author   ForeignKey      one author, many posts
                                         author.posts.all() (related_name)
        Post <-> Tag     ManyToManyField a post has many tags, a tag many posts
    - Tag defined ABOVE Post (or use "Tag" as a string - lazy relation).
    - blog/admin.py:
        from .models import Post, Author, Tag
        admin.site.register(Post)
        admin.site.register(Author)
        admin.site.register(Tag)
    - Error (python manage.py check / makemigrations / runserver):
        SystemCheckError: blog.Post.author: (fields.E320) Field specifies
        on_delete=SET_NULL, but cannot be null.
        HINT: Set null=True argument on the field, or change the on_delete rule.
      SET_NULL = "when the author is deleted, set post.author to NULL" ->
      the column must ALLOW NULL. Fix:
        author = models.ForeignKey(Author, on_delete=models.SET_NULL,
                                   null=True, related_name="posts")
      -> fixed, check: "System check identified no issues (0 silenced)."
    - Next: makemigrations -> blog/migrations/0001_initial.py
      (+ Create model Author, + Create model Tag, + Create model Post), then migrate.

## First migrate in my_site + superuser + admin

    - This project had NEVER been migrated (section 5 had no models), so the
      first migrate applied Django's built-in apps too:
        python .\manage.py makemigrations
          blog\migrations\0001_initial.py
            + Create model Author / + Create model Tag / + Create model Post
        python .\manage.py migrate
          Applying contenttypes.0001_initial... OK
          Applying auth.0001_initial ... auth.0012 ... OK
          Applying admin.0001-0003 ... OK
          Applying blog.0001_initial... OK
          Applying sessions.0001_initial... OK
      -> db.sqlite3 now has the admin/auth/session tables + blog tables:
         blog_author, blog_tag, blog_post, blog_post_tags (M2M join table)
    - python manage.py createsuperuser -> username admin, admin@test.com
        The password is too similar to the username.
        This password is too short. It must contain at least 8 characters.
        This password is too common.
        Bypass password validation and create user anyway? [y/N]: y
      Fine for local learning; never for a real site.
    - runserver -> http://127.0.0.1:8000/admin/
        GET /admin/                     302  -> not logged in, redirect to login
        GET /admin/login/?next=/admin/  200  login page
        POST /admin/login/...           302  login OK -> back to /admin/
        GET /admin/                     200  dashboard
      BLOG section: Authors | Posts | Tags
    - Add post form fields: title, excerpt, image_name, slug, content,
      author (dropdown), tags (multi-select).
      NO date field: auto_now=True makes it non-editable, Django fills it in.
    - Still to do: __str__ on the models (otherwise "Post object (1)" etc.),
      and a Tag/Author must exist before picking one (or use the green +).

## Blog admin config: __str__ + PostAdmin

    - models.py:
        class Tag(models.Model):
            ...
            def __str__(self):
                return self.caption

        class Author(models.Model):
            ...
            def full_name(self):
                return f"{self.first_name} {self.last_name}"

            def __str__(self):
                return self.full_name()
      (methods only -> makemigrations: "No changes detected")
    - admin.py:
        class PostAdmin(admin.ModelAdmin):
            list_filter = ("author", "tags", "date")
            list_display = ("title", "author", "date")
            prepopulated_fields = {"slug": ("title",)}

        admin.site.register(Post, PostAdmin)
        admin.site.register(Author)
        admin.site.register(Tag)
    - Posts list: columns Title | Author | Date, filter sidebar
      By author / By tags / By date. A DateField filter gets ready-made
      choices: Any date, Today, Past 7 days, This month, This year.
      Filtering by "tags" works across the many-to-many too.
    - Add post: slug fills in from the title as you type (prepopulated_fields).
    - Data added in the admin (the 3 posts that used to be hard-coded in views.py):
        author: Sachin Manjrekar
        tags:   Featured, Settings, Hot
        posts:  1 Mountain Hiking        mountains.jpg  hike-in-the-mountains  tag Hot
                2 Programming Is Great!  coding.jpg     programming-is-fun     tag Settings
                3 Nature At Its Best     woods.jpg      nature-at-its-best     tag Featured
        date = 2026-10-27 for all (auto_now -> the day they were saved)
    - Post has no __str__ yet -> shell / dropdowns show "Post object (1)".
      The list page doesn't care because list_display shows the title column.

## Views use the database instead of the hard-coded list

    - Deleted the whole all_posts = [ {...}, {...}, {...} ] list (~65 lines)
      and the date import from blog/views.py.
    - blog/views.py now:
        from django.shortcuts import render, get_object_or_404
        from .models import Post

        def starting_page(request):
            latest_posts = Post.objects.all().order_by("-date")[:3]
            return render(request, "blog/index.html", {"posts": latest_posts})

        def posts(request):
            all_posts = Post.objects.all().order_by("-date")
            return render(request, "blog/all-posts.html", {"all_posts": all_posts})

        def post_detail(request, slug):
            identified_post = get_object_or_404(Post, slug=slug)
            return render(request, "blog/post_detail.html", {"post": identified_post})
    - Before vs now:
        sorted(all_posts, key=get_date)[-3:]   -> order_by("-date")[:3]
           ("-date" = newest first; [:3] on a QuerySet = SQL LIMIT 3,
            the database does the sorting and cutting)
        next((p for p in all_posts if ...), None) + raise Http404()
                                               -> get_object_or_404(Post, slug=slug)
    - Templates: dict key "image" became the model field image_name:
        {% static 'blog/images/'|add:post.image_name %}
      in includes/post.html and post_detail.html. Everything else
      (post.title, post.excerpt, post.slug, post.content, post.date) has the
      same name in the model, so the templates didn't change.
      {{ post.author }} -> Author.__str__ -> "By Sachin Manjrekar".
    - Checked:
        /                               3 latest posts, images ok
        /posts/                         all 3 posts
        /posts/hike-in-the-mountains/   detail, "By Sachin Manjrekar", 27 Oct 2026
        /posts/programming-is-fun/      ok
        /posts/nature-at-its-best/      ok
        /posts/into-the-woods/          404 - the old hard-coded slug; the DB
                                        post got slug nature-at-its-best
    - All 3 posts have the same date (auto_now = the day saved in the admin),
      so "-date" ordering can't tell them apart.
    - Leftovers now unused in views.py: def get_date(post) and
      from django.http import Http404 -> can be deleted.

## Author name as an email link (mailto:)

    - post_detail.html - following the relation post -> author -> email_address:
        <address>By <a href="mailto:{{ post.author.email_address }}">{{ post.author }}</a></address>
      rendered: <a href="mailto:scmanjrekar@test.com">Sachin Manjrekar</a>
      click -> opens the email app with the author's address filled in.
    - post-detail.css:
        #summary a {
          color: white;
          text-decoration: none;
        }
    - Mistakes on the way:
        <a href ="{{ post.author.email_address }}">{{ post.author }}</address>
        1) no </a> -> unclosed link, invalid HTML
        2) no mailto: -> the browser treats the email as a RELATIVE URL:
           /posts/hike-in-the-mountains/scmanjrekar@test.com -> 404
      href kinds: "https://..." (other site), "/posts/" (this site),
                  "mailto:x@y.com" (email), "tel:+91..." (phone)
    - After fixing, the browser still went to the 404 page
      (posts/nature-at-its-best/scmanjrekar@test.com) -> it was the OLD page
      still open in the tab. Ctrl+F5 (hard reload) -> link works.
      Template changes need a page reload; the server already had the fix.

## Showing a post's tags (many-to-many in a template)

    - views.py - pass the tags separately:
        def post_detail(request, slug):
            identified_post = get_object_or_404(Post, slug=slug)
            return render(request, "blog/post_detail.html", {
                "post": identified_post,
                "post_tags": identified_post.tags.all()
            })
    - Why not just post.tags in the template? post.tags is a MANAGER, not a
      list. {% for tag in post.tags.all %} also works in DTL (no parentheses),
      but the course passes the QuerySet from the view.
    - post_detail.html (above the <article>):
        <div>
            {% for tag in post_tags %}
            <span class="tag">{{ tag }}</span>
            {% endfor %}
        </div>
      {{ tag }} -> Tag.__str__ -> caption. Rendered for nature-at-its-best:
        <span class="tag">Featured</span>
    - post-detail.css:
        #summary h2 { ... margin-bottom: 0.25rem; }
        .tag {
          background-color: white;
          color: #390281;
          padding: 0.5rem 1rem;
          border: 8px;
        }
      Note: "border: 8px" alone draws nothing (no style like solid) - for
      rounded corners it should be border-radius: 8px.

## Browser cache: CSS changes not showing

    - Changed CSS but the page looks the same -> browser is using the OLD
      cached .css file.
    - Fix: open DevTools (F12 / right-click > Inspect), then RIGHT-CLICK the
      browser's reload button -> "Empty Cache and Hard Reload".
      (Only shows while DevTools is open.)
    - Lighter options: Ctrl+F5 / Ctrl+Shift+R (hard reload), or in DevTools
      Network tab tick "Disable cache" (works while DevTools stays open).

## Section 9 complete (Blog project: data & models)

## Section 14 begins (Course project: forms, files, sessions)

    - Back in the blog project: using what sections 10-13 taught in the
      feedback project (forms, class-based views, file uploads, sessions).

## Post images are uploads now: image_name -> ImageField

    - blog/models.py:
        image_name = models.CharField(max_length=200)                  # old
        image = models.ImageField(upload_to="posts", null=True)        # new
      null=True so the existing rows could migrate without an image. No
      blank=True, so the admin still requires one.
    - Migration 0002_remove_post_image_name_post_image: removes image_name,
      adds image (the old names in the DB are gone), applied.
    - my_site/settings.py:
        MEDIA_ROOT = BASE_DIR / "uploads"   # on disk: my_site/uploads/posts/
        MEDIA_URL = "/files/"               # in the browser: /files/posts/...
    - blog/urls.py (the feedback project had this in the project urls.py;
      works in either):
        urlpatterns = [
            ...
        ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    - includes/post.html and post_detail.html:
        <img src="{% static 'blog/images/'|add:post.image_name %}" ...>   # old
        <img src="{{ post.image.url }}" ...>                              # new
      {% load static %} removed from post.html (not used there any more).
    - Images uploaded again through the admin: mountains.jpg, coding.jpg and
      woods.jpg are in uploads/posts/ and were deleted from
      blog/static/blog/images/.
    - Static vs uploads: design images stay in static, images added through
      the site go to uploads.
        - The header photo on the starting page is a design image:
          {% static 'blog/images/sachin.jpg' %} ->
          blog/static/blog/images/sachin.jpg (kept in static).
    - auto_now on date: saving the posts to add the images gave all of them
      today's date, so order_by("-date")[:3] now has a tie and a newer post
      isn't guaranteed a place on the starting page.
    - Checked: manage.py check -> no issues; /, /posts/ and a post page -> 200;
      every /files/posts/... image -> 200; findstatic finds
      blog/images/sachin.jpg. (The test client doesn't serve static files, so
      the header photo's URL gives a 404 there - check it in the browser.)
    - Started, commented out in views.py: class StartingPageView(ListView) -
      get_queryset() isn't finished, the function views still run.

## Blog views as classes: ListView and DetailView

    - blog/views.py (from django.views.generic import ListView, DetailView):
        class StartingPageView(ListView):
            template_name = "blog/index.html"
            model = Post
            ordering = ["-date"]
            context_object_name = "posts"

            def get_queryset(self):
                queryset = super().get_queryset()
                data = queryset[:3]
                return data

        class AllPostsView(ListView):
            template_name = "blog/all-posts.html"
            model = Post
            ordering = ["-date"]
            context_object_name = "all_posts"

        class SinglePostView(DetailView):
            template_name = "blog/post_detail.html"
            model = Post

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context["post_tags"] = self.object.tags.all()
                return context
    - blog/urls.py (same URLs and names, so {% url %} links didn't change):
        path('', views.StartingPageView.as_view(), name="starting-page"),
        path("posts/", views.AllPostsView.as_view(), name="posts-page"),
        path("posts/<slug:slug>/", views.SinglePostView.as_view(), name="post_detail-page")
    - ordering = ["-date"] replaces .order_by("-date"). super().get_queryset()
      already has it applied, then [:3] keeps the latest 3.
    - context_object_name keeps the names the templates already use (posts,
      all_posts).
    - DetailView finds the row by <slug:slug> from the URL (matching the
      model's slug field) and gives a 404 by itself. The row is in the
      template as "post" (model name), so post_detail.html didn't change.
      self.object = the loaded post, so its tags can be added to the context.
    - Checked: manage.py check -> no issues; / and /posts/ -> 200 with the same
      posts; all 3 post pages -> 200 with their tags; /posts/nope/ -> 404.
    - Old function view post_detail removed. Left over in views.py, nothing
      uses them now: get_date, imports render, get_object_or_404, Http404.

## Comment model + CommentForm on the single post page

    - blog/models.py:
        class Comment(models.Model):
            user_name = models.CharField(max_length=100)
            user_email = models.EmailField()
            text = models.TextField(max_length=400)
            post = models.ForeignKey(Post, on_delete=models.CASCADE,
                                     related_name="comments")
      CASCADE: deleting a post deletes its comments. post.comments.all()
      gives a post's comments.
      Migration 0003_comment created and applied.
    - New blog/forms.py:
        class CommentForm(forms.ModelForm):
            class Meta:
                model = Comment
                exclude = ["post"]
                labels = {"user_name": "Your Name", "user_email": "Your Email",
                          "text": "Your Comment"}
      exclude = ["post"]: the visitor doesn't choose the post, the view will
      set it from the page they're on.
    - views.py, SinglePostView.get_context_data():
        context["comment_form"] = CommentForm()
    - post_detail.html, below </main>:
        <form>
            {{ comment_form }}
            <button>Save Comment</button>
        </form>
    - Checked: migrations applied; /posts/nature-at-its-best/ -> 200 with
      the 3 fields.
    - Not done yet: the form has no method="POST", action or {% csrf_token %},
      and SinglePostView (DetailView) has no post() -> a POST gives 405, so
      nothing is saved. Comment isn't registered in the admin either.

## Styling the comment form

    - post_detail.html - fields looped by hand so each gets a wrapper to style:
        <section id="comment-form">
            <h2>Your Comment</h2>
            <form>
                {% for form_field in comment_form %}
                <div class="form-control">
                    {{ form_field.label_tag }}
                    {{ form_field }}
                    {{ form_field.errors }}
                </div>
                {% endfor %}
                <button>Save Comment</button>
            </form>
        </section>
    - blog/static/blog/post-detail.css: #comment-form card + button,
      .form-control label / input / textarea, .errorlist.
      Also added for later, not on the page yet: #read-later, #comments,
      #alert, .invalid (needs a class on the wrapper, e.g.
      form-control {% if form_field.errors %}invalid{% endif %}).
      .tag: "border: 8px" corrected to "border-radius: 8px".
    - static/app.css: #main-navigation a got margin-left: 1rem.
    - Mistakes:
        1) old </form> and </div> left after the loop -> the form ended before
           the button, so Save Comment was outside the form.
        2) {{ from_field.errors }} typo -> no crash (an unknown name is just
           empty), but errors would never show. Must be form_field.
    - Checked: /posts/nature-at-its-best/ -> 200, button inside the form.

## Saving comments: SinglePostView(View) with get() and post()

    - DetailView has no post(), so SinglePostView is now a plain View:
        class SinglePostView(View):
            def get(self, request, slug):
                post = Post.objects.get(slug=slug)
                context = {"post": post, "post_tags": post.tags.all(),
                           "comment_form": CommentForm()}
                return render(request, "blog/post_detail.html", context)

            def post(self, request, slug):
                comment_form = CommentForm(request.POST)
                post = Post.objects.get(slug=slug)

                if comment_form.is_valid():
                    comment = comment_form.save(commit=False)
                    comment.post = post
                    comment.save()
                    return HttpResponseRedirect(reverse("post_detail-page", args=[slug]))
                ...render the page again...
    - commit=False: builds the Comment without saving it. The form excludes
      post, so saving straight away would fail (post is required). Set
      comment.post first, then comment.save().
    - reverse("post_detail-page", args=[slug]) = the {% url %} tag in Python,
      turns a URL name into the path.
    - post_detail.html:
        <form action="{% url 'post_detail-page' post.slug %}" method='POST'>
            {% csrf_token %}
    - Mistake: "post-detail-page" in the template and view, but the name in
      urls.py is "post_detail-page" -> NoReverseMatch, 500 on every post page,
      so no comment could be stored. Names must match exactly.
    - Mistake: the last context used a new CommentForm() -> errors didn't show
      and the typed text was lost. Fixed: "comment_form": comment_form (the
      bound form holds both). get() keeps CommentForm(), it wants an empty one.
    - Checked: comments are stored (3 rows, all on post 2); valid POST ->
      302 back to the post and one new row; invalid POST -> 200, errors shown
      and typed text kept (test rows rolled back).
    - Error alert at the top of post_detail.html, because the form is far
      down the page and the errors are easy to miss:
        {% if comment_form.errors %}
        <div id="alert">
            <h2>Saving the comment failed</h2>
            <p>Please check the comment form below the post and fix your errors.</p>
            <a href="#comment-form">Fix!</a>
        </div>
        {% endif %}
      href="#comment-form" jumps to the element with id="comment-form".
      Field wrapper: <div class="form-control {% if form_field.errors %} invalid {% endif %}">
      -> the red .invalid styles apply to that field.
    - Mistake: {% if comment_form.erros %} typo -> no crash (unknown name is
      empty), the alert just never showed. Fixed to .errors.
    - Open points:
        - /posts/nope/ -> 500 (Post.DoesNotExist), was a 404 with DetailView.
          get_object_or_404(Post, slug=slug) fixes it. (Fixed before deploying.)

## Outputting the comments on the post page

    - views.py - in the context of BOTH get() and post() (post() renders the
      page again after an invalid comment, so it needs them too):
        "comments": post.comments.all().order_by("-id")
      post.comments = related_name="comments" on the ForeignKey -> only this
      post's comments. "-id" = newest first (Comment has no date field).
    - post_detail.html, above the form:
        <ul>
            {% for comment in comments %}
            <li>
                <h2>{{ comment.user_name }}</h2>
                <p>{{ comment.text|linebreaks }}</p>
            </li>
            {% endfor %}
        </ul>
    - Checked: "Programming Is Great!" -> 200, shows its 4 comments, also after
      an invalid POST; the other 2 posts -> 200 with 0 comments.
    - Mistake: the list's section also had id="comment-form", so the id was on
      the page twice: the list got the form's card style and the "Fix!" link
      jumped to the list, not the form. Fixed: <section id="comments">
      (post-detail.css already has #comments styles). An id is for one
      element only.

## Comments in the admin: CommentAdmin + Post.__str__

    - admin.py:
        class CommentAdmin(admin.ModelAdmin):
            list_display = ("user_name", "post")

        admin.site.register(Comment, CommentAdmin)
    - list_display = the columns on the list page. Without it, the only column
      is the object's name.
    - models.py - Post had no __str__, so the post column and the post dropdown
      would show "Post object (2)":
        def __str__(self):
            return self.title
    - __str__ is plain Python, the table doesn't change -> no migration
      (makemigrations --check: "No changes detected").
    - Checked: /admin/blog/comment/ -> 200, shows the 4 comments with post
      "Programming Is Great!"; the add and change pages -> 200; the post
      dropdown lists the titles.
    - Comment has no __str__, so a single comment is still named
      "Comment object (4)" (e.g. on its change and delete pages). The list
      isn't affected, list_display sets its columns.

## Moving the media route to the main urls.py

    - static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) went from
      blog/urls.py to my_site/urls.py, with its two imports.
    - It only worked in blog/urls.py because the blog is included at ''. With
      path('blog/', include('blog.urls')) the route would be /blog/files/...,
      but post.image.url still gives /files/... -> every image 404s.
    - Media settings are project-wide, so the route belongs with the project.
    - static() adds no routes when DEBUG is off, so the check needs DEBUG on.
    - Checked: the 3 images -> 200 image/jpeg at the same /files/posts/... URLs.

## Managing Read Later via the session

    - urls.py:
        path("read-later", views.ReadLaterView.as_view(), name="read-later"),
    - post_detail.html - own form, so it doesn't reach SinglePostView.post():
        <form action="{% url 'read-later' %}" method="POST">
            {% csrf_token %}
            <input type="hidden" value="{{ post.id }}" name="post_id">
            <button>Read Later</button>
        </form>
      type="hidden" = sent with the form, but not shown on the page.
    - views.py:
        class ReadLaterView(View):
            def get(self, request):
                stored_posts = request.session.get("stored_posts")
                context = {}
                if stored_posts is None or len(stored_posts) == 0:
                    context["posts"] = []
                    context["has_posts"] = False
                else:
                    posts = Post.objects.filter(id__in=stored_posts)
                    context["posts"] = posts
                    context["has_posts"] = True
                return render(request, "blog/stored-posts.html", context)

            def post(self, request):
                stored_posts = request.session.get("stored_posts")
                if stored_posts is None:
                    stored_posts = []
                post_id = int(request.POST["post_id"])
                if post_id not in stored_posts:
                    stored_posts.append(post_id)
                    request.session["stored_posts"] = stored_posts
                return HttpResponseRedirect("/")
    - Session stores ids, not Post objects (JSON only, same as section 13).
    - session.get() -> None the first time, session["x"] would be a KeyError.
    - int(): POST values are strings. Without it, "1" and 1 don't match, so
      the "not in" check would miss duplicates.
    - Assign the list back to the session: append() alone changes the list, but
      the session doesn't know it changed, so it wouldn't be saved.
    - id__in=stored_posts -> all posts whose id is in the list. An id with no
      post (deleted later) is just skipped, no error.
    - stored-posts.html: {% if not has_posts %} shows the empty message, and
      each post links to its page. base.html nav: "Stored Posts" link.
    - Mistake: {% url in "post_detail-page" post.slug %} -> the first word is
      the URL name, so "in" was read as an empty variable: "Reverse for ''
      not found". Only crashed once a post was saved, because the for loop
      doesn't run on an empty list. Removed the "in".
    - Checked: no saved posts -> 200 with the message; saving -> 302 to /;
      saving the same post twice keeps one id; 2 saved posts -> listed with
      links; a new visitor has their own empty list (test rows rolled back).
    - Open points:
        - /read-later has no trailing slash, unlike posts/. (Fixed before deploying.)

## Read Later page styling (stored-posts.css)

    - stored-posts.html loads its own CSS:
        {% load static %}
        {% block css_files %}
        <link rel="stylesheet" href="{% static 'blog/stored-posts.css' %}">
        {% endblock %}
      and the section gets an id for the CSS: <section id="stored-posts">
    - blog/static/blog/stored-posts.css:
        - #main-navigation: same purple bar as all-posts.css and post-detail.css.
        - #stored-posts: white centered card (max-width: 30rem).
        - #stored-posts ul: list-style: none, no margin or padding.
        - #stored-posts a: display: block + padding -> the whole row is clickable,
          not just the text. width: 100% stays inside the card because app.css
          has box-sizing: border-box (padding counts inside the width).
        - a:hover: grey background.
    - Checked: findstatic finds the CSS; /read-later -> 200 with the link tag,
      both with no saved posts (message) and with a saved post (link to its page).

## Read Later button: save or remove

    - views.py - SinglePostView gets a helper method. Not a route, get() and
      post() call it with self:
        def is_stored_post(self, request, post_id):
            stored_posts = request.session.get("stored_posts")
            if stored_posts is not None:
                is_saved_for_later = post_id in stored_posts
            else:
                is_saved_for_later = False

            return is_saved_for_later
    - In the context of BOTH get() and post() (an invalid comment renders the
      page again, and the button must keep the right label):
        "saved_for_later": self.is_stored_post(request, post.id)
    - post_detail.html:
        <button>
            {% if saved_for_later %}
                Remove from "Read Later" List
            {% else %}
                Read Later
            {% endif %}
        </button>
    - ReadLaterView.post() now toggles. The assignment moved out of the if, so
      a removal gets saved too:
        if post_id not in stored_posts:
            stored_posts.append(post_id)
        else:
            stored_posts.remove(post_id)
        request.session["stored_posts"] = stored_posts
    - Mistake: a <button> inside the <button>. Buttons can't be nested, so the
      browser closes the first one when it reaches the second -> an empty extra
      button. Removed the outer pair.
    - Checked: new visitor -> "Read Later"; save -> session [1], label "Remove
      from..."; another post keeps "Read Later"; invalid comment keeps the
      label; click again -> session [], back to "Read Later"; /read-later ->
      the empty message (test rows rolled back).

## Section 14 complete (Course project: forms, files, sessions)

## Section 15 begins (Deployment)

## Fixes before deploying

    - views.py - a wrong slug is a 404 now, not a 500, in get() and post():
        post = get_object_or_404(Post, slug=slug)
      Post.objects.get() raises Post.DoesNotExist, and nothing catches it.
    - urls.py - trailing slash, same as posts/:
        path("read-later/", views.ReadLaterView.as_view(), name="read-later"),
      Links use {% url %}, so they updated by themselves. APPEND_SLASH sends
      /read-later to /read-later/ with a 301.
    - views.py - removed get_date, left over from the old list of post dicts.
    - models.py - a comment has a real name in the admin:
        def __str__(self):
            return f"{self.user_name} on {self.post}"
      Plain Python again -> no migration.
    - Checked: GET and POST /posts/nope/ -> 404; with DEBUG off it uses
      templates/404.html; Read Later save, list and remove still work on
      /read-later/; a valid comment is still saved (test rows rolled back).

## Django does not serve static or uploaded files automatically

    - In development they only work because of DEBUG = True:
        - Static files: runserver with django.contrib.staticfiles serves them.
        - Uploads: the static(settings.MEDIA_URL, ...) route in my_site/urls.py.
    - With DEBUG = False both stop. static() returns an empty list, so there is
      no /files/ route at all (checked: DEBUG on -> ^files/..., DEBUG off -> []).
    - python manage.py runserver is a development-only server. In production
      something else has to serve those files. 3 options (course slide):

| Option | Notes |
|---|---|
| Configure Django to serve such files (via urls.py) | Okay for smaller sites, not performance-optimized though |
| Configure a web server to serve static files AND the Django app | Same server and device but separate processes, better for performance |
| Use a dedicated service / server for static and uploaded files | Initial setup is more complex but offers the best performance |

    - This deployment uses AWS.
    - Static files live in many folders (each app + STATICFILES_DIRS), so they
      also need one place to be gathered: STATIC_ROOT + manage.py collectstatic
      (see "Collecting static files" below).

## Deployment considerations (course slide)

| Step | Why |
|---|---|
| Choose a database (reconsider SQLite) | SQLite might work but might be too slow or be erased (depends on the hosting provider) |
| Adjust settings | Adjust config for the chosen hosting provider, disable development-only settings |
| Collect static files | Static files are NOT served automatically (just like user uploads) |
| Handle static & uploaded files serving | Same reason: neither is served automatically |
| Choose a host + deploy! | Also dive into host-specific docs + examples |

## Choosing a database: SQL vs NoSQL

    - Prefer SQL, because Django's model system supports it (models, migrations,
      relations). NoSQL databases aren't supported by Django's ORM out of the box.
    - SQL options: SQLite, MySQL, Postgres. For a live site the slide points to
      MySQL or Postgres instead of SQLite.
    - SQLite is one file (db.sqlite3) next to the code. On a host the server's
      disk may be replaced on every deploy -> the data is gone. A database
      server keeps the data apart from the app.
    - Article: https://academind.com/articles/sql-vs-nosql

## Django is NOT a webserver: WSGI and ASGI

    - Django is a framework for Python. It knows how to work with incoming
      requests and create responses.
    - It does NOT listen for incoming requests or handle any other server tasks.
      In development, python manage.py runserver does that part.
    - In production a real server program (e.g. Gunicorn for WSGI, Uvicorn or
      Daphne for ASGI) listens and hands each request to Django through one of
      the two entry files startproject made in my_site/my_site/:
        - wsgi.py - WSGI (Web Server Gateway Interface), the classic standard,
          one request at a time per worker:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_site.settings')
            application = get_wsgi_application()
          settings.py points to it: WSGI_APPLICATION = 'my_site.wsgi.application'
        - asgi.py - ASGI (Asynchronous Server Gateway Interface), the newer one,
          also supports async views and long connections like websockets.
    - Both just expose an object called application. The server is told where
      it is (e.g. my_site.wsgi:application). This blog has no async code, so
      WSGI is enough.

## Collecting static files: STATIC_ROOT + collectstatic

    - settings.py:
        STATIC_ROOT = BASE_DIR / "staticfiles"
    - Then:
        python manage.py collectstatic
        -> 137 static files copied to '...\my_site\staticfiles'.
    - It copies every static file from all the places Django looks into one
      folder, so a web server or file service only has to serve that folder:
        - static/ (STATICFILES_DIRS) -> app.css
        - blog/static/ -> blog/*.css (5) and blog/images/sachin.jpg
        - django.contrib.admin's own static folder -> admin/ (131 files: the
          admin's CSS, JS, icons). The admin needs them too.
    - STATIC_ROOT is where files are collected TO. STATICFILES_DIRS is where
      extra files are collected FROM. They must be different folders.
    - Development doesn't use staticfiles/: runserver still serves the
      originals. After changing a CSS file, run collectstatic again before
      deploying, or the copy is old.

## Serving static files via urls.py

    - my_site/urls.py - a second static() route, this time for the collected
      folder:
        ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
          + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
      The \ continues the line, so both lists are added to urlpatterns.
    - This is option 1 from the slide: Django serves the files itself. Okay for
      small sites, not built for speed.
    - Checked (DEBUG on): /static/app.css, /static/blog/post-detail.css and
      /static/admin/css/base.css -> 200 text/css from staticfiles/; uploads
      and pages still 200.
    - Catch: static() only adds the route when DEBUG is True:
        DEBUG on  -> [<URLPattern '^static/(?P<path>.*)$'>]
        DEBUG off -> []
      So with DEBUG = False (production) this line serves nothing, the same as
      the /files/ line. It's a development helper, Django's way of saying
      "don't serve files like this in production".
    - Locally with runserver, the staticfiles app answers /static/ before the
      URL patterns are checked, so it serves the originals and this route
      isn't reached anyway.

## Virtual environment for the project (venv)

    - A venv = a separate Python with its own packages, just for this project.
      The host installs exactly these packages too, not whatever is on my PC.
    - Create (in my_site/):
        python3 -m venv django_my_site
      -> folder django_my_site/ with Scripts/, Lib/, pyvenv.cfg.
    - Creating it does NOT switch to it. Activate in each new terminal:
        .\django_my_site\Scripts\Activate.ps1
      -> the prompt starts with (django_my_site).
    - It starts empty, so install again inside it:
        pip install django pillow
      -> Django 6.1.2, pillow 13.0.0 (+ asgiref, sqlparse, tzdata).
    - The venv writes its own .gitignore with * -> git ignores the whole folder.
    - python3 on this PC is a second Python 3.14 (AppData\Local\Python, 3.14.2),
      not C:\Python314 (3.14.4). The venv uses 3.14.2. Fine either way.
    - Checked with the venv's python: manage.py check is clean; pages, an
      upload and a static file -> 200; /posts/nope/ -> 404.
    - .vscode/settings.json pointed VS Code at C:\Python314, so it now points
      at the venv:
        "python.defaultInterpreterPath": "${workspaceFolder}\\django_my_site\\Scripts\\python.exe",
        "python-envs.defaultEnvManager": "ms-python.python:venv",
        "python.terminal.activateEnvironment": true
      ${workspaceFolder} = the opened folder (my_site), so no full path.

## requirements.txt: the package list for the host

    - With the venv active:
        python -m pip freeze > requirements.txt
      -> every package in the venv with its exact version:
        asgiref==3.13.0
        Django==6.1.2
        pillow==13.0.0
        sqlparse==0.6.1
        tzdata==2026.6
    - The host installs the same versions with pip install -r requirements.txt.
      That's why the venv matters: freeze from the system Python would list
      everything ever installed on this PC.
    - Mistake: > in Windows PowerShell 5.1 writes UTF-16. pip can read it, but
      git treats it as a binary file (no diff), and other tools may not read
      it. Rewritten as plain UTF-8 from Git Bash (same command). In PowerShell:
        python -m pip freeze | Out-File -Encoding utf8 requirements.txt
    - Run freeze again after installing a new package.
    - Checked: pip install -r requirements.txt --dry-run reads it fine.

## Settings from environment variables: DEBUG, SECRET_KEY, ALLOWED_HOSTS

    - settings.py:
        from os import getenv

        DEBUG = getenv("IS_PRODUCTION", "false").lower() != "true"

        SECRET_KEY = getenv("SECRET_KEY")
        if DEBUG and not SECRET_KEY:
            SECRET_KEY = "django-insecure-local-development-only"

        APP_HOST = getenv("APP_HOST")
        ALLOWED_HOSTS = [APP_HOST] if APP_HOST else []
    - On my PC nothing is set -> DEBUG on, the dev key, localhost allowed.
      On AWS (Environment properties, Source: Plain text): IS_PRODUCTION=True,
      SECRET_KEY=<new key>, APP_HOST=<domain>. Parameter Store / Secrets
      Manager would look the value up in another AWS service (needs extra
      IAM permissions).
    - DEBUG is the OPPOSITE of "is production", so != "true". .lower() makes
      True / true / TRUE all count (the AWS console has "True").
    - Mistake: DEBUG = getenv("IS_PRODUCTION", "false") == "true" -> DEBUG off
      on my PC (400 on every page, runserver won't start), and
      IS_PRODUCTION=true would turn it ON in production.
    - Env vars are always text. My first try:
        DEBUG = getenv("IS_PRODUCTION", True)
      Mistake 1: any text that isn't empty counts as True, so
      IS_PRODUCTION=false gave DEBUG = "false" -> still on. Comparing with
      == "true" gives a real True/False.
      Mistake 2: the name was the wrong way round (production -> DEBUG on).
    - Mistake: ALLOWED_HOSTS = [getenv("APP_HOST")] -> [None] on my PC. The
      list isn't empty, so Django stops allowing localhost by itself:
      400 Bad Request (DisallowedHost) on 127.0.0.1:8000. Empty list instead.
    - The old key was on GitHub, so it's public forever (git history). It's
      removed from the file, and production gets a NEW key, made once with:
        python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    - No key in production -> Django refuses to start: "The SECRET_KEY setting
      must not be empty". Better than running with a key everyone knows.
    - Side effect: a new local key ends old sessions (admin login, Read Later
      list), because they were signed with the old key.
    - Checked:
        - no env vars -> DEBUG True, 127.0.0.1 and localhost -> 200
        - production vars -> DEBUG False, own host 200, other host 400
        - production without SECRET_KEY -> ImproperlyConfigured
        - IS_PRODUCTION=True and =true -> DEBUG False both times

## Deploying to AWS Elastic Beanstalk: step by step (reference)

    Elastic Beanstalk (EB) = the AWS service the course uses to run the app.
    Steps in the order done so far (more get added as the course goes on).

    1. Settings from environment variables (my_site/settings.py):
        from os import getenv

        DEBUG = getenv("IS_PRODUCTION", "false").lower() != "true"

        SECRET_KEY = getenv("SECRET_KEY")
        if DEBUG and not SECRET_KEY:
            SECRET_KEY = "django-insecure-local-development-only"

        APP_HOST = getenv("APP_HOST")
        ALLOWED_HOSTS = [APP_HOST] if APP_HOST else []

    2. Where collected static files go (settings.py):
        STATIC_ROOT = BASE_DIR / "staticfiles"

    3. Collect static files:
        python manage.py collectstatic
       -> staticfiles/ (137 files)

    4. Static files and uploads via urls.py (my_site/urls.py):
        ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
          + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    5. Virtual environment + packages:
        python3 -m venv django_my_site
        .\django_my_site\Scripts\Activate.ps1
        pip install django pillow
       VS Code: .vscode/settings.json points at the venv.

    6. requirements.txt (venv active):
        python -m pip freeze | Out-File -Encoding utf8 requirements.txt
       (plain > in Windows PowerShell 5.1 writes UTF-16)

    7. EB config file: .ebextensions/django.config
       Correct version (YAML: colons, spaces not tabs):
        option_settings:
          aws:elasticbeanstalk:container:python:
            WSGIPath: my_site.wsgi:application
       my_site.wsgi = my_site/wsgi.py, application = the object inside it.
       Mistakes in my first version (fixed):
        option_settings;
          aws:elasticbeanstalk:container:python;
          SWGIPath: mysite.wsgi:application
        - ; instead of : on lines 1-2 -> not valid YAML.
        - SWGIPath -> must be WSGIPath.
        - mysite -> the folder is my_site.
       Mistakes on the way to fixing it:
        - option_setting (no s) -> EB only knows option_settings.
        - WSGIPath line indented 2 spaces, same as the line above -> it was a
          sibling, not inside the python section. Indentation = nesting in
          YAML, so it needs 4.

    8. Zip the CONTENTS of my_site/ (not the folder itself) -> code.zip.
       manage.py, requirements.txt and .ebextensions/ are at the top of the
       zip. In it: .ebextensions/, blog/, my_site/, templates/, staticfiles/,
       uploads/, db.sqlite3, manage.py, requirements.txt. Not the venv.

    9. Elastic Beanstalk -> Environment details -> Upload local file ->
       upload code.zip.

    10. Environment properties: Source = Plain text (not Parameter Store or
        Secrets Manager, those look the value up in other AWS services and
        need extra permissions):
            IS_PRODUCTION = True
            APP_HOST      = (set)

    11. Click Create.
        -> "Elastic Beanstalk is launching your environment" (environment
        Django-blog-env, region ap-southeast-2). It failed after a few seconds,
        because the zip still had the broken django.config (step 7):
            ERROR The configuration file .ebextensions/django.config ...
            contains invalid YAML or JSON. YAML exception: Invalid Yaml:
            mapping values are not allowed here ... line 3, column 11:
            SWGIPath: mysite.wsgi:application
            ERROR Failed to launch environment.
        The ; at the end of lines 1-2 means they aren't "key:" lines, so the
        parser doesn't expect a "key: value" on line 3 (column 11 = the colon
        after SWGIPath). EB reads the file before anything else, so nothing
        was started.

    12. New zip (current settings.py, mysite -> my_site in django.config) and
        a deploy to the same environment:
            Status: Failed, Type: Environment Update
            ERROR Failed Environment update activity. Reason: Environment not
            found with ID: e-...
        An environment that fails to launch is removed by EB, so there was no
        environment left to update. A failed launch means creating it again.
        Tried a deploy to it a second time (with the fixed zip) -> the same
        "Environment not found" error, same ID.

    13. Create environment again (Environments -> Create environment), with
        the fixed code.zip (correct django.config + current settings.py) and
        the environment properties, Source = Plain text:
            IS_PRODUCTION = True
            SECRET_KEY    = a new key, made with:
                python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
            APP_HOST      = the environment's domain (no http://, no /)
        -> "Environment successfully launched."

    14. Opened the domain -> Bad Request (400) on every page. Set APP_HOST to
        the URL from the address bar and deployed again -> still 400.
        The 400 came from Django (DisallowedHost), so Django was running and
        the SECRET_KEY worked; only the host didn't match. APP_HOST must be
        the domain only, no http:// and no trailing /:
            django-blog-env-1.eba-tep4bxha.ap-southeast-2.elasticbeanstalk.com
        Changing environment properties restarts the app by itself, no new
        deploy needed.
        -> The blog is live: home, all posts, a post, Read Later, admin login
        -> 200; /posts/nope/ -> 404.
        -> But no CSS and no images: /static/... and /files/... -> 404. With
        DEBUG off, static() in urls.py adds no routes (see "Serving static
        files via urls.py"), so nothing serves those files yet.

    15. Why the instructor's site had CSS and images: his settings.py
        (course branch deployment-03-deploying-with-elastic-beanstalk) has
            DEBUG = getenv("IS_DEVELOPMENT", True)
        Not set -> True; set to False -> the text "False", which also counts
        as True. So his live site runs with DEBUG on, and static() serves the
        files. Same urls.py as mine.
        To match the video: Configuration -> Updates, monitoring, and logging
        -> Edit -> IS_PRODUCTION = False -> Apply.
        -> DEBUG on, the site looks like local: CSS, the header image, post
        images and admin CSS -> 200.
        Downside: DEBUG on in production = error pages show code and
        settings to anyone. Set IS_PRODUCTION back to True later.

## Route 53, SSL, load balancer: what they are

    - The browser shows "Not secure" for the live blog because it's plain
      http://. These three are what a real site adds:
    - Route 53 = AWS's DNS service, the internet's phone book: turns a name
      (e.g. sachinsblog.com) into the server's address. Buy a domain there
      (or elsewhere) and point it at the EB environment, instead of the long
      ...elasticbeanstalk.com name.
    - SSL (HTTPS) = encrypts the traffic between browser and server, so
      logins, form data and cookies can't be read on the way (padlock,
      https://). Needs a certificate that proves you own the domain; AWS
      Certificate Manager (ACM) gives them out free. Only for a domain you
      own, and AWS owns elasticbeanstalk.com -> HTTPS needs your own domain.
    - Load balancer = sits in front of the app servers and spreads visitors
      over them; if one server is busy or broken, traffic goes to another.
      ACM certificates are attached to the load balancer, not the server, so
      on AWS HTTPS usually comes with one. My environment is "Single
      instance" (free tier preset): one server, no load balancer. A load
      balancer costs money even with little traffic.
    - Together:
        browser -> sachinsblog.com (Route 53) -> load balancer (SSL
        certificate) -> Django server(s)
        Also: the config still had ; on lines 1-2 and SWGIPath, so it would
        have failed the same way.

## Helpful resources

    - Course code snapshot repository (branch per lesson):
        https://github.com/academind/django-practical-guide-course-code
    - Django docs:
        https://docs.djangoproject.com/en/6.0/
    - Blog project course files (CSS + images), and lesson snapshots in the
      branches starting with "prj-urls-views-templates-...":
        https://github.com/academind/django-practical-guide-course-code/tree/prj-urls-views-templates-zz-extra-files
    - Example snapshot (first lesson of this section):
        https://github.com/academind/django-practical-guide-course-code/tree/prj-urls-views-templates-01-adding-urls-and-views
    - Section 9 code snapshots = branches starting with "prj-data-models-...", e.g.:
        https://github.com/academind/django-practical-guide-course-code/tree/prj-data-models-01-added-models-and-relations
    - Section 9 module slides:
        https://github.com/academind/django-practical-guide-course-code/tree/prj-data-models-zz-extra-files/slides
    - Section 14 code snapshots = branches starting with "prj-blog-uploads-sessions-...", e.g.:
        https://github.com/academind/django-practical-guide-course-code/tree/prj-blog-uploads-sessions-01-serving-uploaded-files/
    - SQL vs NoSQL (Academind article):
        https://academind.com/articles/sql-vs-nosql
    - Virtual environments (Python docs), with the activate commands for
      macOS / Linux and Windows further down:
        https://docs.python.org/3/library/venv.html#creating-virtual-environments
      The easiest way to activate is to let VS Code do it (.vscode/settings.json).
    - Path converters (str, int, slug, uuid, path) in URLs:
        https://docs.djangoproject.com/en/3.1/topics/http/urls/#path-converters
    - PEP 8 (Python style guide):
        https://peps.python.org/pep-0008/
