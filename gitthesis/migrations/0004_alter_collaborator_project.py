# Generated by Django 5.1.1 on 2024-10-11 19:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitthesis', '0003_project_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collaborator',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gitthesis.project'),
        ),
    ]
