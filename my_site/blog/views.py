from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count, F
from .models import Post
from django.views.generic import ListView
from .forms import CommentForm
from django.views import View
# Create your views here.


def post_cards():
    # The post card shows the author, the tags and the number of comments.
    # Without the next three lines every card would run 3 more queries
    # (N+1 problem). See "N+1 queries" in LEARNING_LOG.md.
    return (
        Post.objects
        .select_related("author")               # FK  -> JOIN, same query
        .prefetch_related("tags")               # M2M -> 1 extra query for ALL posts
        .annotate(comment_count=Count("comments"))  # COUNT + GROUP BY in SQL
        .order_by("-date")
    )


class StartingPageView(ListView):
    template_name = "blog/index.html"
    context_object_name = "posts"

    def get_queryset(self):
        return post_cards()[:3]


class AllPostsView(ListView):
    template_name = "blog/all-posts.html"
    context_object_name = "all_posts"

    def get_queryset(self):
        return post_cards()


class SinglePostView(View):
    def is_stored_post(self, request, post_id):
        stored_posts = request.session.get("stored_posts")
        if stored_posts is not None:
            is_saved_for_later = post_id in stored_posts
        else:
            is_saved_for_later = False

        return is_saved_for_later

    def get_post(self, slug):
        # select_related: post.author in the template needs no extra query
        return get_object_or_404(Post.objects.select_related("author"), slug=slug)

    def get(self,request,slug):
        post = self.get_post(slug)

        # F(): the database adds 1 itself (UPDATE ... SET view_count = view_count + 1).
        # No lost updates when two people open the post at the same moment.
        Post.objects.filter(pk=post.pk).update(view_count=F("view_count") + 1)
        post.view_count += 1  # the object in memory still has the old value

        context = {
            "post":post,
            "post_tags": post.tags.all(),
            "comment_form": CommentForm(),
            "comments": post.comments.all().order_by("-id"),
            "saved_for_later": self.is_stored_post(request, post.id)
        }
        return render(request, "blog/post_detail.html", context)

    
    def post(self, request, slug):
        comment_form = CommentForm(request.POST)
        post = self.get_post(slug)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            return HttpResponseRedirect(reverse("post_detail-page", args=[slug]))

        context = {
            "post":post,
            "post_tags": post.tags.all(),
            "comment_form": comment_form,
            "comments": post.comments.all().order_by("-id"),
            "saved_for_later": self.is_stored_post(request, post.id)

        }
        return render(request, "blog/post_detail.html", context)


class ReadLaterView(View):

    def get(self, request):
        stored_posts = request.session.get("stored_posts")

        context = {}

        if stored_posts is None or len(stored_posts) == 0:
            context["posts"] = []
            context["has_posts"] = False

        else:
            # 1 query for all stored posts (id__in), not 1 per id.
            # only(): the page shows just the title and the link.
            posts = Post.objects.filter(id__in=stored_posts).only("title", "slug")
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
        else:
            stored_posts.remove(post_id)
        request.session["stored_posts"] = stored_posts

        return HttpResponseRedirect("/")