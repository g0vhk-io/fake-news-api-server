# Generated by Django 2.1.7 on 2019-09-08 08:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0009_auto_20190907_0546'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('created', 'Created'), ('status_updated', 'Status Updated'), ('resolved', 'Case Closed'), ('reverted', 'Reverted')], max_length=128)),
                ('description', models.CharField(blank=True, default='', max_length=1024)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='commented_by',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='report',
            name='report_type',
            field=models.CharField(choices=[('image', 'Image'), ('link', 'Link'), ('text', 'Text')], max_length=128),
        ),
        migrations.AddField(
            model_name='event',
            name='report',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='report.Report'),
        ),
    ]
