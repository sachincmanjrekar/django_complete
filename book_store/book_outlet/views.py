from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.db.models import Avg

from .models import Book

# Create your views here.

def index(request):
    if request.GET.get("slow"):
        # /?slow=1 -> the N+1 version: 1 query for the books, then more queries for EACH book in the template
        books = Book.objects.all().order_by("title")
    else:
        books = (
            Book.objects
            .select_related("author__address")         # ForeignKey / OneToOne: JOIN, same query
            .prefetch_related("published_countries")   # ManyToMany: 1 extra query for ALL books
            .order_by("title")
        )
    num_books = books.count()
    avg_rating = books.aggregate(Avg("rating"))  # {"rating__avg": 3.0}

    return render(request, "book_outlet/index.html", {
        "books": books,
        "total_number_of_books": num_books,
        "average_rating": avg_rating["rating__avg"],
    })


def book_detail(request, slug):
    # try:
    #     book = Book.objects.get(pk=id)
    # except:
    #     raise Http404()
    book = get_object_or_404(Book, slug=slug)
    return render(request, "book_outlet/book_detail.html", 
                  {"title": book.title, 
                   "author": book.author,
                   "rating": book.rating,
                   "is_bestseller": book.is_bestselling})
