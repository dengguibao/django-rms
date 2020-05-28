from django.conf import settings as origin_settings

def settings(request):
    return {'settings': origin_settings}