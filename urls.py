from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponseRedirect
from django.views.generic.simple import redirect_to


admin.autodiscover()

urlpatterns = patterns('swe.views',
                       url(r'^test/$', 'test'),
                       # Content pages
                       url(r'^$', 'home'),
                       url(r'^home/$', 'home'),
                       url(r'^service/$', 'service'),
                       url(r'^prices/$', 'prices'),
                       url(r'^about/$', 'about'),
                       url(r'^register/$', 'register'),
                       url(r'^privacy/$', 'privacy'),
                       url(r'^terms/$', 'terms'),
                       url(r'^contact/$', 'contact'),
                       url(r'^careers/$', 'careers'),
                       # Misc forms
                       url(r'^confirm/(?P<activation_key>\w*)$', 'confirmactivation'),
                       url(r'^activationrequest/$', 'activationrequest'),
                       url(r'^login/$', 'login'),
                       url(r'^logout/$', 'logout'),
                       url(r'^account/$', 'account'),
                       url(r'^resetpassword/$', 'requestresetpassword'),
                       url(r'^newpassword/(?P<resetpassword_key>\w*)$', 'completeresetpassword'),
                       url(r'^changepassword/$', 'changepassword'),
                       url(r'^claimdiscount/$', 'claimdiscount'),
                       # Order
                       url(r'^order/$', redirect_to, {'url': '/order/1/'}),
                       url(r'^order/1/$', 'uploadmanuscript'),
                       url(r'^order/2/$', 'orderdetails'),
                       url(r'^order/3/$', 'serviceoptions'),
                       url(r'^order/4/$', 'submit'),
                       # Payment processing
                       url(r'^awsconfirm/$', 'awsconfirm'),
                       url(r'^paymentreceived/$', 'paymentreceived'),
                       url(r'^paymentcanceled/$', 'paymentcanceled'),
)

if settings.BLOCK_SERVICE:
    urlpatterns += patterns('swe.views', url(r'^comebacksoon/$', 'block'))

urlpatterns += patterns('',
    (r'^fj3i28/j23ifo2/a8v892/fjuw37822jir/$', include('paypal.standard.ipn.urls')),
)

urlpatterns += patterns('',
    url(r'^044096020admin/', include(admin.site.urls)),
    )

urlpatterns += staticfiles_urlpatterns()
