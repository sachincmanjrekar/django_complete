from django.db import connection
from django.db.models import F
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from .models import Author, Comment, Post, Tag


def make_posts(count):
    author = Author.objects.create(
        first_name="Sachin", last_name="Manjrekar", email_address="s@test.com"
    )
    tags = [Tag.objects.create(caption=c) for c in ("Featured", "Nature")]
    for i in range(count):
        post = Post.objects.create(
            title=f"Post {i}",
            excerpt="An excerpt",
            image="posts/test.jpg",
            slug=f"post-{i}",
            content="Some long enough content",
            author=author,
        )
        post.tags.set(tags)
        Comment.objects.create(
            user_name="Max", user_email="m@test.com", text="Nice!", post=post
        )


def make_posts_more(count):
    author = Author.objects.first()
    for i in range(count):
        post = Post.objects.create(
            title=f"More {i}", excerpt="x", image="posts/test.jpg",
            slug=f"more-{i}", content="Some long enough content", author=author,
        )
        post.tags.set(Tag.objects.all())


class PostListQueryTests(TestCase):
    """The number of queries must NOT grow with the number of posts."""

    def test_all_posts_page_runs_two_queries(self):
        make_posts(5)
        # 1) posts + author (JOIN) + comment count (GROUP BY)
        # 2) tags for all 5 posts (prefetch_related, WHERE post_id IN (...))
        with self.assertNumQueries(2):
            response = self.client.get(reverse("posts-page"))
        self.assertContains(response, "By Sachin Manjrekar", count=5)
        self.assertContains(response, "1 comment", count=5)
        self.assertContains(response, "Featured", count=5)

    def test_all_posts_page_same_queries_for_1_or_20_posts(self):
        make_posts(1)
        with CaptureQueriesContext(connection) as one:
            self.client.get(reverse("posts-page"))
        make_posts_more(19)
        with CaptureQueriesContext(connection) as twenty:
            self.client.get(reverse("posts-page"))
        self.assertEqual(len(one), len(twenty))

    def test_starting_page_runs_two_queries(self):
        make_posts(5)
        with self.assertNumQueries(2):
            response = self.client.get(reverse("starting-page"))
        self.assertEqual(len(response.context["posts"]), 3)

    def test_without_the_fix_it_is_n_plus_1(self):
        # The "before" version: plain Post.objects.all()
        make_posts(5)
        with CaptureQueriesContext(connection) as queries:
            for post in Post.objects.all():
                post.author.full_name()   # +1 query per post
                list(post.tags.all())     # +1 query per post
                post.comments.count()     # +1 query per post
        self.assertEqual(len(queries), 1 + 3 * 5)


class SinglePostTests(TestCase):
    def test_view_count_goes_up_with_f_expression(self):
        make_posts(1)
        url = reverse("post_detail-page", args=["post-0"])
        self.client.get(url)
        response = self.client.get(url)
        self.assertContains(response, "Read 2 times")
        self.assertEqual(Post.objects.get(slug="post-0").view_count, 2)

    def test_f_expression_does_not_lose_updates(self):
        # Two "requests" that loaded the post at the same time.
        make_posts(1)
        first = Post.objects.get(slug="post-0")
        second = Post.objects.get(slug="post-0")
        for post in (first, second):
            Post.objects.filter(pk=post.pk).update(view_count=F("view_count") + 1)
        self.assertEqual(Post.objects.get(slug="post-0").view_count, 2)


class ReadLaterTests(TestCase):
    def test_stored_posts_load_in_one_query(self):
        make_posts(5)
        for post in Post.objects.all():
            self.client.post(reverse("read-later"), {"post_id": post.id})
        # 1) load the session  2) all stored posts with id__in
        with self.assertNumQueries(2):
            response = self.client.get(reverse("read-later"))
        self.assertContains(response, "Post 4")
