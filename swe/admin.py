from django.contrib import admin
from swe.models import ManuscriptOrder, OriginalDocument, ManuscriptEdit, ServiceType, Subject, WordCountRange


class OriginalDocumentInline(admin.StackedInline):
    model = OriginalDocument


class ManuscriptEditInline(admin.StackedInline):
    model = ManuscriptEdit


class ManuscriptOrderAdmin(admin.ModelAdmin):
    inlines = [OriginalDocumentInline, ManuscriptEditInline]


admin.site.register(ManuscriptOrder, ManuscriptOrderAdmin)
admin.site.register([ServiceType, Subject, WordCountRange])
