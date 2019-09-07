from django.urls import path
from .views import *

urlpatterns = [
    path('upload_image_report', ImageUploadView.as_view()),
    path('upload_text_report', TextUploadView.as_view()),
    path('upload_link_report', LinkUploadView.as_view()),
    path('reports', ListReportView.as_view())
]
