from django import forms
from .models import Contact, Group


TAILWIND_INPUT_CLASS = (
    "w-full px-3.5 py-2.5 bg-surface-container-low hover:bg-surface-container rounded-lg "
    "border border-outline-variant/50 font-body-base text-body-sm text-on-surface placeholder:text-outline "
    "focus:outline-none focus:bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
)

TAILWIND_SELECT_CLASS = (
    "w-full px-3.5 py-2.5 bg-surface-container-low hover:bg-surface-container rounded-lg "
    "border border-outline-variant/50 font-body-base text-body-sm text-on-surface "
    "focus:outline-none focus:bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
)


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
            "name": forms.TextInput(attrs={"class": TAILWIND_INPUT_CLASS, "placeholder": "Имя"}),
            "firstname": forms.TextInput(attrs={"class": TAILWIND_INPUT_CLASS, "placeholder": "Фамилия"}),
            "number": forms.NumberInput(attrs={"class": TAILWIND_INPUT_CLASS, "placeholder": "79001234567"}),
            "birthday": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"class": TAILWIND_INPUT_CLASS, "type": "date"},
            ),
            "group": forms.Select(attrs={"class": TAILWIND_SELECT_CLASS}),
            "is_favorite": forms.CheckboxInput(
                attrs={"class": "w-5 h-5 rounded border-outline-variant/60 text-primary focus:ring-primary/20 accent-primary cursor-pointer"}
            ),
            "tags": forms.TextInput(
                attrs={
                    "class": TAILWIND_INPUT_CLASS,
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
            "name": forms.TextInput(attrs={"class": TAILWIND_INPUT_CLASS, "placeholder": "Название группы"}),
            "description": forms.Textarea(
                attrs={"class": TAILWIND_INPUT_CLASS, "rows": 3, "placeholder": "Краткое описание группы"}
            ),
        }
