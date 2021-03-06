# Generated by Django 2.1.7 on 2019-08-25 01:49

from django.db import migrations, models
import report.models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0003_auto_20190824_1750'),
    ]

    operations = [
        migrations.AddField(
            model_name='linkreport',
            name='url_hash',
            field=models.CharField(default='', max_length=64, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='imagereport',
            name='image',
            field=models.ImageField(upload_to=report.models.rename_upload_file),
        ),
        migrations.AlterField(
            model_name='imagereport',
            name='image_hash',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
