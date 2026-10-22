from django import forms

from blog.models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3, "maxlength": 500}),
        }
        labels = {"text": "Текст поста"}

    def clean_text(self):
        text = self.cleaned_data["text"].strip()
        if not text:
            raise forms.ValidationError("Пост не может быть пустым")
        if len(text) > 500:
            raise forms.ValidationError("Пост не длиннее 500 символов")
        return text
