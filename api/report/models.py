from django.db import models
from django.core.files.storage import default_storage
from enum import Enum
import imagehash
from PIL import Image
from url_normalize import url_normalize
from goose3 import Goose
import os
from uuid import uuid4
# Create your models here.

ReportTypes = (
  ('image', 'Image'),
  ('link', 'Link')
)


def rename_upload_file(instance, filename):
    basefilename, file_extension = os.path.splitext(filename)
    return 'fakenews/image/' + str(uuid4()) + file_extension

class ImageReport(models.Model):
    image_hash = models.CharField(max_length=128, unique=True)
    image = models.ImageField(upload_to=rename_upload_file)


class LinkReport(models.Model):
    url = models.CharField(max_length=2048)
    url_hash = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=1024, blank=True)
    text = models.CharField(max_length=4096, blank=True)
    short_text = models.CharField(max_length=4096, blank=True)
    image = models.CharField(max_length=4096, blank=True)


    def save(self, *args, **kwargs):
        self.url = url_normalize(self.url)
        g = Goose()
        article = g.extract(url=self.url)
        self.title = article.title
        self.short_text = article.meta_description
        self.text = article.cleaned_text
        self.image = article.opengraph.get('image', '') if article.top_image is None else article.top_image.src
        super(LinkReport, self).save(*args, **kwargs)

class Report(models.Model):
    report_type = models.CharField(max_length=128, choices=ReportTypes)
    link_report = models.ForeignKey(LinkReport, on_delete=models.CASCADE, null=True, blank=True)
    image_report = models.ForeignKey(ImageReport, on_delete=models.CASCADE, null=True, blank=True)

