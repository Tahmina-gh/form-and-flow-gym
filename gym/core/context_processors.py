from django.conf import settings

def site(request):
    return {
        'SITE_NAME': 'Form & Flow',
        'WHATSAPP_LINK': 'https://wa.me/%s' % settings.WHATSAPP_NUMBER,
    }
