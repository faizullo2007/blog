
from django.db.models import Count, Exists, OuterRef

from .models import Like


def posts_with_likes(queryset, request):
    queryset = queryset.select_related("author", "author__profile").annotate(
        likes_count=Count("likes", distinct=True)
    )
    if request.user.is_authenticated:
        liked = Like.objects.filter(post=OuterRef("pk"), user=request.user)
        queryset = queryset.annotate(liked=Exists(liked))
    return queryset
