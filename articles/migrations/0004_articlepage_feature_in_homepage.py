# Generated by Django 3.1.14 on 2022-01-13 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0003_sectionpage_image_and_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepage',
            name='feature_in_homepage',
            field=models.BooleanField(default=False, help_text='Whether this article should appear with other featured articles at the top of the home page'),
        ),
    ]