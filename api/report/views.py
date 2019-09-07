from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import *
from rest_framework import serializers
from PIL import Image
import imagehash
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from resizeimage import resizeimage
import hashlib
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
import urltools
from datetime import datetime


def get_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


class ListReportView(APIView):
    def get(self, request, *args, **kwargs):
        def get_image_report(r):
            if r is None:
                return None
            return {'image': r.image.url, 'description': r.description}

        def get_link_report(r):
            if r is None:
                return None
            return {'url': r.url, 'title': r.title, 'short_text': r.short_text, 'image': r.image}
        reports = Report.objects.all().prefetch_related('image_report', 'link_report')
        output = [{'type': r.report_type, 'status': r.status, 'image': get_image_report(r.image_report), 'link': get_link_report(r.link_report)} for r in reports]
        return Response(output)


def check_too_many_reports():
    today = datetime.now().date()
    num_today_reports = Report.objects.filter(created_at__date=today).count()
    print(num_today_reports)
    if num_today_reports >= 50:
        return Response({'too_many': True, 'result': 'Not Okay'})
    return None


class ImageUploadView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    def post(self, request, *args, **kwargs):
      image_data = request.data.get('image', None)
      description = request.data.get('description', '')
      r = check_too_many_reports()
      if r is not None:
          return r
      if image_data is not None:
          orig_image = image_data
          pil_image = Image.open(orig_image)
          width, height = pil_image.size
          max_dim = 1200
          if width > max_dim :
              pil_image = resizeimage.resize_width(pil_image, max_dim)
          elif height > max_dim :
              pil_image = resizeimage.resize_height(pil_image, max_dim)
          output = BytesIO()
          pil_image.save(output, format='JPEG', quality=100)
          output.seek(0)
          inmemory = InMemoryUploadedFile(output, 'image', 'a.jpg', 'image/jpeg', output.getbuffer().nbytes, None)
          image_hash_text = imagehash.phash(pil_image)
          existed_object = get_or_none(ImageReport, image_hash=image_hash_text)
          if existed_object is not None:
              print(existed_object.__dict__)
              return Response({'result': 'already_existed', 'key': existed_object.id, 'report': existed_object.image_hash}, status=status.HTTP_201_CREATED)
          else:
              image_report = ImageReport()
              image_report.image_hash = image_hash_text
              image_report.image = inmemory
              image_report.description = description
              image_report.save()
              report = Report()
              report.report_type = 'image'
              report.image_report = image_report
              report.save()
              return Response({'key': image_report.id}, status=status.HTTP_201_CREATED)
      else:
          return Response({'reason': 'Image is invalid.'}, status=status.HTTP_400_BAD_REQUEST)


class LinkUploadView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    def post(self, request, *args, **kwargs):
        url = request.data.get('url', None)
        r = check_too_many_reports()
        print(r)
        if r is not None:
           return r
        if url is not None:
            url = normalize(url)
            url_hash = str(hashlib.md5(url.encode('utf-8')).hexdigest())
            existed_object = get_or_none(LinkReport, url_hash=url_hash) 
            if existed_object is not None:
                return Response({'result': 'already_existed', 'key': existed_object.id, 'report': existed_object.url_hash}, status=status.HTTP_201_CREATED)
            else:
                link_report = LinkReport()
                link_report.url = url
                link_report.url_hash = url_hash
                link_report.save()
                report = Report()
                report.report_type = 'link'
                report.link_report = link_report
                report.save()
                return Response({'key': link_report.id}, status=status.HTTP_201_CREATED)
        else:
            return Response({'reason': 'URL is invalid.'}, status=status.HTTP_399_BAD_REQUEST)
