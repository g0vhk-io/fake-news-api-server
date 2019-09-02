from django.db import models
from django.core.files.storage import default_storage
from enum import Enum
import imagehash
from PIL import Image
from goose3 import Goose
import os
from uuid import uuid4
import urltools
# Create your models here.

ReportTypes = (
  ('image', 'Image'),
  ('link', 'Link')
)

ReportStatuses = (
  ('pending', 'Pending'),
  ('processing', 'Processing'),
  ('factchecked', 'Fact Checked'),
  ('partially_wrong', 'Partially Wrong'),
  ('wrong', 'Wrong')
)

def normalize(url):
    url = urltools.normalize(url)
    return url.split('?')[0]


def rename_upload_file(instance, filename):
    basefilename, file_extension = os.path.splitext(filename)
    return 'fakenews/image/' + str(uuid4()) + file_extension

class ImageReport(models.Model):
    image_hash = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=2048, blank=True)
    image = models.ImageField(upload_to=rename_upload_file)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LinkReport(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    url = models.CharField(max_length=2048)
    url_hash = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=1024, blank=True)
    text = models.CharField(max_length=4096, blank=True)
    short_text = models.CharField(max_length=4096, blank=True)
    image = models.CharField(max_length=4096, blank=True)


    def save(self, *args, **kwargs):
        self.url = normalize(self.url)
        try:
            g = Goose()
            article = g.extract(url=self.url)
            self.title = article.title
            self.short_text = article.meta_description
            self.text = article.cleaned_text
            self.image = article.opengraph.get('image', '') if article.top_image is None else article.top_image.src
        except:
            pass
        super(LinkReport, self).save(*args, **kwargs)

class Report(models.Model):
    status = models.CharField(max_length=128, choices=ReportStatuses, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    report_type = models.CharField(max_length=128, choices=ReportTypes)
    link_report = models.ForeignKey(LinkReport, on_delete=models.CASCADE, null=True, blank=True)
    image_report = models.ForeignKey(ImageReport, on_delete=models.CASCADE, null=True, blank=True)


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    comment = models.CharField(max_length=4096)
