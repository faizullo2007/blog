from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from .models import Like, Post, Profile

User = get_user_model()

admin.site.site_header = "СОЦ·СЕТЬ — Админ-панель"
admin.site.site_title = "СОЦ·СЕТЬ Admin"
admin.site.index_title = "Управление соцсетью · 1996"
admin.site.empty_value_display = "—"


def badge(text, bg, fg="#ffffff"):
    return format_html(
        '<span style="display:inline-block;min-width:18px;text-align:center;'
        'padding:2px 8px;border:1px solid #000;background:{};color:{};'
        'font-family:Helvetica,Arial,sans-serif;font-size:11px;font-weight:700;'
        'text-transform:uppercase;letter-spacing:.3px;">{}</span>',
        bg, fg, text,
    )


class AgeGroupFilter(admin.SimpleListFilter):
    title = "возрастная группа"
    parameter_name = "age_group"

    def lookups(self, request, model_admin):
        return [
            ("child", "до 18"),
            ("young", "18–29"),
            ("adult", "30–59"),
            ("senior", "60+"),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == "child":
            return queryset.filter(age__lt=18)
        if value == "young":
            return queryset.filter(age__gte=18, age__lte=29)
        if value == "adult":
            return queryset.filter(age__gte=30, age__lte=59)
        if value == "senior":
            return queryset.filter(age__gte=60)
        return queryset


class HasPostsFilter(admin.SimpleListFilter):
    title = "наличие постов"
    parameter_name = "has_posts"

    def lookups(self, request, model_admin):
        return [("yes", "есть посты"), ("no", "нет постов")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(posts__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(posts__isnull=True)
        return queryset


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0
    max_num = 1
    verbose_name_plural = "Анкета"
    fields = ("name", "age", "work", "hobby")


class PostInline(admin.TabularInline):
    model = Post
    fk_name = "author"
    extra = 0
    fields = ("text", "created_at")
    readonly_fields = ("created_at",)
    show_change_link = True


class LikeInline(admin.TabularInline):
    model = Like
    extra = 0
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at",)
    show_change_link = True
    verbose_name_plural = "Лайки"


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline, PostInline]
    list_display = (
        "username",
        "email",
        "profile_name",
        "posts_badge",
        "likes_received_badge",
        "status_badge",
        "date_joined",
    )
    list_filter = BaseUserAdmin.list_filter + (HasPostsFilter,)
    search_fields = ("username", "email", "first_name", "last_name", "profile__name")
    ordering = ("-date_joined",)
    list_per_page = 25
    save_on_top = True
    show_facets = admin.ShowFacets.ALWAYS

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("profile")
            .annotate(
                _posts=Count("posts", distinct=True),
                _likes_recv=Count("posts__likes", distinct=True),
            )
        )

    @admin.display(description="Имя")
    def profile_name(self, obj):
        profile = getattr(obj, "profile", None)
        return getattr(profile, "name", "") or "—"

    @admin.display(description="Постов", ordering="_posts")
    def posts_badge(self, obj):
        return badge(obj._posts, "#000000")

    @admin.display(description="Лайков получено", ordering="_likes_recv")
    def likes_received_badge(self, obj):
        return badge(obj._likes_recv, "#e91d2a")

    @admin.display(description="Статус")
    def status_badge(self, obj):
        if obj.is_superuser:
            return badge("SUPER", "#6a26a4")
        if obj.is_staff:
            return badge("STAFF", "#000000")
        return badge("USER", "#9ab6c8", "#000000")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user_link", "name", "age_badge", "work", "posts_badge", "hobby_short")
    list_display_links = ("name",)
    list_editable = ("work",)
    list_filter = ("work", AgeGroupFilter)
    search_fields = ("user__username", "name", "work", "hobby")
    autocomplete_fields = ("user",)
    list_select_related = ("user",)
    list_per_page = 25
    save_on_top = True
    fieldsets = (
        ("Пользователь", {"fields": ("user",)}),
        ("Анкета", {"fields": ("name", "age", "work", "hobby")}),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .annotate(_posts=Count("user__posts", distinct=True))
        )

    @admin.display(description="Пользователь", ordering="user__username")
    def user_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.user_id])
        return format_html('<a href="{}">@{}</a>', url, obj.user.username)

    @admin.display(description="Возраст", ordering="age")
    def age_badge(self, obj):
        if obj.age is None:
            return badge("—", "#9ab6c8", "#000000")
        if obj.age < 18:
            return badge(obj.age, "#8e8a25")
        if obj.age < 30:
            return badge(obj.age, "#6a26a4")
        if obj.age < 60:
            return badge(obj.age, "#000000")
        return badge(obj.age, "#e91d2a")

    @admin.display(description="Постов", ordering="_posts")
    def posts_badge(self, obj):
        return badge(obj._posts, "#000000")

    @admin.display(description="Увлечения")
    def hobby_short(self, obj):
        if not obj.hobby:
            return "—"
        return obj.hobby if len(obj.hobby) <= 40 else obj.hobby[:40] + "…"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author_link", "text_preview", "likes_badge", "created_at")
    list_display_links = ("id", "text_preview")
    list_filter = ("created_at", "author")
    search_fields = ("text", "author__username")
    date_hierarchy = "created_at"
    autocomplete_fields = ("author",)
    readonly_fields = ("created_at", "likes_badge")
    inlines = [LikeInline]
    list_select_related = ("author",)
    ordering = ("-created_at",)
    list_per_page = 30
    save_on_top = True
    fieldsets = (
        (None, {"fields": ("author", "text")}),
        ("Служебное", {"fields": ("created_at", "likes_badge")}),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("author")
            .annotate(_likes=Count("likes", distinct=True))
        )

    @admin.display(description="Автор", ordering="author__username")
    def author_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.author_id])
        return format_html('<a href="{}">@{}</a>', url, obj.author.username)

    @admin.display(description="Текст")
    def text_preview(self, obj):
        return obj.text if len(obj.text) <= 60 else obj.text[:60] + "…"

    @admin.display(description="Лайков", ordering="_likes")
    def likes_badge(self, obj):
        count = getattr(obj, "_likes", obj.likes.count())
        return badge(count, "#e91d2a")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user_link", "post_preview", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "post__text")
    date_hierarchy = "created_at"
    autocomplete_fields = ("user", "post")
    list_select_related = ("user", "post")
    list_per_page = 50

    @admin.display(description="Пользователь", ordering="user__username")
    def user_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.user_id])
        return format_html('<a href="{}">@{}</a>', url, obj.user.username)

    @admin.display(description="Пост")
    def post_preview(self, obj):
        text = obj.post.text
        return text if len(text) <= 50 else text[:50] + "…"
