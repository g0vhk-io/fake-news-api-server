from django.db import models
from django.core.files.storage import default_storage
from enum import Enum
import imagehash
from PIL import Image
# Create your models here.

ReportTypes = (
  ('image', 'Image'),
  ('link', 'Link')
)


class ImageReport(models.Model):
    image_hash = models.CharField(max_length=128, blank=True)
    image = models.ImageField(upload_to='fakenews/image')

    def save(self, *args, **kwargs):
        image = self.image
        image_hash_text = imagehash.phash(Image.open(image))
        self.image_hash = image_hash_text
        super(ImageReport, self).save(*args, **kwargs)

class LinkReport(models.Model):
    url = models.CharField(max_length=2048)


class Report(models.Model):
    report_type = models.CharField(max_length=128, choices=ReportTypes)
    link_report = models.ForeignKey(LinkReport, on_delete=models.CASCADE, null=True, blank=True)
    image_report = models.ForeignKey(ImageReport, on_delete=models.CASCADE, null=True, blank=True)

