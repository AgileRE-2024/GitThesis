# Generated by Django 5.1.1 on 2024-11-08 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitthesis', '0015_comment_is_solved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='content',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='sectionversion',
            name='content',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]