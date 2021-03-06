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
from django.shortcuts import get_object_or_404


def get_image_report(r):
    if r is None:
        return None
    return {'image': r.image.url, 'description': r.description}

def get_link_report(r):
    if r is None:
        return None
    return {'url': r.url, 'title': r.title, 'short_text': r.short_text, 'image': r.image}


def get_text_report(r):
    if r is None:
        return None
    return {'description': r.description}

def get_comment(comment):
    if comment is None:
        return None
    return {'md': comment.comment}


def save_created_event(report):
    event = Event()
    event.event_type = "created"
    event.description = "提交報告"
    event.report = report
    event.save()


def save_status_updated_event(report, new_status):
    event = Event()
    event.event_type = "status_updated"
    event.description = "狀態更新 (%s)" % (new_status)
    event.report = report
    event.save()



def get_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


class ListReportView(APIView):
    def get(self, request, *args, **kwargs):
        reports = Report.objects.all().prefetch_related('image_report', 'link_report').order_by('-created_at')
        output = [{'type': r.report_type, 'status': r.status, 'image': get_image_report(r.image_report), 'link': get_link_report(r.link_report), 'id': r.id, 'text': get_text_report(r.text_report)} for r in reports]
        return Response(output)


class ReportDetailView(APIView):
    def get(self, request, *args, **kwargs):
        pk = int(kwargs['report_id'])
        r = get_object_or_404(Report, pk=pk)
        comment = Comment.objects.filter(report__id=pk).first()
        output = {'comment': get_comment(comment), 'type': r.report_type, 'status': r.status, 'image': get_image_report(r.image_report), 'link': get_link_report(r.link_report), 'text': get_text_report(r.text_report), 'id': r.id}
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
              save_created_event(report)
              return Response({'key': report.id}, status=status.HTTP_201_CREATED)
      else:
          return Response({'reason': 'Image is invalid.'}, status=status.HTTP_400_BAD_REQUEST)

class TextUploadView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    def post(self, request, *args, **kwargs):
        text = request.data.get('text', None)
        r = check_too_many_reports()
        print(r)
        if r is not None:
           return r
        else:
            #TODO: check uniqueness via similarity
            text_report = TextReport()
            text_report.description = text
            text_report.save()
            report = Report()
            report.report_type = 'text'
            report.text_report = text_report
            report.save()
            save_created_event(report)
            return Response({'key': report.id}, status=status.HTTP_201_CREATED)
 

class CommentView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    def post(self, request, *args, **kwargs):
        report_id = int(request.data.get('report_id', '-1'))
        commented_by = int(request.data.get('commented_by', '1'))
        new_status = request.data.get('status', None)
        md = request.data.get('comment', '')
        report =  get_or_none(Report, id=report_id)
        print(report.status, new_status)
        if new_status is not None and new_status != report.status:
            report.status = new_status
            save_status_updated_event(report, new_status)
            report.save()
        if report is not None:
            comment, created = Comment.objects.get_or_create(report_id=report_id,defaults={'commented_by': commented_by})
            if created:
                comment.report = report
            comment.comment = md
            comment.save()
            return Response({'result': 'ok'}, status=status.HTTP_201_CREATED)
        return Response({'reason': 'Invalid.'}, status=status.HTTP_400_BAD_REQUEST)


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
                save_created_event(report)
                return Response({'key': report.id}, status=status.HTTP_201_CREATED)
        else:
            return Response({'reason': 'URL is invalid.'}, status=status.HTTP_400_BAD_REQUEST)
