from django.shortcuts import render
from rest_framework.parsers import FileUploadParser
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


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageReport
        fields = "__all__"

class ImageUploadView(APIView):
    parser_class = (FileUploadParser,)
    def post(self, request, *args, **kwargs):
      image_data = request.data.get('image', None)
      if image_data is not None:
          orig_image = image_data
          pil_image = Image.open(orig_image)
          width, height = pil_image.size
          max_dim = 1200
          if width > max_dim :
              pil_image = resizeimage.resize_width(pil_image, max_dim)
          elif height > max_dim :
              pil_image = resizeimage.resize_height(pil_image, max_dim)
          print(orig_image.__dict__)
          output = BytesIO()
          pil_image.save(output, format='JPEG', quality=100)
          output.seek(0)
          inmemory = InMemoryUploadedFile(output, 'image', 'a.jpg', 'image/jpeg', output.getbuffer().nbytes, None)
          image_hash_text = imagehash.phash(pil_image)
          existed_object = ImageReport.objects.filter(image_hash=image_hash_text).first()
          if existed_object is not None:
              print(existed_object.__dict__)
              return Response({'result': 'already_existed', 'key': existed_object.id, 'report': existed_object.image_hash}, status=status.HTTP_201_CREATED)
          else:
              image_report = ImageReport()
              image_report.image_hash = image_hash_text
              image_report.image = inmemory
              image_report.save()
              return Response({'key': image_report.id}, status=status.HTTP_201_CREATED)
      else:
          return Response({'reason': 'Image is invalid.'}, status=status.HTTP_400_BAD_REQUEST)
