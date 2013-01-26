from django.conf import settings

def global_context(request):
    return {
        'google_tracking_id': settings.GOOGLE_TRACKING_ID,
        'root_url': settings.ROOT_URL,
        }
