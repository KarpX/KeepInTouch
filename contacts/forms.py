from django import forms
from .models import Contact, Group


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            "name",
            "firstname",
            "number",
            "birthday",
            "group",
            "is_favorite",
            "tags",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Имя"}),
            "firstname": forms.TextInput(attrs={"class": "form-control", "placeholder": "Фамилия"}),
            "number": forms.NumberInput(attrs={"class": "form-control", "placeholder": "79001234567"}),
            "birthday": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"class": "form-control", "type": "date"},
            ),
            "group": forms.Select(attrs={"class": "form-select"}),
            "is_favorite": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "tags": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "коллеги, проект, спорт (через запятую)",
                    "list": "existingTagsList",
                    "id": "id_tags",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["group"].queryset = Group.objects.filter(owner=user)
        self.fields["group"].empty_label = "— Без группы —"
        self.fields["birthday"].widget.format = "%Y-%m-%d"
        self.fields["birthday"].input_formats = ["%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d"]


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Название группы"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Краткое описание группы"}
            ),
        }
