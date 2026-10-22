from django.shortcuts import render

from blog.models import Post
from blog.utils import posts_with_likes


def interesting(request):
    posts = posts_with_likes(Post.objects.all(), request)
    return render(request, "interesting.html", {"posts": posts})
