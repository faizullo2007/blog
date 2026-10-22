from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect, render

from blog.models import Profile

from .forms import RegistrationForm

User = get_user_model()


def register(request):
    if request.user.is_authenticated:
        return redirect("cabinet")

    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data["login"],
                email=data["email"],
                password=data["password"],
            )
            Profile.objects.create(
                user=user,
                name=data["name"],
                age=data["age"],
                work=data["work"],
                hobby=data["hobby"],
            )
            login(request, user)  # авто-вход после регистрации
            return redirect("cabinet")
    return render(request, "registration.html", {"form": form})
