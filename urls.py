from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.create_update import create_object
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from swe.views import home

admin.autodiscover()

urlpatterns = patterns('swe.views',
    url(r'^[/]?$', 'home'),
    url(r'^home[/]?$', 'home'),
    url(r'^service[/]?$', 'service'),
    url(r'^prices[/]?$', 'prices'),
    url(r'^about[/]?$', 'about'),
    url(r'^register[/]?$', 'register'),
    url(r'^confirm[/]?$', 'confirm'),
    url(r'^confirm/(?P<activation_key>\w+)$', 'confirm'),
    url(r'^activationrequest[/]?$', 'activationrequest'),
    url(r'^login[/]?$', 'login'),
    url(r'^logout[/]?$', 'logout'),
    url(r'^account[/]?$', 'account'),
    url(r'^order[/]?$', 'order'),
    url(r'^privacy[/]?$', 'privacy'),
    url(r'^terms[/]?$', 'terms'),
    url(r'^contact[/]?$', 'contact'),
    url(r'^careers[/]?$', 'careers'),
    url(r'^comebacksoon[/]?$', 'block'),
)

urlpatterns += patterns('swe.editorviews',
    url(r'^editor[/]?$', 'home'),
    url(r'^editor/home[/]?$', 'home'),
    )

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
    )

urlpatterns += staticfiles_urlpatterns()

if not settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )
