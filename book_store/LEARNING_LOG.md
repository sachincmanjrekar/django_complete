## Section 6: Data and models

## django-admin startproject book_store

    - Creates a new Django project named "book_store" (inside django_complete/,
      next to mypage, monthly_challenges and my_site).
    - Makes a folder "book_store" containing:
        manage.py          -> tool to run project commands (runserver, migrate, startapp, ...)
        book_store/        -> project settings package
            __init__.py    -> marks the folder as a Python package
            settings.py    -> project configuration (installed apps, database, etc.)
            urls.py        -> main URL routes of the site
            asgi.py        -> entry point for async web servers
            wsgi.py        -> entry point for regular web servers

## python manage.py startapp book_outlet

    - Creates the "book_outlet" app (admin.py, apps.py, migrations/, models.py,
      tests.py, views.py).
    - Registered in book_store/settings.py:
        INSTALLED_APPS = [
            ...
            'django.contrib.staticfiles',
            'book_outlet'
        ]
      (needed for models + migrations, not only templates).

## Database setting (SQLite by default)

    - settings.py:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
    - SQLite = a SQL database stored in ONE file (db.sqlite3), no server needed;
      good for development. Production often uses PostgreSQL/MySQL (change ENGINE).
    - SQL databases store data in tables (rows + columns); see SQL vs NoSQL link.

## First model (book_outlet/models.py)

    - A model = a Python class that describes one database table:
        from django.db import models

        class Book(models.Model):
            title = models.CharField(max_length=50)
            rating = models.IntegerField()
    - class Book(models.Model) -> table book_outlet_book (app name + model name).
    - Each class attribute = a column:
        CharField(max_length=50) -> text, max 50 characters (max_length required)
        IntegerField()           -> whole numbers
    - Django adds an id column automatically (primary key, BigAutoField, 1, 2, 3...).
    - No SQL written by hand - Django's ORM turns Python into SQL.

## Migrations (makemigrations + migrate)

    - python manage.py makemigrations
        -> compares models.py with existing migrations and writes a new file:
           book_outlet/migrations/0001_initial.py
        operations = [
            migrations.CreateModel(
                name='Book',
                fields=[
                    ('id', models.BigAutoField(auto_created=True, primary_key=True, ...)),
                    ('title', models.CharField(max_length=50)),
                    ('rating', models.IntegerField()),
                ],
            ),
        ]
      (only a plan/instructions - the database is NOT changed yet)
    - python manage.py migrate
        -> runs all migrations not yet applied -> creates the tables in db.sqlite3:
           book_outlet_book + Django's own (auth_user, django_session, admin...).
    - Applied migrations are recorded in the django_migrations table, so each
      runs only once.
    - Rule: change models.py -> makemigrations -> migrate.
    - Migration files ARE committed to git (they describe the database);
      db.sqlite3 is NOT (it's in .gitignore).

## Inserting data with the Django shell (save)

    - python manage.py shell -> Python shell with the project loaded.
    - Create a row:
        >>> from book_outlet.models import Book
        >>> harry_potter = Book(title="h1", rating=5)
        >>> harry_potter.save()        # INSERT INTO book_outlet_book ...
        >>> lord_of_the_rings = Book(title="lr", rating=4)
        >>> lord_of_the_rings.save()
    - Book(...) only creates a Python object; save() writes it to the database.
    - id is filled in automatically: now the table has
        id 1 -> "h1", rating 5
        id 2 -> "lr", rating 4
    - Read them back:
        >>> Book.objects.all()
        <QuerySet [<Book: Book object (1)>, <Book: Book object (2)>]>

## __str__ (readable output for a model)

    - Default output "Book object (1)" says nothing about the book.
    - models.py:
        class Book(models.Model):
            title = models.CharField(max_length=50)
            rating = models.IntegerField()

            def __str__(self):
                return f"{self.title} ({self.rating})"
    - Now (restart the shell to load the change):
        >>> Book.objects.all()
        <QuerySet [<Book: h1 (5)>, <Book: lr (4)>]>
    - __str__ is a normal Python method, NOT a field -> no new column,
      no makemigrations needed.
    - Also used later by the admin site and anywhere the object is printed.

## Helpful resources

    - Course code snapshot repository (branch per lesson):
        https://github.com/academind/django-practical-guide-course-code
    - SQL vs NoSQL databases (Academind article):
        https://academind.com/articles/sql-vs-nosql
    - Django docs:
        https://docs.djangoproject.com/en/6.0/
    - Models (fields, Meta, methods):
        https://docs.djangoproject.com/en/6.0/topics/db/models/
    - Model field reference (CharField, IntegerField, options...):
        https://docs.djangoproject.com/en/6.0/ref/models/fields/
    - Migrations (makemigrations, migrate, showmigrations):
        https://docs.djangoproject.com/en/6.0/topics/migrations/
    - PEP 8 (Python style guide):
        https://peps.python.org/pep-0008/
