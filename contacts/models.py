from datetime import date, datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Case, F, Q, Value, When
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode


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


class ContactQuerySet(models.QuerySet):
    """Набор запросов для работы с контактами (ПР10)."""

    def active(self):
        """Возвращает только активные контакты."""
        return self.filter(status=self.model.Status.ACTIVE)

    def archived(self):
        """Возвращает архивированные контакты."""
        return self.filter(status=self.model.Status.ARCHIVED)

    def blocked(self):
        """Возвращает заблокированные контакты."""
        return self.filter(status=self.model.Status.BLOCKED)

    def favorites(self):
        """Возвращает избранные контакты."""
        return self.filter(is_favorite=True)

    def for_group(self, group):
        """Возвращает контакты указанной группы."""
        return self.filter(group=group)

    def for_birthday_month(self, month: int):
        """Возвращает контакты, родившиеся в указанном месяце."""
        return self.filter(birthday__month=month)


class ContactManager(models.Manager.from_queryset(ContactQuerySet)):
    """Менеджер модели Contact с дополнительными методами QuerySet (ПР10)."""

    pass


class Contact(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Активен"
        ARCHIVED = "archived", "В архиве"
        BLOCKED = "blocked", "Заблокирован"

    name = models.CharField(max_length=100, verbose_name="Имя")
    firstname = models.CharField(max_length=100, verbose_name="Фамилия", blank=True)
    number = models.BigIntegerField(verbose_name="Номер телефона")
    birthday = models.DateField(verbose_name="Дата рождения")
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус",
    )
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
    has_surname = models.GeneratedField(
        expression=Case(
            When(~Q(firstname=""), then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Указана фамилия",
    )
    slug = models.SlugField(
        max_length=220,
        blank=True,
        unique=True,
        editable=False,
        verbose_name="URL-идентификатор",
    )

    objects = ContactManager()

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"
        ordering = ["name", "firstname"]

    def __str__(self):
        return f"{self.name} {self.firstname}".strip()

    def save(self, *args, **kwargs):
        if not self.slug:
            full_name = f"{self.name} {self.firstname}".strip()
            transliterated = unidecode(full_name)
            base_slug = slugify(transliterated) or "contact"
            if self.pk:
                self.slug = f"{base_slug}-{self.pk}"
            else:
                super().save(*args, **kwargs)
                self.slug = f"{base_slug}-{self.pk}"
                super().save(update_fields=["slug"])
                return
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Возвращает канонический URL карточки контакта."""
        if self.slug:
            try:
                return reverse("contacts:contact_detail_slug", kwargs={"slug": self.slug})
            except Exception:
                pass
        return reverse("contacts:contact_detail", kwargs={"pk": self.pk})

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

    @property
    def initials(self) -> str:
        first = self.name.strip()[:1].upper() if self.name else ""
        last = self.firstname.strip()[:1].upper() if self.firstname else ""
        return (first + last) if (first + last) else (first or "К")

    @property
    def formatted_phone(self) -> str:
        num_str = str(self.number)
        if len(num_str) == 11 and (num_str.startswith("7") or num_str.startswith("8")):
            return f"+7 ({num_str[1:4]}) {num_str[4:7]}-{num_str[7:9]}-{num_str[9:11]}"
        return f"+{num_str}"

    @property
    def days_until_birthday(self):
        if not self.birthday:
            return None
        bday = self.birthday
        if isinstance(bday, str):
            try:
                bday = datetime.strptime(bday, "%Y-%m-%d").date()
            except ValueError:
                return None
        today = date.today()
        try:
            bday_this_year = bday.replace(year=today.year)
        except ValueError:
            bday_this_year = bday.replace(year=today.year, day=28)

        if bday_this_year < today:
            try:
                bday_next = bday.replace(year=today.year + 1)
            except ValueError:
                bday_next = bday.replace(year=today.year + 1, day=28)
            return (bday_next - today).days
        return (bday_this_year - today).days

    @property
    def age(self):
        if not self.birthday:
            return None
        bday = self.birthday
        if isinstance(bday, str):
            try:
                bday = datetime.strptime(bday, "%Y-%m-%d").date()
            except ValueError:
                return None
        today = date.today()
        return today.year - bday.year - ((today.month, today.day) < (bday.month, bday.day))

    @property
    def next_age(self):
        a = self.age
        return a + 1 if a is not None else None
