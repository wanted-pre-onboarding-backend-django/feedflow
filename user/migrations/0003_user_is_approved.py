# Generated by Django 5.0.7 on 2024-08-26 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_alter_user_managers_remove_user_date_joined_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_approved",
            field=models.BooleanField(default=False),
        ),
    ]
