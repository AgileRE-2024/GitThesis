# Generated by Django 5.1.1 on 2024-11-08 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitthesis', '0014_alter_comment_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='is_solved',
            field=models.BooleanField(default=False),
        ),
    ]