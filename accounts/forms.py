from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=False, label="Имя")
    last_name = forms.CharField(max_length=50, required=False, label="Фамилия")
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tailwind_cls = (
            "w-full px-3.5 py-2.5 bg-surface-container-low hover:bg-surface-container rounded-lg "
            "border border-outline-variant/50 font-body-base text-body-sm text-on-surface placeholder:text-outline "
            "focus:outline-none focus:bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
        )
        for field in self.fields.values():
            field.widget.attrs["class"] = tailwind_cls
