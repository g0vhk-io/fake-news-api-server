# Generated by Django 2.1.7 on 2019-09-14 14:11

from django.db import migrations
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0010_auto_20190908_0838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='comment',
            field=markdownx.models.MarkdownxField(),
        ),
    ]
