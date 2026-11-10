from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.db.models import Avg, Max, Min, Sum, Count, Q, F

from .models import Book, Author

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
    # aggregate: ONE result for the whole queryset, a dict
    stats = Book.objects.aggregate(
        avg_rating=Avg("rating"), best=Max("rating"), worst=Min("rating"), total_views=Sum("views")
    )  # {"avg_rating": 4.33, "best": 5, "worst": 3, "total_views": 7}

    # annotate: a computed value ADDED TO EACH ROW (each author gets .num_books and .avg_rating)
    authors = Author.objects.annotate(
        num_books=Count("books"), avg_rating=Avg("books__rating")  # "books" = related_name of Book.author
    ).order_by("-num_books", "last_name")

    # Q: OR conditions (filter(a, b) is always AND)
    top_picks = Book.objects.filter(Q(rating=5) | Q(is_bestselling=True))   # rating 5 OR bestseller
    both = Book.objects.filter(rating=5, is_bestselling=True)              # rating 5 AND bestseller

    return render(request, "book_outlet/index.html", {
        "books": books,
        "total_number_of_books": num_books,
        "average_rating": stats["avg_rating"],
        "stats": stats,
        "authors": authors,
        "top_picks": top_picks,
        "both": both,
    })


def book_detail(request, slug):
    # try:
    #     book = Book.objects.get(pk=id)
    # except:
    #     raise Http404()
    # F: +1 INSIDE the database (UPDATE ... SET views = views + 1), no read-modify-write race
    Book.objects.filter(slug=slug).update(views=F("views") + 1)
    book = get_object_or_404(Book, slug=slug)  # Loaded after the update -> shows the new count
    return render(request, "book_outlet/book_detail.html", 
                  {"title": book.title, 
                   "author": book.author,
                   "rating": book.rating,
                   "is_bestseller": book.is_bestselling,
                   "views": book.views})
