from django import template
from django.conf import settings

class RequestGlobalContext(template.RequestContext):
    def __init__(self,request, variables):
        # These are universal context settings
        variables['is_authenticated']=request.user.is_authenticated()
        variables['is_editor']=request.user.groups.filter(name='Editors').exists() or request.user.groups.filter(name='Managers').exists()
        variables['is_manager']=request.user.groups.filter(name='Managers').exists()
        variables['GOOGLE_TRACKING_ID']=settings.GOOGLE_TRACKING_ID
        return super(RequestGlobalContext,self).__init__(request, variables)
