from django.shortcuts import get_object_or_404, redirect, render

from blog.models import Post
from blog.utils import posts_with_likes

from .forms import PostForm


def cabinet(request):
    if not request.user.is_authenticated:
        return redirect("login")

    form = PostForm()
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("cabinet")

    posts = posts_with_likes(request.user.posts.all(), request)
    profile = getattr(request.user, "profile", None)
    return render(
        request,
        "cabinet.html",
        {"form": form, "posts": posts, "profile": profile, "owner": request.user},
    )


def delete_post(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    post = get_object_or_404(Post, pk=pk)
    if post.author_id == request.user.id and request.method == "POST":
        post.delete()
    return redirect("cabinet")
