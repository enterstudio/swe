from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.create_update import create_object
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
import django
from swe.views import home

admin.autodiscover()

urlpatterns = patterns('swe.views',
    url(r'^/$', 'home'),
    url(r'^home/$', 'home'),
    url(r'^service/$', 'service'),
    url(r'^prices/$', 'prices'),
    url(r'^about/$', 'about'),
    url(r'^register/$', 'register'),
    url(r'^confirm/$', 'confirm'),
    url(r'^confirm/(?P<activation_key>\w+)$', 'confirm'),
    url(r'^activationrequest/$', 'activationrequest'),
    url(r'^login/$', 'login'),
    url(r'^logout/$', 'logout'),
    url(r'^account/$', 'account'),
    url(r'^order/$', 'order'),
    url(r'^privacy/$', 'privacy'),
    url(r'^terms/$', 'terms'),
    url(r'^contact/$', 'contact'),
    url(r'^careers/$', 'careers'),
    url(r'^comebacksoon/$', 'block'),
    url(r'^paypal/$', 'paypal', name='paypal'),
    url(r'^paymentreceived/$', 'paymentreceived'),
    url(r'^paymentcanceled/$', 'paymentcanceled'),
)

urlpatterns += patterns('',
    (r'^fj3i28/j23ifo2/a8v892/fjuw37822jir/$', include('paypal.standard.ipn.urls')),
)

urlpatterns += patterns('swe.editorviews',
    url(r'^editor[/]?$', 'home'),
    url(r'^editor/home[/]?$', 'home'),
    )

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
    )

urlpatterns += staticfiles_urlpatterns()
