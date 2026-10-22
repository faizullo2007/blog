from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationForm(forms.Form):
    name = forms.CharField(label="Имя", max_length=50)
    login = forms.CharField(label="Логин", max_length=150)
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    repeat_password = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput)
    age = forms.IntegerField(label="Возраст", min_value=1, max_value=120)
    work = forms.CharField(label="Работа", max_length=50)
    hobby = forms.CharField(label="Увлечения", max_length=1000, required=False)

    def clean_login(self):
        login = self.cleaned_data["login"].strip()
        if User.objects.filter(username=login).exists():
            raise forms.ValidationError("Этот логин уже занят")
        return login

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < 8:
            raise forms.ValidationError("Пароль должен быть не короче 8 символов")
        return password

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        repeat = cleaned.get("repeat_password")
        if password and repeat and password != repeat:
            self.add_error("repeat_password", "Пароли не совпадают")
        return cleaned
