# Generated by Django 5.1.1 on 2024-12-06 09:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitthesis', '0017_merge_20241109_0337'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='solved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='solved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='solved_comments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='sectionversion',
            name='characters_added',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='sectionversion',
            name='characters_removed',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='sectionversion',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='versions_updated', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='sectionversion',
            name='content',
            field=models.TextField(blank=True, default=''),
        ),
    ]
