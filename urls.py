from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponseRedirect
from django.views.generic.simple import redirect_to


admin.autodiscover()

urlpatterns = patterns('swe.views',
    url(r'^test$', 'test'),
    url(r'^$', 'home'),
    url(r'^home/$', 'home'),
    url(r'^service/$', 'service'),
    url(r'^prices/$', 'prices'),
    url(r'^about/$', 'about'),
    url(r'^register/$', 'register'),
    url(r'^confirm/(?P<activation_key>\w*)$', 'confirmactivation'),
    url(r'^activationrequest/$', 'activationrequest'),
    url(r'^login/$', 'login'),
    url(r'^logout/$', 'logout'),
    url(r'^account/$', 'account'),
    url(r'^order/$', redirect_to, {'url': '/order/1/'}),
    url(r'^order/1/$', 'order'),
    url(r'^order/2/$', 'serviceoptions'),
    url(r'^order/3/$', 'uploadmanuscript'),
    url(r'^awsconfirm/$', 'awsconfirm'),
    url(r'^order/4/$', 'submit'),
    url(r'^privacy/$', 'privacy'),
    url(r'^terms/$', 'terms'),
    url(r'^contact/$', 'contact'),
    url(r'^careers/$', 'careers'),
    url(r'^resetpassword/$', 'requestresetpassword'),
    url(r'^newpassword/(?P<resetpassword_key>\w*)$', 'completeresetpassword'),
    url(r'^changepassword/$', 'changepassword'),
    url(r'^comebacksoon/$', 'block'),
    url(r'^paymentreceived/$', 'paymentreceived'),
    url(r'^paymentcanceled/$', 'paymentcanceled'),
)

urlpatterns += patterns('',
    (r'^fj3i28/j23ifo2/a8v892/fjuw37822jir/$', include('paypal.standard.ipn.urls')),
)

urlpatterns += patterns('',
    url(r'^044096020admin/', include(admin.site.urls)),
    )

urlpatterns += staticfiles_urlpatterns()


