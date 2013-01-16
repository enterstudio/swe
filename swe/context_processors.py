from django.conf import settings

def global_context(request):
    return {
        'is_authenticated': request.user.is_authenticated,
        'GOOGLE_TRACKING_ID': settings.GOOGLE_TRACKING_ID,
        'root_url': settings.ROOT_URL,
        }
