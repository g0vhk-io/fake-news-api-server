from django.contrib import admin
from .models import *
from markdownx.admin import MarkdownxModelAdmin
# Register your models here.
admin.site.register(ImageReport)

admin.site.register(TextReport)
admin.site.register(LinkReport)
admin.site.register(Event)
admin.site.register(Report)
admin.site.register(Comment, MarkdownxModelAdmin)
