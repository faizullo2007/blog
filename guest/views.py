from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render

from blog.utils import posts_with_likes

User = get_user_model()


def guest_room(request, username):
    if request.user.is_authenticated and request.user.username == username:
        return redirect("cabinet")

    owner = get_object_or_404(User, username=username)
    posts = posts_with_likes(owner.posts.all(), request)
    profile = getattr(owner, "profile", None)
    return render(
        request,
        "guest_room.html",
        {"owner": owner, "profile": profile, "posts": posts},
    )
