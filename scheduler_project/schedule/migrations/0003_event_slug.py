# Generated by Django 3.1.7 on 2021-03-21 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_auto_20210321_2157'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='slug',
            field=models.SlugField(default=None, max_length=250, unique_for_date='planning date'),
        ),
    ]
