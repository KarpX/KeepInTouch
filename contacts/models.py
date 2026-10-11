from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="contact_groups",
        verbose_name="Владелец",
    )

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Contact(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    firstname = models.CharField(max_length=100, verbose_name="Фамилия", blank=True)
    number = models.BigIntegerField(verbose_name="Номер телефона")
    birthday = models.DateField(verbose_name="Дата рождения")
    is_favorite = models.BooleanField(default=False, verbose_name="Избранное")
    tags = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Теги (через запятую)",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name="Владелец",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contacts",
        verbose_name="Группа",
    )

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"
        ordering = ["name", "firstname"]

    def __str__(self):
        return f"{self.name} {self.firstname}"

    def toggle_favorite(self):
        self.is_favorite = not self.is_favorite
        self.save(update_fields=["is_favorite"])

    def matches(self, query: str) -> bool:
        q = query.lower()
        group_name = self.group.name.lower() if self.group else ""
        return (
            q in self.name.lower()
            or q in self.firstname.lower()
            or q in str(self.number)
            or q in group_name
            or q in self.tags.lower()
        )

    @property
    def tag_list(self) -> list[str]:
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(",") if t.strip()]
