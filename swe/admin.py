from django.contrib import admin
from swe.models import ManuscriptOrder, OriginalDocument, ManuscriptEdit, ServiceType, Subject, WordCountRange, ServiceList, PricePoint
from swe.models import SubjectList, SubjectCategory, Subject, UserProfile

admin.site.register([ServiceType, Subject, WordCountRange, UserProfile])

class OriginalDocumentInline(admin.StackedInline):
    model = OriginalDocument

class ManuscriptEditInline(admin.StackedInline):
    model = ManuscriptEdit

class ManuscriptOrderAdmin(admin.ModelAdmin):
    inlines = [OriginalDocumentInline, ManuscriptEditInline]

admin.site.register(ManuscriptOrder, ManuscriptOrderAdmin)

class PricePointInline(admin.StackedInline):
    model = PricePoint

class ServiceListAdmin(admin.ModelAdmin):
    inlines = [PricePointInline]

admin.site.register(ServiceList, ServiceListAdmin)

class SubjectInline(admin.StackedInline):
    model = Subject

class SubjectCategoryAdmin(admin.ModelAdmin):
    inlines = [SubjectInline]

admin.site.register(SubjectCategory, SubjectCategoryAdmin)

class SubjectCategoryInline(admin.StackedInline):
    model = SubjectCategory

class SubjectListAdmin(admin.ModelAdmin):
    inlines = [SubjectCategoryInline]

admin.site.register(SubjectList, SubjectListAdmin)

