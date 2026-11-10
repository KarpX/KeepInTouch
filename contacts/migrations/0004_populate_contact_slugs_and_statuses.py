from django.db import migrations
from django.utils.text import slugify
from unidecode import unidecode


def populate_slugs_and_statuses(apps, schema_editor):
    Contact = apps.get_model("contacts", "Contact")
    for contact in Contact.objects.all().order_by("pk"):
        full_name = f"{contact.name} {contact.firstname}".strip()
        transliterated = unidecode(full_name)
        base_slug = slugify(transliterated) or "contact"
        contact.slug = f"{base_slug}-{contact.pk}"
        if not contact.status:
            contact.status = "active"
        contact.save(update_fields=["slug", "status"])


class Migration(migrations.Migration):

    dependencies = [
        ("contacts", "0003_add_status_slug_generated_fields"),
    ]

    operations = [
        migrations.RunPython(populate_slugs_and_statuses, migrations.RunPython.noop),
    ]
