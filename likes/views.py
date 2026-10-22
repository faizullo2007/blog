from django.shortcuts import get_object_or_404, redirect

from blog.models import Like, Post


def like_toggle(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST" and post.author_id != request.user.id:
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER")
    return redirect(next_url or "interesting")
